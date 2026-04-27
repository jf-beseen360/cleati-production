@echo off
REM CLEATI V3.3 - Production Server Launcher
REM Démarrage du serveur intelligent complet

echo.
echo ========================================
echo   CLEATI V3.3 SERVER
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Please run INSTALLER.bat first
    pause
    exit /b 1
)

echo Installing dependencies...
pip install --upgrade pip fastapi uvicorn pydantic >nul 2>&1

echo.
echo ========================================
echo   Starting CLEATI V3.3 Server
echo ========================================
echo.

echo [INFO] Server starting on http://127.0.0.1:8000
echo [INFO] API documentation: http://127.0.0.1:8000/docs
echo.
echo [INFO] Modules loaded:
echo   ✓ Financial Intelligence Engine
echo   ✓ Green Impact Intelligence Engine
echo   ✓ Business Plan Architect
echo   ✓ Monitoring & Evaluation Auto-Architect
echo.
echo [INFO] DO NOT CLOSE THIS WINDOW while testing
echo [INFO] Press Ctrl+C to stop the server
echo.

python -m uvicorn cleati_production_api_v3:app --host 127.0.0.1 --port 8000 --reload
