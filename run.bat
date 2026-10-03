@echo off
setlocal
echo ==========================================================
echo Starting Loan Approval Prediction System
echo ==========================================================
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your PATH.
    echo Please install Python 3.10+ from python.org and add it to PATH.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [INFO] Creating Python virtual environment (.venv)...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo [INFO] Installing required dependencies...
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo [INFO] Starting web application at http://127.0.0.1:5000 ...
start http://127.0.0.1:5000
python app.py
pause
