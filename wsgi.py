#!/usr/bin/env python3
"""
WSGI Entry Point for Server Maintenance Scheduler
This file is used by gunicorn and other WSGI servers
"""

import os
import logging
from app import create_app

# Create the application instance
application = create_app()

# For gunicorn compatibility
app = application

if __name__ == "__main__":
    # For development only
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 