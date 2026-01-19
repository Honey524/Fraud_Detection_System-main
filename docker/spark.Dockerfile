FROM apache/spark:3.4.1

USER root

WORKDIR /app

RUN pip install kafka-python requests

COPY spark_processing ./spark_processing

CMD ["/opt/spark/bin/spark-submit", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1", \
     "/app/spark_processing/spark_job.py"]
