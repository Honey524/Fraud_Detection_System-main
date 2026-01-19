#!/bin/bash

echo "Stopping all services..."

# Kill Python processes running the services
pkill -f "ml_service/app.py"
pkill -f "alert_service/alert_app.py"

echo "✓ All services stopped"