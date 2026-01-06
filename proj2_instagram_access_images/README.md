# Project 2: Instagram Image URL Extraction

## Overview

This project demonstrates how to handle dynamically loaded web content and navigate platform restrictions when scraping. Instagram loads content with JavaScript, making simple HTTP requests insufficient for extracting public content.

## Challenge

Instagram's modern web interface presents several obstacles:
- **Dynamic Content Loading**: Content loads with JavaScript, not in initial HTML
- **Anti-Scraping Measures**: Instagram detects and blocks simple automated requests
- **Full Page Rendering Required**: Pages must be fully rendered before content is available
- **Mixed Assets**: UI elements and actual post images use similar URL patterns, making filtering necessary

Simple HTTP requests return only the initial HTML shell without the actual post images, requiring a browser-based approach.

## Solution

Built a Playwright-based scraper that:
- Renders pages with a headless browser to execute JavaScript
- Targets specific DOM elements (post grid images) while filtering out UI assets
- Handles srcset attributes to extract highest-quality image URLs
- Implements respectful scraping practices (delays, proper user agents)
- Saves image URLs to JSON for later viewing or downloading

## Learning Objectives

### 1. Learn to navigate platform restrictions ethically

Understood the difference between:
- **Ethical scraping**: Public content, rate limiting, respecting robots.txt
- **Unethical practices**: Violating terms of service, aggressive scraping, bypassing security measures

Learned to implement respectful delays and proper user agents to minimize impact on servers.

### 2. Gain experience in using browser developer tools for network analysis

Used DevTools to:
- Analyze network requests and identify CDN patterns
- Distinguish between UI assets and actual content URLs
- Inspect DOM structure after JavaScript execution
- Debug selector issues and timing problems

### 3. Understand how to handle dynamically loaded content

Discovered that many modern websites require JavaScript execution:
- Learned to use Playwright to render pages fully before extraction
- Handled scroll-based lazy loading of content
- Waited for specific DOM elements to appear
- Managed timing issues with proper waits and delays

### 4. Develop AI-assisted programming skills for automating complex tasks

Used AI to:
- Design the scraping strategy and selector approach
- Debug selector issues and optimize extraction logic
- Handle edge cases (srcset attributes, UI asset filtering)
- Iterate on code based on Instagram's specific structure

## Technologies

- Python
- Playwright (browser automation)
- Regex (URL pattern matching)
- JSON

## Usage

```bash
# Use default profile (grapeot)
python ig_image_download.py

# Specify a profile
python ig_image_download.py https://www.instagram.com/username/

# Run with visible browser (for debugging)
python ig_image_download.py --headed

# Increase scrolls to load more posts
python ig_image_download.py --max-scrolls 10
```

## Output

Saves image URLs to JSON files in `data/{username}/`:
- `image_urls.json` - Contains profile info and list of image URLs
- URLs are cleaned and deduplicated
- Highest quality versions are selected from srcset attributes

## Files

- `ig_image_download.py` - Main scraping script
- `data/{username}/image_urls.json` - Extracted URLs for each profile

## Key Features

- **Smart Filtering**: Distinguishes between post images and UI assets
- **Quality Selection**: Picks highest resolution from srcset attributes
- **Respectful Scraping**: Implements delays and proper headers
- **Error Handling**: Gracefully handles timeouts and missing elements
- **Flexible Configuration**: Command-line options for different use cases

## Ethical Considerations

- Only scrapes public profiles
- Implements rate limiting with delays
- Uses proper user agents
- Respects Instagram's terms of service
- For educational purposes only
