# 🌐 Network Setup Guide - Multi-PC Access

## Overview
Allow multiple computers to access the same Record Keeping System over your local network.

## 🖥️ Setup Methods

### Method 1: Single Server (Recommended)
**One computer hosts the system, others access via browser**

#### Server Computer Setup:
1. **Install the system** on one main computer (the "server")
2. **Modify the app.py file** - change the last line:
   ```python
   # Change from:
   app.run(host='0.0.0.0', port=5000, debug=False)
   
   # To:
   app.run(host='0.0.0.0', port=5000, debug=False)
   ```

3. **Configure Windows Firewall:**
   - Open Windows Defender Firewall
   - Click "Allow an app or feature through Windows Defender Firewall"
   - Click "Change Settings" then "Allow another app..."
   - Browse and select `python.exe`
   - Check both "Private" and "Public" boxes
   - Click OK

4. **Find the server's IP address:**
   ```cmd
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

5. **Start the system:**
   - Run `START_SYSTEM.bat`
   - Keep this window open (don't close it)

#### Client Computer Setup:
1. **No installation needed** on client computers
2. **Just open a web browser** and go to:
   ```
   http://SERVER_IP_ADDRESS:5000
   ```
   Example: `http://192.168.1.100:5000`

3. **Login** with the same credentials as the server

### Method 2: Individual Installations
**Each computer has its own copy (separate data)**

#### On Each Computer:
1. Copy the installation package
2. Run `INSTALL_WINDOWS.bat`
3. Each system will have its own data

## 🔧 Network Configuration

### Finding IP Addresses:
```cmd
ipconfig /all
```

### Testing Connection:
```cmd
ping SERVER_IP_ADDRESS
```

### Common IP Ranges:
- Home networks: `192.168.1.x` or `192.168.0.x`
- Office networks: `10.0.0.x` or `172.16.x.x`

## 🔐 Security Considerations

### Local Network Only (Recommended):
- System only accessible within your office/home network
- External internet cannot access it
- Safest option for sensitive data

### Internet Access (Advanced):
⚠️ **Not recommended without proper security setup**
- Requires port forwarding on router
- Needs HTTPS and stronger authentication
- Consider security implications

## 📱 Access Methods

### Desktop Computers:
- Use any web browser
- Bookmark: `http://SERVER_IP:5000`
- Works like a normal website

### Mobile Devices:
- Open browser on phone/tablet
- Navigate to server IP address
- Responsive design works on mobile

### Multiple Simultaneous Users:
- ✅ Multiple people can use the system at once
- ✅ Real-time updates between users
- ✅ Each user sees changes immediately
- ✅ User-specific permissions maintained

## 🛠️ Troubleshooting

### Cannot Connect from Other Computers:

1. **Check Windows Firewall:**
   - Temporarily disable Windows Firewall to test
   - If it works, add Python exception properly

2. **Verify Server is Running:**
   - Server computer must have the system running
   - Don't close the command prompt window

3. **Check Network:**
   ```cmd
   ping SERVER_IP
   ```

4. **Try Different Port:**
   - Change port in app.py: `app.run(host='0.0.0.0', port=5001)`
   - Access with: `http://SERVER_IP:5001`

### Slow Performance:
- Use wired ethernet connections when possible
- Ensure good WiFi signal strength
- Consider server computer specifications

### Data Conflicts:
- All users share the same data
- Changes are immediately visible to all users
- Use proper user roles (admin vs regular users)

## 📋 Network Setup Checklist

**Server Computer:**
- [ ] System installed and working locally
- [ ] app.py modified for network access
- [ ] Windows Firewall configured
- [ ] IP address identified
- [ ] System started and running

**Client Computers:**
- [ ] Connected to same network
- [ ] Can ping server computer
- [ ] Browser tested with server IP
- [ ] Bookmarks created for easy access

**Network:**
- [ ] All computers on same network
- [ ] Internet connection stable
- [ ] Router/switch functioning properly

## 🎯 Recommended Setup

**For Small Office (5-10 users):**
- One dedicated server computer
- Wired ethernet for server
- WiFi OK for client computers
- Regular backups of server data

**For Home Use (2-5 users):**
- Any computer can be the server
- WiFi connections acceptable
- Backup data regularly

---

**Network setup complete! All computers can now access the same Record Keeping System.**
