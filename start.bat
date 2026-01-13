@echo off
REM Script de demarrage SmartDoc Assistant
REM Par Muhammad Ehab

echo ============================================================
echo    SMARTDOC ASSISTANT - DEMARRAGE
echo ============================================================
echo.

REM Verifier que l'environnement virtuel existe
if not exist "env\Scripts\python.exe" (
    echo [ERREUR] Environnement virtuel non trouve!
    echo Creez-le avec: python -m venv env
    echo Puis installez: env\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Verifier que .env existe
if not exist ".env" (
    echo [ERREUR] Fichier .env non trouve!
    echo Copiez .env.example vers .env et configurez votre API key
    pause
    exit /b 1
)

echo [OK] Environnement virtuel detecte
echo [OK] Fichier .env detecte
echo.

REM Desactiver la variable d'environnement systeme si elle existe
set ANTHROPIC_API_KEY=

echo Demarrage du serveur SmartDoc Assistant...
echo.
echo Le serveur va demarrer sur http://localhost:3000
echo.
echo POUR UTILISER L'APPLICATION:
echo   1. Le serveur va demarrer automatiquement
echo   2. Ouvrez frontend\index.html dans votre navigateur
echo   3. Cliquez sur l'icone parametres (engrenage)
echo   4. Configurez:
echo      - URL API: http://localhost:3000
echo      - User ID: user_muhammad_ehab
echo   5. Sauvegardez et commencez a chatter!
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo ============================================================
echo.

REM Demarrer le serveur
env\Scripts\python.exe demo_server.py 3000
