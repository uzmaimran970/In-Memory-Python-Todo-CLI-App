# Quickstart: Phase 5 Local Deployment

**Branch**: `005-dapr-kafka-cloud-deploy`
**Date**: 2026-01-23

This guide walks through deploying the Phase 5 event-driven architecture on local Minikube.

## Prerequisites

Before starting, ensure you have these tools installed:

```bash
# Check versions
minikube version      # >= 1.30
kubectl version       # >= 1.28
helm version          # >= 3.12
dapr --version        # >= 1.12
docker --version      # >= 24.0
```

## Step 1: Start Minikube Cluster

```bash
# Start with sufficient resources
minikube start --driver=docker --cpus=4 --memory=8192

# Verify cluster is running
kubectl get nodes
```

## Step 2: Install Dapr on Kubernetes

```bash
# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts
helm repo update

# Install Dapr runtime
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --wait

# Verify Dapr pods
kubectl get pods -n dapr-system
# Expected: dapr-operator, dapr-sidecar-injector, dapr-placement, dapr-sentry
```

## Step 3: Deploy Kafka

```bash
# Add Bitnami repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Kafka (single-node for dev)
helm install kafka bitnami/kafka \
  --set replicaCount=1 \
  --set controller.replicaCount=1 \
  --set listeners.client.protocol=PLAINTEXT \
  --set listeners.controller.protocol=PLAINTEXT \
  --wait

# Verify Kafka is running
kubectl get pods -l app.kubernetes.io/name=kafka
```

## Step 4: Create Kubernetes Secrets

```bash
# Database credentials (replace with your Neon DB connection string)
kubectl create secret generic db-credentials \
  --from-literal=connection-string="postgresql://user:pass@host:5432/db?sslmode=require"

# Kafka credentials (empty for local, filled for cloud)
kubectl create secret generic kafka-credentials \
  --from-literal=username="" \
  --from-literal=password=""
```

## Step 5: Deploy Dapr Components

```bash
# From project root
kubectl apply -f deploy/dapr-components/

# Verify components
kubectl get components
# Expected: taskpubsub, statestore, kubernetes-secrets, reminder-cron
```

## Step 6: Create Kafka Topics

```bash
# Get Kafka pod name
KAFKA_POD=$(kubectl get pods -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}')

# Create topics
kubectl exec -it $KAFKA_POD -- kafka-topics.sh --create \
  --topic task-events \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

kubectl exec -it $KAFKA_POD -- kafka-topics.sh --create \
  --topic reminders \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

kubectl exec -it $KAFKA_POD -- kafka-topics.sh --create \
  --topic task-updates \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

# Create dead-letter topics
kubectl exec -it $KAFKA_POD -- kafka-topics.sh --create \
  --topic task-events-deadletter \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1

# Verify topics
kubectl exec -it $KAFKA_POD -- kafka-topics.sh --list \
  --bootstrap-server localhost:9092
```

## Step 7: Build and Deploy Services

```bash
# Build Docker images (uses Minikube's Docker daemon)
eval $(minikube docker-env)

# Build backend
docker build -t todo-backend:latest ./backend

# Build frontend
docker build -t todo-frontend:latest ./frontend

# Build microservices
docker build -t notification-svc:latest ./services/notification
docker build -t recurring-svc:latest ./services/recurring
docker build -t audit-svc:latest ./services/audit
docker build -t websocket-svc:latest ./services/websocket

# Deploy all services via Helm
helm upgrade --install todo-app ./deploy/helm-charts \
  --set backend.image=todo-backend:latest \
  --set frontend.image=todo-frontend:latest \
  --set notification.image=notification-svc:latest \
  --set recurring.image=recurring-svc:latest \
  --set audit.image=audit-svc:latest \
  --set websocket.image=websocket-svc:latest

# Wait for pods
kubectl wait --for=condition=ready pod -l app=todo-app --timeout=300s
```

## Step 8: Verify Deployment

```bash
# Check all pods are running
kubectl get pods

# Check services
kubectl get svc

# Check Dapr sidecars are injected
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'
```

## Step 9: Access the Application

```bash
# Start minikube tunnel (in a separate terminal)
minikube tunnel

# Get frontend URL
kubectl get svc todo-frontend
# Access at http://localhost:8080
```

## Step 10: Verify Event Flow

```bash
# Watch Kafka topics for events
KAFKA_POD=$(kubectl get pods -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}')

# In separate terminals:
kubectl exec -it $KAFKA_POD -- kafka-console-consumer.sh \
  --topic task-events \
  --bootstrap-server localhost:9092 \
  --from-beginning

kubectl exec -it $KAFKA_POD -- kafka-console-consumer.sh \
  --topic task-updates \
  --bootstrap-server localhost:9092 \
  --from-beginning
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name> -c daprd  # Dapr sidecar logs
kubectl logs <pod-name> -c <app-container>
```

### Kafka connection issues
```bash
# Check Kafka service
kubectl get svc kafka
# Test connectivity
kubectl run kafka-test --rm -it --image=bitnami/kafka -- \
  kafka-topics.sh --list --bootstrap-server kafka.default.svc.cluster.local:9092
```

### Dapr component issues
```bash
# Check component status
kubectl get components -o yaml
# Check Dapr operator logs
kubectl logs -n dapr-system -l app=dapr-operator
```

## Cleanup

```bash
# Remove application
helm uninstall todo-app

# Remove Kafka
helm uninstall kafka

# Remove Dapr
helm uninstall dapr -n dapr-system

# Delete secrets
kubectl delete secret db-credentials kafka-credentials

# Stop Minikube
minikube stop
```

## Next Steps

Once local deployment is verified:
1. Run integration tests: `pytest tests/integration/`
2. Test all user stories manually
3. Proceed to cloud deployment (see `cloud-deployment.md`)
