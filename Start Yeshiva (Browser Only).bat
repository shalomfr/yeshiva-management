@echo off
chcp 65001 > nul
title מערכת ניהול ישיבה - Flask Server

echo.
echo ================================================
echo      מערכת ניהול ישיבה - Flask Server
echo ================================================
echo.
echo מפעיל את השרת...
echo Starting Flask server...
echo.

cd /d "%~dp0"

python app.py

if errorlevel 1 (
    echo.
    echo ================================================
    echo שגיאה בהפעלת השרת!
    echo Error starting the server!
    echo ================================================
    echo.
    pause
)



