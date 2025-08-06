@echo off
echo ================================
echo Creating EXE Distribution Package
echo ================================
echo.

set "PACKAGE_DIR=LGU_System_EXE_Package"

REM Clean up any existing package
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"

echo Copying EXE and support files...
copy "dist\LGU_Record_System.exe" "%PACKAGE_DIR%\"
copy "dist\README_EXE.txt" "%PACKAGE_DIR%\"
copy "dist\START_LGU_SYSTEM.bat" "%PACKAGE_DIR%\"

REM Create additional helpful files
echo Creating Quick Start guide...
(
echo LGU RECORD KEEPING SYSTEM - QUICK START
echo =====================================
echo.
echo STEP 1: Double-click "START_LGU_SYSTEM.bat"
echo        ^(This will automatically open your browser^)
echo.
echo STEP 2: Login with default credentials:
echo        Username: admin
echo        Password: admin123
echo.
echo STEP 3: Start using the system!
echo.
echo IMPORTANT: Change the default passwords after first login
echo.
echo For detailed instructions, see README_EXE.txt
echo.
echo =====================================
echo System Requirements: Windows 7/8/10/11
echo File Size: ~48MB
echo No Installation Required!
) > "%PACKAGE_DIR%\QUICK_START.txt"

echo.
echo ================================
echo EXE Package Created Successfully!
echo ================================
echo.
echo Package location: %PACKAGE_DIR%
echo Package contents:
echo - LGU_Record_System.exe ^(48MB^)
echo - START_LGU_SYSTEM.bat ^(Easy launcher^)
echo - README_EXE.txt ^(Detailed instructions^)
echo - QUICK_START.txt ^(Quick start guide^)
echo.
echo DISTRIBUTION:
echo 1. Copy the entire '%PACKAGE_DIR%' folder to any Windows computer
echo 2. No Python installation required on target computer
echo 3. No internet required for operation
echo 4. Portable - runs from any folder
echo.
echo TO USE: Double-click START_LGU_SYSTEM.bat on target computer
echo.
pause
