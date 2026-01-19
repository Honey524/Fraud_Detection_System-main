from flask import Flask, request, jsonify
from flask_cors import CORS
from notifier import AlertNotifier
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize alert notifier
notifier = AlertNotifier()
logger.info("✓ Alert Service initialized")

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'service': 'alert-service'
    }), 200

@app.route('/alert', methods=['POST'])
def create_alert():
    """
    Create fraud alert
    """
    try:
        data = request.get_json()
        
        if not data or 'transaction' not in data or 'prediction' not in data:
            return jsonify({'error': 'Invalid alert data'}), 400
        
        transaction = data['transaction']
        prediction = data['prediction']
        
        # Send alert
        alert = notifier.send_alert(transaction, prediction)
        
        logger.warning(
            f"🚨 FRAUD ALERT: {alert['alert_id']} | "
            f"Transaction: {transaction['transaction_id']} | "
            f"Amount: ${transaction['amount']:.2f} | "
            f"Risk: {alert['risk_level']} | "
            f"Probability: {prediction['fraud_probability']:.4f}"
        )
        
        return jsonify({
            'status': 'alert_created',
            'alert': alert
        }), 200
    
    except Exception as e:
        logger.error(f"Alert creation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/alerts/recent', methods=['GET'])
def get_recent_alerts():
    """
    Get recent alerts
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        alerts = notifier.get_recent_alerts(limit=limit)
        return jsonify(alerts), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alerts/summary', methods=['GET'])
def get_alert_summary():
    """
    Get alert summary
    """
    try:
        summary = notifier.get_alert_summary()
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚨 ALERT SERVICE")
    print("=" * 60)
    print("✓ Service starting on http://localhost:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)