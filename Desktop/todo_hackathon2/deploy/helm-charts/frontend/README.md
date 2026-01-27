# Next.js Frontend Deployment Guide

## Overview
This guide explains how to build and deploy the Next.js frontend application using Docker and Helm.

## Prerequisites
- Docker installed
- Kubernetes cluster running (e.g., Minikube)
- Helm installed

## Step-by-Step Deployment

### 1. Build Docker Image
```bash
cd /mnt/c/Users/pc/Desktop/todo_hackathon2/deploy/helm-charts/frontend/
docker build -t nextjs-frontend:latest .
```

### 2. Run Container Locally (Optional)
```bash
docker run -d -p 3000:3000 nextjs-frontend:latest
```

### 3. Deploy to Kubernetes using Helm
```bash
cd /mnt/c/Users/pc/Desktop/todo_hackathon2
./scripts/install-frontend-helm.sh
```

### 4. Verify Deployment
```bash
# Check if pods are running
kubectl get pods

# Check if services are created
kubectl get services

# Get the service URL
minikube service frontend-release-frontend --url
```

## Troubleshooting

### If Docker build fails:
- Make sure you're in the correct directory
- Ensure package.json exists in the app/ directory
- Check if all dependencies are properly defined

### If Helm deployment fails:
- Ensure your Kubernetes cluster is running
- Verify Helm is properly installed
- Check if the namespace exists or can be created

## Application Structure
```
app/
├── package.json
├── pages/
│   └── index.js
└── next.config.js
Dockerfile
```

The application is configured to run on port 3000 with 2 replicas as specified in the Helm values.