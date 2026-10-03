@echo off
setlocal
echo ==========================================================
echo Building Loan Approval Prediction System
echo ==========================================================
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your PATH.
    echo Please install Python 3.10+ from python.org and add it to PATH.
    pause
    exit /b 1
)

python scripts\build_release.py
if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Build folder created at: %~dp0build\
    echo [SUCCESS] Distribution archive created at: %~dp0dist\
) else (
    echo.
    echo [ERROR] Build encountered an error.
)
pause
