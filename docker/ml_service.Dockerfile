FROM python:3.10-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python deps with timeout & retries
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --default-timeout=300 \
    --retries 10 \
    -r requirements.txt

# Copy required code
COPY ml_model ./ml_model
COPY ml_service ./ml_service
COPY kafka_streaming ./kafka_streaming

EXPOSE 5000

CMD ["python", "ml_service/app.py"]
