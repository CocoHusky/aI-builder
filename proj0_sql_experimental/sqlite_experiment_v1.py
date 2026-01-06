import sqlite3
import pandas as pd
import os
from datetime import datetime

# --- Connect to SQLite ---
# Use the database in the data folder
db_path = os.path.join(os.path.dirname(__file__), "data", "northwind.db")
conn = sqlite3.connect(db_path)

print("=" * 80)
print("NORTHWIND DATABASE - HIGH-LEVEL SUMMARY")
print("=" * 80)
print(f"\nDatabase Path: {db_path}\n")

# --- Get all tables ---
tables_query = """
SELECT name FROM sqlite_master 
WHERE type='table' 
ORDER BY name
"""
tables_df = pd.read_sql(tables_query, conn)
tables = tables_df['name'].tolist()

print(f"Total Tables: {len(tables)}\n")
print("-" * 80)

# --- Summary for each table ---
summary_data = []
table_schemas = {}  # Store detailed schema info for visualization

for table in tables:
    # Quote table name to handle spaces and special characters
    quoted_table = f'"{table}"'
    
    # Get row count
    count_query = f"SELECT COUNT(*) as count FROM {quoted_table}"
    count_df = pd.read_sql(count_query, conn)
    row_count = count_df['count'].iloc[0]
    
    # Get column information with details
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({quoted_table})")
    columns_info = cursor.fetchall()
    
    # Get foreign key information
    cursor.execute(f"PRAGMA foreign_key_list({quoted_table})")
    foreign_keys = cursor.fetchall()
    
    # Process column information
    columns = []
    primary_keys = []
    for col in columns_info:
        col_name = col[1]
        col_type = col[2]
        is_pk = col[5]  # Primary key flag
        is_not_null = col[3]
        
        columns.append({
            'name': col_name,
            'type': col_type,
            'is_primary_key': bool(is_pk),
            'is_not_null': bool(is_not_null)
        })
        
        if is_pk:
            primary_keys.append(col_name)
    
    # Process foreign keys
    fk_info = []
    for fk in foreign_keys:
        fk_info.append({
            'from_column': fk[3],  # Column in this table
            'to_table': fk[2],      # Referenced table
            'to_column': fk[4]      # Referenced column
        })
    
    table_schemas[table] = {
        'columns': columns,
        'primary_keys': primary_keys,
        'foreign_keys': fk_info,
        'row_count': row_count
    }
    
    column_names = [col['name'] for col in columns]
    
    summary_data.append({
        'Table': table,
        'Rows': row_count,
        'Columns': len(columns),
        'Column_Names': ', '.join(column_names)
    })
    
    print(f"\nTable: {table}")
    print(f"  Rows: {row_count:,}")
    print(f"  Columns: {len(columns)}")
    print(f"  Column Names: {', '.join(column_names)}")

# --- Create summary DataFrame ---
summary_df = pd.DataFrame(summary_data)
print("\n" + "=" * 80)
print("SUMMARY TABLE")
print("=" * 80)
print(summary_df.to_string(index=False))

# --- Total statistics ---
total_rows = summary_df['Rows'].sum()
print(f"\nTotal Rows Across All Tables: {total_rows:,}")
print(f"Total Tables: {len(tables)}")

# --- Sample data from each table (first few rows) ---
print("\n" + "=" * 80)
print("SAMPLE DATA FROM EACH TABLE (First 3 Rows)")
print("=" * 80)

for table in tables:
    # Quote table name to handle spaces and special characters
    quoted_table = f'"{table}"'
    sample_query = f"SELECT * FROM {quoted_table} LIMIT 3"
    try:
        sample_df = pd.read_sql(sample_query, conn)
        
        # Handle binary columns (BLOB data) - replace with readable placeholder
        for col in sample_df.columns:
            if sample_df[col].dtype == 'object':
                # Check if column contains binary data
                sample_df[col] = sample_df[col].apply(
                    lambda x: f"<BINARY DATA ({len(x)} bytes)>" if isinstance(x, bytes) else x
                )
        
        print(f"\n{table}:")
        # Truncate long text fields for better readability
        pd.set_option('display.max_colwidth', 50)
        print(sample_df.to_string(index=False))
        pd.reset_option('display.max_colwidth')
        print("-" * 80)
    except Exception as e:
        print(f"\n{table}: Error reading sample - {e}")

# --- Generate Visualizations ---
def generate_mermaid_diagram(table_schemas):
    """Generate Mermaid ER diagram code"""
    mermaid_lines = ["erDiagram"]
    
    # Create mapping for table names (handle spaces)
    table_name_map = {}
    for table_name in table_schemas.keys():
        safe_name = table_name.replace(' ', '_').replace('-', '_')
        table_name_map[table_name] = safe_name
    
    for table_name, schema in table_schemas.items():
        safe_table_name = table_name_map[table_name]
        # Add table definition
        mermaid_lines.append(f"    {safe_table_name} {{")
        
        for col in schema['columns']:
            col_name = col['name'].replace(' ', '_').replace('-', '_')
            col_type = col['type']
            pk_marker = " PK" if col['is_primary_key'] else ""
            nn_marker = " NOT NULL" if col['is_not_null'] and not col['is_primary_key'] else ""
            mermaid_lines.append(f"        {col_type} {col_name}{pk_marker}{nn_marker}")
        
        mermaid_lines.append("    }")
    
    # Add relationships
    for table_name, schema in table_schemas.items():
        for fk in schema['foreign_keys']:
            from_table = table_name_map[table_name]
            to_table = table_name_map.get(fk['to_table'], fk['to_table'].replace(' ', '_').replace('-', '_'))
            mermaid_lines.append(f"    {from_table} ||--o{{ {to_table} : \"has\"")
    
    return "\n".join(mermaid_lines)

