#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

# Print a message to the logs
echo "Starting migration script..."

# Ensure Flask environment variables are set (Render may set these automatically, but this is a safeguard)
export FLASK_APP=web_app.app

# Run database migrations
# The `flask db upgrade` command will apply any pending migrations to the database.
# This ensures the database schema is up-to-date with the models before the app starts.
echo "Running database migrations..."
flask db upgrade

# Start the Gunicorn server
# This is the main web server that will serve the Flask application.
# We bind to 0.0.0.0 to make it accessible from outside the container.
# The port is set to 10000, which is a common practice on Render.
echo "Migrations complete. Starting Gunicorn..."
gunicorn --bind 0.0.0.0:10000 --workers 4 --threads 4 web_app.app:app
