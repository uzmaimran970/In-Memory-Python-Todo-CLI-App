# Quickstart Guide: Local Kubernetes AI Operations (AIOps)

## Prerequisites

Before getting started, ensure you have the following tools installed:

- Docker (v20.10 or later)
- kubectl (v1.20 or later)
- Helm (v3.0 or later)
- Minikube (v1.25 or later)

## Setup Instructions

### 1. Install kubectl-ai Plugin

```bash
# Download and install the kubectl-ai plugin
curl -sL https://run.kubectl.ai/install | bash
```

### 2. Start Minikube Cluster

```bash
# Start a local Minikube cluster
minikube start

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### 3. Verify Setup

```bash
# Check if kubectl-ai is available
kubectl ai --help

# Verify cluster connectivity
kubectl get nodes
```

## Basic Usage

### Deploy an Application

Deploy an application using natural language:

```bash
kubectl-ai "deploy nginx with 2 replicas"
```

### Expose a Service

Expose your application to external traffic:

```bash
kubectl-ai "expose deployment nginx on port 80 --type=NodePort"
```

### Access Your Application

Get the URL to access your application:

```bash
minikube service nginx --url
```

## Fallback to Standard Docker

If kubectl-ai is unavailable, you can use standard Docker and Kubernetes commands:

### Build and Run with Docker

```bash
# Build a Docker image
docker build -t my-app .

# Run the container locally
docker run -d -p 8080:80 my-app
```

### Standard Kubernetes Commands

```bash
# Create a deployment manually
kubectl create deployment nginx --image=nginx --replicas=2

# Expose the deployment
kubectl expose deployment nginx --port=80 --type=NodePort
```

## Verification Steps

### Check Deployment Status

```bash
# Verify your deployment is running
kubectl get deployments

# Check the status of your pods
kubectl get pods

# Check services
kubectl get services
```

### Scale Your Application

```bash
# Scale your deployment to 3 replicas
kubectl scale deployment nginx --replicas=3

# Verify scaling
kubectl get pods
```

## Cleanup

To stop and delete your Minikube cluster:

```bash
minikube stop
minikube delete
```

## Troubleshooting

### Common Issues

1. **kubectl-ai command not found**
   - Ensure the plugin is installed correctly
   - Check that kubectl plugins directory is in your PATH

2. **Minikube won't start**
   - Ensure Docker is running
   - Try with a different driver: `minikube start --driver=docker`

3. **Permission errors**
   - Ensure you have proper permissions to run Docker
   - On Linux, you might need to run commands with sudo or add your user to the docker group