def generate_block_visualization(table_schemas):
    """Generate block-based visualization HTML"""
    blocks_html = '<div class="schema-blocks">'
    
    for table_name, schema in table_schemas.items():
        # Group columns by type
        primary_key_cols = [col for col in schema['columns'] if col['is_primary_key']]
        foreign_key_cols = []
        regular_cols = []
        
        # Identify foreign key columns
        fk_column_names = {fk['from_column'] for fk in schema['foreign_keys']}
        
        for col in schema['columns']:
            if col['is_primary_key']:
                continue
            elif col['name'] in fk_column_names:
                foreign_key_cols.append(col)
            else:
                regular_cols.append(col)
        
        blocks_html += f'''
        <div class="table-block">
            <div class="table-block-header">
                <h3>{table_name}</h3>
                <span class="row-count">{schema['row_count']:,} rows</span>
            </div>
            <div class="table-block-body">
        '''
        
        # Primary Keys
        if primary_key_cols:
            blocks_html += '<div class="column-group pk-group">'
            blocks_html += '<div class="group-label">🔑 Primary Keys</div>'
            for col in primary_key_cols:
                blocks_html += f'''
                <div class="column-item pk-item">
                    <span class="col-name">{col['name']}</span>
                    <span class="col-type">{col['type']}</span>
                </div>
                '''
            blocks_html += '</div>'
        
        # Foreign Keys
        if foreign_key_cols:
            blocks_html += '<div class="column-group fk-group">'
            blocks_html += '<div class="group-label">🔗 Foreign Keys</div>'
            for col in foreign_key_cols:
                # Find the referenced table
                fk_ref = next((fk for fk in schema['foreign_keys'] if fk['from_column'] == col['name']), None)
                ref_info = f" → {fk_ref['to_table']}.{fk_ref['to_column']}" if fk_ref else ""
                blocks_html += f'''
                <div class="column-item fk-item">
                    <span class="col-name">{col['name']}</span>
                    <span class="col-type">{col['type']}</span>
                    <span class="col-ref">{ref_info}</span>
                </div>
                '''
            blocks_html += '</div>'
        
        # Regular Columns
        if regular_cols:
            blocks_html += '<div class="column-group regular-group">'
            blocks_html += '<div class="group-label">📋 Columns</div>'
            for col in regular_cols:
                blocks_html += f'''
                <div class="column-item regular-item">
                    <span class="col-name">{col['name']}</span>
                    <span class="col-type">{col['type']}</span>
                </div>
                '''
            blocks_html += '</div>'
        
        blocks_html += '''
            </div>
        </div>
        '''
    
    blocks_html += '</div>'
    return blocks_html

