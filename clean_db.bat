@echo off
setlocal enabledelayedexpansion
title MoneyShield CI - Nettoyage BDD
color 0C

echo ============================================================
echo    MONEYSHIELD CI - NETTOYAGE BASE DE DONNEES
echo ============================================================
echo.

REM Verification de l'environnement virtuel
if not exist ".venv" (
    echo [ERREUR] Environnement virtuel non trouve.
    echo Veuillez executer start_app.bat d'abord.
    pause
    exit /b 1
)

echo ATTENTION : Cette operation va effacer TOUTES les donnees de la base.
echo Cette action est irreversible.
echo.
set /p confirm="Etes-vous sur de vouloir continuer ? (O/N) : "
if /i not "%confirm%"=="O" (
    echo Operation annulee.
    pause
    exit /b 0
)

echo.
echo Lancement du nettoyage...
.venv\Scripts\python.exe clean_db.py

echo.
pause
