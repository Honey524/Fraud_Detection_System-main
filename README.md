# 🚀 Fraud Detection System

A comprehensive real-time fraud detection system using machine learning, Kafka streaming, Spark processing, and Docker microservices.

## 📋 Features

- **ML-Based Fraud Detection**: RandomForest classifier with SMOTE handling for imbalanced data
- **Real-Time Streaming**: Kafka producer/consumer for transaction streaming
- **Spark Processing**: Distributed processing of transaction streams
- **Alert Service**: Real-time fraud alerts with risk scoring
- **Web Dashboard**: Interactive dashboard for monitoring system health and alerts
- **Microservices Architecture**: Containerized services with Docker and Docker Compose

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Fraud Detection System                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐       ┌──────────────┐                     │
│  │  Producer    │──────▶│    Kafka     │                     │
│  │  (Simulator) │       │  (Broker)    │                     │
│  └──────────────┘       └──────────────┘                     │
│                               │                               │
│                    ┌──────────┴──────────┐                    │
│                    │                     │                    │
│            ┌───────▼──────┐      ┌──────▼────────┐            │
│            │  Spark Job   │      │  ML Service   │            │
│            │ (Processing) │      │  (Scoring)    │            │
│            └───────┬──────┘      └──────────────┘            │
│                    │                     │                    │
│                    └──────────┬──────────┘                    │
│                               │                               │
│                        ┌──────▼──────┐                        │
│                        │   Alert     │                        │
│                        │  Service    │                        │
│                        └──────┬──────┘                        │
│                               │                               │
│                        ┌──────▼──────┐                        │
│                        │  Web UI &   │                        │
│                        │ Dashboard   │                        │
│                        └─────────────┘                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Services

| Service | Port | Purpose |
|---------|------|---------|
| ML Service | 5000 | Fraud prediction endpoint |
| Alert Service | 5001 | Alert management and notifications |
| Web UI | 8000 | Dashboard for monitoring |
| Kafka | 9092 | Message broker |
| Zookeeper | 2181 | Kafka coordination |

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- bash

### Setup Instructions

#### 1. Clone and Navigate

```bash
cd /path/to/Fraud_Detection_System-main
```

#### 2. Create Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Generate Training Data

```bash
python data/generate_data.py
```

This creates:
- `data/raw/transactions_train.csv` (8,000 transactions)
- `data/raw/transactions_test.csv` (2,000 transactions)

#### 5. Train ML Model

```bash
python ml_model/model_training.py
```

This creates:
- `ml_model/fraud_model.pkl` (trained RandomForest model)
- `ml_model/feature_engineer.pkl` (feature engineering pipeline)

#### 6. Start All Services

```bash
./scripts/run_all.sh
```

Or start services individually:

**ML Service** (Terminal 1):
```bash
python ml_service/app.py
```

**Alert Service** (Terminal 2):
```bash
python alert_service/alert_app.py
```

**Web UI** (Terminal 3):
```bash
python web_ui/app.py
```

**Producer** (Terminal 4):
```bash
python kafka_streaming/producer.py
```

#### 7. Access the System

- **Dashboard**: http://localhost:8000
- **ML Service Health**: http://localhost:5000/health
- **Alert Service Health**: http://localhost:5001/health
- **Recent Alerts**: http://localhost:5001/alerts/recent

### Using Docker

#### Build and Start All Services

```bash
docker-compose up --build
```

#### Stop Services

```bash
docker-compose down
```

## 📊 Usage Examples

### Simulate Transactions

```bash
python scripts/simulate_transactions.py --max 50
```

### Check Service Health

```bash
curl http://localhost:5000/health
curl http://localhost:5001/health
```

### Get Recent Alerts

```bash
curl http://localhost:5001/alerts/recent?limit=5
```

### Get Alert Summary

```bash
curl http://localhost:5001/alerts/summary
```

### Single Transaction Prediction

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN123456",
    "amount": 1500.00,
    "amount_log": 7.31,
    "latitude": 40.7128,
    "longitude": -74.0060,
    "hour": 14,
    "day_of_week": 2,
    "is_weekend": 0,
    "is_night": 0,
    "transaction_type": "online"
  }'
```

### Batch Prediction

```bash
curl -X POST http://localhost:5000/batch-predict \
  -H "Content-Type: application/json" \
  -d '[
    {...transaction1...},
    {...transaction2...}
  ]'