# --- Generate HTML Report ---
def generate_html_report(conn, tables, summary_df, total_rows, table_schemas):
    """Generate an HTML visualization of the database structure"""
    
    # Generate summary table HTML
    summary_table_html = summary_df.to_html(classes='summary-table', index=False, escape=False)
    
    # Generate Mermaid ER Diagram
    mermaid_diagram = generate_mermaid_diagram(table_schemas)
    
    # Generate Block Visualization
    block_visualization = generate_block_visualization(table_schemas)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Northwind Database Structure Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .stat-card h3 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .stat-card p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tr:hover {{
            background-color: #f5f5f5;
        }}
        
        .table-section {{
            margin-bottom: 50px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .table-header {{
            background: #667eea;
            color: white;
            padding: 15px 20px;
            font-size: 1.3em;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .table-header:hover {{
            background: #5568d3;
        }}
        
        .table-content {{
            padding: 20px;
            display: none;
        }}
        
        .table-content.active {{
            display: block;
        }}
        
        .table-info {{
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}
        
        .table-info p {{
            margin: 5px 0;
        }}
        
        .binary-data {{
            color: #999;
            font-style: italic;
        }}
        
        .toggle-icon {{
            transition: transform 0.3s;
        }}
        
        .toggle-icon.active {{
            transform: rotate(180deg);
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            background: #f8f9fa;
        }}
        
        /* Schema Block Visualization Styles */
        .schema-blocks {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .table-block {{
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .table-block:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .table-block-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .table-block-header h3 {{
            margin: 0;
            font-size: 1.2em;
            font-weight: 600;
        }}
        
        .row-count {{
            font-size: 0.9em;
            opacity: 0.9;
            background: rgba(255,255,255,0.2);
            padding: 4px 10px;
            border-radius: 12px;
        }}
        
        .table-block-body {{
            padding: 15px;
        }}
        
        .column-group {{
            margin-bottom: 15px;
        }}
        
        .column-group:last-child {{
            margin-bottom: 0;
        }}
        
        .group-label {{
            font-weight: 600;
            font-size: 0.85em;
            color: #667eea;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .column-item {{
            background: #f8f9fa;
            padding: 8px 12px;
            margin-bottom: 5px;
            border-radius: 4px;
            border-left: 3px solid #ddd;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9em;
        }}
        
        .pk-item {{
            border-left-color: #28a745;
            background: #f0f9f4;
        }}
        
        .fk-item {{
            border-left-color: #ffc107;
            background: #fffbf0;
        }}
        
        .regular-item {{
            border-left-color: #6c757d;
        }}
        
        .col-name {{
            font-weight: 500;
            color: #333;
            flex: 1;
        }}
        
        .col-type {{
            color: #666;
            font-size: 0.85em;
            margin-left: 10px;
        }}
        
        .col-ref {{
            color: #667eea;
            font-size: 0.8em;
            font-style: italic;
            margin-left: 10px;
        }}
        
        /* Mermaid Diagram Styles */
        .mermaid-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 40px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        
        .mermaid {{
            text-align: center;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗄️ Northwind Database Structure</h1>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📐 Database Schema Visualization</h2>
                <div class="mermaid-container">
                    <pre class="mermaid">
{mermaid_diagram}
                    </pre>
                </div>
            </div>
            
            <div class="section">
                <h2>🧱 Table Structure Blocks</h2>
                {block_visualization}
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{len(tables)}</h3>
                    <p>Total Tables</p>
                </div>
                <div class="stat-card">
                    <h3>{total_rows:,}</h3>
                    <p>Total Rows</p>
                </div>
                <div class="stat-card">
                    <h3>{summary_df['Columns'].sum()}</h3>
                    <p>Total Columns</p>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Database Overview</h2>
                {summary_table_html}
            </div>
            
            <div class="section">
                <h2>📋 Table Details & Sample Data</h2>
"""
    
    # Add each table with sample data
    for idx, table in enumerate(tables):
        quoted_table = f'"{table}"'
        sample_query = f"SELECT * FROM {quoted_table} LIMIT 5"
        
        try:
            sample_df = pd.read_sql(sample_query, conn)
            
            # Handle binary columns
            for col in sample_df.columns:
                if sample_df[col].dtype == 'object':
                    sample_df[col] = sample_df[col].apply(
                        lambda x: f'<span class="binary-data">BINARY DATA ({len(x)} bytes)</span>' if isinstance(x, bytes) else str(x)[:100] + ('...' if len(str(x)) > 100 else '')
                    )
            
            # Get table info
            table_info = summary_df[summary_df['Table'] == table].iloc[0]
            
            html_content += f"""
                <div class="table-section">
                    <div class="table-header" onclick="toggleTable({idx})">
                        <span>📑 {table}</span>
                        <span class="toggle-icon" id="icon-{idx}">▼</span>
                    </div>
                    <div class="table-content" id="content-{idx}">
                        <div class="table-info">
                            <p><strong>Rows:</strong> {table_info['Rows']:,}</p>
                            <p><strong>Columns:</strong> {table_info['Columns']}</p>
                            <p><strong>Column Names:</strong> {table_info['Column_Names']}</p>
                        </div>
                        {sample_df.to_html(classes='sample-table', index=False, escape=False)}
                    </div>
                </div>
"""
        except Exception as e:
            html_content += f"""
                <div class="table-section">
                    <div class="table-header" onclick="toggleTable({idx})">
                        <span>📑 {table}</span>
                        <span class="toggle-icon" id="icon-{idx}">▼</span>
                    </div>
                    <div class="table-content" id="content-{idx}">
                        <p style="color: red;">Error loading data: {str(e)}</p>
                    </div>
                </div>
"""
    
    html_content += """
            </div>
        </div>
        
        <div class="footer">
            <p>Northwind Database Structure Report | Generated with Python & Pandas</p>
        </div>
    </div>
    
    <script>
        function toggleTable(idx) {
            const content = document.getElementById('content-' + idx);
            const icon = document.getElementById('icon-' + idx);
            
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                icon.classList.remove('active');
            } else {
                content.classList.add('active');
                icon.classList.add('active');
            }
        }
        
        // Style the summary table
        document.addEventListener('DOMContentLoaded', function() {
            const summaryTable = document.getElementById('summary-table');
            if (summaryTable) {
                summaryTable.style.width = '100%';
            }
        });
    </script>
</body>
</html>
"""
    
    return html_content

# Generate and save HTML report
html_report = generate_html_report(conn, tables, summary_df, total_rows, table_schemas)
html_file_path = os.path.join(os.path.dirname(__file__), "northwind_database_report.html")

with open(html_file_path, 'w', encoding='utf-8') as f:
    f.write(html_report)

print(f"\n✅ HTML Report generated successfully!")
print(f"📄 Open this file in your browser: {html_file_path}")

conn.close()
print("\n" + "=" * 80)
print("Summary Complete!")
print("=" * 80)
