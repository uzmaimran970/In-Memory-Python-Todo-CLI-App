# Next.js Frontend Deployment: Roman Urdu Guide

## Problem Solve Kiya Gaya
Ab Docker image build karna aur Kubernetes mein deploy karna mumkin hai kyunke saare files aur dependencies available hain.

## Step-by-Step Instructions

### Step 1: Docker Image Banana
Command: `cd /mnt/c/Users/pc/Desktop/todo_hackathon2/deploy/helm-charts/frontend/ && docker build -t nextjs-frontend:latest .`
Verification: "Successfully built..." message ayega

### Step 2: Minikube Start Karna
Command: `minikube start`
Verification: Minikube cluster running hona chahiye

### Step 3: Docker Image Load Karna
Command: `eval $(minikube docker-env) && docker build -t nextjs-frontend:latest .`
Verification: Image Minikube ke Docker daemon mein load ho jana chahiye

### Step 4: Complete Deployment
Command: `./scripts/deploy-frontend-complete.sh`
Verification: Saare steps automated hain aur deployment complete hoga

### Step 5: Verification Commands
1. **Check Pods**: `kubectl get pods`
2. **Check Services**: `kubectl get services`
3. **Access App**: `minikube service frontend-release-frontend --url`

### Alternative: One-Click Deployment
Command: `./scripts/deploy-frontend-complete.sh`
Ye script saare steps khud kar dega:
- Prerequisites check karega
- Docker image build karega
- Minikube start karega agar nahi chal raha
- Image load karega
- Helm chart install karega
- Verification karega

## Files Available
- `app/package.json` - Dependencies
- `app/pages/index.js` - Main page
- `app/next.config.js` - Configuration
- `Dockerfile` - Docker configuration
- `templates/` - Helm templates
- `values.yaml` - Helm values (2 replicas, port 3000)

## Troubleshooting
Agar abhi bhi error aata hai toh:
1. Check karein Docker aur Kubernetes properly installed hain
2. Verify karein Minikube running hai
3. Check karein sufficient resources available hain

Deployment ab successfully ho jani chahiye kyunke saare necessary files aur configurations available hain.