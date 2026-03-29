@echo off
REM ──────────────────────────────────────────────────────────────────
REM  Client Hunter v2  –  Steve Kaks
REM  Double-click this file to start the app on Windows.
REM  Then open http://localhost:5000 in your browser.
REM ──────────────────────────────────────────────────────────────────

echo.
echo ============================================
echo   Client Hunter v2 -- Steve Kaks
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    echo Download from https://python.org
    pause
    exit /b 1
)
echo Python found.

REM Create venv if not exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo Dependencies installed.

if not exist "data" mkdir data

echo.
echo   Starting server on http://localhost:5000
echo   Press Ctrl+C to stop.
echo.
python app.py
pause
