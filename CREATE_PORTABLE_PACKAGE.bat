@echo off
echo ================================
echo Creating Portable Installation Package
echo ================================
echo.

REM Create package directory
set "PACKAGE_DIR=LGU_Record_System_Package"
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"

echo Creating package structure...

REM Copy essential files
copy "app.py" "%PACKAGE_DIR%\"
copy "record_keeper.py" "%PACKAGE_DIR%\"
copy "requirements.txt" "%PACKAGE_DIR%\"
copy "INSTALL_WINDOWS.bat" "%PACKAGE_DIR%\"
copy "INSTALLATION_GUIDE.md" "%PACKAGE_DIR%\"
copy ".gitignore" "%PACKAGE_DIR%\"

REM Copy directories
xcopy /E /I "templates" "%PACKAGE_DIR%\templates"
xcopy /E /I "static" "%PACKAGE_DIR%\static"
mkdir "%PACKAGE_DIR%\uploads"

REM Create README for the package
(
echo # LGU Record Keeping System - Installation Package
echo.
echo ## Quick Installation:
echo 1. Make sure Python 3.7+ is installed on target computer
echo 2. Run INSTALL_WINDOWS.bat
echo 3. Follow the instructions
echo.
echo ## Files included:
echo - Complete application files
echo - Automated installer
echo - Installation guide
echo - All templates and assets
echo.
echo ## System Requirements:
echo - Windows 7/8/10/11
echo - Python 3.7 or higher
echo - Internet connection ^(for initial setup^)
echo.
echo For detailed instructions, see INSTALLATION_GUIDE.md
) > "%PACKAGE_DIR%\README.txt"

REM Create a simple launcher
(
echo @echo off
echo echo Starting LGU Record Keeping System...
echo cd /d "%%~dp0"
echo python app.py
echo pause
) > "%PACKAGE_DIR%\START_SYSTEM.bat"

echo.
echo ================================
echo Package created successfully!
echo ================================
echo.
echo Package location: %PACKAGE_DIR%
echo.
echo To distribute:
echo 1. Copy the entire '%PACKAGE_DIR%' folder to target computer
echo 2. Run INSTALL_WINDOWS.bat on the target computer
echo 3. Use START_SYSTEM.bat to launch the application
echo.
echo The package contains everything needed for installation!
echo.
pause
