@echo off
setlocal enabledelayedexpansion
title MoneyShield CI - Demarrage Systeme
color 0A

echo ===============================================================================
echo    MONEYSHIELD CI - SYSTEME DE PROTECTION ANTI-FRAUDE
echo    Demarrage de l'infrastructure
echo ===============================================================================
echo.

REM --- ETAPE 1 : VERIFICATIONS PRELIMINAIRES ---
echo [1/5] Verification de l'environnement

REM Verification Python
python --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo [ERREUR] Python n'est pas detecte. Veuillez installer Python 3.9+.
    pause
    exit /b 1
)
echo    - Python : OK

REM Verification Docker
docker --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo [ERREUR] Docker n'est pas lance. Veuillez demarrer Docker Desktop.
    pause
    exit /b 1
)
echo    - Docker : OK
echo.

REM --- ETAPE 2 : ENVIRONNEMENT VIRTUEL ---
echo [2/5] Configuration Python

if not exist ".venv" (
    echo    - Creation de l'environnement virtuel...
    python -m venv .venv
    if !ERRORLEVEL! NEQ 0 (
        echo [ERREUR] Echec de la creation de .venv
        pause
        exit /b 1
    )
    
    echo    - Installation des dependances...
    .venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
    .venv\Scripts\python.exe -m pip install -r requirements.txt >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo [ERREUR] Echec de l'installation des librairies.
        pause
        exit /b 1
    )
    echo    - Dependances installees.
    echo    - Dependances installees.
) else (
    echo    - Environnement virtuel existant detecte.
    echo    - Mise a jour des dependances...
    .venv\Scripts\python.exe -m pip install -r requirements.txt >nul 2>&1
)
echo.

REM --- ETAPE 2.5 : BASE DE DONNEES ---
echo [2.5/5] Verification de la Base de Donnees

.venv\Scripts\python.exe init_db.py
if !ERRORLEVEL! NEQ 0 (
    echo [ERREUR] Impossible de creer/verifier la base de donnees.
    pause
    exit /b 1
)
echo.

REM --- ETAPE 3 : MODELE IA ---
echo [3/5] Verification du Modele IA

set PYTHONPATH=%CD%
if not exist "app\detector\modele_fraude.pkl" (
    echo    - Modele introuvable. Entrainement initial en cours...
    echo      (Cette operation peut prendre quelques secondes)
    
    .venv\Scripts\python.exe -m app.detector.entrainement
    
    if !ERRORLEVEL! NEQ 0 (
        echo [ERREUR] L'entrainement du modele a echoue.
        pause
        exit /b 1
    )
    echo    - Modele genere et sauvegarde.
) else (
    echo    - Modele IA present.
)
echo.

REM --- ETAPE 4 : DEMARRAGE DES SERVICES ---
echo [4/5] Lancement des conteneurs Docker

echo    - Arret des anciens conteneurs potentiels...
docker-compose down >nul 2>&1

echo    - Demarrage des services (hors detecteur)...
docker-compose up -d --build zookeeper kafka generator dashboard api

if !ERRORLEVEL! NEQ 0 (
    echo [ERREUR] Impossible de lancer les services de base.
    pause
    exit /b 1
)

echo    - Attente de la stabilisation (5s)...
timeout /t 5 /nobreak > nul

echo    - Demarrage du DETECTEUR (en dernier)...
docker-compose up -d --build detector

if !ERRORLEVEL! NEQ 0 (
    echo [ERREUR] Impossible de lancer le detecteur.
    echo Verifiez les logs avec : docker-compose logs
    pause
    exit /b 1
)
echo    - Services demarres avec succes.
echo.

REM --- ETAPE 5 : INITIALISATION ---
echo [5/5] Finalisation

echo    - Attente de la stabilisation des services (10s)...
timeout /t 10 /nobreak > nul

echo.
echo ===============================================================================
echo    SYSTEME OPERATIONNEL
echo ===============================================================================
echo.
echo    Etat des services :
echo    - Infrastructure (Kafka/Zookeeper) : EN LIGNE
echo    - Detection Fraude (IA)            : EN LIGNE
echo    - Generateur Transactions          : EN LIGNE
echo    - Tableau de Bord                  : EN LIGNE
echo    - API REST                         : EN LIGNE
echo.
echo    ACCES : 
echo    - Dashboard : http://localhost:8501
echo    - API Docs  : http://localhost:8000/docs
echo.
echo ===============================================================================

REM Ouverture du navigateur
start http://localhost:8501

echo Appuyez sur une touche pour fermer ce terminal.
echo Les services continuent de fonctionner en arriere-plan.
pause >nul