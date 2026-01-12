@echo off
setlocal enabledelayedexpansion
title MoneyShield CI - Arret Systeme
color 0C

echo ===============================================================================
echo    MONEYSHIELD CI - ARRET DU SYSTEME
echo ===============================================================================
echo.

REM --- VERIFICATION DOCKER ---
docker --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo [ERREUR] Docker n'est pas accessible.
    echo Impossible d'arreter les conteneurs proprement.
    pause
    exit /b 1
)

REM --- ARRET DES SERVICES ---
echo [1/2] Arret des services en cours...
docker-compose down

if !ERRORLEVEL! EQU 0 (
    echo    - Conteneurs arretes et supprimes.
) else (
    echo [ERREUR] L'arret a rencontre un probleme.
    echo Essayez manuellement : docker-compose down
)
echo.

REM --- NETTOYAGE ---
echo [2/2] Verification du nettoyage...
docker ps -q --filter "name=kafka" --filter "name=zookeeper" >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo    - Environnement propre.
) else (
    echo    - Attention : Certains conteneurs semblent encore actifs.
)

echo.
echo ===============================================================================
echo    SYSTEME ARRETE
echo ===============================================================================
echo.
echo Vous pouvez fermer cette fenetre.
pause >nul
