#!/bin/bash

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$PROJECT_DIR"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        FRAUD DETECTION SYSTEM - KUBERNETES DEPLOYMENT          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check Minikube
echo "📋 STEP 1: Verifying Minikube Status..."
if ! minikube status | grep -q "Running"; then
    echo "❌ Minikube is not running. Start it with: minikube start"
    exit 1
fi
echo "✅ Minikube is running"
echo ""

# Step 2: Configure Docker
echo "🐳 STEP 2: Configuring Docker for Minikube..."
eval $(minikube docker-env)
echo "✅ Docker configured for Minikube"
echo ""

# Step 3: Build Images
echo "🔨 STEP 3: Building Docker Images..."
echo "   Building ML Service..."
docker build -t fraud-ml-service:latest -f docker/ml_service.Dockerfile . > /dev/null 2>&1
echo "   ✅ ML Service built"

echo "   Building Alert Service..."
docker build -t fraud-alert-service:latest -f docker/alert_service.Dockerfile . > /dev/null 2>&1
echo "   ✅ Alert Service built"

echo "   Building Web UI..."
docker build -t fraud-web-ui:latest -f docker/web_ui.Dockerfile . > /dev/null 2>&1
echo "   ✅ Web UI built"

echo "   Building Producer..."
docker build -t fraud-producer:latest -f docker/producer.Dockerfile . > /dev/null 2>&1
echo "   ✅ Producer built"

echo "   Building Spark..."
docker build -t fraud-spark:latest -f docker/spark.Dockerfile . > /dev/null 2>&1
echo "   ✅ Spark built"
echo ""

# Step 4: Create Namespace
echo "📦 STEP 4: Creating Kubernetes Namespace..."
kubectl create namespace fraud-detection --dry-run=client -o yaml | kubectl apply -f -
echo "✅ Namespace created"
echo ""

# Step 5: Apply Manifests
echo "🚀 STEP 5: Deploying Manifests to Kubernetes..."
kubectl apply -f k8s/ -n fraud-detection
echo "✅ Manifests deployed"
echo ""

# Step 6: Wait for deployments
echo "⏳ STEP 6: Waiting for pods to be ready (this may take a minute)..."
kubectl wait --for=condition=ready pod -l app -n fraud-detection --timeout=300s 2>/dev/null || true
echo "✅ Pods are starting"
echo ""

# Step 7: Check status
echo "📊 STEP 7: Deployment Status..."
echo ""
kubectl get pods -n fraud-detection
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    DEPLOYMENT COMPLETE! ✅                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 ACCESS SERVICES (in separate terminals):"
echo ""
echo "   ML Service:"
echo "   $ kubectl port-forward -n fraud-detection svc/fraud-ml-service 5000:5000"
echo "   Then: curl http://localhost:5000/health"
echo ""
echo "   Alert Service:"
echo "   $ kubectl port-forward -n fraud-detection svc/fraud-alert-service 5001:5001"
echo "   Then: curl http://localhost:5001/health"
echo ""
echo "   Web Dashboard:"
echo "   $ kubectl port-forward -n fraud-detection svc/fraud-web-ui 8000:8000"
echo "   Then: open http://localhost:8000"
echo ""
echo "📚 USEFUL COMMANDS:"
echo ""
echo "   View all pods:        kubectl get pods -n fraud-detection"
echo "   View logs:            kubectl logs -f <pod-name> -n fraud-detection"
echo "   Delete deployment:    kubectl delete -f k8s/ -n fraud-detection"
echo "   Shell access:         kubectl exec -it <pod-name> -n fraud-detection -- /bin/bash"
echo ""
