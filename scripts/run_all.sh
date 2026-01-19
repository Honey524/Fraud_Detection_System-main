#!/bin/bash

echo "=========================================="
echo "🚀 FRAUD DETECTION SYSTEM WITH WEB UI"
echo "=========================================="
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Please run: source venv/bin/activate"
    exit 1
fi

echo "✓ Virtual environment: activated"
echo ""

# Check if model exists
if [ ! -f "ml_model/fraud_model.pkl" ]; then
    echo "⚠️  ML model not found! Training model first..."
    python ml_model/model_training.py
    echo ""
fi

# Start ML Service
echo "Starting ML Scoring Service..."
python ml_service/app.py &
ML_PID=$!
sleep 5

# Check if ML service started successfully
if ps -p $ML_PID > /dev/null; then
    echo "✓ ML Service started (PID: $ML_PID)"
else
    echo "❌ ML Service failed to start"
    exit 1
fi

# Start Alert Service
echo "Starting Alert Service..."
python alert_service/alert_app.py &
ALERT_PID=$!
sleep 3

# Check if Alert service started successfully
if ps -p $ALERT_PID > /dev/null; then
    echo "✓ Alert Service started (PID: $ALERT_PID)"
else
    echo "❌ Alert Service failed to start"
    kill $ML_PID
    exit 1
fi

# Start Web UI
echo "Starting Web Dashboard..."
python web_ui/app.py &
WEB_PID=$!
sleep 3

# Check if Web UI started successfully
if ps -p $WEB_PID > /dev/null; then
    echo "✓ Web Dashboard started (PID: $WEB_PID)"
else
    echo "❌ Web Dashboard failed to start"
    kill $ML_PID $ALERT_PID
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ ALL SERVICES RUNNING"
echo "=========================================="
echo "🌐 Web Dashboard: http://localhost:8000"
echo "🤖 ML Service: http://localhost:5000"
echo "🚨 Alert Service: http://localhost:5001"
echo ""
echo "PIDs: ML=$ML_PID, Alert=$ALERT_PID, Web=$WEB_PID"
echo ""
echo "To stop all services, run:"
echo "  ./scripts/stop_all.sh"
echo "Or manually:"
echo "  kill $ML_PID $ALERT_PID $WEB_PID"
echo "=========================================="

# Wait for user interrupt
wait