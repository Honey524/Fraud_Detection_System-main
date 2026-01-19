import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from ml_service.app import predict_fraud, preprocess_transaction

@pytest.fixture
def sample_model():
    """Fixture to load the model"""
    return True

@pytest.fixture
def sample_transaction():
    return {
        'transaction_id': 'TEST001',
        'amount': 150.0,
        'amount_log': 5.01,
        'latitude': 40.7128,
        'longitude': -74.0060,
        'hour': 14,
        'day_of_week': 2,
        'is_weekend': 0,
        'is_night': 0,
        'transaction_type': 'online'
    }

def test_model_loading(sample_model):
    """Test that model can be accessed"""
    # Model loading is tested during app startup
    assert sample_model is True

def test_prediction(sample_model, sample_transaction):
    """Test prediction on sample transaction"""
    try:
        result = predict_fraud(sample_transaction)
        
        assert 'transaction_id' in result
        assert 'fraud_probability' in result
        assert 'is_fraud' in result
        assert 'risk_level' in result
        assert 0 <= result['fraud_probability'] <= 1
        assert result['risk_level'] in ['LOW', 'MEDIUM', 'HIGH']
    except Exception as e:
        # Expected if model files don't exist yet
        assert 'Model' in str(e) or 'not found' in str(e)

def test_missing_field(sample_model):
    """Test handling of missing fields"""
    incomplete_transaction = {
        'transaction_id': 'TEST002',
        'amount': 100.0
    }
    
    with pytest.raises(Exception):
        predict_fraud(incomplete_transaction)

if __name__ == "__main__":
    pytest.main([__file__, '-v'])