@echo off
title MoneyShield CI - Arret
color 02

echo ============================================================
echo   🛡️  MONEYSHIELD CI - Arret de l'Application
echo ============================================================
echo.

echo [1/2] 🛑 Arret des services Docker (Kafka)...
docker-compose down
if %ERRORLEVEL% EQU 0 (
    echo ✅ OK - Kafka arrete
) else (
    echo ⚠️  ATTENTION: Kafka n'a pas pu etre arrete
)
echo.

echo [2/2] 🛑 Fermeture des services Python...
echo Veuillez fermer manuellement les fenetres suivantes:
echo   - MoneyShield CI - Generateur
echo   - MoneyShield CI - Detecteur
echo   - MoneyShield CI - Dashboard
echo.

REM Tenter de tuer les processus Python si possible
echo ⏳ Tentative d'arret automatique des processus Python...
taskkill /FI "WINDOWTITLE eq MoneyShield CI - Generateur*" /F > nul 2>&1
taskkill /FI "WINDOWTITLE eq MoneyShield CI - Detecteur*" /F > nul 2>&1
taskkill /FI "WINDOWTITLE eq MoneyShield CI - Dashboard*" /F > nul 2>&1
echo ✅ OK - Arret automatique tente
echo.

echo ============================================================
echo   ✅ Application arretee
echo ============================================================
echo.
echo Si certains services sont toujours actifs:
echo   - Fermez manuellement les fenetres de terminaux
echo   - Ou redemarrez votre ordinateur
echo.

pause
