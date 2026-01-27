# Fallback Procedures Guide

## Overview
This guide describes the fallback procedures to follow when AI-powered tools like kubectl-ai are unavailable. The system is designed to continue functioning using standard Docker and Kubernetes commands.

## When to Use Fallback Procedures

Use these fallback procedures when:
- The kubectl-ai plugin is not installed or not working
- Natural language commands are not executing properly
- You receive errors indicating kubectl-ai is unavailable
- You prefer to use standard Kubernetes commands

## Docker Fallback Operations

### Building Images
Instead of using AI commands to build Docker images, use the standard Docker command:

```bash
# Instead of: kubectl ai "build image from Dockerfile"
docker build -t my-app:latest .
```

### Running Containers
Instead of using AI commands to run containers:

```bash
# Instead of: kubectl ai "run container my-app"
docker run -d --name my-app -p 8080:80 my-app:latest
```

### Using the Docker Deployment Script
For more complex Docker operations, use the provided script:

```bash
chmod +x scripts/deploy-with-docker.sh
./scripts/deploy-with-docker.sh build . my-app:latest
./scripts/deploy-with-docker.sh run my-app:latest my-app-container 8080:80
```

## Standard Kubernetes Fallback Operations

### Creating Deployments
Instead of using AI commands to create deployments:

```bash
# Instead of: kubectl ai "create deployment nginx with 2 replicas"
kubectl create deployment nginx --image=nginx --replicas=2
```

### Exposing Services
Instead of using AI commands to expose services:

```bash
# Instead of: kubectl ai "expose deployment nginx on port 80"
kubectl expose deployment nginx --port=80 --type=NodePort
```

### Scaling Applications
Instead of using AI commands to scale applications:

```bash
# Instead of: kubectl ai "scale deployment nginx to 3 replicas"
kubectl scale deployment nginx --replicas=3
```

### Using the Standard Kubernetes Deployment Script
For more complex Kubernetes operations, use the provided script:

```bash
chmod +x scripts/deploy-standard-k8s.sh
./scripts/deploy-standard-k8s.sh create my-app nginx:latest 2 80
./scripts/deploy-standard-k8s.sh scale my-app 3
```

## Checking Tool Availability

To check if kubectl-ai is available:

```bash
chmod +x scripts/fallback-handler.sh
./scripts/fallback-handler.sh check-availability
```

## Automatic Fallback Activation

The system can automatically detect when kubectl-ai is unavailable and suggest fallback commands:

```bash
# Example of using the fallback handler
./scripts/fallback-handler.sh run \
  "deploy my-app with 2 replicas" \
  "kubectl create deployment my-app --image=my-app --replicas=2"
```

## Verification with Fallback Tools

Even when using fallback tools, you can still verify your deployments:

```bash
# Check deployments
kubectl get deployments

# Check services
kubectl get services

# Check pods
kubectl get pods

# Use the verification script
chmod +x scripts/verify-deployment.sh
./scripts/verify-deployment.sh
```

## Troubleshooting Fallback Operations

### Docker Commands Not Working
1. Verify Docker is running: `systemctl status docker`
2. Check Docker version: `docker --version`
3. Ensure you have proper permissions to run Docker

### Kubernetes Commands Not Working
1. Verify kubectl is installed: `kubectl version --client`
2. Check if you can connect to the cluster: `kubectl cluster-info`
3. Ensure your kubeconfig is properly configured

### Need to Restart Minikube
If your cluster is not responding:
```bash
minikube status
minikube start
```

## Best Practices

1. Always test your fallback procedures in a development environment first
2. Keep both AI and standard command knowledge up to date
3. Document any custom configurations needed for fallback operations
4. Regularly verify that fallback tools are available and working
5. Train team members on both AI and standard command procedures