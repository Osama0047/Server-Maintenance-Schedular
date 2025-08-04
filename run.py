#!/usr/bin/env python3
"""
Server Maintenance Scheduler
Run script for starting the application
"""

import os
import sys
import logging
from app import create_app

def setup_logging():
    """Set up logging configuration"""
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_environment():
    """Validate environment configuration"""
    required_env_vars = []
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment validation passed")
    return True

def test_database_connection(app):
    """Test database connection"""
    try:
        from models import db
        from sqlalchemy import text
        with app.app_context():
            # Test a simple query
            db.session.execute(text('SELECT 1'))
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main entry point"""
    print("🚀 Starting Server Maintenance Scheduler...")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Create the application
    print("📊 Initializing application...")
    try:
        app = create_app()
    except Exception as e:
        print(f"❌ Application initialization failed: {e}")
        sys.exit(1)
    
    # Test database connection
    if not test_database_connection(app):
        print("💡 Tip: Check your DATABASE_URL environment variable")
        sys.exit(1)
    
    # Get configuration from environment
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'on']
    
    print(f"🌐 Server will be available at: http://localhost:{port}")
    print(f"🔧 Debug mode: {'Enabled' if debug else 'Disabled'}")
    print(f"🗄️  Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("=" * 50)
    print("✅ Server Maintenance Scheduler is ready!")
    print("📱 Open your browser and navigate to the URL above")
    print("\n🔹 Features available:")
    print("   • Dashboard: Real-time server and maintenance overview")
    print("   • Servers: Manage your server inventory")
    print("   • Maintenance: Schedule and track maintenance activities")
    print("   • API: RESTful API for integrations")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("👋 Thank you for using Server Maintenance Scheduler!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 