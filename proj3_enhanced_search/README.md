# Project 3: Enhanced Search Bookmarklet

## Overview

This project creates a browser bookmarklet that automates alternative search engine queries. Instead of manually copying and pasting search terms between different search engines, this tool allows you to quickly open your current Google search query in other search engines with a single click.

## Challenge

When researching or comparing information, you often want to see results from multiple search engines:
- **Google** - Most comprehensive but may have filter bubbles
- **DuckDuckGo** - Privacy-focused, different ranking algorithm
- **Bing** - Microsoft's search engine with different results
- **Brave Search** - Independent index, no tracking

Manually copying search queries and opening new tabs for each engine is time-consuming and interrupts your workflow.

## Solution

A JavaScript bookmarklet that:
- Extracts the current search query from Google search results
- Prompts you to choose an alternative search engine
- Opens the same query in your chosen engine in a new tab
- Works instantly without leaving your current page

## How It Works

The bookmarklet is a small JavaScript snippet that:
1. Reads the search query from the current Google search URL
2. Shows a prompt asking which search engine to use
3. Constructs the appropriate search URL for the chosen engine
4. Opens the search in a new tab

## Usage

### Installation

1. Open `bookmark.txt` and copy the entire JavaScript code
2. Create a new bookmark in your browser
3. Edit the bookmark and paste the code as the URL
4. Name it something like "Search Alternative" or "Alt Search"

### Using the Bookmarklet

1. Perform a search on Google (e.g., search for "Python web scraping")
2. Click your bookmarklet
3. Choose which search engine to use:
   - `1` = DuckDuckGo
   - `2` = Bing
   - `3` = Brave Search
4. A new tab opens with the same search query on your chosen engine

## Supported Search Engines

- **DuckDuckGo** (`1`) - Privacy-focused search
- **Bing** (`2`) - Microsoft's search engine
- **Brave Search** (`3`) - Independent search index

## Key Learnings

- **Browser Automation**: Learned how to use JavaScript to interact with browser APIs
- **URL Manipulation**: Understanding how to parse and construct URLs with query parameters
- **Bookmarklet Development**: Creating useful browser extensions without complex setup
- **User Experience**: Designing simple interfaces (prompts) for quick interactions
- **Cross-Platform Search**: Understanding how different search engines structure their URLs

## Technical Details

The bookmarklet:
- Uses `URLSearchParams` to extract the search query from Google's URL
- Uses `window.open()` to open new tabs securely
- Includes `noopener,noreferrer` for security
- Uses `encodeURIComponent()` to properly encode search queries

## Files

- `bookmark.txt` - The JavaScript bookmarklet code (URL-encoded)

## Example Use Cases

- **Research Comparison**: Compare how different search engines rank the same query
- **Privacy Alternative**: Quickly switch to DuckDuckGo for privacy-focused searches
- **Result Diversity**: See different perspectives on the same topic
- **Bypass Filters**: Check if search results differ across engines

## Future Enhancements

Potential improvements:
- Add more search engines (Yahoo, Startpage, etc.)
- Keyboard shortcuts for faster selection
- Remember last used search engine
- Support for other search engines as starting point (not just Google)
- Batch open in multiple engines at once

## Browser Compatibility

Works in all modern browsers that support:
- JavaScript ES6+ features
- `URLSearchParams` API
- `window.open()` method

Tested on: Chrome, Firefox, Safari, Edge
