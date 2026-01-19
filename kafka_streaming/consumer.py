from kafka import KafkaConsumer
import json

class TransactionConsumer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='transactions'):
        """
        Initialize Kafka consumer
        """
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='fraud-detection-consumer'
        )
        print(f"✓ Kafka Consumer initialized (topic: {topic})")
    
    def consume_messages(self, max_messages=None):
        """
        Consume messages from Kafka
        """
        print("\n📥 Consuming transactions...")
        print("=" * 60)
        
        count = 0
        try:
            for message in self.consumer:
                transaction = message.value
                count += 1
                
                print(f"[{count}] Received: {transaction['transaction_id']} | "
                      f"Amount: ${transaction['amount']:.2f}")
                
                if max_messages and count >= max_messages:
                    break
        
        except KeyboardInterrupt:
            print("\n⚠️  Consumer interrupted")
        finally:
            self.close()
            print(f"\n✅ Consumed {count} transactions")
    
    def close(self):
        """Close consumer"""
        self.consumer.close()
        print("✓ Consumer closed")

if __name__ == "__main__":
    consumer = TransactionConsumer()
    consumer.consume_messages()