@echo off
chcp 65001 > nul
title מערכת ניהול ישיבה - Yeshiva Management System

echo.
echo ================================================
echo      מערכת ניהול ישיבה - Yeshiva System
echo ================================================
echo.
echo מפעיל את המערכת...
echo Starting the system...
echo.

cd /d "%~dp0"

python run_app.py

if errorlevel 1 (
    echo.
    echo ================================================
    echo שגיאה בהפעלת המערכת!
    echo Error starting the system!
    echo ================================================
    echo.
    echo האם Python מותקן? Is Python installed?
    echo נסה להריץ: python --version
    echo.
    pause
)



