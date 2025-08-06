# Date Formats Guide - Record Keeping System

This guide explains all the date formats supported by the record keeping system and how they are processed.

## 📅 Supported Input Formats

The system can read and automatically convert the following date formats:

### 1. **ISO Format (Recommended)**
- **Date only**: `2025-01-07`
- **Date with time**: `2025-01-07 14:30:00`
- **Description**: International standard format (YYYY-MM-DD)
- **Usage**: Best for data consistency and sorting

### 2. **US Format (Your Preferred Format)**
- **Date only**: `08.01.2025` or `08/01/2025` (MM.DD.YYYY or MM/DD/YYYY)
- **Date with time**: `08.01.2025 14:30:00`
- **Description**: Month-Day-Year format where `08.01.2025` = August 1, 2025
- **Priority**: This format is checked first in the system

### 3. **Alternative US Format**
- **Date only**: `08-01-2025` (MM-DD-YYYY)
- **Date with time**: `08-01-2025 14:30:00`
- **Description**: Month-Day-Year format with dashes

### 4. **Readable Format (Legacy)**
- **Date only**: `January 7, 2025`
- **Date with time**: `January 7, 2025 at 2:30 PM`
- **Description**: Human-readable format (automatically converted to ISO)

## 🔄 How Date Processing Works

### Input Processing
1. **Automatic Detection**: The system tries to identify the format automatically
2. **Pattern Matching**: Uses regex patterns to match common formats
3. **Fallback**: If patterns fail, uses pandas date parsing (if available)
4. **Standardization**: All dates are converted to ISO format for storage

### Storage Format
- **Standard**: All dates are stored in ISO format (`YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`)
- **Consistency**: Ensures proper sorting and date calculations
- **No Date**: Records without dates are stored as `"No Date"`

## 📊 Examples of Date Conversion

| Input Format | Input Example | Stored As | Display As |
|--------------|---------------|-----------|------------|
| ISO | `2025-01-07` | `2025-01-07` | `2025-01-07` |
| ISO with time | `2025-01-07 14:30:00` | `2025-01-07 14:30:00` | `2025-01-07 14:30:00` |
| European | `07.01.2025` | `2025-01-07` | `2025-01-07` |
| European with time | `07.01.2025 14:30:00` | `2025-01-07 14:30:00` | `2025-01-07 14:30:00` |
| US | `01/07/2025` | `2025-01-07` | `2025-01-07` |
| Readable | `January 7, 2025` | `2025-01-07` | `2025-01-07` |
| Readable with time | `January 7, 2025 at 2:30 PM` | `2025-01-07 14:30:00` | `2025-01-07 14:30:00` |

## 🛠️ Working with Dates

### When Adding Records
- **Manual Entry**: Enter dates in any supported format
- **Auto-Generated**: Leave blank to use current date/time
- **Import**: Excel/CSV files can contain dates in any supported format

### When Importing Data
- **Excel Files**: Date columns are automatically detected and converted
- **CSV Files**: Dates are parsed using the same logic
- **Flexibility**: Mix different formats in the same import file

### Date Search and Filtering
- **Range Queries**: Use ISO format for date ranges (`2025-01-01` to `2025-01-31`)
- **Search**: Search by any date format, automatically converted
- **Analytics**: Date-based analytics use the standardized ISO format

## ⚠️ Special Cases

### Invalid Dates
- **Invalid Input**: `32/13/2025` → Skipped or kept as original text
- **Empty Values**: Empty cells → Stored as `"No Date"`
- **Non-dates**: Text like `"TBD"` → Kept as original text

### Time Handling
- **Date Only**: Automatically adds `00:00:00` time
- **Time Included**: Preserves the exact time
- **12-hour Format**: `2:30 PM` → Converted to `14:30:00`

## 🔧 Code Implementation

### Main Date Parsing Function
Located in `record_keeper.py`, the `_parse_and_format_date()` method:

```python
def _parse_and_format_date(self, date_str: str) -> str:
    # Tries multiple patterns in order:
    # 1. European format (DD.MM.YYYY)
    # 2. US format (MM/DD/YYYY)
    # 3. ISO format (YYYY-MM-DD)
    # 4. ISO with time (YYYY-MM-DD HH:MM:SS)
    # 5. European with time
    # 6. Pandas fallback parsing
```

### Legacy Format Conversion
The system automatically updates old readable formats to ISO:

```python
def _convert_readable_to_iso(self, date_str: str) -> str:
    # Converts "January 7, 2025" to "2025-01-07"
    # Converts "January 7, 2025 at 2:30 PM" to "2025-01-07 14:30:00"
```

## 📝 Best Practices

### For Data Entry
1. **Use ISO format** (`2025-01-07`) for consistency
2. **Include time** if specific timing matters
3. **Leave blank** for current date/time auto-generation

### For Imports
1. **Mixed formats OK**: The system handles multiple formats in one file
2. **Check results**: Review imported dates to ensure correct interpretation
3. **Use headers**: Excel files should have clear column headers

### For Searching
1. **Use ISO format** for date range searches
2. **Partial matches work**: Search for `2025-01` finds all January 2025 records
3. **Text search**: Can search readable text in dates

## 🔍 Troubleshooting

### Common Issues
1. **Ambiguous dates**: `01/02/2025` could be Jan 2 or Feb 1
   - **Solution**: Use ISO format `2025-01-02` or `2025-02-01`

2. **Import errors**: Some dates not recognized
   - **Solution**: Check format consistency in source file

3. **Analytics errors**: "No Date" records cause issues
   - **Solution**: System now skips invalid dates in analytics

### Error Messages
- `"No Date"`: Record has no valid date
- `"time data 'X' does not match format"`: Date parsing failed
- Import warnings: Some dates could not be parsed

## 📚 Related Files
- `record_keeper.py`: Main date processing logic
- `app.py`: Web interface date handling
- `templates/`: HTML forms with date inputs
- `analytics.html`: Date-based reporting

---

**Need Help?** If you encounter date-related issues, check this guide first. The system is designed to be flexible and handle most common date formats automatically.
