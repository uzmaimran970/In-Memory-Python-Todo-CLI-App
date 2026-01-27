#!/bin/bash
# T013: Create Kubernetes Secrets for Phase 5
# Prerequisites: kubectl configured, environment variables set

set -e

echo "=== Creating Kubernetes Secrets ==="

# Check for required environment variables
if [ -z "$DATABASE_URL" ]; then
  echo "WARNING: DATABASE_URL not set. Using placeholder."
  DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
fi

if [ -z "$COHERE_API_KEY" ]; then
  echo "WARNING: COHERE_API_KEY not set. Using placeholder."
  COHERE_API_KEY="placeholder-key"
fi

# Create database credentials secret
echo "Creating db-credentials secret..."
kubectl create secret generic db-credentials \
  --from-literal=connection-string="$DATABASE_URL" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create API keys secret
echo "Creating api-keys secret..."
kubectl create secret generic api-keys \
  --from-literal=cohere-api-key="$COHERE_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

# Create Kafka credentials secret (empty for local, fill for cloud)
echo "Creating kafka-credentials secret..."
kubectl create secret generic kafka-credentials \
  --from-literal=username="${KAFKA_USERNAME:-}" \
  --from-literal=password="${KAFKA_PASSWORD:-}" \
  --dry-run=client -o yaml | kubectl apply -f -

# Verify secrets
echo "=== Kubernetes Secrets Created ==="
kubectl get secrets | grep -E "(db-credentials|api-keys|kafka-credentials)"
