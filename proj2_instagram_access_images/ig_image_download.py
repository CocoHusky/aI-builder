import argparse
import json
import re
import time
from pathlib import Path
from typing import List, Optional, Set

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Keep CDN-like URLs
CDN_HOST_RE = re.compile(r"(cdninstagram\.com|fbcdn\.net|scontent[^/]+)", re.IGNORECASE)

# Drop IG UI assets (your example)
UI_ASSET_RE = re.compile(r"(static\.cdninstagram\.com/rsrc\.php|/rsrc\.php/)", re.IGNORECASE)


def normalize_profile_url(profile: str) -> str:
    profile = profile.strip()
    if profile.startswith("http"):
        return profile if profile.endswith("/") else profile + "/"
    return f"https://www.instagram.com/{profile.strip('/')}/"


def pick_best_from_srcset(srcset: str) -> Optional[str]:
    """
    srcset format: "url1 150w, url2 320w, url3 640w"
    Pick the largest width entry.
    """
    if not srcset:
        return None
    best_url = None
    best_w = -1
    for entry in [e.strip() for e in srcset.split(",") if e.strip()]:
        parts = entry.split()
        if not parts:
            continue
        url = parts[0]
        w = -1
        if len(parts) >= 2 and parts[1].endswith("w"):
            try:
                w = int(parts[1][:-1])
            except ValueError:
                w = -1
        if w > best_w:
            best_w = w
            best_url = url
    return best_url


def is_ui_asset(url: str) -> bool:
    return bool(UI_ASSET_RE.search(url or ""))


def looks_like_post_media(url: str) -> bool:
    """
    Heuristic to keep likely media thumbnails while rejecting UI assets.
    IG media URLs commonly contain scontent/fbcdn and often t51.2885.
    """
    if not url or not url.startswith("http"):
        return False
    if is_ui_asset(url):
        return False
    if not CDN_HOST_RE.search(url):
        return False

    u = url.lower()
    return any(
        token in u
        for token in (
            "scontent",
            "fbcdn",
            "t51.2885",
            "/v/t51",
        )
    )


def extract_profile_grid_image_urls(profile_url: str, headless: bool = True, max_scrolls: int = 5) -> List[str]:
    """
    Render the profile page and scrape only the post grid thumbnails.
    """
    urls: Set[str] = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()

        page.goto(profile_url, wait_until="domcontentloaded", timeout=45_000)

        # If IG shows a login wall, article may still exist but grid might not populate.
        try:
            page.wait_for_selector("article", timeout=15_000)
        except PlaywrightTimeoutError:
            pass

        # Scroll to load more tiles
        for _ in range(max_scrolls):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)

        # KEY: only images inside post links within the grid
        img_elems = page.query_selector_all("article a img")

        for img in img_elems:
            src = img.get_attribute("src") or ""
            srcset = img.get_attribute("srcset") or ""
            candidate = pick_best_from_srcset(srcset) or src
            if not candidate:
                continue

            # Remove UI assets and keep likely media
            if looks_like_post_media(candidate):
                urls.add(candidate)

        context.close()
        browser.close()

    return sorted(urls)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Extract Instagram post-grid image URLs from a public profile using Playwright."
    )
    ap.add_argument("profile", nargs="?", default="https://www.instagram.com/grapeot/")
    ap.add_argument("--out", default="", help="Output JSON path (default: data/<username>/image_urls.json)")
    ap.add_argument("--headed", action="store_true", help="Run with a visible browser window (debug)")
    ap.add_argument("--max-scrolls", type=int, default=5, help="How many scrolls to load more posts")
    args = ap.parse_args()

    url = normalize_profile_url(args.profile)
    username = url.rstrip("/").split("/")[-1] or "instagram_user"

    proj_dir = Path(__file__).resolve().parent
    out_path = Path(args.out) if args.out else (proj_dir / "data" / username / "image_urls.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading (Playwright): {url}")
    urls = extract_profile_grid_image_urls(url, headless=not args.headed, max_scrolls=args.max_scrolls)

    data = {
        "profile": username,
        "profile_url": url,
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "image_count": len(urls),
        "image_urls": urls,
    }

    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Saved {len(urls)} URLs -> {out_path}")

    if len(urls) == 0:
        print("\nNo URLs found. Common reasons:")
        print("- IG served a login wall / anti-bot page.")
        print("- Profile has restricted content.")
        print("- Try: --headed and increase --max-scrolls.\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
