@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo     ZEN HUB PRO - WARZONE (LOCAL)
echo ========================================
echo.

if not exist "backend\.env" (
  echo [ERREUR] backend\.env introuvable.
  pause
  exit /b 1
)

if not exist "frontend\.env" (
  echo [ERREUR] frontend\.env introuvable.
  pause
  exit /b 1
)

echo [1/4] Synchronisation de la base armes (objectif: 101)
cd /d "%~dp0backend"
python import_wzstats_weapons.py
python add_future_weapons.py

echo [2/4] Lancement backend sur http://localhost:8002
start "ZEN HUB PRO Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn server:app --host 0.0.0.0 --port 8002 --reload"

timeout /t 2 /nobreak >nul

echo [3/4] Lancement frontend sur http://localhost:3001
start "ZEN HUB PRO Frontend" cmd /k "cd /d "%~dp0frontend" && set PORT=3001 && npm start"

timeout /t 6 /nobreak >nul

echo [4/4] Ouverture de l'application
start "" "http://localhost:3001"

echo.
echo ZEN HUB PRO demarre. Fermez les deux fenetres pour arreter l'app.
pause
endlocal
