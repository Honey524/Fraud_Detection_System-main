from flask import Flask, render_template, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/ml-status')
def ml_status():
    """Check ML service status"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=2)
        return jsonify({'status': 'online' if response.ok else 'offline'})
    except:
        return jsonify({'status': 'offline'})

@app.route('/api/alert-status')
def alert_status():
    """Check alert service status"""
    try:
        response = requests.get('http://localhost:5001/health', timeout=2)
        return jsonify({'status': 'online' if response.ok else 'offline'})
    except:
        return jsonify({'status': 'offline'})

if __name__ == '__main__':
    print("=" * 60)
    print("🌐 WEB DASHBOARD")
    print("=" * 60)
    print("✓ Dashboard URL: http://localhost:8000")
    print("=" * 60)
    print("\nMake sure ML Service and Alert Service are running:")
    print("  - ML Service: http://localhost:5000")
    print("  - Alert Service: http://localhost:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8000, debug=True)
