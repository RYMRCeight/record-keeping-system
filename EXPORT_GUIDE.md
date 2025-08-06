# Data Export Guide - Record Keeping System

## Overview
The Record Keeping System allows exporting data in multiple formats including Excel, CSV, JSON, TXT, and HTML. Below are the methods to perform these exports.

### Supported Export Formats
1. **Excel (.xlsx)**
2. **CSV (.csv)**
3. **JSON (.json)**
4. **Text Report (.txt)**
5. **HTML Report (.html)**

## How to Export Data

### Method 1: Web Interface
1. Start the Flask application:
   ```bash
   python app.py
   ```
2. Go to `http://localhost:5000` in your browser.
3. In the "Export Data" section, choose your format:
   - **Excel**: Click "[📊 Excel (.xlsx)](/export/excel)"
   - **CSV**: Click "[📋 CSV (.csv)](/export/csv)"
   - **JSON**: Click "[🔧 JSON (.json)](/export/json)"
4. Check the uploads folder for the generated file.

### Method 2: Command Line
1. Run the command line script:
   ```bash
   python record_keeper.py
   ```
2. Choose option 7: "Export to Excel"
3. Follow the prompts to specify your export options

### Method 3: Python Code
Export directly through the code for flexibility:
```python
from record_keeper import RecordKeeper

# Create a keeper instance
keeper = RecordKeeper()

# Export to Excel
excel_file = 'my_exported_records.xlsx'
if keeper.export_to_excel(excel_file):
    print(f"Excel exported: {excel_file} created successfully")

# Export to CSV
import pandas as pd
records = keeper.get_all_records()
data = [record.to_dict() for record in records]
df = pd.DataFrame(data)
df.to_csv('my_exported_records.csv', index=False)
print("CSV exported successfully")

# Export to JSON
import json
with open('my_exported_records.json', 'w') as f:
    json.dump(data, f, indent=2)
print("JSON exported successfully")
```

## Export Locations
All exported files are written to the `uploads` directory within the project folder unless specified otherwise.

## Tips for Successful Exports
1. **Check Formats**: Ensure the chosen export format is supported by your target application.
2. **Verify Output**: Open exported files to verify data integrity and accuracy.
3. **Automate Tasks**: Consider scripts to automate frequent exports.

## Summary
Exporting data in versatile formats enhances flexibility to analyze, report, and back up your records. Utilize your web interface for user-friendly exports or integrate scripts and command line to streamline your workflow.
