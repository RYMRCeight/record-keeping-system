# Record Keeping System - Login Guide

## Overview
The Record Keeping Management System now includes a secure login system with role-based access control. There are two types of users with different permissions.

## Default User Accounts

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Administrator

### User Account  
- **Username**: `user`
- **Password**: `user123`
- **Role**: Regular User

**⚠️ IMPORTANT**: Please change these default passwords after first login for security!

## User Roles and Permissions

### Admin (Full Access)
Administrators can perform ALL operations:
- ✅ Add new records
- ✅ View all records  
- ✅ Search records
- ✅ Search by date range
- ✅ **Delete records** (Admin only)
- ✅ **View statistics** (Admin only)
- ✅ Export to Excel
- ✅ **Import from Excel** (Admin only)
- ✅ Create Excel templates
- ✅ Logout

### User (Limited Access)
Regular users have restricted permissions:
- ✅ Add new records
- ✅ View all records
- ✅ Search records  
- ✅ Search by date range
- ❌ Delete records (Permission denied)
- ❌ View statistics (Permission denied)
- ✅ Export to Excel
- ❌ Import from Excel (Permission denied)
- ✅ Create Excel templates
- ✅ Logout

## How to Use

1. **Start the System**
   ```bash
   python record_keeper.py
   ```

2. **Login**
   - Enter your username when prompted
   - Enter your password when prompted
   - System will show "Login successful!" if credentials are correct

3. **Work with Records**
   - The main menu shows your current user and role
   - Options that require admin privileges will show "Permission denied" for regular users

4. **Logout**
   - Choose option 9 to logout
   - You'll return to the login screen

5. **Exit**
   - Choose option 10 to exit the system completely

## Security Features

- **Password Hashing**: All passwords are hashed using SHA-256
- **Session Management**: Users must login to access the system
- **Role-Based Access**: Different permissions based on user role
- **Secure Storage**: User credentials stored in encrypted format in `users.json`

## File Structure

- `users.json` - Stores user accounts and hashed passwords
- `records.json` - Stores all document records
- `record_keeper.py` - Main application with login system

## Troubleshooting

**Login Failed**
- Check username and password spelling
- Ensure caps lock is not on
- Use default credentials if this is first time

**Permission Denied**  
- This is normal for regular users trying to access admin features
- Login as admin to access restricted features

**System Won't Start**
- Ensure Python is installed
- Check that all required files are in the same directory

## Admin Features

Admins have exclusive access to:
- **Delete Records**: Remove unwanted records permanently
- **Import from Excel**: Bulk import records from Excel files  
- **View Statistics**: See detailed analytics about records
- **User Management**: (Future feature - add/remove users)

## User Features  

Regular users can:
- **Add Records**: Create new document records
- **View & Search**: Browse and find existing records
- **Export Data**: Save records to Excel for external use
- **Generate Templates**: Create Excel templates for data entry

This role separation ensures data security while allowing appropriate access for different user types.
