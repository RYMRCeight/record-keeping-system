#!/usr/bin/env python3
"""
Interactive edit tester to help diagnose editing issues
"""

from record_keeper import RecordKeeper, AuthManager

def debug_edit():
    print("=== RECORD EDIT DEBUGGER ===")
    
    # Initialize components
    keeper = RecordKeeper()
    auth = AuthManager()
    
    # Login
    print("\n1. LOGIN TEST")
    username = input("Enter username (default: admin): ").strip() or "admin"
    password = input("Enter password (default: admin123): ").strip() or "admin123"
    
    if auth.login(username, password):
        print(f"✓ Login successful as {username} ({auth.current_user.role})")
    else:
        print("✗ Login failed")
        return
    
    # Show records
    print("\n2. LOADING RECORDS")
    records = keeper.get_all_records()
    print(f"Found {len(records)} records")
    
    if not records:
        print("No records available to edit")
        return
    
    # Show first 5 records
    print("\nFirst 5 records:")
    for i, record in enumerate(records[:5], 1):
        print(f"{i}. {record}")
    
    # Select record to edit
    print("\n3. SELECT RECORD TO EDIT")
    try:
        choice = input(f"Enter record number (1-{min(5, len(records))}): ").strip()
        record_index = int(choice) - 1
        
        if 0 <= record_index < len(records):
            selected_record = records[record_index]
            print(f"Selected: {selected_record}")
        else:
            print("Invalid selection")
            return
    except ValueError:
        print("Invalid number")
        return
    
    # Show edit options
    print("\n4. EDIT OPTIONS")
    print("What would you like to edit?")
    print("1. Sender")
    print("2. Subject") 
    print("3. Destination")
    print("4. Date")
    print("5. Status")
    
    edit_choice = input("Enter choice (1-5): ").strip()
    
    if edit_choice == "1":
        new_value = input(f"Enter new sender (current: {selected_record.sender}): ").strip()
        field = "sender"
    elif edit_choice == "2":
        new_value = input(f"Enter new subject (current: {selected_record.subject}): ").strip()
        field = "subject"
    elif edit_choice == "3":  
        new_value = input(f"Enter new destination (current: {selected_record.destination}): ").strip()
        field = "destination"
    elif edit_choice == "4":
        new_value = input(f"Enter new date (current: {selected_record.date}): ").strip()
        field = "date"
    elif edit_choice == "5":
        print("Status options: Pending, Completed")
        new_value = input(f"Enter new status (current: {selected_record.status}): ").strip()
        field = "status"
    else:
        print("Invalid choice")
        return
    
    if not new_value:
        print("No changes made (empty input)")
        return
    
    # Perform edit
    print(f"\n5. PERFORMING EDIT")
    print(f"Editing {field} to: {new_value}")
    
    edit_kwargs = {field: new_value}
    success = keeper.edit_record(selected_record.id, **edit_kwargs)
    
    if success:
        print("✓ Edit successful!")
        
        # Show updated record
        updated_records = keeper.get_all_records()
        for record in updated_records:
            if record.id == selected_record.id:
                print(f"Updated record: {record}")
                break
    else:
        print("✗ Edit failed!")
        
        # Debug information
        print("Debug info:")
        print(f"Record ID: {selected_record.id}")
        print(f"Field: {field}")
        print(f"New value: {new_value}")
        print(f"Edit function returned: {success}")

if __name__ == "__main__":
    debug_edit()
