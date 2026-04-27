@echo off
REM CLEATI V3.3 - Test Suite Launcher
REM Installs dependencies and runs comprehensive tests

echo.
echo ========================================
echo   CLEATI V3.3 - TEST SUITE
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Checking/Installing dependencies...
pip install --upgrade pip fastapi uvicorn pydantic >nul 2>&1

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Running CLEATI V3.3 Test Suite
echo ========================================
echo.

python test_suite_cleati_v3.py

echo.
echo ========================================
echo   Tests Complete!
echo ========================================
echo.
pause
