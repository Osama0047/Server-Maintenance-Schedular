#!/usr/bin/env python3
"""
Server Maintenance Scheduler
Run script for starting the application
"""

import os
import sys
import logging
from app import app, create_tables

def setup_logging():
    """Set up logging configuration"""
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main entry point"""
    print("🚀 Starting Server Maintenance Scheduler...")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Create database tables and initialize scheduler
    print("📊 Initializing database and scheduler...")
    create_tables()
    
    # Get configuration from environment
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'on']
    
    print(f"🌐 Server will be available at: http://localhost:{port}")
    print(f"🔧 Debug mode: {'Enabled' if debug else 'Disabled'}")
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