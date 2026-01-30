@echo off
:: USB Backup Tool – Windows launcher
:: Double-click this file on the USB stick to launch the backup GUI.

cd /d "%~dp0"

:: Try compiled executable first, then fall back to Python.
if exist "%~dp0USB-Backup-Tool.exe" (
    start "" "%~dp0USB-Backup-Tool.exe"
) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
        python "%~dp0main.py"
    ) else (
        echo Python not found. Please install Python 3.10+ or use the compiled .exe.
        pause
    )
)
