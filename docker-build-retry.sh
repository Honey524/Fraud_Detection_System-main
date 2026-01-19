#!/bin/bash
# Docker build retry script with network timeout handling

set -e

RETRY_COUNT=3
RETRY_DELAY=10

echo "🔨 Building Docker images with retry logic..."

for i in $(seq 1 $RETRY_COUNT); do
    echo "Attempt $i of $RETRY_COUNT"
    
    if sudo docker compose build --progress=plain 2>&1 | tee /tmp/docker-build-attempt-$i.log; then
        echo "✅ Build successful!"
        exit 0
    else
        if [ $i -lt $RETRY_COUNT ]; then
            echo "⚠️ Build failed, waiting ${RETRY_DELAY}s before retry..."
            sleep $RETRY_DELAY
            echo "🔄 Restarting Docker to clear network issues..."
            sudo systemctl restart docker
            sleep 5
        fi
    fi
done

echo "❌ Build failed after $RETRY_COUNT attempts"
echo "Check logs: /tmp/docker-build-attempt-*.log"
exit 1
