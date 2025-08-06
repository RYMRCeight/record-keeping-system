#!/usr/bin/env python3
"""
Windows 10 Setup and Configuration Script
Optimizes the record keeping system for Windows 10
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher required for Windows 10 compatibility")
        print(f"Current version: {platform.python_version()}")
        return False
    print(f"✅ Python {platform.python_version()} - Compatible")
    return True

def install_requirements():
    """Install required packages for Windows 10"""
    requirements = [
        'flask>=2.0.0',
        'pandas>=1.3.0',
        'openpyxl>=3.0.0',
        'plotly>=5.0.0',        # For advanced charts
        'python-docx>=0.8.11',  # Word document support
        'PyPDF2>=2.0.0',        # PDF support
        'Pillow>=8.0.0',        # Image processing
        'python-barcode>=0.13.1', # Barcode generation
        'qrcode>=7.0.0',        # QR code generation
        'cryptography>=3.4.8',  # Security features
        'schedule>=1.1.0',      # Task scheduling
        'psutil>=5.8.0',        # System monitoring
    ]
    
    print("📦 Installing required packages for Windows 10...")
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print(f"✅ {package.split('>=')[0]}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    return True

def create_windows_directories():
    """Create Windows-friendly directory structure"""
    base_dir = Path.cwd()
    directories = [
        "data",
        "uploads",
        "exports",
        "templates",
        "documents",
        "backups",
        "logs",
        "config"
    ]
    
    print("📁 Creating directory structure...")
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(exist_ok=True)
        print(f"✅ {directory}/")
    
    return True

def create_windows_service_files():
    """Create Windows service and batch files"""
    
    # Create batch file to start the application
    start_bat = """@echo off
title Record Keeping System
echo Starting Record Keeping System...
cd /d "%~dp0"
python app.py
pause"""
    
    with open("start_app.bat", "w") as f:
        f.write(start_bat)
    
    # Create batch file for CLI
    cli_bat = """@echo off
title Record Keeping System - CLI
echo Record Keeping System - Command Line Interface
cd /d "%~dp0"
python record_keeper.py
pause"""
    
    with open("start_cli.bat", "w") as f:
        f.write(cli_bat)
    
    print("✅ Windows batch files created")
    return True

def create_desktop_shortcut():
    """Create desktop shortcut (Windows 10)"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Record Keeping System.lnk")
        target = os.path.join(os.getcwd(), "start_app.bat")
        wDir = os.getcwd()
        icon = os.path.join(os.getcwd(), "start_app.bat")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()
        
        print("✅ Desktop shortcut created")
        return True
    except ImportError:
        print("ℹ️  Desktop shortcut creation requires pywin32 package")
        return False

def optimize_for_windows():
    """Apply Windows 10 specific optimizations"""
    
    # Set Windows-friendly paths
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Create Windows registry entry (optional)
    print("⚙️  Applying Windows 10 optimizations...")
    
    # Configure matplotlib for Windows (if using charts)
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        print("✅ Matplotlib configured for Windows")
    except ImportError:
        pass
    
    return True

def create_config_file():
    """Create Windows-specific configuration"""
    config = {
        "system": {
            "platform": "windows",
            "data_directory": "./data",
            "upload_directory": "./uploads",
            "export_directory": "./exports",
            "max_file_size": "50MB",
            "allowed_extensions": [".xlsx", ".xls", ".pdf", ".docx", ".jpg", ".png"]
        },
        "database": {
            "type": "json",
            "file": "./data/records.json",
            "backup_enabled": True,
            "backup_interval": "daily"
        },
        "security": {
            "enable_encryption": False,
            "session_timeout": 3600,
            "max_login_attempts": 5
        },
        "features": {
            "enable_ocr": False,
            "enable_barcode": True,
            "enable_notifications": True,
            "enable_backup": True
        }
    }
    
    import json
    with open("config/app_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration file created")
    return True

def main():
    """Main setup function"""
    print("🚀 Record Keeping System - Windows 10 Setup")
    print("=" * 50)
    
    # Check system compatibility
    if not check_python_version():
        return False
    
    print(f"💻 Operating System: {platform.system()} {platform.release()}")
    print(f"🖥️  Architecture: {platform.architecture()[0]}")
    
    # Run setup steps
    steps = [
        ("Installing packages", install_requirements),
        ("Creating directories", create_windows_directories),
        ("Creating batch files", create_windows_service_files),
        ("Creating configuration", create_config_file),
        ("Applying optimizations", optimize_for_windows),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Failed: {step_name}")
            return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Double-click 'start_app.bat' to run the web interface")
    print("2. Double-click 'start_cli.bat' to run the command line interface")
    print("3. Access the web interface at: http://localhost:5000")
    print("\n💡 Tip: Pin the batch files to your taskbar for quick access!")
    
    return True

if __name__ == "__main__":
    main()
