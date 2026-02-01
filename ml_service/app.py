from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import joblib
import pandas as pd
import numpy as np
import os
import sys

# CRITICAL: Add ml_model to path BEFORE importing/loading anything
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
ml_model_dir = os.path.join(parent_dir, 'ml_model')
sys.path.insert(0, ml_model_dir)  # Add ml_model directory to path
sys.path.insert(0, parent_dir)

# Now import the feature engineering module
import feature_engineering

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for model and feature engineer
model = None
feature_engineer = None

def load_models():
    """Load ML model and feature engineer"""
    global model, feature_engineer
    
    try:
        model_path = os.path.join(parent_dir, 'ml_model', 'fraud_model.pkl')
        fe_path = os.path.join(parent_dir, 'ml_model', 'feature_engineer.pkl')
        
        logger.info(f"Loading model from: {model_path}")
        logger.info(f"Loading feature engineer from: {fe_path}")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        if not os.path.exists(fe_path):
            raise FileNotFoundError(f"Feature engineer file not found: {fe_path}")
        
        # Load model
        model = joblib.load(model_path)
        
        # Load feature engineer
        feature_engineer = joblib.load(fe_path)
        
        logger.info("✓ Models loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def preprocess_transaction(transaction):
    """Preprocess incoming transaction"""
    df = pd.DataFrame([transaction])
    
    required_cols = [
        'amount', 'amount_log', 'latitude', 'longitude',
        'hour', 'day_of_week', 'is_weekend', 'is_night',
        'transaction_type'
    ]
    
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    return df

def predict_fraud(transaction):
    """Predict fraud for a transaction"""
    try:
        # Preprocess
        df = preprocess_transaction(transaction)
        
        # Transform features
        X = feature_engineer.transform(df)
        
        # Predict
        fraud_probability = model.predict_proba(X)[0][1]
        is_fraud = int(fraud_probability > 0.5)
        
        # Risk level
        if fraud_probability < 0.3:
            risk_level = "LOW"
        elif fraud_probability < 0.7:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        return {
            'transaction_id': transaction.get('transaction_id', 'UNKNOWN'),
            'fraud_probability': float(fraud_probability),
            'is_fraud': bool(is_fraud),
            'risk_level': risk_level
        }
    
    except Exception as e:
        raise Exception(f"Prediction error: {str(e)}")

# Load models on startup
models_loaded = load_models()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    if models_loaded and model is not None:
        return jsonify({
            'status': 'healthy',
            'service': 'ml-scoring-service',
            'model_loaded': True
        }), 200
    else:
        return jsonify({
            'status': 'unhealthy',
            'service': 'ml-scoring-service',
            'model_loaded': False,
            'error': 'Models failed to load'
        }), 503

@app.route('/predict', methods=['POST'])
def predict():
    """Predict fraud for a transaction"""
    if not models_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        transaction = request.get_json()
        
        if not transaction:
            return jsonify({'error': 'No transaction data provided'}), 400
        
        result = predict_fraud(transaction)
        
        logger.info(f"Prediction: {result['transaction_id']} - "
                   f"Fraud Probability: {result['fraud_probability']:.4f}")
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    """Predict fraud for multiple transactions"""
    if not models_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        transactions = request.get_json()
        
        if not isinstance(transactions, list):
            return jsonify({'error': 'Expected list of transactions'}), 400
        
        results = []
        for txn in transactions:
            result = predict_fraud(txn)
            results.append(result)
        
        return jsonify(results), 200
    
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 ML SCORING SERVICE")
    print("=" * 60)
    if models_loaded:
        print("✓ ML Model loaded successfully")
    else:
        print("❌ Failed to load ML model")
        print("   Check logs above for details")
    print("✓ Service listening on container port 5000 (mapped to host 5002)")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)