import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    roc_auc_score, roc_curve, precision_recall_curve
)
import matplotlib.pyplot as plt
import seaborn as sns
from feature_engineering import FeatureEngineer

def evaluate_model():
    """
    Comprehensive model evaluation
    """
    print("=" * 60)
    print("📊 MODEL EVALUATION")
    print("=" * 60)
    
    # Load test data
    print("\n1️⃣ Loading test data...")
    df_test = pd.read_csv('data/raw/transactions_test.csv')
    print(f"   Test transactions: {len(df_test)}")
    
    # Load feature engineer and model
    print("\n2️⃣ Loading model and feature engineer...")
    fe = FeatureEngineer.load('ml_model/feature_engineer.pkl')
    model = joblib.load('ml_model/fraud_model.pkl')
    
    # Transform features
    print("\n3️⃣ Transforming features...")
    X_test = fe.transform(df_test)
    y_test = df_test['is_fraud'].values
    
    # Predictions
    print("\n4️⃣ Making predictions...")
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    # Classification Report
    print("\n5️⃣ Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Fraud']))
    
    # Confusion Matrix
    print("\n6️⃣ Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # ROC-AUC
    roc_auc = roc_auc_score(y_test, y_proba)
    print(f"\n7️⃣ ROC-AUC Score: {roc_auc:.4f}")
    
    # Feature Importance
    print("\n8️⃣ Top Feature Importances:")
    feature_importance = pd.DataFrame({
        'feature': fe.feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(feature_importance.head(10))
    
    print("\n" + "=" * 60)
    print("✅ EVALUATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    evaluate_model()