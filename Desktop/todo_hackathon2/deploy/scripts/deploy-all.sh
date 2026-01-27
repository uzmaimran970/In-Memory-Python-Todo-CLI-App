#!/bin/bash
# Deploy All Services Script (T080)
# One-command deployment to Minikube with Dapr + Kafka
set -e

echo "=========================================="
echo "  Todo App - Full Deployment"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NAMESPACE="${NAMESPACE:-todo-app}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Step 1: Check prerequisites
log_info "Checking prerequisites..."
command -v kubectl >/dev/null 2>&1 || { log_error "kubectl not found"; exit 1; }
command -v helm >/dev/null 2>&1 || { log_error "helm not found"; exit 1; }
command -v docker >/dev/null 2>&1 || { log_error "docker not found"; exit 1; }

# Check if Dapr is installed
if ! dapr status -k >/dev/null 2>&1; then
    log_warn "Dapr not installed on cluster. Installing..."
    bash "$SCRIPT_DIR/install-dapr.sh"
fi

# Step 2: Create namespace
log_info "Creating namespace: $NAMESPACE"
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Create secrets
log_info "Creating secrets..."
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
fi

kubectl create secret generic todo-secrets \
    --namespace="$NAMESPACE" \
    --from-literal=database-url="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/todo}" \
    --from-literal=jwt-secret="${JWT_SECRET:-dev-secret-key}" \
    --from-literal=cohere-api-key="${COHERE_API_KEY:-}" \
    --dry-run=client -o yaml | kubectl apply -f -

# Step 4: Install Kafka
log_info "Installing Kafka..."
bash "$SCRIPT_DIR/install-kafka.sh"

# Step 5: Create Kafka topics
log_info "Waiting for Kafka to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n "$NAMESPACE" --timeout=120s 2>/dev/null || true
sleep 10
bash "$SCRIPT_DIR/create-topics.sh"

# Step 6: Apply Dapr components
log_info "Applying Dapr components..."
kubectl apply -f "$PROJECT_ROOT/deploy/dapr-components/" -n "$NAMESPACE"

# Step 7: Build Docker images (for Minikube)
if minikube status >/dev/null 2>&1; then
    log_info "Building images in Minikube Docker..."
    eval $(minikube docker-env)
fi

log_info "Building Docker images..."
docker build -t todo-backend:latest "$PROJECT_ROOT/backend/"
docker build -t todo-frontend:latest "$PROJECT_ROOT/frontend/"
docker build -t todo-recurring:latest "$PROJECT_ROOT/services/recurring/"
docker build -t todo-notification:latest "$PROJECT_ROOT/services/notification/"
docker build -t todo-websocket:latest "$PROJECT_ROOT/services/websocket/"
docker build -t todo-audit:latest "$PROJECT_ROOT/services/audit/"

# Step 8: Deploy with Helm
log_info "Deploying services with Helm..."

helm upgrade --install backend "$PROJECT_ROOT/deploy/helm-charts/backend/" \
    --namespace "$NAMESPACE" \
    --set image.repository=todo-backend \
    --set image.tag=latest \
    --set image.pullPolicy=Never

helm upgrade --install frontend "$PROJECT_ROOT/deploy/helm-charts/frontend/" \
    --namespace "$NAMESPACE" \
    --set image.repository=todo-frontend \
    --set image.tag=latest \
    --set image.pullPolicy=Never

helm upgrade --install recurring-service "$PROJECT_ROOT/deploy/helm-charts/recurring-service/" \
    --namespace "$NAMESPACE" \
    --set image.repository=todo-recurring \
    --set image.tag=latest \
    --set image.pullPolicy=Never

helm upgrade --install notification-service "$PROJECT_ROOT/deploy/helm-charts/notification-service/" \
    --namespace "$NAMESPACE" \
    --set image.repository=todo-notification \
    --set image.tag=latest \
    --set image.pullPolicy=Never

helm upgrade --install websocket-service "$PROJECT_ROOT/deploy/helm-charts/websocket-service/" \
    --namespace "$NAMESPACE" \
    --set image.repository=todo-websocket \
    --set image.tag=latest \
    --set image.pullPolicy=Never

helm upgrade --install audit-service "$PROJECT_ROOT/deploy/helm-charts/audit-service/" \
    --namespace "$NAMESPACE" \
    --set image.repository=todo-audit \
    --set image.tag=latest \
    --set image.pullPolicy=Never

# Step 9: Apply monitoring
log_info "Applying monitoring configuration..."
kubectl apply -f "$PROJECT_ROOT/deploy/k8s/monitoring.yaml"

# Step 10: Apply ingress
log_info "Applying ingress..."
kubectl apply -f "$PROJECT_ROOT/deploy/k8s/ingress.yaml"

# Step 11: Wait for deployments
log_info "Waiting for deployments to be ready..."
kubectl rollout status deployment/backend -n "$NAMESPACE" --timeout=120s 2>/dev/null || log_warn "Backend not ready yet"
kubectl rollout status deployment/frontend -n "$NAMESPACE" --timeout=120s 2>/dev/null || log_warn "Frontend not ready yet"

# Step 12: Show status
echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
kubectl get pods -n "$NAMESPACE"
echo ""

# Get service URLs
if minikube status >/dev/null 2>&1; then
    FRONTEND_URL=$(minikube service frontend -n "$NAMESPACE" --url 2>/dev/null || echo "pending")
    BACKEND_URL=$(minikube service backend -n "$NAMESPACE" --url 2>/dev/null || echo "pending")
    echo "Frontend: $FRONTEND_URL"
    echo "Backend:  $BACKEND_URL"
fi

log_info "Done! All services deployed to namespace: $NAMESPACE"
