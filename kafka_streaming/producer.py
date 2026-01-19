import os
from kafka import KafkaProducer
import json
import pandas as pd
import time
import random
from datetime import datetime

class TransactionProducer:
    def __init__(self, bootstrap_servers=None, topic='transactions'):
        self.topic = topic
        bootstrap_servers = bootstrap_servers or os.getenv('KAFKA_BROKER', 'kafka:29092')
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"✓ Kafka Producer initialized (topic: {topic}, broker: {bootstrap_servers})")

    def send_transaction(self, transaction):
        """Send a transaction to Kafka"""
        self.producer.send(self.topic, value=transaction)
        self.producer.flush()
        
    def send_transactions_from_file(self, file_path, delay=2.0, loop=True):
        """Send transactions from CSV file"""
        print(f"📊 Loading transactions from {file_path}")
        df = pd.read_csv(file_path)
        print(f"✓ Loaded {len(df)} transactions")
        print(f"⏱️  Sending with {delay}s delay (loop={loop})")
        print("=" * 60)
        
        count = 0
        while True:
            for idx, row in df.iterrows():
                transaction = row.to_dict()
                # Convert numpy types to Python types
                transaction = {k: float(v) if isinstance(v, (float, int)) else str(v) 
                             for k, v in transaction.items()}
                
                self.send_transaction(transaction)
                count += 1
                print(f"✓ Sent transaction {count}: ID={transaction.get('transaction_id', 'N/A')}")
                time.sleep(delay)
            
            if not loop:
                break
            print(f"\n🔄 Looping back to start...\n")

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 KAFKA TRANSACTION PRODUCER")
    print("=" * 60)
    
    # Wait for Kafka to be ready
    print("⏳ Waiting for Kafka to be ready...")
    time.sleep(10)
    
    producer = TransactionProducer()
    producer.send_transactions_from_file('data/sample_transactions.csv', delay=3.0, loop=True)
