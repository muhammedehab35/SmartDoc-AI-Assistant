@echo off
REM ###############################################################################
REM Script de déploiement SmartDoc Assistant sur AWS (Windows)
REM Usage: deploy.bat [dev|prod]
REM ###############################################################################

setlocal enabledelayedexpansion

REM Configuration
set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=dev

set STACK_NAME=smartdoc-%ENVIRONMENT%
set REGION=%AWS_REGION%
if "%REGION%"=="" set REGION=us-east-1

for /f %%i in ('powershell -Command "Get-Date -Format 'yyyyMMddHHmmss'"') do set TIMESTAMP=%%i
set BUCKET_NAME=smartdoc-deployment-%ENVIRONMENT%-%TIMESTAMP%

echo ========================================
echo 🚀 Déploiement SmartDoc Assistant
echo ========================================
echo.
echo Environnement: %ENVIRONMENT%
echo Région: %REGION%
echo Stack: %STACK_NAME%
echo.

REM Vérifier les prérequis
echo 📋 Vérification des prérequis...

where aws >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ AWS CLI n'est pas installé
    exit /b 1
)

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Python n'est pas installé
    exit /b 1
)

if "%ANTHROPIC_API_KEY%"=="" (
    echo ❌ Variable d'environnement ANTHROPIC_API_KEY non définie
    echo Définissez-la avec: set ANTHROPIC_API_KEY=your_key
    exit /b 1
)

echo ✅ Prérequis OK
echo.

REM 1. Créer le bucket S3
echo 📦 Création du bucket S3 de déploiement...
aws s3 mb s3://%BUCKET_NAME% --region %REGION% 2>nul
echo ✅ Bucket créé: %BUCKET_NAME%
echo.

REM 2. Package les Lambdas
echo 📦 Package des fonctions Lambda...

REM Fonction pour packager une Lambda
call :package_lambda orchestrator
call :package_lambda medication-agent
call :package_lambda symptom-agent
call :package_lambda emergency-agent

echo.

REM 3. Upload vers S3
echo ⬆️  Upload des packages vers S3...
aws s3 cp orchestrator.zip s3://%BUCKET_NAME%/
aws s3 cp medication-agent.zip s3://%BUCKET_NAME%/
aws s3 cp symptom-agent.zip s3://%BUCKET_NAME%/
aws s3 cp emergency-agent.zip s3://%BUCKET_NAME%/
echo ✅ Packages uploadés
echo.

REM 4. Déployer CloudFormation
echo 🏗️  Déploiement de l'infrastructure CloudFormation...
aws cloudformation deploy ^
    --template-file infrastructure\cloudformation.yaml ^
    --stack-name %STACK_NAME% ^
    --parameter-overrides ^
        AnthropicApiKey=%ANTHROPIC_API_KEY% ^
        DeploymentBucket=%BUCKET_NAME% ^
        Environment=%ENVIRONMENT% ^
    --capabilities CAPABILITY_NAMED_IAM ^
    --region %REGION% ^
    --no-fail-on-empty-changeset

echo ✅ Infrastructure déployée
echo.

REM 5. Récupérer l'URL de l'API
echo 🔍 Récupération de l'URL API...
for /f "delims=" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text --region %REGION%') do set API_URL=%%i

echo.
echo ========================================
echo ✅ Déploiement terminé avec succès!
echo ========================================
echo.
echo 🌐 URL de l'API: %API_URL%
echo 📦 Bucket S3: %BUCKET_NAME%
echo 🏗️  Stack: %STACK_NAME%
echo.
echo 📝 Prochaines étapes:
echo   1. Tester l'API
echo   2. Créer des utilisateurs test
echo   3. Configurer le frontend avec cette URL
echo.

REM Nettoyer les fichiers zip locaux
echo 🧹 Nettoyage des fichiers temporaires...
del /f /q orchestrator.zip medication-agent.zip symptom-agent.zip emergency-agent.zip 2>nul
echo ✅ Nettoyage terminé
echo.

echo 🎉 SmartDoc Assistant est maintenant déployé!
goto :eof

REM ===== FONCTION POUR PACKAGER UNE LAMBDA =====
:package_lambda
set AGENT_NAME=%1
set LAMBDA_DIR=lambda\%AGENT_NAME%
set OUTPUT_ZIP=%AGENT_NAME%.zip

echo   📦 Package %AGENT_NAME%...

REM Créer un répertoire temporaire
set TEMP_DIR=%TEMP%\smartdoc_%AGENT_NAME%_%RANDOM%
mkdir %TEMP_DIR%

REM Copier les fichiers
xcopy /E /I /Q %LAMBDA_DIR% %TEMP_DIR%
xcopy /E /I /Q shared %TEMP_DIR%

REM Installer les dépendances
if exist "%LAMBDA_DIR%\requirements.txt" (
    pip install -r %LAMBDA_DIR%\requirements.txt -t %TEMP_DIR% --quiet
)

REM Créer le zip
cd %TEMP_DIR%
powershell Compress-Archive -Path * -DestinationPath %OUTPUT_ZIP% -Force
move /Y %OUTPUT_ZIP% %~dp0..\
cd %~dp0..

REM Nettoyer
rd /s /q %TEMP_DIR%

echo   ✅ %AGENT_NAME%.zip créé
goto :eof
