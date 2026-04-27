@echo off
REM Lance le serveur CLEATI V3.2

cd /d "%~dp0"

echo.
echo ========================================
echo   CLEATI V3.2 - SERVEUR
echo ========================================
echo.
echo Serveur en cours de lancement...
echo Adresse: http://localhost:8000
echo.
echo Installation des dependances...
pip install -q fastapi uvicorn pydantic sqlalchemy reportlab openpyxl python-docx 2>nul

echo Demarrage du serveur...
echo.

uvicorn cleati_production_api:app --reload --host 0.0.0.0 --port 8000

pause