```

## 📂 Project Structure

```
Fraud_Detection_System-main/
├── alert_service/              # Alert management service
│   ├── alert_app.py           # Flask app
│   ├── notifier.py            # Alert notifier
│   └── fraud_alerts.json      # Alert logs
│
├── ml_service/                # ML scoring service
│   └── app.py                 # Flask endpoint
│
├── ml_model/                  # ML training pipeline
│   ├── model_training.py      # Model trainer
│   ├── feature_engineering.py # Feature transformer
│   ├── evaluate_model.py      # Model evaluation
│   ├── fraud_model.pkl        # Trained model (generated)
│   └── feature_engineer.pkl   # Feature engineer (generated)
│
├── kafka_streaming/           # Kafka producer/consumer
│   ├── producer.py            # Transaction producer
│   └── consumer.py            # Stream consumer
│
├── spark_processing/          # Spark streaming job
│   └── spark_job.py           # Spark stream processor
│
├── web_ui/                    # Web dashboard
│   ├── app.py                 # Flask app
│   ├── templates/
│   │   └── index.html         # Dashboard UI
│   └── static/
│       ├── css/
│       │   └── dashboard.css
│       └── js/
│           └── dashboard.js
│
├── data/                      # Data generation
│   ├── generate_data.py       # Synthetic data generator
│   ├── sample_transactions.csv
│   └── raw/
│       ├── transactions_train.csv (generated)
│       └── transactions_test.csv (generated)
│
├── docker/                    # Docker configurations
│   ├── ml_service.Dockerfile
│   ├── alert_service.Dockerfile
│   ├── producer.Dockerfile
│   ├── web_ui.Dockerfile
│   └── spark.Dockerfile
│
├── k8s/                       # Kubernetes configs (optional)
│   ├── fraud-ml-service.yml
│   ├── fraud-alert-service.yml
│   ├── fraud-producer.yml
│   ├── fraud-spark.yml
│   └── fraud-web-ui.yml
│
├── scripts/                   # Utility scripts
│   ├── run_all.sh            # Start all services
│   ├── stop_all.sh           # Stop all services
│   └── simulate_transactions.py # Test data generator
│
├── tests/                     # Unit tests
│   ├── test_ml_service.py     # ML service tests
│   └── test_alert_service.py  # Alert service tests
│
├── docker-compose.yml         # Docker composition
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/
```

### Run with Coverage

```bash
pytest --cov=ml_service --cov=alert_service tests/
```

## 📊 Data Pipeline

### Transaction Features

The system generates and processes transactions with:

- **transaction_id**: Unique transaction identifier
- **amount**: Transaction amount ($)
- **amount_log**: Log-transformed amount
- **merchant_id**: Merchant identifier
- **user_id**: User identifier
- **latitude/longitude**: Transaction location
- **hour**: Hour of transaction (0-23)
- **day_of_week**: Day of week (0-6)
- **is_weekend**: Boolean flag
- **is_night**: Night-time flag (20:00-06:00)
- **transaction_type**: Type (online, in-store, ATM)
- **is_fraud**: Label (0=normal, 1=fraud)

### Model Features

The ML model uses 9 features after engineering:
1. amount
2. amount_log
3. latitude
4. longitude
5. hour
6. day_of_week
7. is_weekend
8. is_night
9. transaction_type_encoded

## 🎯 Model Performance

- **Algorithm**: RandomForest Classifier
- **Class Imbalance Handling**: SMOTE
- **Training Data**: ~8,000 transactions
- **Fraud Ratio**: ~2%
- **Features**: 9 engineered features
- **Output**: Fraud probability (0-1)

### Risk Levels

- **LOW**: Fraud probability < 0.3
- **MEDIUM**: 0.3 ≤ Fraud probability < 0.7
- **HIGH**: Fraud probability ≥ 0.7

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Kill process on port
lsof -i :8000
kill -9 <PID>

# Restart services
./scripts/run_all.sh
```

### Model Not Found

```bash
# Regenerate training data and model
python data/generate_data.py
python ml_model/model_training.py
```

### Kafka Connection Issues

```bash
# Check Kafka container status
docker ps | grep kafka

# Restart Docker Compose
docker-compose restart kafka
```

### Service Health Check Failed

```bash
# Check individual service logs
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:8000/
```

## 📚 Dependencies

- **Web Framework**: Flask, Flask-CORS
- **ML**: scikit-learn, pandas, numpy, joblib, imbalanced-learn
- **Streaming**: kafka-python, PySpark
- **Testing**: pytest
- **Utilities**: python-dotenv, matplotlib, seaborn

## 🔐 Security Notes

- The system uses basic logging for alerts
- Consider implementing proper alerting/notification services
- For production, add authentication/authorization
- Encrypt sensitive data and API communications

## 📝 License

MIT License - See LICENSE file for details

## 👥 Contributing

1. Create a feature branch
2. Commit your changes
3. Push to the branch
4. Create a Pull Request

## 📞 Support

For issues and questions, please create an issue in the repository.

---

**Happy Fraud Detection! 🚀**
