#!/usr/bin/env python3
"""
Health Check Script for Server Maintenance Scheduler
Run this script to diagnose deployment issues
"""

import os
import sys
import logging
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

def check_environment():
    """Check environment variables"""
    print("🔍 Checking Environment Variables...")
    
    env_vars = {
        'SECRET_KEY': os.environ.get('SECRET_KEY'),
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'production'),
        'PORT': os.environ.get('PORT', '5000'),
        'HOST': os.environ.get('HOST', '0.0.0.0')
    }
    
    for key, value in env_vars.items():
        if value:
            if key == 'SECRET_KEY':
                print(f"✅ {key}: {'*' * min(len(str(value)), 20)}")
            else:
                print(f"✅ {key}: {value}")
        else:
            print(f"⚠️  {key}: Not set")
    
    return True

def check_database():
    """Check database connection"""
    print("\n🗄️  Checking Database Connection...")
    
    try:
        # Import here to avoid circular imports
        from app import app
        from models import db
        
        with app.app_context():
            # Test database connection
            db.create_all()
            result = db.session.execute('SELECT 1').fetchone()
            if result:
                print("✅ Database connection successful")
                
                # Check if tables exist
                from models import Server, MaintenanceSchedule
                server_count = Server.query.count()
                maintenance_count = MaintenanceSchedule.query.count()
                
                print(f"✅ Found {server_count} servers")
                print(f"✅ Found {maintenance_count} maintenance schedules")
                
                return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_application():
    """Check if application starts correctly"""
    print("\n🔧 Checking Application Startup...")
    
    try:
        from app import app
        print(f"✅ Flask app created successfully")
        print(f"✅ Debug mode: {app.debug}")
        print(f"✅ Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Test that routes are registered
        with app.test_request_context():
            from flask import url_for
            routes = [
                url_for('index'),
                url_for('get_servers'),
                url_for('get_dashboard_stats'),
                url_for('servers_page'),
            ]
            print(f"✅ Routes registered: {len(routes)} routes found")
        
        return True
    except Exception as e:
        print(f"❌ Application error: {e}")
        return False

def check_scheduler():
    """Check scheduler initialization"""
    print("\n⏰ Checking Scheduler...")
    
    try:
        from app import scheduler
        if scheduler.scheduler.running:
            print("✅ Scheduler is running")
            jobs = scheduler.get_scheduled_jobs()
            print(f"✅ Found {len(jobs)} scheduled jobs")
        else:
            print("⚠️  Scheduler is not running")
        return True
    except Exception as e:
        print(f"❌ Scheduler error: {e}")
        return False

def check_http_endpoints(base_url="http://localhost:5000"):
    """Check if HTTP endpoints are responding"""
    if not HAS_REQUESTS:
        print(f"\n⚠️  Skipping HTTP checks - 'requests' package not available")
        print("   Install with: pip install requests")
        return
        
    print(f"\n🌐 Checking HTTP Endpoints at {base_url}...")
    
    endpoints = [
        ('/', 'Dashboard'),
        ('/api/servers', 'Servers API'),
        ('/api/dashboard/stats', 'Dashboard Stats API'),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: HTTP {response.status_code}")
            else:
                print(f"⚠️  {name}: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {name}: Connection failed - {e}")

def main():
    """Run all health checks"""
    print("🏥 Server Maintenance Scheduler - Health Check")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    checks = [
        check_environment,
        check_database,
        check_application,
        check_scheduler,
    ]
    
    all_passed = True
    for check in checks:
        try:
            if not check():
                all_passed = False
        except Exception as e:
            print(f"❌ Check failed: {e}")
            all_passed = False
    
    # Test HTTP endpoints if requested
    if len(sys.argv) > 1 and sys.argv[1] == '--test-http':
        base_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:5000"
        check_http_endpoints(base_url)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All checks passed! Your application should be working correctly.")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        print("\n💡 Common solutions:")
        print("   • Set SECRET_KEY environment variable")
        print("   • Check DATABASE_URL format")
        print("   • Ensure all dependencies are installed")
        print("   • Check file permissions")
    
    print("\n📖 For more help, check the DEPLOYMENT.md file")

if __name__ == '__main__':
    main() 