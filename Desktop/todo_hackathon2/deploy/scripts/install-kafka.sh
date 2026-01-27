#!/bin/bash
# T011: Install Kafka on Kubernetes via Bitnami Helm Chart
# Prerequisites: kubectl, helm, minikube running

set -e

echo "=== Installing Kafka on Kubernetes ==="

# Add Bitnami Helm repository
echo "Adding Bitnami Helm repository..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Kafka (single-node for local development)
echo "Installing Kafka..."
helm upgrade --install kafka bitnami/kafka \
  --set replicaCount=1 \
  --set controller.replicaCount=1 \
  --set listeners.client.protocol=PLAINTEXT \
  --set listeners.controller.protocol=PLAINTEXT \
  --set kraft.enabled=true \
  --set zookeeper.enabled=false \
  --wait --timeout 10m

# Verify installation
echo "Verifying Kafka installation..."
kubectl get pods -l app.kubernetes.io/name=kafka

echo "=== Kafka Installation Complete ==="
echo "Kafka broker available at: kafka.default.svc.cluster.local:9092"
