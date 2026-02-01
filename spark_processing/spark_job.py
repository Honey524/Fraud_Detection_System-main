from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
import os
import json


# Define schema for incoming transactions
transaction_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("hour", IntegerType(), True),
    StructField("day_of_week", IntegerType(), True),
    StructField("is_weekend", IntegerType(), True),
    StructField("is_night", IntegerType(), True),
    StructField("transaction_type", StringType(), True),
    StructField("amount_log", DoubleType(), True),
    StructField("from_account", StringType(), True),
    StructField("to_account", StringType(), True)
])


def start_spark_streaming():
    print("=" * 60)
    print("⚡ STARTING SPARK STREAMING JOB")
    print("=" * 60)

    kafka_broker = os.getenv('KAFKA_BROKER', 'kafka:9092')
    checkpoint_dir = os.getenv('CHECKPOINT_DIR', '/app/checkpoints')

    spark = SparkSession.builder \
        .appName("FraudDetectionStreaming") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    print("\n✓ Spark session created")
    print("✓ Connecting to Kafka...")

    raw = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", kafka_broker) \
        .option("subscribe", "transactions") \
        .option("startingOffsets", os.getenv('STARTING_OFFSETS', 'latest')) \
        .load()

    transactions = raw.select(from_json(col("value").cast("string"), transaction_schema).alias("data")).select("data.*")

    print("✓ Stream configured")

    # Define output schema (append prediction fields)
    output_schema = StructType(transaction_schema.fields + [
        StructField('fraud_probability', DoubleType(), True),
        StructField('is_fraud', IntegerType(), True),
        StructField('risk_level', StringType(), True)
    ])

    def predict_iter(iterator):
        import joblib
        import pandas as pd

        model_path = os.getenv('MODEL_PATH', '/app/ml_model/fraud_model.pkl')
        fe_path = os.getenv('FE_PATH', '/app/ml_model/feature_engineer.pkl')

        model = joblib.load(model_path)
        fe = joblib.load(fe_path)

        for pdf in iterator:
            if pdf.empty:
                yield pdf
                continue

            try:
                X = fe.transform(pdf)
                probs = model.predict_proba(X)[:, 1]
                is_fraud = (probs > 0.5).astype(int)
                risk = pd.cut(probs, bins=[-1, 0.3, 0.7, 1.0], labels=['LOW', 'MEDIUM', 'HIGH'])

                pdf['fraud_probability'] = probs
                pdf['is_fraud'] = is_fraud
                pdf['risk_level'] = risk.astype(str)
            except Exception:
                pdf['fraud_probability'] = 0.0
                pdf['is_fraud'] = 0
                pdf['risk_level'] = 'LOW'

            yield pdf

    result = transactions.mapInPandas(predict_iter, schema=output_schema)

    out = result.selectExpr("CAST(transaction_id AS STRING) AS key", "to_json(struct(*)) AS value")

    query = out.writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_broker) \
        .option("topic", os.getenv('PREDICTIONS_TOPIC', 'predictions')) \
        .option("checkpointLocation", checkpoint_dir) \
        .outputMode("append") \
        .start()

    print("\n🚀 Streaming to Kafka 'predictions' topic...")
    query.awaitTermination()


if __name__ == '__main__':
    start_spark_streaming()