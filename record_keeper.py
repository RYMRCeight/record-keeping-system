#!/usr/bin/env python3
"""
Record Keeping Management System
A simple system to track document records with date, sender, subject, and destination.
"""

import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
import re
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

class User:
    """Represents a user with authentication and role information."""
    
    def __init__(self, username: str, password: str, role: str = "user"):
        self.username = username
        self.password_hash = self._hash_password(password)
        self.role = role  # "admin" or "user"
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return self._hash_password(password) == self.password_hash
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary for JSON serialization."""
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create User from dictionary."""
        user = cls.__new__(cls)
        user.username = data['username']
        user.password_hash = data['password_hash']
        user.role = data['role']
        return user

class AuthManager:
    """Manages user authentication and authorization."""
    
    def __init__(self, users_file: str = "users.json"):
        self.users_file = users_file
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
        self.load_users()
        self._ensure_default_admin()
    
    def _ensure_default_admin(self):
        """Ensure default admin user exists."""
        if not self.users:
            # Create default admin user
            admin = User("admin", "admin123", "admin")
            regular_user = User("user", "user123", "user")
            self.users["admin"] = admin
            self.users["user"] = regular_user
            self.save_users()
            print("Default users created:")
            print("Admin - Username: admin, Password: admin123")
            print("User - Username: user, Password: user123")
            print("Please change these passwords after first login!")
    
    def load_users(self):
        """Load users from JSON file."""
        if not os.path.exists(self.users_file):
            return
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.users = {username: User.from_dict(user_data) 
                             for username, user_data in data.items()}
        except Exception as e:
            print(f"Error loading users: {e}")
            self.users = {}
    
    def save_users(self):
        """Save users to JSON file."""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                user_data = {username: user.to_dict() 
                           for username, user in self.users.items()}
                json.dump(user_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate user and set current user."""
        if username in self.users:
            user = self.users[username]
            if user.verify_password(password):
                self.current_user = user
                return True
        return False
    
    def logout(self):
        """Logout current user."""
        self.current_user = None
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in."""
        return self.current_user is not None
    
    def is_admin(self) -> bool:
        """Check if current user is admin."""
        return self.current_user and self.current_user.role == "admin"
    
    def can_delete(self) -> bool:
        """Check if current user can delete records."""
        return self.is_admin()
    
    def can_import(self) -> bool:
        """Check if current user can import records."""
        return self.is_logged_in()  # Allow all logged-in users to import
    
    def can_view_stats(self) -> bool:
        """Check if current user can view statistics."""
        return self.is_admin()
    
    def add_user(self, username: str, password: str, role: str = "user") -> bool:
        """Add new user (admin only)."""
        if not self.is_admin():
            return False
        
        if username in self.users:
            return False  # User already exists
        
        self.users[username] = User(username, password, role)
        self.save_users()
        return True
    
    def change_password(self, username: str, current_password: str, new_password: str) -> bool:
        """Change user password with current password verification."""
        if not self.is_logged_in():
            return False
        
        # Users can only change their own password with verification
        if self.current_user.username == username:
            if username in self.users:
                # Verify current password
                if self.users[username].verify_password(current_password):
                    self.users[username].password_hash = self.users[username]._hash_password(new_password)
                    self.save_users()
                    return True
        return False
    
    def change_user_password(self, username: str, new_password: str) -> bool:
        """Change any user's password (admin only, no current password required)."""
        if not self.is_admin():
            return False
        
        if username in self.users:
            self.users[username].password_hash = self.users[username]._hash_password(new_password)
            self.save_users()
            return True
        return False
    
    def get_current_user(self) -> Optional[User]:
        """Get current logged in user."""
        return self.current_user

class DocumentRecord:
    """Represents a single document record."""
    _id_counter = None  # Store counter in file for persistence
    
    def __init__(self, sender: str, subject: str, destination: str, date: Optional[str] = None, record_id: Optional[str] = None, auto_date: bool = True, status: str = "Pending"):
        self.id = record_id if record_id else self._generate_id()
        # Only auto-generate date if auto_date is True and no date is provided
        if date:
            self.date = date
        elif auto_date:
            self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.date = "No Date"
        self.sender = sender
        self.subject = subject
        self.destination = destination
        # Ensure status is only "Pending" or "Completed"
        self.status = "Completed" if status in ["Done", "Completed"] else "Pending"
        
    def _generate_id(self) -> str:
        """Generate an ID with format 'MAYOR'S OFFICE - 001' starting from 001."""
        # Increment counter for each new record
        DocumentRecord._id_counter += 1
        # Format the ID as requested - simplified format starting from 001
        formatted_id = f"MAYOR'S OFFICE - {DocumentRecord._id_counter:03d}"
        return formatted_id
    
    def to_dict(self) -> Dict:
        """Convert record to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'date': self.date,
            'sender': self.sender,
            'subject': self.subject,
            'destination': self.destination,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DocumentRecord':
        """Create DocumentRecord from dictionary."""
        # Handle backward compatibility for records without status
        status = data.get('status', 'Pending')
        record = cls(data['sender'], data['subject'], data['destination'], data['date'], data['id'], status=status)
        return record
    
    def __str__(self) -> str:
        """String representation of the record."""
        status_indicator = "✅" if self.status == "Completed" else "⏳"
        return f"[{self.id}] {status_indicator} {self.status} | {self.date} | From: {self.sender} | To: {self.destination} | Subject: {self.subject}"

class RecordKeeper:
    """Main class for managing document records."""
    
    COUNTER_FILE = "counter.txt"
    
    def __init__(self, data_file: str = "records.json"):
        self.data_file = data_file
        self.records: List[DocumentRecord] = []
        self.load_records()
        self._load_counter()
    
    def _load_counter(self):
        """Load the ID counter from file."""
        if os.path.exists(self.COUNTER_FILE):
            with open(self.COUNTER_FILE, 'r') as file:
                try:
                    DocumentRecord._id_counter = int(file.read().strip())
                except ValueError:
                    DocumentRecord._id_counter = 0
        else:
            DocumentRecord._id_counter = 0

    def _save_counter(self):
        """Save the current ID counter to file."""
        with open(self.COUNTER_FILE, 'w') as file:
            file.write(str(DocumentRecord._id_counter))
    
    def _parse_and_format_date(self, date_str: str) -> str:
        """Parse various date formats and return a standardized date string."""
        if not date_str or str(date_str).strip().lower() in ['nan', 'nat', 'none', '']:
            return None
        
        date_str = str(date_str).strip()
        
        # Common date patterns to try
        date_patterns = [
            # US format with dots or slashes: MM.DD.YYYY or MM/DD/YYYY (your preferred format)
            (r'^(\d{1,2})[./](\d{1,2})[./](\d{4})$', 'us_format'),
            # US format with dashes: MM-DD-YYYY
            (r'^(\d{1,2})-(\d{1,2})-(\d{4})$', '%m-%d-%Y'),
            # ISO format: YYYY-MM-DD
            (r'^(\d{4})-(\d{1,2})-(\d{1,2})$', '%Y-%m-%d'),
            # ISO with time: YYYY-MM-DD HH:MM:SS
            (r'^(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2}):(\d{1,2})$', '%Y-%m-%d %H:%M:%S'),
            # US format with time: MM.DD.YYYY HH:MM:SS or MM/DD/YYYY HH:MM:SS
            (r'^(\d{1,2})[./](\d{1,2})[./](\d{4})\s+(\d{1,2}):(\d{1,2}):(\d{1,2})$', 'us_format_time'),
        ]
        
        for pattern, format_str in date_patterns:
            match = re.match(pattern, date_str)
            if match:
                try:
                    # Handle US format: MM.DD.YYYY or MM/DD/YYYY (your preferred format)
                    if format_str == 'us_format':
                        month, day, year = match.groups()
                        parsed_date = datetime.strptime(f"{month}/{day}/{year}", '%m/%d/%Y')
                    # Handle US format with time: MM.DD.YYYY HH:MM:SS or MM/DD/YYYY HH:MM:SS
                    elif format_str == 'us_format_time':
                        month, day, year, hour, minute, second = match.groups()
                        parsed_date = datetime.strptime(f"{month}/{day}/{year} {hour}:{minute}:{second}", '%m/%d/%Y %H:%M:%S')
                    else:
                        parsed_date = datetime.strptime(date_str, format_str)
                    
                    # Format as standard ISO format: "2025-01-07" or "2025-01-07 14:30:00"
                    if parsed_date.hour == 0 and parsed_date.minute == 0 and parsed_date.second == 0:
                        # Date only
                        return parsed_date.strftime('%Y-%m-%d')
                    else:
                        # Date with time
                        return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                        
                except ValueError:
                    continue
        
        # If no pattern matches, try pandas date parsing as fallback
        try:
            if PANDAS_AVAILABLE:
                parsed_date = pd.to_datetime(date_str, infer_datetime_format=True)
                if pd.notna(parsed_date):
                    parsed_date = parsed_date.to_pydatetime()
                    if parsed_date.hour == 0 and parsed_date.minute == 0 and parsed_date.second == 0:
                        return parsed_date.strftime('%Y-%m-%d')
                    else:
                        return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
        
        # If all else fails, return the original string
        return date_str
    
    def add_record(self, sender: str, subject: str, destination: str, date: Optional[str] = None) -> DocumentRecord:
        """Add a new document record."""
        record = DocumentRecord(sender, subject, destination, date)
        self.records.append(record)
        self.save_records()
        self._save_counter()
        return record
    
    def get_all_records(self) -> List[DocumentRecord]:
        """Get all records."""
        return self.records.copy()
    
    def search_records(self, query: str) -> List[DocumentRecord]:
        """Search records by ID, date, sender, subject, or destination."""
        if not query:
            return self.records.copy()
        
        query = query.lower()
        matching_records = []
        
        for record in self.records:
            # Search in all fields: ID, date, sender, subject, destination
            if (query in record.id.lower() or 
                query in record.date.lower() or 
                query in record.sender.lower() or 
                query in record.subject.lower() or 
                query in record.destination.lower()):
                matching_records.append(record)
        
        return matching_records
    
    def get_records_by_date_range(self, start_date: str, end_date: str) -> List[DocumentRecord]:
        """Get records within a date range (YYYY-MM-DD format)."""
        matching_records = []
        
        for record in self.records:
            record_date = record.date.split(' ')[0]  # Extract date part
            if start_date <= record_date <= end_date:
                matching_records.append(record)
        
        return matching_records
    
    def delete_record(self, record_id: str) -> bool:
        """Delete a record by ID."""
        for i, record in enumerate(self.records):
            if record.id == record_id:
                del self.records[i]
                self.save_records()
                
                # Check if all records have been deleted and reset counter if so
                if len(self.records) == 0:
                    DocumentRecord._id_counter = 0
                    self._save_counter()
                    print("All records deleted. Counter reset to start from 001 for next record.")
                
                return True
        return False
    
    def edit_record(self, record_id: str, **kwargs) -> bool:
        """Edit a record by ID with provided field updates."""
        for record in self.records:
            if record.id == record_id:
                # Update only provided fields
                if 'sender' in kwargs:
                    record.sender = kwargs['sender']
                if 'subject' in kwargs:
                    record.subject = kwargs['subject']
                if 'destination' in kwargs:
                    record.destination = kwargs['destination']
                if 'date' in kwargs:
                    record.date = kwargs['date']
                if 'status' in kwargs:
                    record.status = kwargs['status']
                self.save_records()
                return True
        return False
    
    def mark_as_completed(self, record_id: str) -> bool:
        """Mark a record as completed."""
        return self.edit_record(record_id, status="Completed")
    
    def mark_as_pending(self, record_id: str) -> bool:
        """Mark a record as pending."""
        return self.edit_record(record_id, status="Pending")
    
    def mark_as_done(self, record_id: str) -> bool:
        """Mark a record as done (alias for completed)."""
        return self.mark_as_completed(record_id)
    
    def save_records(self):
        """Save records to JSON file."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([record.to_dict() for record in self.records], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving records: {e}")
    
    def load_records(self):
        """Load records from JSON file."""
        if not os.path.exists(self.data_file):
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.records = [DocumentRecord.from_dict(record_data) for record_data in data]
                # Update existing dates to ISO format
                self._update_existing_dates_to_iso()
                # Set counter to highest existing ID + 1
                self._initialize_counter_from_records()
        except Exception as e:
            print(f"Error loading records: {e}")
            self.records = []
    
    def _initialize_counter_from_records(self):
        """Initialize counter based on existing records to avoid ID conflicts."""
        if not self.records:
            return
        
        max_counter = 0
        for record in self.records:
            # Extract number from ID format "LGU_TNGLN-MAYOR'S OFFICE - 001"
            try:
                id_parts = record.id.split(' - ')
                if len(id_parts) == 2:
                    number_str = id_parts[1]
                    number = int(number_str)
                    max_counter = max(max_counter, number)
            except (ValueError, IndexError):
                continue
        
        # Set counter to max found + 1, but don't go backwards
        if DocumentRecord._id_counter is None:
            DocumentRecord._id_counter = max_counter
        elif max_counter > DocumentRecord._id_counter:
            DocumentRecord._id_counter = max_counter
        
        # Save the counter if it was updated
        self._save_counter()
    
    def _update_existing_dates_to_iso(self):
        """Update existing records to use ISO date format."""
        updated_count = 0
        
        for record in self.records:
            if record.date and record.date != "No Date":
                # Check if date is in readable format and needs conversion
                if self._is_readable_format(record.date):
                    # Convert readable format to ISO format
                    new_date = self._convert_readable_to_iso(record.date)
                    if new_date and new_date != record.date:
                        record.date = new_date
                        updated_count += 1
                # Also check if date is in MM.DD.YYYY or MM/DD/YYYY format and needs conversion
                elif self._needs_date_format_update(record.date):
                    new_date = self._parse_and_format_date(record.date)
                    if new_date and new_date != record.date:
                        record.date = new_date
                        updated_count += 1
        
        # Save updated records if any were changed
        if updated_count > 0:
            self.save_records()
            print(f"Updated {updated_count} existing date(s) to ISO format.")
    
    def _is_readable_format(self, date_str: str) -> bool:
        """Check if date is in readable format (e.g., 'January 7, 2025')."""
        if not date_str or date_str == "No Date":
            return False
        
        # Check for readable format patterns
        readable_patterns = [
            r'^[A-Za-z]+ \d{1,2}, \d{4}$',  # "January 7, 2025"
            r'^[A-Za-z]+ \d{1,2}, \d{4} at \d{1,2}:\d{2} [AP]M$',  # "January 7, 2025 at 2:30 PM"
        ]
        
        for pattern in readable_patterns:
            if re.match(pattern, date_str):
                return True
        
        return False
    
    def _convert_readable_to_iso(self, date_str: str) -> str:
        """Convert readable date format to ISO format."""
        if not date_str:
            return None
        
        try:
            # Handle date with time format: "January 7, 2025 at 2:30 PM"
            if " at " in date_str:
                date_part, time_part = date_str.split(" at ")
                # Parse date part: "January 7, 2025"
                parsed_date = datetime.strptime(date_part, '%B %d, %Y')
                # Parse time part: "2:30 PM"
                parsed_time = datetime.strptime(time_part, '%I:%M %p').time()
                # Combine date and time
                combined_datetime = datetime.combine(parsed_date.date(), parsed_time)
                return combined_datetime.strftime('%Y-%m-%d %H:%M:%S')
            else:
                # Handle date only format: "January 7, 2025"
                parsed_date = datetime.strptime(date_str, '%B %d, %Y')
                return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            # If parsing fails, return original string
            return date_str
    
    def _needs_date_format_update(self, date_str: str) -> bool:
        """Check if date needs format update (MM.DD.YYYY or MM/DD/YYYY format)."""
        if not date_str or date_str == "No Date":
            return False
        
        # Check if it's in MM.DD.YYYY or MM/DD/YYYY format and not already ISO
        us_format_pattern = r'^\d{1,2}[./]\d{1,2}[./]\d{4}(\s+\d{1,2}:\d{2}:\d{2})?$'
        iso_pattern = r'^\d{4}-\d{1,2}-\d{1,2}(\s+\d{1,2}:\d{2}:\d{2})?$'
        
        # Return True if it matches US format but not ISO format
        return re.match(us_format_pattern, date_str) and not re.match(iso_pattern, date_str)
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about the records."""
        try:
            if not self.records:
                return {
                    'total_records': 0,
                    'unique_senders': 0,
                    'unique_destinations': 0,
                    'pending_count': 0,
                    'completed_count': 0,
                    'senders': [],
                    'destinations': []
                }
            
            total_records = len(self.records)
            senders = set(record.sender for record in self.records if record.sender)
            destinations = set(record.destination for record in self.records if record.destination)
            
            # Count status statistics
            pending_count = sum(1 for record in self.records if record.status == 'Pending')
            completed_count = sum(1 for record in self.records if record.status == 'Completed')
            
            return {
                'total_records': total_records,
                'unique_senders': len(senders),
                'unique_destinations': len(destinations),
                'pending_count': pending_count,
                'completed_count': completed_count,
                'senders': list(senders),
                'destinations': list(destinations)
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                'total_records': 0,
                'unique_senders': 0,
                'unique_destinations': 0,
                'pending_count': 0,
                'completed_count': 0,
                'senders': [],
                'destinations': []
            }
    
    def export_to_excel(self, filename: str) -> bool:
        """Export records to Excel file."""
        if not PANDAS_AVAILABLE:
            print("Error: pandas library not available. Install with: pip install pandas openpyxl")
            return False
        
        try:
            # Convert records to list of dictionaries
            data = [record.to_dict() for record in self.records]
            
            if not data:
                print("No records to export.")
                return False
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Reorder columns for better readability
            column_order = ['id', 'date', 'sender', 'subject', 'destination']
            df = df[column_order]
            
            # Export to Excel
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            df.to_excel(filename, index=False, sheet_name='Document Records')
            print(f"Records exported successfully to {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False
    
    def import_from_excel(self, filename: str, replace_existing: bool = False) -> bool:
        """Import records from Excel file."""
        if not PANDAS_AVAILABLE:
            print("Error: pandas library not available. Install with: pip install pandas openpyxl")
            return False
        
        try:
            if not os.path.exists(filename):
                print(f"Error: File {filename} not found.")
                return False
            
            # Read Excel file
            df = pd.read_excel(filename)
            
            # Normalize column names to lowercase for case-insensitive matching
            original_columns = df.columns.tolist()
            normalized_columns = {col.lower().strip(): col for col in df.columns}
            
            # Check for both 'destination' and 'to' columns (to is alias for destination)
            destination_col = None
            if 'destination' in normalized_columns:
                destination_col = normalized_columns['destination']
            elif 'to' in normalized_columns:
                destination_col = normalized_columns['to']
            
            # Validate required columns - only sender and subject are truly required
            required_columns = ['sender', 'subject']
            missing_columns = [col for col in required_columns if col not in normalized_columns]
            
            if missing_columns:
                print(f"Error: Missing required columns: {missing_columns}")
                print(f"Required columns: sender, subject")
                print(f"Optional columns: destination (or 'to'), date")
                print(f"Found columns: {list(df.columns)}")
                return False
            
            # Backup current records if not replacing
            if not replace_existing:
                original_records = self.records.copy()
            else:
                self.records = []
                # Reset ID counter when replacing all records
                DocumentRecord._id_counter = 0
                self._save_counter()
                print("ID counter reset - numbering will start from 001 for new records.")
            
            imported_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Extract data from row using normalized column names
                    sender_col = normalized_columns.get('sender')
                    subject_col = normalized_columns.get('subject')
                    date_col = normalized_columns.get('date')
                    
                    sender = str(row[sender_col]).strip() if sender_col and pd.notna(row[sender_col]) else ""
                    subject = str(row[subject_col]).strip() if subject_col and pd.notna(row[subject_col]) else ""
                    
                    # Handle destination - use empty string if column doesn't exist or is empty
                    destination = ""
                    if destination_col and pd.notna(row[destination_col]):
                        destination = str(row[destination_col]).strip()
                    
                    # Skip rows with missing sender or subject (required fields)
                    if not sender or not subject:
                        continue
                    
                    # Handle date column with parsing and formatting
                    date = None
                    if date_col and pd.notna(row[date_col]):
                        raw_date = str(row[date_col]).strip()
                        if raw_date:
                            date = self._parse_and_format_date(raw_date)
                    
                    # Create and add record - ID is always auto-generated, no auto-date for imports
                    record = DocumentRecord(sender, subject, destination, date, auto_date=False)
                    
                    # Note: ID is always auto-generated and cannot be overridden from Excel
                    
                    self.records.append(record)
                    imported_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Error importing row {index + 1}: {e}")
            
            if imported_count > 0:
                self.save_records()
                print(f"Successfully imported {imported_count} record(s).")
                if error_count > 0:
                    print(f"Encountered {error_count} error(s) during import.")
                return True
            else:
                print("No valid records found to import.")
                if not replace_existing:
                    self.records = original_records
                return False
                
        except Exception as e:
            print(f"Error importing from Excel: {e}")
            return False
    
    def restore_from_backup(self, filename: str, replace_existing: bool = True) -> bool:
        """Restore records from a JSON backup file."""
        try:
            if not os.path.exists(filename):
                print(f"Error: Backup file {filename} not found.")
                return False
            
            # Read backup file
            with open(filename, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Validate backup file structure
            if 'backup_info' not in backup_data or 'records' not in backup_data:
                print("Error: Invalid backup file format.")
                return False
            
            backup_info = backup_data['backup_info']
            records_data = backup_data['records']
            
            print(f"Backup Information:")
            print(f"  Created: {backup_info.get('created_at', 'Unknown')}")
            print(f"  Created by: {backup_info.get('created_by', 'Unknown')}")
            print(f"  Total records: {backup_info.get('total_records', 0)}")
            print(f"  Backup version: {backup_info.get('backup_version', '1.0')}")
            
            # Backup current records if not replacing
            if not replace_existing:
                original_records = self.records.copy()
            else:
                self.records = []
                # Reset ID counter when replacing all records
                DocumentRecord._id_counter = 0
                self._save_counter()
                print("ID counter reset - numbering will start from 001 for new records.")
            
            restored_count = 0
            error_count = 0
            
            for record_data in records_data:
                try:
                    # Extract data from backup
                    sender = record_data.get('sender', '')
                    subject = record_data.get('subject', '')
                    destination = record_data.get('destination', '')
                    date = record_data.get('date')
                    status = record_data.get('status', 'Pending')
                    
                    # Skip records with missing required fields
                    if not sender or not subject:
                        continue
                    
                    # Create record with original date (no auto-date)
                    record = DocumentRecord(sender, subject, destination, date, auto_date=False, status=status)
                    
                    self.records.append(record)
                    restored_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Error restoring record: {e}")
            
            if restored_count > 0:
                self.save_records()
                print(f"Successfully restored {restored_count} record(s) from backup.")
                if error_count > 0:
                    print(f"Encountered {error_count} error(s) during restore.")
                return True
            else:
                print("No valid records found in backup to restore.")
                if not replace_existing:
                    self.records = original_records
                return False
                
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False
    
    def create_excel_template(self, filename: str) -> bool:
        """Create an Excel template file for importing records."""
        if not PANDAS_AVAILABLE:
            print("Error: pandas library not available. Install with: pip install pandas openpyxl")
            return False
        
        try:
            # Create sample data for template (ID is auto-generated, not included)
            template_data = {
                'date': ['2024-01-01 10:00:00', '2024-01-02 14:30:00'],
                'sender': ['John Smith', 'Jane Doe'],
                'subject': ['Sample Invoice', 'Project Report'],
                'destination': ['Accounting Department', 'Management Team']
            }
            
            df = pd.DataFrame(template_data)
            
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            # Create Excel file with formatting
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Template')
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Template']
                
                # Add instructions in a separate sheet
                instructions = pd.DataFrame({
                    'Instructions': [
                        '1. Fill in the template with your data',
                        '2. Required columns: sender, subject, destination',
                        '3. Optional column: date (YYYY-MM-DD HH:MM:SS format)',
                        '4. IDs are AUTOMATICALLY generated - do NOT include ID column',
                        '5. Each record gets format: LGU_TNGLN-MAYOR\'S OFFICE - 001, 002, etc.',
                        '6. Delete these sample rows before importing',
                        '7. Save the file before importing',
                        '8. Use either "destination" or "to" as column header'
                    ]
                })
                instructions.to_excel(writer, index=False, sheet_name='Instructions')
            
            print(f"Excel template created: {filename}")
            print("Fill in your data and use the import function to load records.")
            return True
            
        except Exception as e:
            print(f"Error creating Excel template: {e}")
            return False
    def update_existing_ids_to_new_format(self) -> bool:
        """Update existing record IDs from old format to new format."""
        try:
            updated_count = 0
            
            for record in self.records:
                # Check if record has old format: "LGU_TNGLN-MAYOR'S OFFICE - XXX"
                if record.id.startswith("LGU_TNGLN-MAYOR'S OFFICE - "):
                    # Extract the number part
                    old_id_parts = record.id.split(" - ")
                    if len(old_id_parts) >= 2:
                        number_part = old_id_parts[-1]  # Get the last part (the number)
                        # Create new ID with simplified format
                        new_id = f"MAYOR'S OFFICE - {number_part}"
                        record.id = new_id
                        updated_count += 1
            
            if updated_count > 0:
                self.save_records()
                print(f"Successfully updated {updated_count} existing record ID(s) to new format.")
                print("Old format: LGU_TNGLN-MAYOR'S OFFICE - XXX")
                print("New format: MAYOR'S OFFICE - XXX")
                return True
            else:
                print("No records found with old ID format to update.")
                return True
                
        except Exception as e:
            print(f"Error updating existing IDs: {e}")
            return False
    
    def reset_all_data(self) -> bool:
        """Reset all data in the system - clear all records and reset counter."""
        try:
            # Clear all records
            self.records = []
            self.save_records()
            
            # Reset ID counter to 0
            DocumentRecord._id_counter = 0
            self._save_counter()
            
            print("All data has been reset successfully.")
            return True
            
        except Exception as e:
            print(f"Error resetting data: {e}")
            return False
            return False

def main():
    """Main function to demonstrate the record keeping system with login."""
    
    auth = AuthManager()
    keeper = RecordKeeper()

    while True:
        if not auth.is_logged_in():
            print("\n--- Login ---")
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            if auth.login(username, password):
                print("Login successful!")
            else:
                print("Login failed. Please try again.")
                continue
        
        print("\n" + "="*50)
        print(f"RECORD KEEPING MANAGEMENT SYSTEM - Logged in as {auth.get_current_user().username} ({auth.get_current_user().role})")
        print("="*50)
        print("1. Add new record")
        print("2. View all records")
        print("3. Search records")
        print("4. Search by date range")
        print("5. Edit record")
        print("6. Mark record as done")
        print("7. Delete record")
        print("8. View statistics")
        print("9. Export to Excel")
        print("10. Import from Excel (Append)")
        print("11. Import from Excel (Replace)")
        print("12. Create Backup")
        print("13. Create Report")
        print("14. Update existing IDs to new format")
        print("15. Logout")
        print("16. Exit")
        print("-"*50)
        
        choice = input("Enter your choice (1-16): ").strip()
        
        if choice == '1':
            print("\n--- Add New Record ---")
            sender = input("Enter sender name: ").strip()
            subject = input("Enter subject: ").strip()
            destination = input("Enter destination: ").strip()
            
            use_custom_date = input("Use custom date? (y/n): ").strip().lower()
            date = None
            if use_custom_date == 'y':
                date = input("Enter date (YYYY-MM-DD HH:MM:SS): ").strip()
            
            try:
                record = keeper.add_record(sender, subject, destination, date)
                print(f"\nRecord added successfully!")
                print(f"Record ID: {record.id}")
            except Exception as e:
                print(f"Error adding record: {e}")
        
        elif choice == '2':
            print("\n--- All Records ---")
            records = keeper.get_all_records()
            if not records:
                print("No records found.")
            else:
                for i, record in enumerate(records, 1):
                    print(f"{i}. {record}")
        
        elif choice == '3':
            print("\n--- Search Records ---")
            query = input("Enter search term (sender/subject/destination): ").strip()
            if query:
                records = keeper.search_records(query)
                if not records:
                    print("No matching records found.")
                else:
                    print(f"Found {len(records)} matching record(s):")
                    for i, record in enumerate(records, 1):
                        print(f"{i}. {record}")
        
        elif choice == '4':
            print("\n--- Search by Date Range ---")
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
            
            try:
                records = keeper.get_records_by_date_range(start_date, end_date)
                if not records:
                    print("No records found in the specified date range.")
                else:
                    print(f"Found {len(records)} record(s) in date range:")
                    for i, record in enumerate(records, 1):
                        print(f"{i}. {record}")
            except Exception as e:
                print(f"Error searching by date range: {e}")
        
        elif choice == '5':
            print("\n--- Edit Record ---")
            records = keeper.get_all_records()
            if not records:
                print("No records to edit.")
            else:
                print("Available records:")
                for i, record in enumerate(records, 1):
                    print(f"{i}. {record}")
                
                try:
                    record_num = int(input("\nEnter record number to edit: ").strip()) - 1
                    if 0 <= record_num < len(records):
                        record = records[record_num]
                        print(f"\nEditing record: {record.id}")
                        print(f"Current values:")
                        print(f"  Date: {record.date}")
                        print(f"  Sender: {record.sender}")
                        print(f"  Subject: {record.subject}")
                        print(f"  Destination: {record.destination}")
                        print(f"  Status: {record.status}")
                        
                        print("\nEnter new values (press Enter to keep current value):")
                        
                        # Date
                        new_date = input(f"Date [{record.date}]: ").strip()
                        if not new_date:
                            new_date = record.date
                        
                        # Sender
                        new_sender = input(f"Sender [{record.sender}]: ").strip()
                        if not new_sender:
                            new_sender = record.sender
                        
                        # Subject
                        new_subject = input(f"Subject [{record.subject}]: ").strip()
                        if not new_subject:
                            new_subject = record.subject
                        
                        # Destination
                        new_destination = input(f"Destination [{record.destination}]: ").strip()
                        if not new_destination:
                            new_destination = record.destination
                        
                        # Status
                        print("\nStatus options: Pending, Completed")
                        new_status = input(f"Status [{record.status}]: ").strip()
                        if not new_status:
                            new_status = record.status
                        elif new_status not in ["Pending", "Completed"]:
                            print("Invalid status. Keeping current status.")
                            new_status = record.status
                        
                        # Update the record
                        if keeper.edit_record(record.id, 
                                            date=new_date,
                                            sender=new_sender, 
                                            subject=new_subject, 
                                            destination=new_destination,
                                            status=new_status):
                            print("\nRecord updated successfully!")
                            print(f"Updated record: {keeper.get_all_records()[record_num]}")
                        else:
                            print("Failed to update record.")
                    else:
                        print("Invalid record number.")
                except ValueError:
                    print("Please enter a valid number.")
        
        elif choice == '6':
            print("\n--- Mark Record as Done ---")
            records = keeper.get_all_records()
            if not records:
                print("No records to mark as done.")
            else:
                # Show only non-done records
                pending_records = [r for r in records if r.status != "Done"]
                if not pending_records:
                    print("All records are already marked as done!")
                else:
                    print("Records that can be marked as done:")
                    for i, record in enumerate(pending_records, 1):
                        print(f"{i}. {record}")
                    
                    try:
                        record_num = int(input("\nEnter record number to mark as done: ").strip()) - 1
                        if 0 <= record_num < len(pending_records):
                            record = pending_records[record_num]
                            if keeper.mark_as_done(record.id):
                                print(f"\nRecord {record.id} marked as done successfully!")
                                # Find and show the updated record
                                updated_records = keeper.get_all_records()
                                for updated_record in updated_records:
                                    if updated_record.id == record.id:
                                        print(f"Updated record: {updated_record}")
                                        break
                            else:
                                print("Failed to mark record as done.")
                        else:
                            print("Invalid record number.")
                    except ValueError:
                        print("Please enter a valid number.")
        
        elif choice == '7':
            print("\n--- Delete Record ---")
            if not auth.can_delete():
                print("Permission denied: You do not have the rights to delete records.")
                continue
            
            records = keeper.get_all_records()
            if not records:
                print("No records to delete.")
            else:
                print("Available records:")
                for i, record in enumerate(records, 1):
                    print(f"{i}. {record}")
                
                try:
                    record_num = int(input("Enter record number to delete: ").strip()) - 1
                    if 0 <= record_num < len(records):
                        record_id = records[record_num].id
                        if keeper.delete_record(record_id):
                            print("Record deleted successfully!")
                        else:
                            print("Failed to delete record.")
                    else:
                        print("Invalid record number.")
                except ValueError:
                    print("Please enter a valid number.")
        
        elif choice == '8':
            print("\n--- Statistics ---")
            if not auth.can_view_stats():
                print("Permission denied: You do not have the rights to view statistics.")
                continue
            stats = keeper.get_statistics()
            print(f"Total Records: {stats['total_records']}")
            print(f"Unique Senders: {stats['unique_senders']}")
            print(f"Unique Destinations: {stats['unique_destinations']}")
            
            if stats['senders']:
                print("\nSenders:")
                for sender in sorted(stats['senders']):
                    print(f"  - {sender}")
            
            if stats['destinations']:
                print("\nDestinations:")
                for dest in sorted(stats['destinations']):
                    print(f"  - {dest}")
        
        elif choice == '9':
            print("\n--- Export to Excel ---")
            filename = input("Enter filename for export (without .xlsx): ").strip()
            if filename:
                if keeper.export_to_excel(filename):
                    print(f"\nExport completed! File saved as {filename}.xlsx")
                else:
                    print("Export failed.")
            else:
                print("Please enter a valid filename.")
        
        elif choice == '10':
            print("\n--- Import from Excel (Append Mode) ---")
            if not auth.can_import():
                print("Permission denied: You do not have the rights to import records.")
                continue
            
            filename = input("Enter Excel filename to import: ").strip()
            if filename:
                if not filename.endswith('.xlsx'):
                    filename += '.xlsx'
                
                print("\nAppending records to existing data...")
                if keeper.import_from_excel(filename, False):  # False means append
                    print("\nImport completed successfully!")
                    print(f"Total records now: {len(keeper.get_all_records())}")
                else:
                    print("Import failed.")
            else:
                print("Please enter a valid filename.")
        
        elif choice == '11':
            print("\n--- Import from Excel (Replace Mode) ---")
            if not auth.can_import():
                print("Permission denied: You do not have the rights to import records.")
                continue
            
            filename = input("Enter Excel filename to import: ").strip()
            if filename:
                if not filename.endswith('.xlsx'):
                    filename += '.xlsx'
                
                confirm = input("\nWARNING: This will replace ALL existing records. Are you sure? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    print("\nReplacing all existing records...")
                    if keeper.import_from_excel(filename, True):  # True means replace
                        print("\nImport completed successfully!")
                        print(f"Total records now: {len(keeper.get_all_records())}")
                    else:
                        print("Import failed.")
                else:
                    print("Import cancelled.")
            else:
                print("Please enter a valid filename.")
        
        elif choice == '12':
            print("\n--- Create System Backup ---")
            if not auth.can_import():  # Using can_import for admin check
                print("Permission denied: You do not have the rights to create backups.")
                continue
            
            if keeper.records:
                print("Creating comprehensive system backup...")
                backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'backup_{backup_time}.json'
                
                try:
                    # Create comprehensive backup with metadata
                    backup_data = {
                        'backup_info': {
                            'created_at': datetime.now().isoformat(),
                            'created_by': auth.get_current_user().username,
                            'total_records': len(keeper.records),
                            'backup_version': '1.0'
                        },
                        'records': [record.to_dict() for record in keeper.get_all_records()],
                        'statistics': keeper.get_statistics()
                    }
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(backup_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"System backup created successfully as {filename}.")
                    print(f"Backup contains {len(keeper.records)} records with metadata.")
                except Exception as e:
                    print(f"Error creating backup: {e}")
            else:
                print("No records available to backup.")
        
        elif choice == '13':
            print("\n--- Create Report ---")
            if keeper.records:
                print("Generating report...")
                stats = keeper.get_statistics()
                report_time = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'report_{report_time}.html'
                
                try:
                    records_html = ""
                    for record in keeper.get_all_records():
                        records_html += f"<tr><td>{record.id}</td><td>{record.date}</td><td>{record.sender}</td><td>{record.subject}</td><td>{record.destination}</td></tr>"
                    
                    html_content = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css'>
    <title>Record Report</title>
    <style>
        body {{ margin: 20px; }}
        .report-container {{ max-width: 800px; margin: 0 auto; }}
        .table {{ margin-bottom: 30px; }}
    </style>
</head>
<body>
    <div class='report-container'>
        <h1>📊 Record Report</h1>
        <p>Generated by: {auth.get_current_user().username} at {datetime.now().strftime('%B %d, %Y - %I:%M %p')}</p>
        <p>Total Records: {stats['total_records']}</p>
        <h2>Statistics</h2>
        <ul class='list-group'>
            <li class='list-group-item'>Unique Senders: {stats['unique_senders']}</li>
            <li class='list-group-item'>Unique Destinations: {stats['unique_destinations']}</li>
        </ul>
        <h2>Records Summary</h2>
        <table class='table table-striped'>
            <thead><tr><th>ID</th><th>Date</th><th>Sender</th><th>Subject</th><th>Destination</th></tr></thead>
            <tbody>
                {records_html}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print(f"Report generated successfully as {filename}.")
                except Exception as e:
                    print(f"Error generating report: {e}")
            else:
                print("No records available to generate a report.")
        
        elif choice == '14':
            print("\n--- Update Existing IDs to New Format ---")
            if not auth.can_import():  # Using can_import for admin-like operations
                print("Permission denied: You do not have the rights to update record IDs.")
                continue
            
            if keeper.records:
                print("This will update existing record IDs from old format to new format:")
                print("Old format: LGU_TNGLN-MAYOR'S OFFICE - XXX")
                print("New format: MAYOR'S OFFICE - XXX")
                print("")
                
                # Show records with old format if any exist
                old_format_records = [r for r in keeper.records if r.id.startswith("LGU_TNGLN-MAYOR'S OFFICE - ")]
                if old_format_records:
                    print(f"Found {len(old_format_records)} record(s) with old ID format that will be updated.")
                    if len(old_format_records) <= 10:  # Show up to 10 records
                        print("Records to be updated:")
                        for i, record in enumerate(old_format_records[:10], 1):
                            print(f"  {i}. {record.id} -> MAYOR'S OFFICE - {record.id.split(' - ')[-1]}")
                    else:
                        print(f"First 10 records to be updated:")
                        for i, record in enumerate(old_format_records[:10], 1):
                            print(f"  {i}. {record.id} -> MAYOR'S OFFICE - {record.id.split(' - ')[-1]}")
                        print(f"  ... and {len(old_format_records) - 10} more records.")
                    
                    confirm = input("\nProceed with updating record IDs? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        if keeper.update_existing_ids_to_new_format():
                            print("\nID update completed successfully!")
                        else:
                            print("\nID update failed.")
                    else:
                        print("ID update cancelled.")
                else:
                    print("All records already use the new ID format. No updates needed.")
            else:
                print("No records available to update.")
        
        elif choice == '15':
            print("\nLogging out...")
            auth.logout()
        
        elif choice == '16':
            print("\nThank you for using Record Keeping Management System!")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 16.")

if __name__ == "__main__":
    main()
