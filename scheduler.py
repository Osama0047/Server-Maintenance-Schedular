from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging
import pytz
from models import db, Server, MaintenanceSchedule, ServerStatus, MaintenanceStatus

class MaintenanceScheduler:
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.app = app
        self.logger = logging.getLogger(__name__)
        
    def init_app(self, app):
        self.app = app
        self.scheduler.start()
        with app.app_context():
            self._reschedule_existing_jobs()
    
    def _reschedule_existing_jobs(self):
        """Reschedule existing maintenance jobs on app startup"""
        try:
            scheduled_maintenances = MaintenanceSchedule.query.filter_by(
                status=MaintenanceStatus.SCHEDULED
            ).all()
            
            for maintenance in scheduled_maintenances:
                if maintenance.scheduled_start > datetime.utcnow():
                    self._schedule_maintenance_job(maintenance)
                    
        except Exception as e:
            self.logger.error(f"Error rescheduling existing jobs: {e}")
    
    def schedule_maintenance(self, maintenance_id):
        """Schedule a maintenance task"""
        with self.app.app_context():
            maintenance = MaintenanceSchedule.query.get(maintenance_id)
            if not maintenance:
                raise ValueError(f"Maintenance schedule {maintenance_id} not found")
            
            self._schedule_maintenance_job(maintenance)
            
    def _schedule_maintenance_job(self, maintenance):
        """Internal method to schedule a maintenance job"""
        try:
            # Schedule start maintenance job
            start_job_id = f"start_maintenance_{maintenance.id}"
            self.scheduler.add_job(
                func=self._start_maintenance,
                trigger=DateTrigger(run_date=maintenance.scheduled_start),
                args=[maintenance.id],
                id=start_job_id,
                replace_existing=True
            )
            
            # Schedule end maintenance job
            end_job_id = f"end_maintenance_{maintenance.id}"
            self.scheduler.add_job(
                func=self._end_maintenance,
                trigger=DateTrigger(run_date=maintenance.scheduled_end),
                args=[maintenance.id],
                id=end_job_id,
                replace_existing=True
            )
            
            self.logger.info(f"Scheduled maintenance {maintenance.id} for server {maintenance.server.name}")
            
        except Exception as e:
            self.logger.error(f"Error scheduling maintenance {maintenance.id}: {e}")
    
    def cancel_maintenance(self, maintenance_id):
        """Cancel a scheduled maintenance"""
        try:
            start_job_id = f"start_maintenance_{maintenance_id}"
            end_job_id = f"end_maintenance_{maintenance_id}"
            
            if self.scheduler.get_job(start_job_id):
                self.scheduler.remove_job(start_job_id)
            if self.scheduler.get_job(end_job_id):
                self.scheduler.remove_job(end_job_id)
                
            with self.app.app_context():
                maintenance = MaintenanceSchedule.query.get(maintenance_id)
                if maintenance:
                    maintenance.status = MaintenanceStatus.CANCELLED
                    db.session.commit()
                    
            self.logger.info(f"Cancelled maintenance {maintenance_id}")
            
        except Exception as e:
            self.logger.error(f"Error cancelling maintenance {maintenance_id}: {e}")
    
    def _start_maintenance(self, maintenance_id):
        """Start maintenance mode for a server"""
        with self.app.app_context():
            try:
                maintenance = MaintenanceSchedule.query.get(maintenance_id)
                if not maintenance:
                    self.logger.error(f"Maintenance {maintenance_id} not found")
                    return
                
                server = maintenance.server
                
                # Update server status
                server.status = ServerStatus.MAINTENANCE
                
                # Update maintenance schedule
                maintenance.status = MaintenanceStatus.IN_PROGRESS
                maintenance.actual_start = datetime.utcnow()
                
                db.session.commit()
                
                self.logger.info(f"Started maintenance for server {server.name}")
                
                # Here you would implement actual server maintenance actions
                # For example: stopping services, sending notifications, etc.
                self._perform_maintenance_actions(server, 'start')
                
            except Exception as e:
                self.logger.error(f"Error starting maintenance {maintenance_id}: {e}")
    
    def _end_maintenance(self, maintenance_id):
        """End maintenance mode for a server"""
        with self.app.app_context():
            try:
                maintenance = MaintenanceSchedule.query.get(maintenance_id)
                if not maintenance:
                    self.logger.error(f"Maintenance {maintenance_id} not found")
                    return
                
                server = maintenance.server
                
                # Update server status
                server.status = ServerStatus.ONLINE
                
                # Update maintenance schedule
                maintenance.status = MaintenanceStatus.COMPLETED
                maintenance.actual_end = datetime.utcnow()
                
                db.session.commit()
                
                self.logger.info(f"Ended maintenance for server {server.name}")
                
                # Here you would implement actual server recovery actions
                self._perform_maintenance_actions(server, 'end')
                
                # Schedule recurring maintenance if applicable
                if maintenance.recurring:
                    self._schedule_recurring_maintenance(maintenance)
                
            except Exception as e:
                self.logger.error(f"Error ending maintenance {maintenance_id}: {e}")
    
    def _perform_maintenance_actions(self, server, action):
        """Perform actual maintenance actions (placeholder for real implementations)"""
        if action == 'start':
            self.logger.info(f"Starting maintenance actions for {server.name}")
            # Implement actual maintenance start actions here:
            # - Stop services
            # - Send notifications
            # - Update load balancer
            # - etc.
        elif action == 'end':
            self.logger.info(f"Ending maintenance actions for {server.name}")
            # Implement actual maintenance end actions here:
            # - Start services
            # - Health checks
            # - Update load balancer
            # - Send recovery notifications
            # - etc.
    
    def _schedule_recurring_maintenance(self, maintenance):
        """Schedule the next occurrence of a recurring maintenance"""
        try:
            if not maintenance.recurring_pattern:
                return
                
            # Calculate next occurrence based on pattern
            next_start = None
            if maintenance.recurring_pattern == 'weekly':
                next_start = maintenance.scheduled_start + timedelta(weeks=1)
            elif maintenance.recurring_pattern == 'monthly':
                next_start = maintenance.scheduled_start + timedelta(days=30)
            elif maintenance.recurring_pattern == 'daily':
                next_start = maintenance.scheduled_start + timedelta(days=1)
            
            if next_start and next_start > datetime.utcnow():
                duration = maintenance.scheduled_end - maintenance.scheduled_start
                next_end = next_start + duration
                
                # Create new maintenance schedule
                new_maintenance = MaintenanceSchedule(
                    server_id=maintenance.server_id,
                    title=maintenance.title,
                    description=maintenance.description,
                    scheduled_start=next_start,
                    scheduled_end=next_end,
                    status=MaintenanceStatus.SCHEDULED,
                    recurring=True,
                    recurring_pattern=maintenance.recurring_pattern
                )
                
                db.session.add(new_maintenance)
                db.session.commit()
                
                # Schedule the new maintenance
                self._schedule_maintenance_job(new_maintenance)
                
                self.logger.info(f"Scheduled recurring maintenance for {maintenance.server.name}")
                
        except Exception as e:
            self.logger.error(f"Error scheduling recurring maintenance: {e}")
    
    def get_scheduled_jobs(self):
        """Get list of currently scheduled jobs"""
        return [
            {
                'id': job.id,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'func_name': job.func.__name__ if job.func else None
            }
            for job in self.scheduler.get_jobs()
        ]
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown() 