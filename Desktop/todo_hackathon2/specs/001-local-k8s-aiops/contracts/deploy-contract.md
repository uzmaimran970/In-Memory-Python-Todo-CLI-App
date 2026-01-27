# API Contract: Local Kubernetes AI Operations

## Deploy Application via Natural Language

**Endpoint**: `kubectl-ai deploy <application> with <replicas> replicas`

**Request**:
- Command: Natural language command to deploy an application
- Parameters:
  - application: Name of the application to deploy
  - replicas: Number of replicas to create

**Response**:
- Status: Success or failure indication
- Message: Descriptive message about the operation
- Resource Info: Details about the deployed resources

**Example**:
```bash
kubectl-ai deploy frontend with 2 replicas
```

**Expected Result**:
- Creates a Deployment resource named "frontend" with 2 replicas
- Creates associated Service resource for the deployment
- Returns success message with resource details

## Expose Service

**Endpoint**: `kubectl-ai expose service <name> on port <port>`

**Request**:
- Command: Natural language command to expose a service
- Parameters:
  - name: Name of the service to expose
  - port: Port number to expose the service on

**Response**:
- Status: Success or failure indication
- Message: Descriptive message about the operation
- Service Info: Details about the exposed service

**Example**:
```bash
kubectl-ai expose service on port 80
```

**Expected Result**:
- Creates a Service resource exposing the deployment on port 80
- Returns success message with service details

## Verify Deployment

**Endpoint**: `kubectl get pods` (standard kubectl command)

**Request**:
- Command: Standard kubectl command to check pod status

**Response**:
- List of pods with status information
- Ready status for each pod

**Example**:
```bash
kubectl get pods
```

**Expected Result**:
- Shows all pods in the current namespace
- Status column indicates if pods are running