@echo off
setlocal enabledelayedexpansion
title MoneyShield CI - Demarrage Dockerise
color 0A

echo ============================================================
echo    MONEYSHIELD CI - Protection Fraude Mobile Money
echo    Lancement de l'architecture Docker (v2.1)
echo ============================================================
echo.

REM --- ETAPE 1 : VERIFICATION DE PYTHON ---
echo [1/5] Verification de Python
python --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo.
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH.
    echo Veuillez installer Python 3.9+ depuis https://www.python.org/
    echo.
    echo Appuyez sur une touche pour quitter...
    pause >nul
    exit /b 1
)
echo       Python detecte : OK
echo.

REM --- ETAPE 2 : PREPARATION DE L'ENVIRONNEMENT LOCAL ---
echo [2/5] Preparation de l'environnement virtuel

if not exist ".venv" (
    echo       Environnement virtuel non trouve - Creation en cours
    python -m venv .venv
    if !ERRORLEVEL! NEQ 0 (
        echo.
        echo [ERREUR] Impossible de creer l'environnement virtuel.
        echo.
        echo Appuyez sur une touche pour quitter...
        pause >nul
        exit /b 1
    )
    
    echo       Installation des dependances en cours
    if exist "requirements.txt" (
        .venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
        .venv\Scripts\python.exe -m pip install -r requirements.txt >nul 2>&1
        if !ERRORLEVEL! NEQ 0 (
            echo.
            echo [ERREUR] Echec de l'installation des dependances.
            echo.
            echo Appuyez sur une touche pour quitter...
            pause >nul
            exit /b 1
        )
        echo       Dependances installees avec succes.
    ) else (
        echo       [AVERTISSEMENT] requirements.txt introuvable.
        echo       Installation minimale en cours
        .venv\Scripts\python.exe -m pip install pandas scikit-learn joblib streamlit kafka-python faker numpy >nul 2>&1
        if !ERRORLEVEL! NEQ 0 (
            echo.
            echo [ERREUR] Echec de l'installation minimale.
            echo.
            echo Appuyez sur une touche pour quitter...
            pause >nul
           exit /b 1
        )
        echo       Installation minimale terminee.
    )
) else (
    echo       Environnement virtuel detecte : OK
)
echo.

REM --- ETAPE 3 : GENERATION DU MODELE IA ---
echo [3/5] Verification du modele IA

REM Definition du PYTHONPATH pour les imports relatifs
set PYTHONPATH=%CD%

if exist "app\detector\modele_fraude.pkl" (
    echo       Modele IA existant detecte : OK
) else (
    echo       Le modele est manquant - Entrainement en cours
    echo       Veuillez patienter (~10-20 secondes)
    echo.
    
    REM Utilisation de -m pour gerer correctement les imports
    .venv\Scripts\python.exe -m app.detector.entrainement
    
    if !ERRORLEVEL! NEQ 0 (
        echo.
        echo [ERREUR CRITIQUE] Echec de l'entrainement du modele IA.
        echo Verifiez que :
        echo    1. Vous etes a la racine du projet
        echo    2. Les fichiers de config sont presents
        echo.
        echo Appuyez sur une touche pour quitter...
        pause >nul
        exit /b 1
    )
    echo       Modele genere avec succes !
)
echo.

REM --- ETAPE 4 : LANCEMENT DOCKER COMPOSE ---
echo [4/5] Lancement des conteneurs Docker
echo       Verification de Docker

docker --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo.
    echo [ERREUR] Docker n'est pas lance ou installe.
    echo Veuillez lancer Docker Desktop.
    echo.
    echo Appuyez sur une touche pour quitter...
    pause >nul
    exit /b 1
)

echo       Docker detecte : OK
echo       Construction et demarrage des services
echo.

docker-compose up -d --build

if !ERRORLEVEL! NEQ 0 (
    echo.
    echo [ERREUR DOCKER] Impossible de lancer les services.
    echo Verifiez que le fichier docker-compose.yml est present.
    echo.
    echo Appuyez sur une touche pour quitter...
    pause >nul
    exit /b 1
)
echo.

REM --- ETAPE 5 : FINALISATION ---
echo [5/5] Attente de la stabilisation des services
timeout /t 10 /nobreak > nul

echo.
echo ============================================================
echo    APPLICATION MONEYSHIELD CI DEMARREE AVEC SUCCES !
echo ============================================================
echo.
echo    Architecture deployee :
echo    - Zookeeper et Kafka (Infrastructure messaging)
echo    - Generator (Simulateur de transactions)
echo    - Detector (IA anti-fraude et Base de donnees)
echo    - Dashboard (Interface Web Streamlit)
echo.
echo    ACCES DASHBOARD : http://localhost:8501
echo.
echo    COMMANDES UTILES :
echo    - Voir les logs       : docker-compose logs -f
echo    - Arreter tout        : docker-compose down
echo.
echo ============================================================

REM Ouverture automatique du navigateur
echo Ouverture du dashboard
timeout /t 2 /nobreak > nul
start http://localhost:8501

echo.
echo Appuyez sur une touche pour fermer cette fenetre.
echo (Les services continueront de tourner en arriere-plan)
pause >nul