import sys
sys.path.append('../alert_service')

import pytest
from notifier import AlertNotifier
import os

@pytest.fixture
def notifier():
    test_log_file = 'test_fraud_alerts.json'
    notifier = AlertNotifier(log_file=test_log_file)
    yield notifier
    # Cleanup
    if os.path.exists(test_log_file):
        os.remove(test_log_file)

@pytest.fixture
def sample_alert_data():
    transaction = {
        'transaction_id': 'TEST001',
        'user_id': 'U12345',
        'merchant_id': 'M5678',
        'amount': 500.0,
        'transaction_type': 'online',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'hour': 23,
        'day_of_week': 5
    }
    
    prediction = {
        'fraud_probability': 0.85,
        'risk_level': 'HIGH'
    }
    
    return transaction, prediction

def test_send_alert(notifier, sample_alert_data):
    """Test alert creation"""
    transaction, prediction = sample_alert_data
    alert = notifier.send_alert(transaction, prediction)
    
    assert 'alert_id' in alert
    assert alert['transaction_id'] == 'TEST001'
    assert alert['fraud_probability'] == 0.85

def test_get_recent_alerts(notifier, sample_alert_data):
    """Test retrieving recent alerts"""
    transaction, prediction = sample_alert_data
    
    # Send multiple alerts
    for i in range(5):
        transaction['transaction_id'] = f'TEST{i:03d}'
        notifier.send_alert(transaction, prediction)
    
    alerts = notifier.get_recent_alerts(limit=3)
    assert len(alerts) == 3

def test_alert_summary(notifier, sample_alert_data):
    """Test alert summary"""
    transaction, prediction = sample_alert_data
    
    # Send alerts with different risk levels
    for risk in ['HIGH', 'MEDIUM', 'LOW']:
        prediction['risk_level'] = risk
        notifier.send_alert(transaction, prediction)
    
    summary = notifier.get_alert_summary()
    assert summary['total_alerts'] == 3
    assert summary['high_risk'] == 1
    assert summary['medium_risk'] == 1
    assert summary['low_risk'] == 1

if __name__ == "__main__":
    pytest.main([__file__, '-v'])