@echo off
REM Setup script for the static site generator blog (Windows)

echo Setting up your static site generator blog...
echo.

REM Check Python version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is required but not installed.
    echo Please install Python 3.8 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo Your blog is ready to use!
echo.
echo Quick Start Commands:
echo ---------------------
echo   Build site:    python build.py
echo   Preview:       python serve.py
echo   
echo After running 'python serve.py', open http://localhost:8000 in your browser
echo.
echo See README.md for full documentation
echo.
pause
