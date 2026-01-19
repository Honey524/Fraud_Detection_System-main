import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_transactions(n_samples=10000, fraud_ratio=0.02):
    """
    Generate synthetic transaction data with fraud labels
    """
    np.random.seed(42)
    
    # Generate transaction IDs
    transaction_ids = [f"TXN{str(i).zfill(8)}" for i in range(n_samples)]
    
    # Generate timestamps (last 30 days)
    start_date = datetime.now() - timedelta(days=30)
    timestamps = [start_date + timedelta(seconds=random.randint(0, 30*24*3600)) 
                  for _ in range(n_samples)]
    
    # Generate amounts (normal transactions: $10-500, fraud: $500-5000)
    n_fraud = int(n_samples * fraud_ratio)
    n_normal = n_samples - n_fraud
    
    normal_amounts = np.random.gamma(shape=2, scale=50, size=n_normal)
    fraud_amounts = np.random.gamma(shape=3, scale=800, size=n_fraud)
    amounts = np.concatenate([normal_amounts, fraud_amounts])
    
    # Generate other features
    merchant_ids = [f"M{random.randint(1000, 9999)}" for _ in range(n_samples)]
    user_ids = [f"U{random.randint(10000, 99999)}" for _ in range(n_samples)]
    
    # Location features
    latitudes = np.random.uniform(-90, 90, n_samples)
    longitudes = np.random.uniform(-180, 180, n_samples)
    
    # Time-based features
    hours = [ts.hour for ts in timestamps]
    day_of_week = [ts.weekday() for ts in timestamps]
    
    # Transaction type
    transaction_types = np.random.choice(['online', 'in-store', 'atm'], n_samples, 
                                        p=[0.5, 0.4, 0.1])
    
    # Labels (0: normal, 1: fraud)
    labels = np.concatenate([np.zeros(n_normal), np.ones(n_fraud)])
    
    # Shuffle data
    shuffle_idx = np.random.permutation(n_samples)
    
    # Create DataFrame
    df = pd.DataFrame({
        'transaction_id': np.array(transaction_ids)[shuffle_idx],
        'timestamp': np.array(timestamps)[shuffle_idx],
        'amount': amounts[shuffle_idx],
        'merchant_id': np.array(merchant_ids)[shuffle_idx],
        'user_id': np.array(user_ids)[shuffle_idx],
        'latitude': latitudes[shuffle_idx],
        'longitude': longitudes[shuffle_idx],
        'hour': np.array(hours)[shuffle_idx],
        'day_of_week': np.array(day_of_week)[shuffle_idx],
        'transaction_type': np.array(transaction_types)[shuffle_idx],
        'is_fraud': labels[shuffle_idx].astype(int)
    })
    
    # Add engineered features
    df['amount_log'] = np.log1p(df['amount'])
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    df['is_night'] = df['hour'].apply(lambda x: 1 if x >= 22 or x <= 6 else 0)
    
    return df

if __name__ == "__main__":
    # Generate training data
    print("Generating training data...")
    train_data = generate_transactions(n_samples=10000, fraud_ratio=0.02)
    train_data.to_csv('data/raw/transactions_train.csv', index=False)
    print(f"✓ Training data saved: {len(train_data)} transactions")
    
    # Generate test data
    print("Generating test data...")
    test_data = generate_transactions(n_samples=2000, fraud_ratio=0.02)
    test_data.to_csv('data/raw/transactions_test.csv', index=False)
    print(f"✓ Test data saved: {len(test_data)} transactions")
    
    # Generate sample streaming data
    print("Generating sample streaming data...")
    sample_data = generate_transactions(n_samples=100, fraud_ratio=0.05)
    sample_data.to_csv('data/sample_transactions.csv', index=False)
    print(f"✓ Sample data saved: {len(sample_data)} transactions")
    
    print("\n📊 Data Distribution:")
    print(f"Training fraud cases: {train_data['is_fraud'].sum()} ({train_data['is_fraud'].mean()*100:.2f}%)")
    print(f"Test fraud cases: {test_data['is_fraud'].sum()} ({test_data['is_fraud'].mean()*100:.2f}%)")