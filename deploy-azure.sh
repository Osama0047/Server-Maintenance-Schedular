#!/bin/bash
# Azure Deployment Script for Server Maintenance Scheduler
# This script helps deploy the application to Azure using different methods

set -e

echo "🚀 Azure Deployment Script for Server Maintenance Scheduler"
echo "============================================================"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if user is logged in
if ! az account show &> /dev/null; then
    echo "🔑 Please log in to Azure CLI:"
    az login
fi

# Function to generate secure secret key
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_hex(32))"
}

# Function to deploy to Azure App Service
deploy_app_service() {
    echo "📱 Deploying to Azure App Service..."
    
    read -p "Enter Resource Group name: " RESOURCE_GROUP
    read -p "Enter App Service name: " APP_NAME
    read -p "Enter location (e.g., eastus): " LOCATION
    read -p "Enter database connection string (or press Enter for SQLite): " DATABASE_URL
    
    # Generate secret key
    SECRET_KEY=$(generate_secret_key)
    echo "🔐 Generated SECRET_KEY: $SECRET_KEY"
    
    # Create resource group
    echo "📦 Creating resource group..."
    az group create --name $RESOURCE_GROUP --location $LOCATION
    
    # Create App Service plan
    echo "🏗️  Creating App Service plan..."
    az appservice plan create \
        --name ${APP_NAME}-plan \
        --resource-group $RESOURCE_GROUP \
        --sku B1 \
        --is-linux
    
    # Create Web App
    echo "🌐 Creating Web App..."
    az webapp create \
        --resource-group $RESOURCE_GROUP \
        --plan ${APP_NAME}-plan \
        --name $APP_NAME \
        --runtime "PYTHON|3.11" \
        --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 app:app"
    
    # Configure app settings
    echo "⚙️  Configuring app settings..."
    az webapp config appsettings set \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --settings \
            SECRET_KEY="$SECRET_KEY" \
            FLASK_ENV="production" \
            WEBSITES_PORT="8000" \
            SCM_DO_BUILD_DURING_DEPLOYMENT="true"
    
    if [ ! -z "$DATABASE_URL" ]; then
        az webapp config appsettings set \
            --resource-group $RESOURCE_GROUP \
            --name $APP_NAME \
            --settings DATABASE_URL="$DATABASE_URL"
    fi
    
    # Deploy code
    echo "🚀 Deploying code..."
    az webapp deployment source config-zip \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --src "$(pwd)/deployment.zip"
    
    echo "✅ Deployment completed!"
    echo "🌐 Your app is available at: https://${APP_NAME}.azurewebsites.net"
}

# Function to deploy to Azure Container Instances
deploy_container_instances() {
    echo "🐳 Deploying to Azure Container Instances..."
    
    read -p "Enter Resource Group name: " RESOURCE_GROUP
    read -p "Enter Container Group name: " CONTAINER_GROUP
    read -p "Enter location (e.g., eastus): " LOCATION
    read -p "Enter Azure Container Registry name: " ACR_NAME
    read -p "Enter database connection string (or press Enter for SQLite): " DATABASE_URL
    
    # Generate secret key
    SECRET_KEY=$(generate_secret_key)
    echo "🔐 Generated SECRET_KEY: $SECRET_KEY"
    
    # Create resource group
    echo "📦 Creating resource group..."
    az group create --name $RESOURCE_GROUP --location $LOCATION
    
    # Create Azure Container Registry
    echo "🏗️  Creating Azure Container Registry..."
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $ACR_NAME \
        --sku Basic \
        --admin-enabled true
    
    # Build and push Docker image
    echo "🔨 Building and pushing Docker image..."
    az acr build \
        --registry $ACR_NAME \
        --image maintenance-scheduler:latest \
        .
    
    # Get ACR credentials
    ACR_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)
    ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" --output tsv)
    ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv)
    
    # Deploy container
    echo "🚀 Deploying container..."
    az container create \
        --resource-group $RESOURCE_GROUP \
        --name $CONTAINER_GROUP \
        --image ${ACR_SERVER}/maintenance-scheduler:latest \
        --registry-login-server $ACR_SERVER \
        --registry-username $ACR_USERNAME \
        --registry-password $ACR_PASSWORD \
        --dns-name-label maintenance-scheduler-${RANDOM} \
        --ports 5000 \
        --environment-variables \
            SECRET_KEY="$SECRET_KEY" \
            FLASK_ENV="production" \
            DATABASE_URL="$DATABASE_URL" \
            LOG_LEVEL="INFO"
    
    echo "✅ Deployment completed!"
    
    # Get the FQDN
    FQDN=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_GROUP --query "ipAddress.fqdn" --output tsv)
    echo "🌐 Your app is available at: http://${FQDN}:5000"
}

# Function to create deployment package
create_deployment_package() {
    echo "📦 Creating deployment package..."
    
    # Create a temporary directory
    TEMP_DIR=$(mktemp -d)
    
    # Copy necessary files
    cp -r . $TEMP_DIR/
    cd $TEMP_DIR
    
    # Remove unnecessary files
    rm -rf .git __pycache__ *.pyc .env venv .vscode
    rm -f deployment.zip
    
    # Create zip file
    zip -r deployment.zip . -x "*.git*" "*__pycache__*" "*.pyc" "*.env*" "*venv*" "*.vscode*"
    
    # Move back to original directory
    mv deployment.zip $(pwd)/
    cd - > /dev/null
    
    echo "✅ Deployment package created: deployment.zip"
}

# Main menu
echo "Choose deployment method:"
echo "1) Azure App Service (Recommended)"
echo "2) Azure Container Instances"
echo "3) Create deployment package only"
echo "4) Exit"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        create_deployment_package
        deploy_app_service
        ;;
    2)
        deploy_container_instances
        ;;
    3)
        create_deployment_package
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment process completed!"
echo "📝 Don't forget to:"
echo "   • Set up SSL certificates for HTTPS"
echo "   • Configure custom domain if needed"
echo "   • Set up monitoring and alerts"
echo "   • Configure backup strategy for your database" 