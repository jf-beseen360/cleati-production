@echo off
REM Installation des dependances CLEATI V3.2

echo.
echo ========================================
echo   INSTALLATION DES DEPENDANCES
echo ========================================
echo.
echo Installation de: fastapi, uvicorn, pydantic
echo.
echo Veuillez patienter...
echo.

pip install --upgrade pip
pip install fastapi uvicorn pydantic sqlalchemy reportlab openpyxl python-docx

echo.
echo ========================================
echo   ✓ Installation terminee!
echo ========================================
echo.
echo Les dependances sont maintenant installees.
echo.
echo Vous pouvez maintenant lancer:
echo   LANCER_SERVEUR.bat
echo.
pause
