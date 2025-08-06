@echo off
echo ================================
echo  LGU Record Keeping System
echo  Windows Installation Script
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.7+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✓ Python found!
python --version

REM Create virtual environment (optional but recommended)
echo.
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Warning: Could not create virtual environment. Continuing with system Python...
) else (
    echo ✓ Virtual environment created
    call venv\Scripts\activate.bat
)

REM Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo ✓ Dependencies installed successfully!

REM Create necessary directories
echo.
echo Creating directories...
if not exist "uploads" mkdir uploads
if not exist "uploads\logos" mkdir uploads\logos
echo ✓ Directories created

REM Create desktop shortcut script
echo.
echo Creating launch script...
(
echo @echo off
echo cd /d "%~dp0"
echo if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat
echo echo Starting LGU Record Keeping System...
echo echo Open your browser to: http://localhost:5000
echo echo Press Ctrl+C to stop the server
echo python app.py
echo pause
) > "Start_Record_System.bat"

echo ✓ Launch script created

echo.
echo ================================
echo  Installation Complete!
echo ================================
echo.
echo To start the system:
echo 1. Double-click "Start_Record_System.bat"
echo 2. Open browser to: http://localhost:5000
echo 3. Login with: admin / admin123
echo.
echo Default users:
echo - Admin: admin / admin123
echo - User:  user / user123
echo.
echo IMPORTANT: Change passwords after first login!
echo.
pause
