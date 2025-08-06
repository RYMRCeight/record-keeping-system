# 🖥️ LGU Record Keeping System - Installation Guide

## 📦 Installing on Other Computers

### Method 1: Automated Installation (Recommended)

1. **Download the System**
   - Copy the entire `record-keeping-system` folder to the target computer
   - Or download from GitHub: https://github.com/RYMRCeight/record-keeping-system

2. **Run the Installer**
   - Double-click `INSTALL_WINDOWS.bat`
   - Follow the on-screen instructions
   - The installer will automatically set everything up

3. **Start the System**
   - Double-click `Start_Record_System.bat`
   - Open browser to: http://localhost:5000
   - Login with: `admin` / `admin123`

### Method 2: Manual Installation

#### Prerequisites
1. **Install Python 3.7+**
   - Download from: https://python.org/downloads/
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation

2. **Verify Python Installation**
   ```cmd
   python --version
   pip --version
   ```

#### Installation Steps
1. **Extract Files**
   - Copy the `record-keeping-system` folder to desired location
   - Example: `C:\LGU-Records\`

2. **Open Command Prompt**
   - Navigate to the folder: `cd C:\LGU-Records\record-keeping-system`

3. **Install Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Create Directories**
   ```cmd
   mkdir uploads
   mkdir uploads\logos
   ```

5. **Run the Application**
   ```cmd
   python app.py
   ```

6. **Access the System**
   - Open browser to: http://localhost:5000
   - Login with default credentials

## 🔐 Default Login Credentials

| User Type | Username | Password  | Permissions |
|-----------|----------|-----------|-------------|
| Admin     | `admin`  | `admin123`| Full access |
| Regular   | `user`   | `user123` | Limited access |

⚠️ **SECURITY**: Change these passwords immediately after installation!

## 🗂️ File Structure

```
record-keeping-system/
├── app.py                          # Main application
├── record_keeper.py                # Core logic
├── requirements.txt                # Dependencies
├── INSTALL_WINDOWS.bat            # Auto installer
├── Start_Record_System.bat        # Quick launcher
├── templates/                      # Web pages
├── static/                         # CSS/JS files
├── uploads/                        # File storage
├── records.json                    # Data storage
├── users.json                      # User accounts
└── system_settings.json           # System config
```

## 🌐 Network Access (Optional)

To allow other computers on the network to access the system:

1. **Modify app.py** (last line):
   ```python
   app.run(host='0.0.0.0', port=5000, debug=False)
   ```

2. **Configure Windows Firewall**:
   - Allow Python through Windows Firewall
   - Open port 5000

3. **Access from other computers**:
   - Find the host computer's IP address: `ipconfig`
   - Access from other PCs: `http://HOST_IP:5000`
   - Example: `http://192.168.1.100:5000`

## 🔧 Troubleshooting

### Python Not Found
```
'python' is not recognized as an internal or external command
```
**Solution**: Reinstall Python and check "Add Python to PATH"

### Module Not Found Errors
```
ModuleNotFoundError: No module named 'flask'
```
**Solution**: Run `pip install -r requirements.txt`

### Port Already in Use
```
Address already in use
```
**Solution**: 
- Close other applications using port 5000
- Or change port in app.py: `app.run(port=5001)`

### Permission Errors
**Solution**: Run Command Prompt as Administrator

## 📱 System Requirements

- **OS**: Windows 7/8/10/11
- **Python**: 3.7 or higher
- **RAM**: 512 MB minimum, 1 GB recommended
- **Storage**: 100 MB free space
- **Browser**: Chrome, Firefox, Edge, or Safari

## 🔄 Updates

To update the system:
1. Download new version files
2. Replace old files (keep your data files)
3. Run: `pip install -r requirements.txt`
4. Restart the application

## 🆘 Support

For installation issues:
1. Check this guide first
2. Verify Python installation
3. Check Windows firewall settings
4. Contact system administrator

## 📋 Quick Start Checklist

- [ ] Python 3.7+ installed with PATH
- [ ] Files extracted to desired location
- [ ] Run `INSTALL_WINDOWS.bat`
- [ ] Double-click `Start_Record_System.bat`
- [ ] Open browser to http://localhost:5000
- [ ] Login with admin/admin123
- [ ] Change default passwords
- [ ] System ready to use!

---
**LGU Record Keeping System - Local Installation Complete**
