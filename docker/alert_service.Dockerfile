FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir \
    --default-timeout=300 \
    --retries 10 \
    -r requirements.txt

COPY alert_service ./alert_service
COPY ml_model ./ml_model

EXPOSE 5001

CMD ["python", "alert_service/alert_app.py"]
