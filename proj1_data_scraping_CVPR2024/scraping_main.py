import json
import re
import os
import time
import random
import secrets
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

import bibtexparser


BASE_URL = "https://openaccess.thecvf.com/"
ALL_URL = "https://openaccess.thecvf.com/CVPR2024?day=all"


# ----------------------------
# Utilities
# ----------------------------

def generate_unique_id() -> str:
    """
    Random, extremely low collision probability, URL-safe-ish string.
    Example: 'cvpr24_8fK2nQx4m1pZbT7s'
    """
    token = secrets.token_urlsafe(12).replace("-", "").replace("_", "")
    return f"cvpr24_{token}"


def make_session() -> requests.Session:
    s = requests.Session()
    # Browser-ish headers to reduce the odds of being blocked
    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    })
    return s


def get_html(session: requests.Session, url: str, timeout: int = 30) -> str:
    r = session.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text


def sleep_polite(min_s: float = 0.3, max_s: float = 1.0) -> None:
    time.sleep(random.uniform(min_s, max_s))


def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


# ----------------------------
# Parsing: list page
# ----------------------------

def extract_paper_page_urls(all_html: str) -> List[str]:
    """
    Extracts links to individual paper detail pages from the 'all papers' list page.

    CVF typically links to:
      /content/CVPR2024/html/<...>_paper.html
    """
    soup = BeautifulSoup(all_html, "lxml")
    links = soup.find_all("a", href=True)

    paper_urls = []
    for a in links:
        href = a["href"].strip()
        if "/content/CVPR2024/html/" in href and href.endswith("_paper.html"):
            paper_urls.append(urljoin(BASE_URL, href))

    # De-duplicate while preserving order
    seen = set()
    deduped = []
    for u in paper_urls:
        if u not in seen:
            seen.add(u)
            deduped.append(u)

    return deduped


# ----------------------------
# Parsing: detail paper page
# ----------------------------

@dataclass
class PaperRecord:
    id: str
    title: str
    authors: List[str]
    paper_url: str
    abstract: Optional[str]
    links: Dict[str, Optional[str]]          # pdf/supp/arxiv
    bibtex_raw: Optional[str]
    bibtex_fields: Dict[str, str]            # parsed key->value


def _extract_bibtex_text_from_page_text(page_text: str) -> Optional[str]:
    """
    Finds the BibTeX entry in the page's visible text.
    On CVF pages, it often appears as one block starting with '@InProceedings{...'.
    """
    # Make it robust to newlines/spaces
    text = page_text

    # Capture from the first '@' bibtex entry through the matching closing brace.
    # This pattern is conservative: it grabs '@Something{...}' until the last '}'.
    m = re.search(r"(@\w+\s*{.*})\s*$", text, flags=re.DOTALL)
    if m:
        return m.group(1).strip()

    # Fallback: find the first '@InProceedings' and take until last '}'
    idx = text.find("@InProceedings")
    if idx != -1:
        chunk = text[idx:].strip()
        last = chunk.rfind("}")
        if last != -1:
            return chunk[: last + 1].strip()

    return None


def _parse_bibtex_fields(bibtex_raw: str) -> Dict[str, str]:
    """
    Parses BibTeX to a dict of fields (author/title/booktitle/month/year/pages/etc.)
    using bibtexparser.
    """
    try:
        db = bibtexparser.loads(bibtex_raw)
        if not db.entries:
            return {}
        entry = db.entries[0]
        # Remove internal keys you might not want; keep if useful
        # 'ID' is the bibtex key (e.g., Bandyopadhyay_2024_CVPR)
        fields = {}
        for k, v in entry.items():
            # Normalize to strings and strip
            if v is None:
                continue
            fields[str(k)] = clean_text(str(v))
        return fields
    except Exception:
        # If parsing fails, keep empty fields rather than crashing the whole run
        return {}


