from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import *
import requests
import json
import os

# Define schema for incoming transactions
transaction_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("merchant_id", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("hour", IntegerType(), True),
    StructField("day_of_week", IntegerType(), True),
    StructField("transaction_type", StringType(), True),
    StructField("amount_log", DoubleType(), True),
    StructField("is_weekend", IntegerType(), True),
    StructField("is_night", IntegerType(), True),
    StructField("is_fraud", IntegerType(), True)
])

def call_ml_service(transaction_dict):
    """
    Call ML scoring service
    """
    try:
        # Use Docker service name for internal communication
        ml_service_url = os.getenv('ML_SERVICE_URL', 'http://ml_service:5000/predict')
        response = requests.post(
            ml_service_url,
            json=transaction_dict,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': 'ML service error'}
    except Exception as e:
        return {'error': str(e)}

# Register UDF
call_ml_service_udf = udf(call_ml_service, MapType(StringType(), StringType()))

def start_spark_streaming():
    """
    Start Spark Streaming job
    """
    print("=" * 60)
    print("⚡ STARTING SPARK STREAMING JOB")
    print("=" * 60)
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("FraudDetectionStreaming") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    print("\n✓ Spark session created")
    
    # Read from Kafka
    print("✓ Connecting to Kafka...")
    kafka_broker = os.getenv('KAFKA_BROKER', 'kafka:9092')
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_broker) \
        .option("subscribe", "transactions") \
        .option("startingOffsets", "latest") \
        .load()
    
    # Parse JSON
    transactions = df.select(
        from_json(col("value").cast("string"), transaction_schema).alias("data")
    ).select("data.*")
    
    print("✓ Stream configured")
    
    # Process and call ML service
    def process_batch(batch_df, batch_id):
        """
        Process each micro-batch
        """
        if batch_df.count() > 0:
            print(f"\n📦 Processing batch {batch_id} ({batch_df.count()} transactions)")
            
            # Convert to list of dicts for ML service
            transactions_list = batch_df.collect()
            
            for row in transactions_list:
                transaction_dict = row.asDict()
                
                # Call ML service
                result = call_ml_service(transaction_dict)
                
                if 'error' not in result:
                    print(f"   ✓ {transaction_dict['transaction_id']}: "
                          f"Fraud Score = {result.get('fraud_probability', 'N/A'):.4f}, "
                          f"Prediction = {'FRAUD' if result.get('is_fraud') else 'NORMAL'}")
                    
                    # If fraud detected, call alert service
                    if result.get('is_fraud'):
                        try:
                            # Use Docker service name for internal communication
                            alert_service_url = os.getenv('ALERT_SERVICE_URL', 'http://alert_service:5001/alert')
                            alert_response = requests.post(
                                alert_service_url,
                                json={
                                    'transaction': transaction_dict,
                                    'prediction': result
                                },
                                timeout=5
                            )
                            if alert_response.status_code == 200:
                                print(f"      🚨 Alert sent!")
                        except Exception as e:
                            print(f"      ⚠️  Alert service error: {e}")
                else:
                    print(f"   ✗ {transaction_dict['transaction_id']}: {result['error']}")
    
    # Start streaming query
    print("\n🚀 Starting stream processing...")
    print("=" * 60)
    
    query = transactions \
        .writeStream \
        .foreachBatch(process_batch) \
        .outputMode("append") \
        .start()
    
    query.awaitTermination()

if __name__ == "__main__":
    start_spark_streaming()