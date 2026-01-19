"""
ML Model Training for Fraud Detection
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import joblib
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feature_engineering import FeatureEngineer


def train_model():
    """
    Train fraud detection model
    """
    print("=" * 60)
    print("🧠 FRAUD DETECTION MODEL TRAINING")
    print("=" * 60)
    
    # Check if data exists
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'transactions_train.csv')
    
    if not os.path.exists(data_path):
        print("\n❌ Training data not found!")
        print(f"   Expected: {data_path}")
        print("   Run: python data/generate_data.py")
        return False
    
    # Load data
    print("\n1️⃣ Loading data...")
    df = pd.read_csv(data_path)
    print(f"   Total transactions: {len(df)}")
    print(f"   Fraud cases: {df['is_fraud'].sum()} ({df['is_fraud'].mean()*100:.2f}%)")
    
    # Feature engineering
    print("\n2️⃣ Engineering features...")
    fe = FeatureEngineer()
    X, y = fe.fit_transform(df)
    
    # Save feature engineer
    fe_path = os.path.join(os.path.dirname(__file__), 'feature_engineer.pkl')
    fe.save(fe_path)
    
    # Split data
    print("\n3️⃣ Splitting data...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Training set: {len(X_train)}")
    print(f"   Validation set: {len(X_val)}")
    
    # Handle class imbalance with SMOTE
    print("\n4️⃣ Handling class imbalance (SMOTE)...")
    smote = SMOTE(random_state=42)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
    print(f"   Before SMOTE: {len(X_train)} samples")
    print(f"   After SMOTE: {len(X_train_balanced)} samples")
    
    # Train model
    print("\n5️⃣ Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_balanced, y_train_balanced)
    print("   ✓ Model trained successfully")
    
    # Save model
    print("\n6️⃣ Saving model...")
    model_path = os.path.join(os.path.dirname(__file__), 'fraud_model.pkl')
    joblib.dump(model, model_path)
    print(f"   ✓ Model saved to {model_path}")
    
    # Validation performance
    print("\n7️⃣ Validation Performance:")
    y_val_pred = model.predict(X_val)
    y_val_proba = model.predict_proba(X_val)[:, 1]
    
    from sklearn.metrics import classification_report, roc_auc_score
    print(classification_report(y_val, y_val_pred, target_names=['Normal', 'Fraud']))
    print(f"   ROC-AUC Score: {roc_auc_score(y_val, y_val_proba):.4f}")
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = train_model()
    sys.exit(0 if success else 1)