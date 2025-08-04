# Deployment Guide - Server Maintenance Scheduler

This guide covers multiple deployment options for the Server Maintenance Scheduler application.

## 🚀 Quick Deployment Options

### 1. Heroku (Easiest)

**Prerequisites:**
- Heroku account
- Heroku CLI installed

**Steps:**
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY="your-secure-secret-key"
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Open your app
heroku open
```

**Environment Variables for Heroku:**
```bash
heroku config:set SECRET_KEY="your-random-secret-key"
heroku config:set DATABASE_URL="postgresql://..."  # Optional: Use Heroku Postgres
heroku config:set LOG_LEVEL="INFO"
heroku config:set TIMEZONE="America/New_York"
```

### 2. Docker (Recommended for VPS)

**Prerequisites:**
- Docker installed
- Docker Compose installed

**Quick Start:**
```bash
# Clone the repository
git clone https://github.com/yourusername/server-maintenance-scheduler.git
cd server-maintenance-scheduler

# Build and run
docker-compose up -d

# Access at http://localhost:5000
```

**Production Docker:**
```bash
# Build image
docker build -t maintenance-scheduler .

# Run container
docker run -d \
  -p 5000:5000 \
  -e SECRET_KEY="your-secure-secret-key" \
  -e FLASK_ENV=production \
  -v $(pwd)/data:/app/data \
  --name maintenance-app \
  maintenance-scheduler
```

### 3. Railway

**Prerequisites:**
- Railway account
- Railway CLI (optional)

**Steps:**
1. Fork this repository
2. Connect to Railway: https://railway.app
3. Create new project from GitHub repo
4. Set environment variables:
   - `SECRET_KEY`: Your secure secret key
   - `FLASK_ENV`: production
5. Deploy automatically on push

### 4. DigitalOcean App Platform

**Prerequisites:**
- DigitalOcean account

**Steps:**
1. Create new App in DigitalOcean
2. Connect GitHub repository
3. Configure:
   - **Type**: Web Service
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `gunicorn app:app`
   - **Port**: 5000
4. Set environment variables
5. Deploy

### 5. AWS EC2 (Manual Setup)

**Prerequisites:**
- AWS EC2 instance (Ubuntu/Amazon Linux)
- SSH access

**Setup Script:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip nginx git -y

# Clone repository
git clone https://github.com/yourusername/server-maintenance-scheduler.git
cd server-maintenance-scheduler

# Install dependencies
pip3 install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/maintenance-scheduler.service
```

**Systemd Service File:**
```ini
[Unit]
Description=Server Maintenance Scheduler
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/server-maintenance-scheduler
Environment=PATH=/home/ubuntu/.local/bin
Environment=SECRET_KEY=your-secure-secret-key
Environment=FLASK_ENV=production
ExecStart=/home/ubuntu/.local/bin/gunicorn --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable maintenance-scheduler
sudo systemctl start maintenance-scheduler
```

## 🔧 Environment Variables

### Required
- `SECRET_KEY`: Secure random string for session encryption

### Optional
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `FLASK_ENV`: Environment mode (development/production)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)
- `TIMEZONE`: Application timezone (default: UTC)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 5000)

### Production Recommendations
```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export FLASK_ENV="production"
export LOG_LEVEL="INFO"
export DATABASE_URL="postgresql://user:pass@localhost/maintenance_scheduler"
```

## 🛡️ Security Considerations

### Before Production Deployment

1. **Change Secret Key**: Generate a secure random secret key
2. **Use HTTPS**: Configure SSL/TLS certificates
3. **Database Security**: Use PostgreSQL with secure credentials
4. **Firewall**: Restrict access to necessary ports only
5. **Regular Updates**: Keep dependencies updated
6. **Backup Strategy**: Implement database backups

### Generate Secure Secret Key
```python
import secrets
print(secrets.token_hex(32))
```

## 🐳 Docker Production Setup

**With PostgreSQL:**
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SECRET_KEY=your-production-secret-key
      - DATABASE_URL=postgresql://postgres:password@db:5432/maintenance_scheduler
      - FLASK_ENV=production
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=maintenance_scheduler
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=your-secure-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## 🔍 Health Checks

The application includes health check endpoints:

- **GET /** - Basic health check
- **GET /api/dashboard/stats** - API health check

## 📋 Post-Deployment Checklist

- [ ] Application loads without errors
- [ ] Database connection works
- [ ] Scheduler service is running
- [ ] All API endpoints respond correctly
- [ ] Static files load properly
- [ ] SSL certificate is valid (if using HTTPS)
- [ ] Environment variables are set correctly
- [ ] Logs are being written
- [ ] Backup strategy is in place

## 🆘 Troubleshooting

### Common Issues

1. **Application won't start**: Check environment variables and logs
2. **Database errors**: Verify DATABASE_URL and database permissions
3. **Scheduler not working**: Check APScheduler configuration and logs
4. **Static files not loading**: Verify file permissions and web server config

### Log Locations
- **Local**: Console output or `maintenance_scheduler.log`
- **Docker**: `docker logs container_name`
- **Heroku**: `heroku logs --tail`

### Support

For deployment issues:
1. Check the logs for error messages
2. Verify all environment variables are set
3. Ensure all dependencies are installed
4. Check firewall and network settings

---

**Happy Deploying! 🚀** 