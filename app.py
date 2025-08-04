from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import logging
from dateutil import parser

from models import db, Server, MaintenanceSchedule, ServerStatus, MaintenanceStatus
from scheduler import MaintenanceScheduler
from config import config

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Setup logging
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper())
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(__name__)
    
    # Initialize scheduler
    scheduler = MaintenanceScheduler()
    
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    # Initialize scheduler after database setup
    try:
        scheduler.init_app(app)
        logger.info("Scheduler initialized successfully")
    except Exception as e:
        logger.error(f"Scheduler initialization error: {e}")

    # Register routes
    register_routes(app, scheduler)
    
    return app

def register_routes(app, scheduler):
    """Register all application routes"""
    
    @app.route('/')
    def index():
        """Main dashboard"""
        servers = Server.query.all()
        maintenance_schedules = MaintenanceSchedule.query.order_by(MaintenanceSchedule.scheduled_start.desc()).limit(10).all()
        return render_template('index.html', servers=servers, maintenance_schedules=maintenance_schedules)

    # Server Management Endpoints
    @app.route('/api/servers/import', methods=['POST'])
    def import_servers():
        """Import servers from uploaded file (CSV or JSON)"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Read file content
            content = file.read().decode('utf-8')
            imported_servers = []
            errors = []
            
            if file.filename.endswith('.csv'):
                imported_servers, errors = _import_from_csv(content)
            elif file.filename.endswith('.json'):
                imported_servers, errors = _import_from_json(content)
            else:
                return jsonify({'error': 'Unsupported file format. Use CSV or JSON'}), 400
            
            # Import successful servers
            success_count = 0
            for server_data in imported_servers:
                try:
                    # Check if server name already exists
                    if Server.query.filter_by(name=server_data['name']).first():
                        errors.append(f"Server '{server_data['name']}' already exists")
                        continue
                    
                    server = Server(
                        name=server_data['name'],
                        hostname=server_data['hostname'],
                        ip_address=server_data['ip_address'],
                        description=server_data.get('description', ''),
                        status=ServerStatus.ONLINE
                    )
                    
                    db.session.add(server)
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"Error importing '{server_data.get('name', 'Unknown')}': {str(e)}")
            
            db.session.commit()
            
            return jsonify({
                'success_count': success_count,
                'error_count': len(errors),
                'errors': errors,
                'message': f'Successfully imported {success_count} servers'
            })
            
        except Exception as e:
            app.logger.error(f"Error importing servers: {e}")
            return jsonify({'error': 'Failed to import servers'}), 500

    @app.route('/api/servers', methods=['GET'])
    def get_servers():
        """Get all servers"""
        servers = Server.query.all()
        return jsonify([server.to_dict() for server in servers])

    @app.route('/api/servers', methods=['POST'])
    def create_server():
        """Create a new server"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'hostname', 'ip_address']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Check if server name already exists
            if Server.query.filter_by(name=data['name']).first():
                return jsonify({'error': 'Server name already exists'}), 400
            
            server = Server(
                name=data['name'],
                hostname=data['hostname'],
                ip_address=data['ip_address'],
                description=data.get('description', ''),
                status=ServerStatus.ONLINE
            )
            
            db.session.add(server)
            db.session.commit()
            
            return jsonify(server.to_dict()), 201
            
        except Exception as e:
            app.logger.error(f"Error creating server: {e}")
            return jsonify({'error': 'Failed to create server'}), 500

    @app.route('/api/servers/<int:server_id>', methods=['GET'])
    def get_server(server_id):
        """Get a specific server"""
        server = Server.query.get_or_404(server_id)
        return jsonify(server.to_dict())

    @app.route('/api/servers/<int:server_id>', methods=['PUT'])
    def update_server(server_id):
        """Update a server"""
        try:
            server = Server.query.get_or_404(server_id)
            data = request.get_json()
            
            server.name = data.get('name', server.name)
            server.hostname = data.get('hostname', server.hostname)
            server.ip_address = data.get('ip_address', server.ip_address)
            server.description = data.get('description', server.description)
            
            if 'status' in data:
                server.status = ServerStatus(data['status'])
            
            db.session.commit()
            
            return jsonify(server.to_dict())
            
        except Exception as e:
            app.logger.error(f"Error updating server: {e}")
            return jsonify({'error': 'Failed to update server'}), 500

    @app.route('/api/servers/<int:server_id>', methods=['DELETE'])
    def delete_server(server_id):
        """Delete a server"""
        try:
            server = Server.query.get_or_404(server_id)
            
            # Cancel any scheduled maintenance for this server
            for maintenance in server.maintenance_schedules:
                if maintenance.status == MaintenanceStatus.SCHEDULED:
                    scheduler.cancel_maintenance(maintenance.id)
            
            db.session.delete(server)
            db.session.commit()
            
            return jsonify({'message': 'Server deleted successfully'})
            
        except Exception as e:
            app.logger.error(f"Error deleting server: {e}")
            return jsonify({'error': 'Failed to delete server'}), 500

    # Maintenance Schedule Endpoints
    @app.route('/api/maintenance', methods=['GET'])
    def get_maintenance_schedules():
        """Get all maintenance schedules"""
        schedules = MaintenanceSchedule.query.order_by(MaintenanceSchedule.scheduled_start.desc()).all()
        return jsonify([schedule.to_dict() for schedule in schedules])

    @app.route('/api/maintenance', methods=['POST'])
    def create_maintenance_schedule():
        """Create a new maintenance schedule"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['server_id', 'title', 'scheduled_start', 'scheduled_end']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Validate server exists
            server = Server.query.get(data['server_id'])
            if not server:
                return jsonify({'error': 'Server not found'}), 404
            
            # Parse dates
            scheduled_start = parser.parse(data['scheduled_start'])
            scheduled_end = parser.parse(data['scheduled_end'])
            
            # Validate dates
            if scheduled_start >= scheduled_end:
                return jsonify({'error': 'Start time must be before end time'}), 400
            
            if scheduled_start <= datetime.utcnow():
                return jsonify({'error': 'Start time must be in the future'}), 400
            
            maintenance = MaintenanceSchedule(
                server_id=data['server_id'],
                title=data['title'],
                description=data.get('description', ''),
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                recurring=data.get('recurring', False),
                recurring_pattern=data.get('recurring_pattern'),
                status=MaintenanceStatus.SCHEDULED
            )
            
            db.session.add(maintenance)
            db.session.commit()
            
            # Schedule the maintenance job
            scheduler.schedule_maintenance(maintenance.id)
            
            return jsonify(maintenance.to_dict()), 201
            
        except Exception as e:
            app.logger.error(f"Error creating maintenance schedule: {e}")
            return jsonify({'error': 'Failed to create maintenance schedule'}), 500

    @app.route('/api/maintenance/<int:maintenance_id>', methods=['GET'])
    def get_maintenance_schedule(maintenance_id):
        """Get a specific maintenance schedule"""
        maintenance = MaintenanceSchedule.query.get_or_404(maintenance_id)
        return jsonify(maintenance.to_dict())

    @app.route('/api/maintenance/<int:maintenance_id>', methods=['PUT'])
    def update_maintenance_schedule(maintenance_id):
        """Update a maintenance schedule"""
        try:
            maintenance = MaintenanceSchedule.query.get_or_404(maintenance_id)
            data = request.get_json()
            
            # Only allow updates to scheduled maintenance
            if maintenance.status != MaintenanceStatus.SCHEDULED:
                return jsonify({'error': 'Can only update scheduled maintenance'}), 400
            
            # Cancel existing scheduled job
            scheduler.cancel_maintenance(maintenance_id)
            
            # Update fields
            maintenance.title = data.get('title', maintenance.title)
            maintenance.description = data.get('description', maintenance.description)
            
            if 'scheduled_start' in data:
                maintenance.scheduled_start = parser.parse(data['scheduled_start'])
            if 'scheduled_end' in data:
                maintenance.scheduled_end = parser.parse(data['scheduled_end'])
                
            maintenance.recurring = data.get('recurring', maintenance.recurring)
            maintenance.recurring_pattern = data.get('recurring_pattern', maintenance.recurring_pattern)
            
            # Validate dates
            if maintenance.scheduled_start >= maintenance.scheduled_end:
                return jsonify({'error': 'Start time must be before end time'}), 400
            
            if maintenance.scheduled_start <= datetime.utcnow():
                return jsonify({'error': 'Start time must be in the future'}), 400
            
            db.session.commit()
            
            # Reschedule the maintenance job
            scheduler.schedule_maintenance(maintenance.id)
            
            return jsonify(maintenance.to_dict())
            
        except Exception as e:
            app.logger.error(f"Error updating maintenance schedule: {e}")
            return jsonify({'error': 'Failed to update maintenance schedule'}), 500

    @app.route('/api/maintenance/<int:maintenance_id>/cancel', methods=['POST'])
    def cancel_maintenance_schedule(maintenance_id):
        """Cancel a maintenance schedule"""
        try:
            maintenance = MaintenanceSchedule.query.get_or_404(maintenance_id)
            
            if maintenance.status not in [MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS]:
                return jsonify({'error': 'Can only cancel scheduled or in-progress maintenance'}), 400
            
            scheduler.cancel_maintenance(maintenance_id)
            
            return jsonify({'message': 'Maintenance cancelled successfully'})
            
        except Exception as e:
            app.logger.error(f"Error cancelling maintenance: {e}")
            return jsonify({'error': 'Failed to cancel maintenance'}), 500

    @app.route('/api/maintenance/<int:maintenance_id>', methods=['DELETE'])
    def delete_maintenance_schedule(maintenance_id):
        """Delete a maintenance schedule"""
        try:
            maintenance = MaintenanceSchedule.query.get_or_404(maintenance_id)
            
            # Cancel if scheduled
            if maintenance.status == MaintenanceStatus.SCHEDULED:
                scheduler.cancel_maintenance(maintenance_id)
            
            db.session.delete(maintenance)
            db.session.commit()
            
            return jsonify({'message': 'Maintenance schedule deleted successfully'})
            
        except Exception as e:
            app.logger.error(f"Error deleting maintenance schedule: {e}")
            return jsonify({'error': 'Failed to delete maintenance schedule'}), 500

    # Dashboard and utility endpoints
    @app.route('/api/dashboard/stats')
    def get_dashboard_stats():
        """Get dashboard statistics"""
        try:
            total_servers = Server.query.count()
            online_servers = Server.query.filter_by(status=ServerStatus.ONLINE).count()
            maintenance_servers = Server.query.filter_by(status=ServerStatus.MAINTENANCE).count()
            offline_servers = Server.query.filter_by(status=ServerStatus.OFFLINE).count()
            
            scheduled_maintenance = MaintenanceSchedule.query.filter_by(status=MaintenanceStatus.SCHEDULED).count()
            in_progress_maintenance = MaintenanceSchedule.query.filter_by(status=MaintenanceStatus.IN_PROGRESS).count()
            
            # Upcoming maintenance (next 24 hours)
            tomorrow = datetime.utcnow() + timedelta(days=1)
            upcoming_maintenance = MaintenanceSchedule.query.filter(
                MaintenanceSchedule.scheduled_start <= tomorrow,
                MaintenanceSchedule.scheduled_start > datetime.utcnow(),
                MaintenanceSchedule.status == MaintenanceStatus.SCHEDULED
            ).count()
            
            return jsonify({
                'servers': {
                    'total': total_servers,
                    'online': online_servers,
                    'maintenance': maintenance_servers,
                    'offline': offline_servers
                },
                'maintenance': {
                    'scheduled': scheduled_maintenance,
                    'in_progress': in_progress_maintenance,
                    'upcoming_24h': upcoming_maintenance
                }
            })
            
        except Exception as e:
            app.logger.error(f"Error getting dashboard stats: {e}")
            return jsonify({'error': 'Failed to get dashboard stats'}), 500

    @app.route('/api/scheduler/jobs')
    def get_scheduled_jobs():
        """Get currently scheduled jobs"""
        try:
            jobs = scheduler.get_scheduled_jobs()
            return jsonify(jobs)
        except Exception as e:
            app.logger.error(f"Error getting scheduled jobs: {e}")
            return jsonify({'error': 'Failed to get scheduled jobs'}), 500

    # Web interface routes
    @app.route('/servers')
    def servers_page():
        """Servers management page"""
        return render_template('servers.html')

    @app.route('/maintenance')
    def maintenance_page():
        """Maintenance schedules page"""
        return render_template('maintenance.html')

    @app.route('/dashboard')
    def dashboard_page():
        """Dashboard page"""
        return render_template('dashboard.html')

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

def _import_from_csv(content):
    """Parse CSV content and extract server data"""
    import csv
    from io import StringIO
    
    servers = []
    errors = []
    
    try:
        csv_reader = csv.DictReader(StringIO(content))
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because of header
            try:
                # Required fields
                name = row.get('name', '').strip()
                hostname = row.get('hostname', '').strip()
                ip_address = row.get('ip_address', '').strip()
                
                if not name or not hostname or not ip_address:
                    errors.append(f"Row {row_num}: Missing required fields (name, hostname, ip_address)")
                    continue
                
                servers.append({
                    'name': name,
                    'hostname': hostname,
                    'ip_address': ip_address,
                    'description': row.get('description', '').strip()
                })
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                
    except Exception as e:
        errors.append(f"CSV parsing error: {str(e)}")
    
    return servers, errors

def _import_from_json(content):
    """Parse JSON content and extract server data"""
    import json
    
    servers = []
    errors = []
    
    try:
        data = json.loads(content)
        
        # Support both array of servers and single server object
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            errors.append("JSON must contain an array of server objects or a single server object")
            return servers, errors
        
        for index, server_data in enumerate(data):
            try:
                name = server_data.get('name', '').strip()
                hostname = server_data.get('hostname', '').strip()
                ip_address = server_data.get('ip_address', '').strip()
                
                if not name or not hostname or not ip_address:
                    errors.append(f"Server {index + 1}: Missing required fields (name, hostname, ip_address)")
                    continue
                
                servers.append({
                    'name': name,
                    'hostname': hostname,
                    'ip_address': ip_address,
                    'description': server_data.get('description', '').strip()
                })
                
            except Exception as e:
                errors.append(f"Server {index + 1}: {str(e)}")
                
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        errors.append(f"JSON parsing error: {str(e)}")
    
    return servers, errors

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 