#!/usr/bin/env python3
"""
Standalone transaction simulator (without Kafka)
"""
import sys
sys.path.append('..')

import pandas as pd
import time
import requests
from datetime import datetime

def simulate_without_kafka(data_file='data/sample_transactions.csv', 
                          delay=2.0, max_transactions=None):
    """
    Simulate transactions by calling ML service directly
    """
    print("=" * 60)
    print("🎮 TRANSACTION SIMULATOR (Direct Mode)")
    print("=" * 60)
    
    # Check if ML service is running
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code != 200:
            print("❌ ML Service is not running!")
            print("   Start it with: python ml_service/app.py")
            return
    except:
        print("❌ Cannot connect to ML Service!")
        print("   Start it with: python ml_service/app.py")
        return
    
    # Check alert service
    try:
        requests.get('http://localhost:5001/health', timeout=5)
        alert_service_running = True
    except:
        print("⚠️  Alert service not running (alerts will be skipped)")
        alert_service_running = False
    
    # Load transactions
    df = pd.read_csv(data_file)
    if max_transactions:
        df = df.head(max_transactions)
    
    print(f"\n📊 Loaded {len(df)} transactions")
    print(f"⏱️  Delay: {delay} seconds")
    print("=" * 60)
    print()
    
    fraud_count = 0
    total_count = 0
    
    try:
        for _, row in df.iterrows():
            total_count += 1
            
            # Prepare transaction
            transaction = {
                'transaction_id': row['transaction_id'],
                'timestamp': datetime.now().isoformat(),
                'amount': float(row['amount']),
                'merchant_id': row['merchant_id'],
                'user_id': row['user_id'],
                'latitude': float(row['latitude']),
                'longitude': float(row['longitude']),
                'hour': int(row['hour']),
                'day_of_week': int(row['day_of_week']),
                'transaction_type': row['transaction_type'],
                'amount_log': float(row['amount_log']),
                'is_weekend': int(row['is_weekend']),
                'is_night': int(row['is_night'])
            }
            
            # Call ML service
            try:
                response = requests.post(
                    'http://localhost:5000/predict',
                    json=transaction,
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    print(f"[{total_count}] {transaction['transaction_id']}")
                    print(f"     Amount: ${transaction['amount']:.2f}")
                    print(f"     Fraud Probability: {result['fraud_probability']:.4f}")
                    print(f"     Prediction: {'🚨 FRAUD' if result['is_fraud'] else '✅ NORMAL'}")
                    print(f"     Risk Level: {result['risk_level']}")
                    
                    # Send alert if fraud detected
                    if result['is_fraud'] and alert_service_running:
                        fraud_count += 1
                        alert_response = requests.post(
                            'http://localhost:5001/alert',
                            json={
                                'transaction': transaction,
                                'prediction': result
                            },
                            timeout=5
                        )
                        if alert_response.status_code == 200:
                            print(f"     ✓ Alert sent!")
                    
                    print()
                
                else:
                    print(f"[{total_count}] ❌ Prediction failed: {response.status_code}")
            
            except Exception as e:
                print(f"[{total_count}] ❌ Error: {str(e)}")
            
            time.sleep(delay)
    
    except KeyboardInterrupt:
        print("\n⚠️  Simulation interrupted by user")
    
    print("\n" + "=" * 60)
    print("📊 SIMULATION SUMMARY")
    print("=" * 60)
    print(f"Total Transactions: {total_count}")
    print(f"Fraud Detected: {fraud_count}")
    print(f"Fraud Rate: {(fraud_count/total_count)*100:.2f}%")
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Transaction Simulator')
    parser.add_argument('--file', default='data/sample_transactions.csv',
                       help='CSV file with transactions')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay between transactions')
    parser.add_argument('--max', type=int, default=None,
                       help='Max transactions to simulate')
    
    args = parser.parse_args()
    
    simulate_without_kafka(
        data_file=args.file,
        delay=args.delay,
        max_transactions=args.max
    )