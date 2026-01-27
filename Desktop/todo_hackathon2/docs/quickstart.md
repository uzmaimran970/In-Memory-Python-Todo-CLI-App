# Quickstart Guide: Local Kubernetes AI Operations (AIOps)

## Overview
This guide will help you set up a local Kubernetes environment with AI-powered commands using kubectl-ai. This setup is designed for learning and development purposes.

## Prerequisites
Before getting started, ensure you have the following tools installed:

- Docker (v20.10 or later)
- kubectl (v1.20 or later)
- Helm (v3.0 or later) - *Note: Install manually if not already installed*
- Minikube (v1.25 or later) - *Note: Install manually if not already installed*

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install kubectl-ai Plugin
Run the installation script to install the kubectl-ai plugin:
```bash
chmod +x scripts/install-kubectl-ai.sh
./scripts/install-kubectl-ai.sh
```

### 3. Start Minikube Cluster
Run the setup script to start a local Minikube cluster with required addons:
```bash
chmod +x scripts/setup-minikube.sh
./scripts/setup-minikube.sh
```

### 4. Verify Setup
Verify that everything is working correctly:
```bash
chmod +x scripts/test-cluster-status.sh
./scripts/test-cluster-status.sh

chmod +x scripts/test-kubectl-ai.sh
./scripts/test-kubectl-ai.sh
```

## Basic Usage

### Deploy an Application
Deploy an application using natural language:
```bash
kubectl ai "deploy nginx with 2 replicas"
```

### Expose a Service
Expose your application to external traffic:
```bash
kubectl ai "expose deployment nginx on port 80 --type=NodePort"
```

### Access Your Application
Get the URL to access your application:
```bash
minikube service nginx --url
```

## Verification Steps

### Check Deployment Status
Verify your deployment is running:
```bash
chmod +x scripts/verify-deployment.sh
./scripts/verify-deployment.sh
```

This script will show you the status of all deployments, services, and pods in your cluster.

### Scale Your Application
Scale your deployment to 3 replicas:
```bash
kubectl scale deployment nginx --replicas=3
```

## Fallback to Standard Docker

If kubectl-ai is unavailable, you can use standard Docker and Kubernetes commands:

### Standard Kubernetes Commands
```bash
# Create a deployment manually
kubectl create deployment nginx --image=nginx --replicas=2

# Expose the deployment
kubectl expose deployment nginx --port=80 --type=NodePort
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
   - Ensure the plugin is installed correctly by running the install script
   - Check that kubectl plugins directory is in your PATH

2. **Minikube won't start**
   - Ensure Docker is running
   - Try with a different driver: `minikube start --driver=docker`

3. **Permission errors**
   - Ensure you have proper permissions to run Docker
   - On Linux, you might need to run commands with sudo or add your user to the docker group