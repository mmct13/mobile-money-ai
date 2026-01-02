@echo off
title MoneyShield CI - Demarrage Complet
color 02

echo ============================================================
echo   🛡️  MONEYSHIELD CI - Protection Fraude Mobile Money
echo   Demarrage Automatique de Tous les Services
echo ============================================================
echo.

REM Activer l'environnement virtuel
echo [1/6] ⚡ Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERREUR: Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)
echo ✅ OK - Environnement virtuel active
echo.

REM Entraînement du modèle (si nécessaire)
echo [2/6] 🧠 Verification/Entrainement du modele IA...
if exist "app\detector\modele_fraude.pkl" (
    echo ✅ OK - Modele deja entraine (ignorer cette etape)
    echo    💡 Pour re-entrainer: supprimer app\detector\modele_fraude.pkl
) else (
    echo 📚 Entrainement du modele (20000 transactions)...
    python app\detector\entrainement.py
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ ERREUR: Echec de l'entrainement du modele
        pause
        exit /b 1
    )
    echo ✅ OK - Modele entraine avec succes
)
echo.

REM Démarrage de Kafka
echo [3/6] 🚀 Demarrage de Kafka (Docker)...
echo ⏳ Cette etape peut prendre 30 secondes...
docker-compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERREUR: Impossible de demarrer Kafka
    echo 💡 Verifiez que Docker Desktop est lance
    pause
    exit /b 1
)
echo ✅ OK - Kafka demarre

REM Attendre que Kafka soit prêt
echo.
echo [4/6] ⏳ Attente du demarrage de Kafka...
timeout /t 15 /nobreak > nul
echo ✅ OK - Kafka pret
echo.

REM Lancer le générateur dans une nouvelle fenêtre
echo [5/6] 🚀 Lancement des services MoneyShield CI...
echo    📤 Generateur de transactions...
start "MoneyShield CI - Generateur" cmd /k "cd /d %CD% && .venv\Scripts\activate && python app\generator\generateur.py"
timeout /t 2 /nobreak > nul

echo    🕵️  Detecteur de fraude IA...
start "MoneyShield CI - Detecteur" cmd /k "cd /d %CD% && .venv\Scripts\activate && python app\detector\detecteur.py"
timeout /t 3 /nobreak > nul

echo    📊 Dashboard Streamlit...
start "MoneyShield CI - Dashboard" cmd /k "cd /d %CD% && .venv\Scripts\activate && streamlit run app\dashboard\app.py"
echo ✅ OK - Tous les services sont lances
echo.

echo [6/6] ✅ Application demarree avec succes !
echo.
echo ============================================================
echo   🛡️  SERVICES ACTIFS - MONEYSHIELD CI
echo ============================================================
echo   [1] 📊 Kafka (Docker)          - Port 9092
echo   [2] 📤 Generateur              - Fenetre separee
echo   [3] 🕵️  Detecteur IA            - Fenetre separee  
echo   [4] 📈 Dashboard Streamlit     - http://localhost:8501
echo ============================================================
echo.
echo 🌐 Le dashboard s'ouvrira automatiquement dans votre navigateur.
echo.
echo 🛑 Pour arreter l'application:
echo   1. Fermez toutes les fenetres de services
echo   2. Ou executez: stop_app.bat
echo.
echo 📖 Appuyez sur une touche pour ouvrir le dashboard manuellement...
pause > nul

REM Ouvrir le dashboard dans le navigateur
start http://localhost:8501

echo.
echo ✅ Cette fenetre peut etre fermee sans arreter les services.
timeout /t 5
