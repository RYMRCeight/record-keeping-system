#!/usr/bin/env python3
"""
Debug import with detailed error reporting
"""

import traceback
from record_keeper import RecordKeeper, AuthManager

def debug_import(filename):
    """Debug import with detailed error information"""
    
    print(f"🔧 Debug Import: {filename}")
    print("=" * 50)
    
    try:
        # Initialize components
        print("1. Initializing components...")
        auth = AuthManager()
        keeper = RecordKeeper("debug_records.json")
        
        # Login as admin
        print("2. Logging in as admin...")
        if not auth.login("admin", "admin123"):
            print("❌ Failed to login as admin")
            return False
        
        print(f"✅ Logged in as: {auth.get_current_user().username}")
        print(f"✅ Can import: {auth.can_import()}")
        
        # Clear existing records
        print("3. Clearing existing records...")
        keeper.records = []
        keeper.save_records()
        
        # Attempt import with detailed error catching
        print(f"4. Attempting to import {filename}...")
        
        try:
            result = keeper.import_from_excel(filename, False)
            if result:
                records = keeper.get_all_records()
                print(f"✅ Import successful! Total records: {len(records)}")
                
                if records:
                    print("\nImported records:")
                    for i, record in enumerate(records, 1):
                        print(f"{i}. {record}")
                else:
                    print("⚠️ No records were imported (but no error occurred)")
                
                return True
            else:
                print("❌ Import returned False (failed)")
                return False
                
        except Exception as import_error:
            print(f"❌ Import exception occurred:")
            print(f"   Error type: {type(import_error).__name__}")
            print(f"   Error message: {import_error}")
            print(f"   Full traceback:")
            traceback.print_exc()
            return False
            
    except Exception as setup_error:
        print(f"❌ Setup error occurred:")
        print(f"   Error type: {type(setup_error).__name__}")
        print(f"   Error message: {setup_error}")
        print(f"   Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # Use sample file for testing
        filename = "sample_import.xlsx"
        print(f"No filename provided, using default: {filename}")
    
    debug_import(filename)
