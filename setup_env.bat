@echo off
setlocal
echo ============================================================
echo  Qiling Framework Environment Setup (Batch Installer)
echo ============================================================

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [-] Python was not found in PATH. Please install Python 3.8-3.12.
    pause
    exit /b 1
)

REM Set temp directory to D drive if available
if not exist "D:\Temp" mkdir "D:\Temp"
set TEMP=D:\Temp
set TMP=D:\Temp

REM Create virtual environment
if not exist ".venv" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [-] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [*] Installing requirements into .venv...
.\.venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt
if %errorlevel% neq 0 (
    echo [-] Pip install failed.
    pause
    exit /b 1
)

echo [*] Running verification test...
.\.venv\Scripts\python.exe verify_all.py

echo ============================================================
echo  Setup Complete! To activate: .\.venv\Scripts\activate.bat
echo ============================================================
pause
