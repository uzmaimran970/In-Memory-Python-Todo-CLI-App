#!/bin/bash
# T010: Install Dapr on Kubernetes via Helm
# Prerequisites: kubectl, helm, minikube running

set -e

echo "=== Installing Dapr on Kubernetes ==="

# Add Dapr Helm repository
echo "Adding Dapr Helm repository..."
helm repo add dapr https://dapr.github.io/helm-charts
helm repo update

# Create dapr-system namespace if not exists
kubectl create namespace dapr-system --dry-run=client -o yaml | kubectl apply -f -

# Install Dapr
echo "Installing Dapr runtime..."
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system \
  --set global.logAsJson=true \
  --wait

# Verify installation
echo "Verifying Dapr installation..."
kubectl get pods -n dapr-system

echo "=== Dapr Installation Complete ==="
echo "Installed components:"
kubectl get components -A 2>/dev/null || echo "No Dapr components deployed yet"
