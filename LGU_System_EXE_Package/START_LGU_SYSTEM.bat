@echo off
title LGU Record Keeping System
echo ================================
echo  LGU Record Keeping System
echo  Starting Portable Version...
echo ================================
echo.
echo Starting server...
echo Please wait...
echo.
echo After the server starts:
echo 1. Open your web browser
echo 2. Go to: http://localhost:5000
echo 3. Login with: admin / admin123
echo.
echo To stop the server: Close this window or press Ctrl+C
echo.

start "" "http://localhost:5000"
LGU_Record_System.exe

echo.
echo Server stopped. You can close this window.
pause