def parse_paper_detail(session: requests.Session, paper_url: str) -> PaperRecord:
    html = get_html(session, paper_url)
    soup = BeautifulSoup(html, "lxml")

    # Title: best-effort extraction.
    # CVF pages tend to have the title as a prominent text line near the top.
    # Heuristic: first large header-like element, else first strong-ish title candidate.
    title = None
    for tag in ["h1", "h2", "h3"]:
        el = soup.find(tag)
        if el and clean_text(el.get_text()):
            title = clean_text(el.get_text())
            break
    if not title:
        # Fallback: use the document title minus site boilerplate
        title = clean_text(soup.title.get_text()) if soup.title else "UNKNOWN_TITLE"

    # Authors: On CVF pages, authors line is near title.
    # Heuristic: find the first line containing '; Proceedings of' and split before ';'
    page_text = soup.get_text("\n", strip=True)
    authors_line = None
    for line in page_text.splitlines():
        if "; Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition" in line:
            # Format: "Author1, Author2; Proceedings of ..."
            authors_line = line.split(";")[0].strip()
            break

    authors: List[str] = []
    if authors_line:
        authors = [a.strip() for a in authors_line.split(",") if a.strip()]

    # Abstract: find the "Abstract" heading and take the following text block
    abstract = None
    # Heuristic: locate a line that is exactly "Abstract", then take subsequent lines until "Related Material"
    lines = page_text.splitlines()
    try:
        аб_idx = next(i for i, l in enumerate(lines) if l.strip() == "Abstract")
        # collect until "Related Material" or "Bibtex" or end
        collected = []
        for j in range(аб_idx + 1, len(lines)):
            if lines[j].strip() in {"Related Material", "[bibtex]", "bibtex"}:
                break
            collected.append(lines[j])
        abstract = clean_text(" ".join(collected)) if collected else None
    except StopIteration:
        abstract = None

    # Related material links: anchors whose text is pdf/supp/arXiv
    links: Dict[str, Optional[str]] = {"pdf": None, "supp": None, "arxiv": None}
    for a in soup.find_all("a", href=True):
        txt = clean_text(a.get_text()).lower()
        href = urljoin(BASE_URL, a["href"])
        if txt == "pdf":
            links["pdf"] = href
        elif txt == "supp":
            links["supp"] = href
        elif txt == "arxiv":
            links["arxiv"] = href

    # BibTeX raw + parsed fields
    bibtex_raw = _extract_bibtex_text_from_page_text(page_text)
    bibtex_fields = _parse_bibtex_fields(bibtex_raw) if bibtex_raw else {}

    return PaperRecord(
        id=generate_unique_id(),
        title=title,
        authors=authors,
        paper_url=paper_url,
        abstract=abstract,
        links=links,
        bibtex_raw=bibtex_raw,
        bibtex_fields=bibtex_fields,
    )


# ----------------------------
# Main
# ----------------------------

def main(
    out_path: str = "cvpr2024_all_papers.json",
    limit: Optional[int] = None,
    polite_delay: Tuple[float, float] = (0.3, 0.9),
) -> None:
    session = make_session()

    # 1) Fetch the all-papers list page
    all_html = get_html(session, ALL_URL)
    paper_urls = extract_paper_page_urls(all_html)

    if not paper_urls:
        raise RuntimeError(
            "No paper detail URLs found on the ALL page. "
            "The site may have changed HTML structure or blocked the request."
        )

    # Handle limit: 0 means all papers, None means all papers, positive number limits
    if limit is not None and limit > 0:
        paper_urls = paper_urls[:limit]

    # 2) Visit each paper page and extract rich metadata
    records: List[Dict] = []
    for url in tqdm(paper_urls, desc="Scraping paper pages"):
        try:
            rec = parse_paper_detail(session, url)
            records.append({
                "id": rec.id,
                "title": rec.title,
                "authors": rec.authors,
                "paper_url": rec.paper_url,
                "abstract": rec.abstract,
                "links": rec.links,                 # {"pdf":..., "supp":..., "arxiv":...}
                "bibtex_raw": rec.bibtex_raw,
                "bibtex_fields": rec.bibtex_fields, # dict: author/title/booktitle/month/year/pages/ID/ENTRYTYPE/etc
            })
        except Exception as e:
            # Keep going; record failures for later debugging
            records.append({
                "id": generate_unique_id(),
                "paper_url": url,
                "error": str(e),
            })

        sleep_polite(*polite_delay)

    # 3) Write JSON
    payload = {
        "source": ALL_URL,
        "scraped_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "paper_count": len(records),
        "papers": records,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Wrote: {out_path}  (papers={len(records)})")


if __name__ == "__main__":
    # Set limit: 0 or None = all papers, positive number = top N papers
    limit = 0
    
    # Generate filename based on limit
    if limit is None or limit == 0:
        filename = "cvpr2024_all_papers.json"
    else:
        filename = f"cvpr2024_top_{limit}_papers.json"
    
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    output_path = os.path.join(data_dir, filename)
    main(out_path=output_path, limit=limit)
