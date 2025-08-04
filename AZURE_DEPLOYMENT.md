# 🚀 Azure Deployment Guide - Server Maintenance Scheduler

This guide provides comprehensive instructions for deploying the Server Maintenance Scheduler application on Microsoft Azure.

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ **Azure account** with active subscription
- ✅ **Azure CLI** installed ([Download here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
- ✅ **Git** installed on your local machine
- ✅ **Python 3.11+** (for local testing)

## 🎯 Quick Start (Recommended)

### Option 1: Automated Deployment Script

**For Linux/macOS:**
```bash
# Clone the repository
git clone <your-repo-url>
cd server-maintenance-scheduler

# Make script executable and run
chmod +x deploy-azure.sh
./deploy-azure.sh
```

**For Windows:**
```cmd
# Clone the repository
git clone <your-repo-url>
cd server-maintenance-scheduler

# Run Windows deployment script
deploy-azure.bat
```

### Option 2: Manual Azure App Service Deployment

```bash
# 1. Login to Azure
az login

# 2. Create resource group
az group create --name maintenance-rg --location eastus

# 3. Create App Service plan
az appservice plan create \
  --name maintenance-plan \
  --resource-group maintenance-rg \
  --sku B1 \
  --is-linux

# 4. Create Web App
az webapp create \
  --resource-group maintenance-rg \
  --plan maintenance-plan \
  --name my-maintenance-app \
  --runtime "PYTHON|3.11"

# 5. Generate secure secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 6. Configure app settings
az webapp config appsettings set \
  --resource-group maintenance-rg \
  --name my-maintenance-app \
  --settings \
    SECRET_KEY="$SECRET_KEY" \
    FLASK_ENV="production" \
    WEBSITES_PORT="8000"

# 7. Deploy code
az webapp deployment source config-zip \
  --resource-group maintenance-rg \
  --name my-maintenance-app \
  --src deployment.zip
```

## 🐳 Container Deployment Options

### Azure Container Instances

```bash
# Create Azure Container Registry
az acr create \
  --resource-group maintenance-rg \
  --name myregistry \
  --sku Basic

# Build and push image
az acr build \
  --registry myregistry \
  --image maintenance-scheduler:latest .

# Deploy container
az container create \
  --resource-group maintenance-rg \
  --name maintenance-container \
  --image myregistry.azurecr.io/maintenance-scheduler:latest \
  --dns-name-label maintenance-scheduler \
  --ports 5000 \
  --environment-variables \
    SECRET_KEY="your-secure-key" \
    FLASK_ENV="production"
```

### Azure Kubernetes Service (AKS)

For production workloads requiring high availability and scalability:

```bash
# Create AKS cluster
az aks create \
  --resource-group maintenance-rg \
  --name maintenance-aks \
  --node-count 1 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials \
  --resource-group maintenance-rg \
  --name maintenance-aks

# Deploy using Kubernetes manifests
kubectl apply -f k8s/
```

## 🗄️ Database Options

### Option 1: SQLite (Default, Development Only)
- No additional setup required
- Data stored in container/app service
- **Not recommended for production**

### Option 2: Azure Database for PostgreSQL

```bash
# Create PostgreSQL server
az postgres server create \
  --resource-group maintenance-rg \
  --name maintenance-postgres \
  --admin-user myadmin \
  --admin-password SecurePassword123! \
  --sku-name GP_Gen5_2

# Create database
az postgres db create \
  --resource-group maintenance-rg \
  --server-name maintenance-postgres \
  --name maintenance_scheduler

# Update app settings with connection string
az webapp config appsettings set \
  --resource-group maintenance-rg \
  --name my-maintenance-app \
  --settings DATABASE_URL="postgresql://myadmin@maintenance-postgres:SecurePassword123!@maintenance-postgres.postgres.database.azure.com:5432/maintenance_scheduler?sslmode=require"
```

## 🔐 Security Configuration

### Environment Variables

Configure these environment variables in Azure:

```bash
# Required
SECRET_KEY="your-64-character-secure-key"
FLASK_ENV="production"

# Optional
DATABASE_URL="postgresql://..."
LOG_LEVEL="INFO"
TIMEZONE="UTC"
WEBSITES_PORT="8000"  # For App Service
```

### SSL/HTTPS

Azure App Service provides automatic HTTPS:
- Free SSL certificate included
- Custom domain SSL available
- Force HTTPS redirection recommended

## 🔄 CI/CD with Azure DevOps

1. **Create Azure DevOps project**
2. **Connect GitHub repository**
3. **Use provided `azure-pipelines.yml`**
4. **Configure variables:**
   - `SECRET_KEY` (secret)
   - `DATABASE_URL` (secret)
   - `containerRegistry`
   - `imageRepository`

## 📊 Monitoring and Logging

### Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app maintenance-insights \
  --location eastus \
  --resource-group maintenance-rg

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app maintenance-insights \
  --resource-group maintenance-rg \
  --query "instrumentationKey" -o tsv)

# Add to app settings
az webapp config appsettings set \
  --resource-group maintenance-rg \
  --name my-maintenance-app \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="$INSTRUMENTATION_KEY"
```

## 🔧 Troubleshooting

### Common Issues

1. **App won't start**
   ```bash
   # Check logs
   az webapp log tail --resource-group maintenance-rg --name my-maintenance-app
   ```

2. **Database connection errors**
   - Verify connection string format
   - Check firewall rules for PostgreSQL
   - Ensure SSL mode is set correctly

3. **Static files not loading**
   - Verify `WEBSITES_PORT` setting
   - Check static file configuration in Flask app

### Support Commands

```bash
# View app settings
az webapp config appsettings list \
  --resource-group maintenance-rg \
  --name my-maintenance-app

# Restart app
az webapp restart \
  --resource-group maintenance-rg \
  --name my-maintenance-app

# Scale app
az appservice plan update \
  --name maintenance-plan \
  --resource-group maintenance-rg \
  --sku S1
```

## 💰 Cost Optimization

### Recommended Tiers

- **Development**: Free (F1) or Basic (B1)
- **Production**: Standard (S1) or Premium (P1)
- **High Traffic**: Premium (P2/P3) with auto-scaling

### Cost-Saving Tips

1. Use **Azure Reserved Instances** for predictable workloads
2. Enable **auto-scaling** to handle traffic spikes
3. Use **deployment slots** for zero-downtime deployments
4. Consider **Azure Container Instances** for sporadic workloads

## 📞 Support

For Azure-specific deployment issues:

1. **Check logs**: `az webapp log tail`
2. **Verify configuration**: Review environment variables
3. **Test locally**: Ensure app works with production settings
4. **Azure Support**: Use Azure portal support tickets

---

## 🎉 Success!

Your Server Maintenance Scheduler should now be running on Azure. Visit your app URL to verify the deployment:

- **App Service**: `https://your-app-name.azurewebsites.net`
- **Container Instance**: `http://your-container-fqdn:5000`

### Next Steps

- ✅ Configure custom domain
- ✅ Set up monitoring alerts
- ✅ Implement backup strategy
- ✅ Configure auto-scaling
- ✅ Set up staging environments

**Happy Scheduling! 🚀** 