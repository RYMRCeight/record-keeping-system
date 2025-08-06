#!/bin/bash

# Create necessary directories
mkdir -p uploads
mkdir -p uploads/logos

# Set environment variables if not already set
export FLASK_ENV=production

# Start the application
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 0 app:app
