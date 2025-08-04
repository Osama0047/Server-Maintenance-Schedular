import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def get_database_uri():
        """Get database URI with proper handling for different environments"""
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            # Handle Heroku PostgreSQL URL format
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            return database_url
        else:
            # Use SQLite with proper path for production
            db_path = os.environ.get('DB_PATH', 'instance')
            if not os.path.exists(db_path):
                os.makedirs(db_path, exist_ok=True)
            # Use absolute path for Windows compatibility
            db_file = os.path.abspath(os.path.join(db_path, 'maintenance_scheduler.db'))
            return f'sqlite:///{db_file}'
    
    # APScheduler settings
    SCHEDULER_TIMEZONE = os.environ.get('TIMEZONE', 'UTC')
    SCHEDULER_API_ENABLED = True
    
    # Application settings
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'on']
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Set the database URI directly as class attribute
Config.SQLALCHEMY_DATABASE_URI = Config.get_database_uri()

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_maintenance_scheduler.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
} 