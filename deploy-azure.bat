@echo off
REM Azure Deployment Script for Server Maintenance Scheduler (Windows)
REM This script helps deploy the application to Azure using different methods

echo 🚀 Azure Deployment Script for Server Maintenance Scheduler (Windows)
echo ================================================================

REM Check if Azure CLI is installed
where az >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Azure CLI not found. Please install it first:
    echo    https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
    pause
    exit /b 1
)

REM Check if user is logged in
az account show >nul 2>nul
if %errorlevel% neq 0 (
    echo 🔑 Please log in to Azure CLI:
    az login
)

REM Generate secure secret key (simplified for Windows)
set SECRET_KEY=%RANDOM%%RANDOM%%RANDOM%%RANDOM%

echo.
echo Choose deployment method:
echo 1) Azure App Service (Recommended)
echo 2) Azure Container Instances
echo 3) Create deployment package only
echo 4) Exit

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto deploy_app_service
if "%choice%"=="2" goto deploy_container_instances
if "%choice%"=="3" goto create_package
if "%choice%"=="4" goto exit_script
echo ❌ Invalid choice. Please run the script again.
pause
exit /b 1

:deploy_app_service
echo 📱 Deploying to Azure App Service...

set /p RESOURCE_GROUP="Enter Resource Group name: "
set /p APP_NAME="Enter App Service name: "
set /p LOCATION="Enter location (e.g., eastus): "
set /p DATABASE_URL="Enter database connection string (or press Enter for SQLite): "

echo 🔐 Generated SECRET_KEY: %SECRET_KEY%

echo 📦 Creating resource group...
az group create --name %RESOURCE_GROUP% --location %LOCATION%

echo 🏗️  Creating App Service plan...
az appservice plan create --name %APP_NAME%-plan --resource-group %RESOURCE_GROUP% --sku B1 --is-linux

echo 🌐 Creating Web App...
az webapp create --resource-group %RESOURCE_GROUP% --plan %APP_NAME%-plan --name %APP_NAME% --runtime "PYTHON|3.11" --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app"

echo ⚙️  Configuring app settings...
az webapp config appsettings set --resource-group %RESOURCE_GROUP% --name %APP_NAME% --settings SECRET_KEY="%SECRET_KEY%" FLASK_ENV="production" WEBSITES_PORT="8000" SCM_DO_BUILD_DURING_DEPLOYMENT="true"

if not "%DATABASE_URL%"=="" (
    az webapp config appsettings set --resource-group %RESOURCE_GROUP% --name %APP_NAME% --settings DATABASE_URL="%DATABASE_URL%"
)

call :create_package

echo 🚀 Deploying code...
az webapp deployment source config-zip --resource-group %RESOURCE_GROUP% --name %APP_NAME% --src deployment.zip

echo ✅ Deployment completed!
echo 🌐 Your app is available at: https://%APP_NAME%.azurewebsites.net
goto completion

:deploy_container_instances
echo 🐳 Deploying to Azure Container Instances...

set /p RESOURCE_GROUP="Enter Resource Group name: "
set /p CONTAINER_GROUP="Enter Container Group name: "
set /p LOCATION="Enter location (e.g., eastus): "
set /p ACR_NAME="Enter Azure Container Registry name: "
set /p DATABASE_URL="Enter database connection string (or press Enter for SQLite): "

echo 🔐 Generated SECRET_KEY: %SECRET_KEY%

echo 📦 Creating resource group...
az group create --name %RESOURCE_GROUP% --location %LOCATION%

echo 🏗️  Creating Azure Container Registry...
az acr create --resource-group %RESOURCE_GROUP% --name %ACR_NAME% --sku Basic --admin-enabled true

echo 🔨 Building and pushing Docker image...
az acr build --registry %ACR_NAME% --image maintenance-scheduler:latest .

echo 🚀 Deploying container...
for /f "tokens=*" %%i in ('az acr show --name %ACR_NAME% --resource-group %RESOURCE_GROUP% --query "loginServer" --output tsv') do set ACR_SERVER=%%i

az container create --resource-group %RESOURCE_GROUP% --name %CONTAINER_GROUP% --image %ACR_SERVER%/maintenance-scheduler:latest --registry-login-server %ACR_SERVER% --dns-name-label maintenance-scheduler-%RANDOM% --ports 5000 --environment-variables SECRET_KEY="%SECRET_KEY%" FLASK_ENV="production" DATABASE_URL="%DATABASE_URL%" LOG_LEVEL="INFO"

echo ✅ Deployment completed!

for /f "tokens=*" %%i in ('az container show --resource-group %RESOURCE_GROUP% --name %CONTAINER_GROUP% --query "ipAddress.fqdn" --output tsv') do set FQDN=%%i
echo 🌐 Your app is available at: http://%FQDN%:5000
goto completion

:create_package
echo 📦 Creating deployment package...

REM Create deployment package using PowerShell
powershell -Command "Compress-Archive -Path *.py,*.txt,*.md,*.yml,*.yaml,Dockerfile,Procfile,static,templates,instance -DestinationPath deployment.zip -Force"

echo ✅ Deployment package created: deployment.zip
if "%choice%"=="3" goto completion
exit /b 0

:completion
echo.
echo 🎉 Deployment process completed!
echo 📝 Don't forget to:
echo    • Set up SSL certificates for HTTPS
echo    • Configure custom domain if needed
echo    • Set up monitoring and alerts
echo    • Configure backup strategy for your database
pause
exit /b 0

:exit_script
echo 👋 Goodbye!
pause
exit /b 0 