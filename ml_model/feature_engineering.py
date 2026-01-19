"""
Feature Engineering Module for Fraud Detection
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

class FeatureEngineer:
    """Feature engineering for fraud detection"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = None
        
    def fit_transform(self, df):
        """
        Fit and transform training data
        
        Args:
            df: pandas DataFrame with transaction data
            
        Returns:
            X_scaled: numpy array of scaled features
            y: numpy array of labels
        """
        df = df.copy()
        
        # Encode categorical variables
        categorical_cols = ['transaction_type']
        for col in categorical_cols:
            le = LabelEncoder()
            df[col + '_encoded'] = le.fit_transform(df[col])
            self.label_encoders[col] = le
        
        # Select features for model
        self.feature_columns = [
            'amount', 'amount_log', 'latitude', 'longitude',
            'hour', 'day_of_week', 'is_weekend', 'is_night',
            'transaction_type_encoded'
        ]
        
        X = df[self.feature_columns].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, df['is_fraud'].values
    
    def transform(self, df):
        """
        Transform new data using fitted encoders and scaler
        
        Args:
            df: pandas DataFrame with transaction data
            
        Returns:
            X_scaled: numpy array of scaled features
        """
        df = df.copy()
        
        # Encode categorical variables
        for col, le in self.label_encoders.items():
            df[col + '_encoded'] = le.transform(df[col])
        
        X = df[self.feature_columns].values
        X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def save(self, filepath='feature_engineer.pkl'):
        """Save feature engineer"""
        # Get absolute path
        if not os.path.isabs(filepath):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(current_dir, filepath)
        
        joblib.dump(self, filepath)
        print(f"✓ Feature engineer saved to {filepath}")
    
    @staticmethod
    def load(filepath='feature_engineer.pkl'):
        """Load feature engineer"""
        return joblib.load(filepath)


def main():
    """Main function for standalone execution"""
    # Load data
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'transactions_train.csv')
    
    if not os.path.exists(data_path):
        print(f"❌ Training data not found: {data_path}")
        print("   Run: python data/generate_data.py")
        return
    
    df = pd.read_csv(data_path)
    
    # Initialize and fit feature engineer
    fe = FeatureEngineer()
    X, y = fe.fit_transform(df)
    
    # Save
    fe.save('feature_engineer.pkl')
    
    print(f"✓ Feature engineering complete")
    print(f"  Features: {fe.feature_columns}")
    print(f"  Shape: {X.shape}")


if __name__ == "__main__":
    main()