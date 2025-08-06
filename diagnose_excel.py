#!/usr/bin/env python3
"""
Diagnostic tool to analyze Excel files and identify import issues
"""

import pandas as pd
import os
import sys

def diagnose_excel_file(filename):
    """Diagnose Excel file for potential import issues"""
    
    print(f"🔍 Diagnosing Excel file: {filename}")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return False
    
    try:
        # Read the Excel file
        print("📂 Reading Excel file...")
        df = pd.read_excel(filename)
        print(f"✅ File read successfully")
        
        # Basic info
        print(f"\n📊 File Information:")
        print(f"   - Rows: {len(df)}")
        print(f"   - Columns: {len(df.columns)}")
        print(f"   - File size: {os.path.getsize(filename)} bytes")
        
        # Column analysis
        print(f"\n📋 Column Analysis:")
        print(f"   Found columns: {list(df.columns)}")
        
        # Check for required columns
        required_cols = ['sender', 'subject']
        optional_cols = ['destination', 'to', 'date']
        
        missing_required = [col for col in required_cols if col not in df.columns]
        found_optional = [col for col in optional_cols if col in df.columns]
        
        if missing_required:
            print(f"   ❌ Missing required columns: {missing_required}")
        else:
            print(f"   ✅ All required columns found: {required_cols}")
        
        if found_optional:
            print(f"   ✅ Optional columns found: {found_optional}")
        else:
            print(f"   ⚠️  No optional columns found")
        
        # Check destination column
        destination_col = None
        if 'destination' in df.columns:
            destination_col = 'destination'
        elif 'to' in df.columns:
            destination_col = 'to'
        
        if destination_col:
            print(f"   ✅ Destination column: '{destination_col}'")
        else:
            print(f"   ⚠️  No destination column ('destination' or 'to')")
        
        # Data preview
        print(f"\n📄 Data Preview (first 5 rows):")
        print(df.head().to_string(index=True))
        
        # Data quality analysis
        print(f"\n🔍 Data Quality Analysis:")
        
        if 'sender' in df.columns:
            empty_senders = df['sender'].isna().sum() + (df['sender'] == '').sum()
            print(f"   - Empty/null senders: {empty_senders}")
        
        if 'subject' in df.columns:
            empty_subjects = df['subject'].isna().sum() + (df['subject'] == '').sum()
            print(f"   - Empty/null subjects: {empty_subjects}")
        
        if destination_col:
            empty_destinations = df[destination_col].isna().sum() + (df[destination_col] == '').sum()
            print(f"   - Empty/null destinations: {empty_destinations}")
        
        if 'date' in df.columns:
            empty_dates = df['date'].isna().sum()
            print(f"   - Empty/null dates: {empty_dates}")
        
        # Identify potentially importable rows
        if not missing_required:
            valid_rows = 0
            for index, row in df.iterrows():
                sender = str(row['sender']).strip() if pd.notna(row['sender']) else ""
                subject = str(row['subject']).strip() if pd.notna(row['subject']) else ""
                
                if sender and subject:
                    valid_rows += 1
            
            print(f"   ✅ Potentially importable rows: {valid_rows} out of {len(df)}")
            
            if valid_rows == 0:
                print(f"   ❌ No valid rows found! All rows are missing sender or subject.")
            elif valid_rows < len(df):
                skipped = len(df) - valid_rows
                print(f"   ⚠️  {skipped} rows will be skipped due to missing data")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if missing_required:
            print(f"   - Add missing required columns: {missing_required}")
        if not destination_col:
            print(f"   - Consider adding a 'destination' or 'to' column")
        if 'date' not in df.columns:
            print(f"   - Consider adding a 'date' column (YYYY-MM-DD HH:MM:SS format)")
        
        print(f"\n✅ Diagnosis complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # List available Excel files
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        if excel_files:
            print("Available Excel files:")
            for i, f in enumerate(excel_files, 1):
                print(f"{i}. {f}")
            
            try:
                choice = int(input(f"\nEnter file number (1-{len(excel_files)}): ")) - 1
                if 0 <= choice < len(excel_files):
                    filename = excel_files[choice]
                else:
                    print("Invalid choice")
                    return
            except ValueError:
                print("Please enter a valid number")
                return
        else:
            print("No Excel files found in current directory")
            return
    
    diagnose_excel_file(filename)

if __name__ == "__main__":
    main()
