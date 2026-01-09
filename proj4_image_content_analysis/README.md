# Project 4: Image Content Analysis Using GPT-4o

## Overview

This project demonstrates how to use GPT-4o's multimodal capabilities to analyze image content and store structured information in a SQL database. The application provides a GUI for selecting images and automatically extracts detailed information including objects, people, places, and other contextual details.

## Challenge

Analyzing image content manually is time-consuming and subjective. Many applications require automated image understanding for:
- **Content Moderation**: Identifying inappropriate content
- **Accessibility**: Generating alt-text descriptions
- **Cataloging**: Organizing image libraries with metadata
- **Research**: Analyzing visual data at scale
- **Surveillance**: Object and person detection

This project addresses these needs by leveraging AI to provide consistent, detailed image analysis.

## Solution

A Python application with:
- **GUI Interface**: Easy-to-use file browser for selecting images
- **GPT-4o Integration**: Uses OpenAI's vision model for detailed image analysis
- **Structured Data Extraction**: Parses analysis into categories (summary, items, persons, places, things, details)
- **SQL Database**: Stores all analyses in a growing database for future reference
- **Persistent Storage**: Each analysis is saved and can be reviewed later

## Learning Objectives

### 1. Learn how to integrate AI models for image analysis

- Understood how to use OpenAI's GPT-4o vision API
- Learned to encode images in base64 format for API transmission
- Explored multimodal AI capabilities (text + image inputs)
- Discovered how to structure prompts for consistent JSON output

### 2. Develop skills in working with APIs and handling different data types

- Worked with REST APIs and API keys
- Handled image encoding and transmission
- Managed API responses and error handling
- Learned to parse and validate JSON responses from AI models

### 3. Understand the capabilities and limitations of multimodal AI

- Discovered what GPT-4o can accurately identify in images
- Learned about edge cases and when the model might struggle
- Understood the importance of prompt engineering for structured output
- Explored the balance between detail and accuracy

### 4. Enhance problem-solving skills by addressing challenges in AI-assisted programming

- Designed database schema for storing structured image data
- Created GUI for user-friendly interaction
- Handled API errors and edge cases gracefully
- Iterated on prompt design to get consistent JSON output

## Technologies

- **Python**: Core programming language
- **OpenAI API**: GPT-4o for image analysis
- **SQLite**: Database for storing analyses
- **Tkinter**: GUI framework for file selection and results display
- **Base64**: Image encoding for API transmission

## Installation

### Prerequisites

1. Python 3.8 or higher
2. OpenAI API key (get one at https://platform.openai.com/)

### Setup

1. Install required packages:
```bash
pip install openai
```

2. Set your OpenAI API key as an environment variable:

### Using the GUI

1. **Select Image**: Click "Browse..." to choose an image file
2. **Analyze**: Click "Analyze Image" to process with GPT-4o
3. **View Results**: See structured analysis in the results panel
4. **Database**: Results are automatically saved to SQLite database
5. **Review**: Use "View All Analyses" to see previous analyses

### Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

## Database Schema

The application creates a SQLite database at `data/image_analysis.db` with the following structure:

```sql
CREATE TABLE image_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT NOT NULL,
    image_filename TEXT NOT NULL,
    summary TEXT,
    items TEXT,
    persons TEXT,
    places TEXT,
    things TEXT,
    other_details TEXT,
    raw_response TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(image_path)
)
```

### Table Columns

- **id**: Unique identifier for each analysis
- **image_path**: Full path to the analyzed image
- **image_filename**: Just the filename
- **summary**: Brief description of the image
- **items**: Comma-separated list of all items detected
- **persons**: People visible in the image
- **places**: Locations or settings
- **things**: Inanimate objects
- **other_details**: Additional context (colors, mood, weather, etc.)
- **raw_response**: Full JSON response from API
- **analyzed_at**: Timestamp of analysis

## Features

- **GUI File Browser**: Easy image selection
- **Automatic Analysis**: One-click image analysis
- **Structured Output**: Organized into categories
- **Database Storage**: Persistent storage of all analyses
- **View History**: Browse all previous analyses
- **Error Handling**: Graceful handling of API errors

## Example Output

```
SUMMARY
A sunny day at a beach with people playing volleyball and relaxing on the sand.

ITEMS DETECTED
volleyball net, beach ball, sand, ocean, palm trees, beach chairs, towels

PERSONS
Two people playing volleyball, several people sitting on beach chairs

PLACES
Beach, oceanfront, tropical location

THINGS
Volleyball net, beach ball, beach chairs, towels, sand

OTHER DETAILS
Bright sunny day, clear blue sky, warm weather, tropical setting, recreational activity
```

## API Costs

**Note**: GPT-4o API usage incurs costs. Check OpenAI's pricing:
- Image input: ~$0.01-0.03 per image (depending on resolution)
- Text output: Minimal cost for responses

The database helps avoid re-analyzing the same images.

## Files

- `imagerecognition_chatgpt-4o.py` - Main application script
- `data/image_analysis.db` - SQLite database (created automatically)
- `README.md` - This file

## Future Enhancements

Potential improvements:
- Batch processing multiple images
- Export database to CSV/JSON
- Image preview in GUI
- Search/filter database entries
- Custom prompt templates
- Support for video frames
- Integration with other vision APIs
- Confidence scores for detections

## Troubleshooting

### API Key Issues
- Ensure `OPENAI_API_KEY` environment variable is set
- Check that your API key is valid and has credits
- Verify you have access to GPT-4o model

### Database Issues
- Ensure write permissions in the project directory
- Check that `data/` folder can be created

### Image Issues
- Verify image file is not corrupted
- Check file size (very large images may timeout)
- Ensure image format is supported

## Ethical Considerations

- **Privacy**: Be mindful of analyzing images containing personal information
- **API Usage**: Respect rate limits and terms of service
- **Data Storage**: Consider security of stored image paths and analyses
- **Bias**: Be aware that AI models may have biases in image recognition

## Project Context

This project is part of a series exploring different aspects of AI and data processing:
- **Project 0**: Database visualization
- **Project 1**: Web scraping
- **Project 2**: Dynamic content extraction
- **Project 3**: Browser automation tools
- **Project 4**: Multimodal AI integration (this project)
