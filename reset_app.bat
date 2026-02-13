@echo off
setlocal enabledelayedexpansion
title MoneyShield CI - Reset Systeme
color 0E

echo ===============================================================================
echo    MONEYSHIELD CI - REINITIALISATION TOTALE
echo    Action : Remise a zero de l'environnement
echo ===============================================================================
echo.

echo ATTENTION : Cette action va effacer TOUTES les donnees :
echo    - Base de donnees (transactions, utilisateurs...)
echo    - Modeles IA entraines (fichier .pkl)
echo    - Conteneurs et volumes Docker (files d'attente Kafka...)
echo.
set /p confirm="Etes-vous sur de vouloir tout reinitialiser ? (O/N) : "
if /i not "%confirm%"=="O" (
    echo Operation annulee.
    pause
    exit /b 0
)
echo.

REM --- ETAPE 1 : ARRET ET NETTOYAGE DOCKER ---
echo [1/3] Nettoyage Docker...
echo    - Arret des conteneurs et suppression des volumes...
docker-compose down -v
if !ERRORLEVEL! NEQ 0 (
    echo [AVERTISSEMENT] Erreur lors du nettoyage Docker.
    echo Essayez manuellement : docker-compose down -v
) else (
    echo    - Environnement Docker nettoye.
)
echo.

REM --- ETAPE 2 : SUPPRESSION BASE DE DONNEES ---
echo [2/3] Suppression de la Base de Donnees...

if exist "moneyshield.db" (
    del /f /q "moneyshield.db"
    echo    - moneyshield.db supprime.
) else (
    echo    - moneyshield.db n'existe pas.
)

if exist "moneyshield.db-journal" (
    del /f /q "moneyshield.db-journal"
    echo    - moneyshield.db-journal supprime.
)

echo.

REM --- ETAPE 3 : SUPPRESSION MODELES IA ---
echo [3/3] Suppression des Modeles IA...

if exist "app\detector\modele_fraude.pkl" (
    del /f /q "app\detector\modele_fraude.pkl"
    echo    - modele_fraude.pkl supprime.
) else (
    echo    - modele_fraude.pkl n'existe pas.
)

if exist "app\detector\modele_isoforest.pkl" (
    del /f /q "app\detector\modele_isoforest.pkl"
    echo    - modele_isoforest.pkl supprime.
) else (
    echo    - modele_isoforest.pkl n'existe pas.
)

echo.
echo ===============================================================================
echo    REINITIALISATION TERMINEE
echo ===============================================================================
echo.

set /p relaunch="Voulez-vous RELANCER l'application maintenant (start_app.bat) ? (O/N) : "
if /i "%relaunch%"=="O" (
    echo Lancement de start_app.bat...
    timeout /t 2 /nobreak > nul
    start_app.bat
) else (
    echo Fin du programme.
    pause
)
