# Server Maintenance Scheduler

A comprehensive web application for scheduling and automating server maintenance operations. Built with Flask, SQLAlchemy, and APScheduler.

## Features

### 🖥️ Server Management
- **Server Registration**: Add and manage servers with detailed information
- **Bulk Import**: Import multiple servers from CSV or JSON files
- **Status Tracking**: Monitor server status (Online, Maintenance, Offline)
- **Server Details**: Track hostname, IP address, and descriptions

### 🛠️ Maintenance Scheduling
- **Flexible Scheduling**: Schedule maintenance for specific date/time
- **Recurring Maintenance**: Support for daily, weekly, and monthly recurring schedules
- **Automatic Execution**: Automated start/stop of maintenance mode
- **Status Management**: Track maintenance progress and completion

### 📊 Dashboard & Monitoring
- **Real-time Dashboard**: Live overview of server status and maintenance schedules
- **Statistics**: Visual representation of server and maintenance statistics
- **Recent Activity**: Track recent maintenance activities
- **Quick Actions**: Easy access to common operations

### 🔧 Advanced Features
- **REST API**: Complete API for integration with other systems
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Live data updates without page refresh
- **Notifications**: User-friendly notifications for actions and errors

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Quick Start

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

### Environment Setup

For production deployment, set the following environment variables:

```bash
# Security
export SECRET_KEY="your-secure-secret-key"

# Database
export DATABASE_URL="postgresql://user:password@localhost/maintenance_scheduler"

# Timezone
export TIMEZONE="America/New_York"

# Logging
export LOG_LEVEL="INFO"
export LOG_FILE="/var/log/maintenance_scheduler.log"
```

## Usage

### Server Management

1. **Adding Servers**:
   - Navigate to the "Servers" page
   - Click "Add Server"
   - Fill in the server details (name, hostname, IP address)
   - Save the server

2. **Importing Servers** (Bulk Add):
   - Click "Import Servers" button
   - Upload a CSV or JSON file with server details
   - Preview the import before confirming
   - Review import results and errors

3. **Managing Servers**:
   - Edit server information
   - Change server status
   - Delete servers (will cancel scheduled maintenance)

### Scheduling Maintenance

1. **Basic Scheduling**:
   - Go to the "Maintenance" page
   - Click "Schedule Maintenance"
   - Select the server and set the time window
   - Add a description of the maintenance tasks

2. **Recurring Maintenance**:
   - Enable "Recurring Maintenance" in the schedule form
   - Choose the recurrence pattern (daily, weekly, monthly)
   - The system will automatically create new schedules after completion

3. **Managing Schedules**:
   - View all scheduled maintenance
   - Edit upcoming schedules
   - Cancel scheduled maintenance
   - Delete completed/cancelled schedules

### Dashboard Monitoring

The dashboard provides:
- **Server Statistics**: Total, online, maintenance, and offline servers
- **Maintenance Overview**: Scheduled, in-progress, and upcoming maintenance
- **Quick Actions**: Fast access to common operations
- **Real-time Updates**: Data refreshes automatically

## API Documentation

### Server Endpoints

- `GET /api/servers` - List all servers
- `POST /api/servers` - Create a new server
- `GET /api/servers/{id}` - Get server details
- `PUT /api/servers/{id}` - Update server
- `DELETE /api/servers/{id}` - Delete server
- `POST /api/servers/import` - Import servers from file (CSV/JSON)

### Maintenance Endpoints

- `GET /api/maintenance` - List all maintenance schedules
- `POST /api/maintenance` - Create a new maintenance schedule
- `GET /api/maintenance/{id}` - Get maintenance details
- `PUT /api/maintenance/{id}` - Update maintenance schedule
- `POST /api/maintenance/{id}/cancel` - Cancel maintenance
- `DELETE /api/maintenance/{id}` - Delete maintenance schedule

### Dashboard Endpoints

- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/scheduler/jobs` - Get currently scheduled jobs

## Architecture

### Backend Components

- **Flask**: Web framework for API and web interface
- **SQLAlchemy**: Database ORM for data management
- **APScheduler**: Advanced scheduler for maintenance automation
- **SQLite/PostgreSQL**: Database storage

### Frontend Components

- **Bootstrap 5**: Responsive CSS framework
- **jQuery**: JavaScript library for DOM manipulation
- **Font Awesome**: Icon library
- **Custom CSS/JS**: Application-specific styling and functionality

### Key Classes

- **Server**: Model for server information and status
- **MaintenanceSchedule**: Model for maintenance scheduling
- **MaintenanceScheduler**: Service for automated scheduling
- **Flask App**: Web application and API endpoints

## Customization

### Extending Maintenance Actions

The `MaintenanceScheduler` class includes placeholder methods for actual maintenance actions:

```python
def _perform_maintenance_actions(self, server, action):
    if action == 'start':
        # Implement your maintenance start actions:
        # - Stop services
        # - Update load balancer
        # - Send notifications
        pass
    elif action == 'end':
        # Implement your maintenance end actions:
        # - Start services
        # - Health checks
        # - Update monitoring
        pass
```

### Adding New Server Types

Extend the `ServerStatus` enum to add new server statuses:

```python
class ServerStatus(Enum):
    ONLINE = "online"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    UPDATING = "updating"  # New status
```

### Custom Notifications

The application includes a notification system that can be extended for:
- Email notifications
- Slack/Discord integration
- SMS alerts
- Custom webhooks

## Configuration

The application uses a configuration system with different environments:

- **Development**: Debug mode, SQLite database
- **Production**: Optimized for production deployment
- **Testing**: In-memory database, disabled features

Modify `config.py` to customize settings for your environment.

## Import File Formats

### CSV Format
Create a CSV file with the following required columns:
```csv
name,hostname,ip_address,description
Web Server 1,web01.example.com,192.168.1.10,Production web server
Database Server,db01.example.com,192.168.1.20,Primary database server
```

**Required columns:**
- `name` - Unique server name
- `hostname` - Server hostname or FQDN
- `ip_address` - Server IP address

**Optional columns:**
- `description` - Server description

### JSON Format
Create a JSON file with an array of server objects:
```json
[
  {
    "name": "Web Server 1",
    "hostname": "web01.example.com",
    "ip_address": "192.168.1.10",
    "description": "Production web server"
  },
  {
    "name": "Database Server",
    "hostname": "db01.example.com",
    "ip_address": "192.168.1.20",
    "description": "Primary database server"
  }
]
```

Example files are available in the `examples/` directory:
- `examples/servers_example.csv` - CSV format example
- `examples/servers_example.json` - JSON format example

## Security Considerations

### Production Deployment

1. **Secret Key**: Set a strong, random `SECRET_KEY`
2. **Database**: Use PostgreSQL or MySQL instead of SQLite
3. **HTTPS**: Always use HTTPS in production
4. **Firewall**: Restrict access to the application port
5. **Monitoring**: Set up logging and monitoring

### Authentication

The current version doesn't include user authentication. For production use, consider adding:
- User registration/login
- Role-based access control
- API key authentication
- OAuth integration

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Check database URL configuration
   - Ensure database server is running
   - Verify permissions

2. **Scheduler Not Working**:
   - Check timezone settings
   - Verify APScheduler configuration
   - Check application logs

3. **Web Interface Issues**:
   - Clear browser cache
   - Check browser console for JavaScript errors
   - Verify static files are loading

### Logging

Application logs are written to:
- Console (development)
- File specified in `LOG_FILE` environment variable
- Syslog (production)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use, modify, and distribute according to your needs.

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Create an issue with detailed information about your problem

---

**Server Maintenance Scheduler** - Automate your server maintenance with confidence! 