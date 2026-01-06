# Project 0: SQL Database Visualization

## Overview

This project demonstrates how to programmatically analyze and visualize database structures. When working with complex databases, understanding the schema, relationships, and data distribution is crucial for effective data analysis.

## Challenge

Understanding the structure of a complex database with multiple tables and relationships can be overwhelming when looking at raw SQL schemas. The Northwind database contains 14 tables with various relationships, making it difficult to get a high-level overview.

## Solution

Built a Python tool that:
- Connects to SQLite databases and extracts schema information
- Generates interactive HTML reports with visual representations
- Creates Entity-Relationship (ER) diagrams using Mermaid.js
- Displays block-based table structure visualizations
- Shows sample data previews for each table
- Provides comprehensive summary statistics

## Key Learnings

- **Database Metadata Extraction**: Learned to use SQLite PRAGMA commands to extract table information, column types, primary keys, and foreign key relationships
- **Data Visualization**: Created interactive HTML reports with embedded JavaScript libraries (Mermaid.js) to visualize complex data structures
- **Schema Analysis**: Understood how to programmatically analyze database schemas and present them in human-readable formats
- **Relationship Mapping**: Learned to identify and visualize foreign key relationships between tables

## Technologies

- Python
- SQLite
- Pandas
- Mermaid.js
- HTML/CSS/JavaScript

## Usage

```bash
python sqlite_experiment_v1.py
```

This will:
1. Connect to the Northwind database
2. Extract schema information
3. Generate an interactive HTML report (`northwind_database_report.html`)
4. Display summary statistics in the console

## Output

- **Console Output**: Summary statistics and table information
- **HTML Report**: Interactive visualization with:
  - ER diagram showing table relationships
  - Block-based table structure cards
  - Sample data from each table
  - Comprehensive statistics

## Files

- `sqlite_experiment_v1.py` - Main script for database analysis
- `northwind_database_report.html` - Generated interactive report
- `data/northwind.db` - Sample database
