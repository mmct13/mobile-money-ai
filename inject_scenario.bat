@echo off
setlocal enabledelayedexpansion
title MoneyShield CI - Simulation Attaque
color 0C

echo ===============================================================================
echo    MONEYSHIELD CI - SIMULATION D'ATTAQUE
echo    Scenario : Retrait massif suspect a distance
echo ===============================================================================
echo.

REM Verification de l'environnement virtuel
if not exist ".venv" (
    echo [ERREUR] Environnement virtuel non trouve.
    echo Veuillez executer start_app.bat d'abord.
    pause
    exit /b 1
)

echo Lancement de l'attaque simulee...
.venv\Scripts\python.exe inject_scenario.py

if !ERRORLEVEL! NEQ 0 (
    echo [ERREUR] L'attaque a echoue (techniquement).
    pause
    exit /b 1
)

echo.
echo Attaque envoyee. Verifiez le Dashboard !
pause
