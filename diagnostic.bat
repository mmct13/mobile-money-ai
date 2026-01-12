@echo off
setlocal enabledelayedexpansion
title MoneyShield CI - Diagnostic
color 0E

echo ============================================================
echo    MONEYSHIELD CI - DIAGNOSTIC SYSTEME
echo ============================================================
echo.

REM --- TEST 1 : PYTHON ---
echo [TEST 1/5] Verification de Python...
python --version 2>&1
if !ERRORLEVEL! EQU 0 (
    echo [OK] Python est installe
) else (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
)
echo.

REM --- TEST 2 : ENVIRONNEMENT VIRTUEL ---
echo [TEST 2/5] Verification de l'environnement virtuel...
if exist ".venv" (
    echo [OK] Dossier .venv existe
    if exist ".venv\Scripts\python.exe" (
        echo [OK] Python virtuel trouve
        .venv\Scripts\python.exe --version 2>&1
    ) else (
        echo [ERREUR] Python virtuel non trouve dans .venv\Scripts
    )
) else (
    echo [ERREUR] Dossier .venv n'existe pas
)
echo.

REM --- TEST 3 : DEPENDANCES ---
echo [TEST 3/5] Verification des dependances Python...
if exist ".venv\Scripts\python.exe" (
    echo Verification de pandas...
    .venv\Scripts\python.exe -c "import pandas; print('pandas:', pandas.__version__)" 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo [OK] pandas installe
    ) else (
        echo [ERREUR] pandas non installe
    )
    
    echo Verification de sklearn...
    .venv\Scripts\python.exe -c "import sklearn; print('sklearn:', sklearn.__version__)" 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo [OK] sklearn installe
    ) else (
        echo [ERREUR] sklearn non installe
    )
    
    echo Verification de streamlit...
    .venv\Scripts\python.exe -c "import streamlit; print('streamlit:', streamlit.__version__)" 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo [OK] streamlit installe
    ) else (
        echo [ERREUR] streamlit non installe
    )
) else (
    echo [SKIP] Environnement virtuel non trouve
)
echo.

REM --- TEST 4 : DOCKER ---
echo [TEST 4/5] Verification de Docker...
docker --version 2>&1
if !ERRORLEVEL! EQU 0 (
    echo [OK] Docker est installe
    docker ps >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo [OK] Docker est lance et accessible
    ) else (
        echo [ERREUR] Docker est installe mais pas lance
        echo Veuillez lancer Docker Desktop
    )
) else (
    echo [ERREUR] Docker n'est pas installe
)
echo.

REM --- TEST 5 : FICHIERS DU PROJET ---
echo [TEST 5/5] Verification des fichiers du projet...
if exist "app\detector\entrainement.py" (
    echo [OK] app\detector\entrainement.py existe
) else (
    echo [ERREUR] app\detector\entrainement.py manquant
)

if exist "app\detector\detecteur.py" (
    echo [OK] app\detector\detecteur.py existe
) else (
    echo [ERREUR] app\detector\detecteur.py manquant
)

if exist "app\generator\generateur.py" (
    echo [OK] app\generator\generateur.py existe
) else (
    echo [ERREUR] app\generator\generateur.py manquant
)

if exist "app\dashboard\app.py" (
    echo [OK] app\dashboard\app.py existe
) else (
    echo [ERREUR] app\dashboard\app.py manquant
)

if exist "docker-compose.yml" (
    echo [OK] docker-compose.yml existe
) else (
    echo [ERREUR] docker-compose.yml manquant
)

if exist "requirements.txt" (
    echo [OK] requirements.txt existe
) else (
    echo [ERREUR] requirements.txt manquant
)

if exist "app\detector\modele_fraude.pkl" (
    echo [OK] modele_fraude.pkl existe
) else (
    echo [ATTENTION] modele_fraude.pkl manquant (sera genere au demarrage)
)
echo.

echo ============================================================
echo    DIAGNOSTIC TERMINE
echo ============================================================
echo.
echo Si vous voyez des [ERREUR], corrigez-les avant de lancer
echo l'application avec start_app.bat
echo.
pause
