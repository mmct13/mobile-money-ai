@echo off
setlocal enabledelayedexpansion
title MoneyShield CI - Explorateur de Base de Donnees
color 0B

echo ============================================================
echo    MONEYSHIELD CI - Explorateur de Base de Donnees
echo ============================================================
echo.

REM Verification de l'environnement virtuel
if not exist ".venv" (
    echo [ERREUR] Environnement virtuel non trouve.
    echo Veuillez executer start_app.bat d'abord.
    pause
    exit /b 1
)

REM Verification de la base de donnees
if not exist "moneyshield.db" (
    echo [ATTENTION] La base de donnees n'existe pas encore.
    echo Elle sera creee automatiquement par le detecteur.
    echo.
    echo Veuillez lancer l'application avec start_app.bat
    pause
    exit /b 1
)

echo Lancement de l'explorateur de base de donnees
echo.
.venv\Scripts\python.exe view_database.py

pause
