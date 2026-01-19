from datetime import datetime
import json
import os

class AlertNotifier:
    def __init__(self, log_file='fraud_alerts.json'):  # Changed: relative path
        """
        Initialize alert notifier
        """
        # Use absolute path relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_file = os.path.join(current_dir, log_file)
        self._ensure_log_file_exists()
    
    def _ensure_log_file_exists(self):
        """
        Create log file if it doesn't exist
        """
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Create file if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
            print(f"✓ Created log file: {self.log_file}")
    
    def send_alert(self, transaction, prediction):
        """
        Send fraud alert (currently logs to file)
        """
        alert = {
            'alert_id': f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            'timestamp': datetime.now().isoformat(),
            'transaction_id': transaction['transaction_id'],
            'user_id': transaction.get('user_id', 'UNKNOWN'),
            'merchant_id': transaction.get('merchant_id', 'UNKNOWN'),
            'amount': transaction['amount'],
            'fraud_probability': prediction['fraud_probability'],
            'risk_level': prediction['risk_level'],
            'details': {
                'transaction_type': transaction.get('transaction_type', 'UNKNOWN'),
                'location': {
                    'latitude': transaction.get('latitude', 0),
                    'longitude': transaction.get('longitude', 0)
                },
                'time': {
                    'hour': transaction.get('hour', 0),
                    'day_of_week': transaction.get('day_of_week', 0)
                }
            }
        }
        
        # Log to file
        self._log_alert(alert)
        
        return alert
    
    def _log_alert(self, alert):
        """
        Log alert to JSON file
        """
        try:
            # Read existing alerts
            with open(self.log_file, 'r') as f:
                alerts = json.load(f)
            
            # Append new alert
            alerts.append(alert)
            
            # Write back
            with open(self.log_file, 'w') as f:
                json.dump(alerts, f, indent=2)
        
        except Exception as e:
            print(f"Error logging alert: {e}")
    
    def get_recent_alerts(self, limit=10):
        """
        Get recent alerts
        """
        try:
            with open(self.log_file, 'r') as f:
                alerts = json.load(f)
            return alerts[-limit:]
        except:
            return []
    
    def get_alert_summary(self):
        """
        Get summary statistics of alerts
        """
        try:
            with open(self.log_file, 'r') as f:
                alerts = json.load(f)
            
            if not alerts:
                return {'total_alerts': 0}
            
            total = len(alerts)
            high_risk = sum(1 for a in alerts if a['risk_level'] == 'HIGH')
            medium_risk = sum(1 for a in alerts if a['risk_level'] == 'MEDIUM')
            low_risk = sum(1 for a in alerts if a['risk_level'] == 'LOW')
            
            return {
                'total_alerts': total,
                'high_risk': high_risk,
                'medium_risk': medium_risk,
                'low_risk': low_risk
            }
        except:
            return {'total_alerts': 0}