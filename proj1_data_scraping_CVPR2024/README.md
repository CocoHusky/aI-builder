# Project 1: Academic Paper Scraping (CVPR 2024)

## Overview

This project demonstrates web scraping techniques for extracting structured data from academic conference websites. Research papers are published on conference websites, but accessing metadata (titles, authors, abstracts, PDF links) programmatically requires understanding how web pages are structured.

## Challenge

The CVPR 2024 conference website contains hundreds of papers. Manually collecting metadata (titles, authors, abstracts, BibTeX, PDF links) would be time-consuming and error-prone. We needed a way to programmatically extract this information.

## Solution

Developed a web scraper that:
- Extracts paper URLs from the conference listing page
- Parses individual paper pages to collect metadata
- Handles BibTeX data extraction and parsing
- Saves structured JSON output for further analysis
- Implements polite scraping with delays and error handling

## Learning Objectives

### 1. Understand how HTML serves as a bridge between GUIs and APIs

Learned that web pages are essentially structured documents that can be parsed programmatically, even when they appear as visual interfaces. HTML contains the data we need, just structured differently than a traditional API.

### 2. Gain proficiency in using browser developer tools

Used browser DevTools to:
- Inspect network requests to understand data flow
- Analyze HTML structure to identify data patterns
- Test CSS selectors and XPath expressions
- Debug parsing issues in real-time

### 3. Learn how to leverage AI assistance in generating code

Used AI to:
- Generate regex patterns for data extraction
- Create HTML parsing logic with BeautifulSoup
- Design error handling strategies
- Iterate on code improvements based on edge cases

### 4. Develop skills in parsing and structuring data from web pages

Mastered:
- BeautifulSoup for HTML parsing and navigation
- Handling edge cases (missing data, binary content, special characters)
- Structuring output into clean JSON formats
- Data validation and cleaning

## Technologies

- Python
- BeautifulSoup4
- Requests
- BibTeX parser
- JSON

## Usage

```bash
# Scrape top 100 papers (default)
python scraping_main.py

# Scrape all papers
python scraping_main.py --limit 0

# Scrape specific number
python scraping_main.py --limit 50
```

## Output

Saves structured JSON files to `data/` directory:
- `cvpr2024_top_100_papers.json` - Contains metadata for scraped papers
- Each paper includes: title, authors, abstract, links (PDF/supplement/arXiv), BibTeX data

## Files

- `scraping_main.py` - Main scraping script
- `data/` - Directory containing scraped JSON files

## Key Features

- **Polite Scraping**: Implements delays between requests
- **Error Handling**: Continues scraping even if individual pages fail
- **BibTeX Parsing**: Extracts and parses BibTeX entries
- **Flexible Limits**: Can scrape all papers or a specific number
- **Structured Output**: Clean JSON format for easy analysis
