@echo off
title MoneyShield CI - Verification
color 02

echo ============================================================
echo   🛡️  MONEYSHIELD CI - Verification Complete du Projet
echo ============================================================
echo.

REM Activer l'environnement virtuel
echo ⚡ Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo.

echo [1/3] 📦 Test des imports Python...
python test_imports.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERREUR: Tests d'imports echoues
    pause
    exit /b 1
)
echo ✅ OK - Imports valides

echo.
echo [2/3] 📊 Validation du dashboard...
python test_dashboard.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERREUR: Validation du dashboard echouee
    pause
    exit /b 1
)
echo ✅ OK - Dashboard valide

echo.
echo [3/3] 🔍 Verification complete du projet...
python verify_project.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERREUR: Verification complete echouee
    pause
    exit /b 1
)
echo ✅ OK - Projet verifie

echo.
echo ============================================================
echo   ✅ TOUS LES TESTS SONT PASSES !
echo ============================================================
echo.
echo 🎉 Le projet MoneyShield CI est pret a etre utilise.
echo.
echo 📋 Prochaines etapes:
echo   1. 🧠 Entrainer le modele: python app\detector\entrainement.py
echo   2. 🚀 Demarrer Kafka: docker-compose up -d
echo   3. 📤 Lancer le generateur: python app\generator\generateur.py
echo   4. 🕵️  Lancer le detecteur: python app\detector\detecteur.py
echo   5. 📊 Ouvrir le dashboard: streamlit run app\dashboard\app.py
echo.
echo 💡 Ou utilisez simplement: start_app.bat
echo.

pause
