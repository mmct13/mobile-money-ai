@echo off
setlocal enabledelayedexpansion
title MoneyShield CI - Injection Historique
color 0B

echo ===============================================================================
echo    MONEYSHIELD CI - INJECTION DONNEES PASSEES
echo    Action : Ajout de transactions (J-3 a J-1)
echo ===============================================================================
echo.

REM Verification de l'environnement virtuel
if not exist ".venv" (
    echo [ERREUR] Environnement virtuel non trouve.
    echo Veuillez executer start_app.bat d'abord.
    pause
    exit /b 1
)

echo Lancement de l'injection...
.venv\Scripts\python.exe inject_past_data.py

if !ERRORLEVEL! NEQ 0 (
    echo [ERREUR] L'injection a rencontre un probleme.
    pause
    exit /b 1
)

echo.
echo Injection terminee avec succes.
pause
