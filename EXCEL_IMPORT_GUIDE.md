# Excel Import Guide - Record Keeping System

## Overview
Your record keeping system can now read Excel files with the following columns:
- **date** (optional) - Format: YYYY-MM-DD HH:MM:SS
- **sender** (required) - The person or department sending the document
- **subject** (required) - The subject/title of the document
- **to** (required) - The destination person or department (can also use 'destination')

## Supported Column Names
The system accepts either:
- `to` (preferred)
- `destination` (alternative)

Both will be treated as the destination field internally.

## Excel File Format

### Required Columns:
- **sender** - Who sent the document
- **subject** - What the document is about  
- **to** or **destination** - Where the document is going

### Optional Columns:
- **date** - When the document was sent (auto-generated if not provided)
- **id** - Document ID (auto-generated if not provided)

### Sample Excel Structure:
```
| date                | sender              | subject            | to              |
|---------------------|--------------------|--------------------|-----------------|
| 2025-01-01 09:00:00 | John Smith         | Invoice #12345     | Accounting      |
| 2025-01-01 10:30:00 | Marketing Dept     | Monthly Report     | Management      |
| 2025-01-01 14:15:00 | HR Department      | Employee Contract  | Legal Dept      |
```

## How to Import Excel Files

### Method 1: Web Interface
1. Open your browser and go to `http://localhost:5000`
2. In the "Export and Import Section" at the bottom
3. Click "Choose File" and select your Excel file
4. Click "Import from Excel"
5. Check for success/error messages

### Method 2: Command Line Interface
1. Run: `python record_keeper.py`
2. Choose option 8: "Import from Excel"
3. Enter your Excel filename
4. Choose whether to replace existing records (y/n)

### Method 3: Python Code
```python
from record_keeper import RecordKeeper

# Create keeper instance
keeper = RecordKeeper()

# Import Excel file
success = keeper.import_from_excel("your_file.xlsx")

if success:
    print("Import successful!")
    records = keeper.get_all_records()
    print(f"Total records: {len(records)}")
else:
    print("Import failed!")
```

## Creating a Template
You can generate an Excel template with sample data:

### Using Web Interface:
- This feature will be added in a future update

### Using Command Line:
1. Run: `python record_keeper.py`
2. Choose option 9: "Create Excel template"
3. Enter a filename (without .xlsx extension)
4. The template will be created with sample data and instructions

### Using Python Code:
```python
from record_keeper import RecordKeeper

keeper = RecordKeeper()
keeper.create_excel_template("my_template")
```

## Error Handling
The system will report errors for:
- Missing required columns (sender, subject, to/destination)
- Empty or invalid data
- File not found
- Corrupted Excel files

## Tips for Best Results
1. **Use consistent date formats**: YYYY-MM-DD HH:MM:SS
2. **Avoid empty rows**: The system will skip them but it's better to remove them
3. **Check column names**: Make sure they match exactly (case-sensitive)
4. **Save as .xlsx**: Older .xls formats may not work properly
5. **Test with small files first**: Import a few records to verify formatting

## Troubleshooting

### Common Issues:
1. **"Missing required columns" error**
   - Check that your Excel file has 'sender', 'subject', and either 'to' or 'destination' columns
   - Column names are case-sensitive

2. **"No valid records found" error**
   - Check for empty rows or cells
   - Ensure data is properly formatted

3. **Import appears successful but no records show**
   - Check if you chose to replace existing records
   - Verify the file path is correct

### File Location:
- Place your Excel files in the same directory as your Python scripts
- Or provide the full path to the file

## Example Files
The system includes `sample_import_data.xlsx` which demonstrates the correct format with sample data.
