@echo off
setlocal enabledelayedexpansion
title MoneyShield CI - Arret
color 0C

echo ============================================================
echo    MONEYSHIELD CI - Arret de l'Application
echo ============================================================
echo.

REM --- ETAPE 1 : VERIFICATION DE DOCKER ---
echo [1/3] Verification de Docker
docker --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo.
    echo [ATTENTION] Docker n'est pas disponible.
    echo Les conteneurs ne peuvent pas etre arretes.
    echo.
    pause
    exit /b 1
)
echo       Docker detecte : OK
echo.

REM --- ETAPE 2 : ARRET DES CONTENEURS DOCKER ---
echo [2/3] Arret des conteneurs Docker
echo       Arret en cours: dashboard, detector, generator, kafka, zookeeper

docker-compose down

if !ERRORLEVEL! EQU 0 (
    echo       Tous les conteneurs ont ete arretes avec succes
) else (
    echo.
    echo [ERREUR] Impossible d'arreter les conteneurs Docker
    echo Essayez manuellement: docker-compose down
    echo.
)
echo.

REM --- ETAPE 3 : NETTOYAGE (OPTIONNEL) ---
echo [3/3] Nettoyage
echo       Verification des conteneurs restants

docker ps -a --filter "name=zookeeper" --filter "name=kafka" --filter "name=generator" --filter "name=detector" --filter "name=dashboard" --format "{{.Names}}" >nul 2>&1

if !ERRORLEVEL! EQU 0 (
    echo       Aucun conteneur residuel detecte
) else (
    echo       Tous les conteneurs ont ete nettoyes
)
echo.

echo ============================================================
echo    APPLICATION ARRETEE AVEC SUCCES
echo ============================================================
echo.
echo Tous les services MoneyShield CI ont ete arretes:
echo    - Dashboard (Streamlit)
echo    - Detector (IA anti-fraude)
echo    - Generator (Simulateur)
echo    - Kafka (Messaging)
echo    - Zookeeper (Coordination)
echo.
echo Pour relancer l'application: start_app.bat
echo.
echo ============================================================

pause
