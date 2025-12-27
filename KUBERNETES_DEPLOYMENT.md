# AI-Powered Todo Chatbot - Complete Kubernetes Deployment Guide

**Phases Covered**: III, IV, V
**Technologies**: Docker, Kubernetes, Minikube, Helm, Dapr, Kafka, DigitalOcean DOKS

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Project Structure](#project-structure)
4. [Phase III: Local Development](#phase-iii-local-development)
5. [Phase IV: Local Kubernetes (Minikube)](#phase-iv-local-kubernetes-minikube)
6. [Phase V: Cloud Deployment (DOKS)](#phase-v-cloud-deployment-doks)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

---

## Overview

This guide walks you through deploying the AI-Powered Todo Chatbot across three phases:

- **Phase III**: AI chatbot integration with OpenAI (local development)
- **Phase IV**: Local Kubernetes deployment using Minikube with Dapr
- **Phase V**: Production cloud deployment on DigitalOcean DOKS with Kafka

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)                  │
│                     Nginx serving static files                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/REST
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│           ┌──────────────────────────────────┐              │
│           │  AI Chatbot Service (OpenAI)     │              │
│           │  Task Management Service          │              │
│           │  Dapr Service-to-Service          │              │
│           └──────────────────────────────────┘              │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌────────────────┐            ┌──────────────────┐
│   PostgreSQL   │            │  Redis (Dapr)    │
│   (Database)   │            │  State Store     │
└────────────────┘            └──────────────────┘
                                       │
                               ┌───────┴────────┐
                               │                │
                         (Phase V only)         │
                               │                │
                     ┌─────────▼───────┐        │
                     │  Kafka Broker   │        │
                     │  (Event Stream) │        │
                     └─────────────────┘        │
```

---

## Prerequisites

### Required Software

| Tool | Version | Purpose | Installation Link |
|------|---------|---------|-------------------|
| **Docker Desktop** | Latest | Container runtime | [Install Docker](https://www.docker.com/products/docker-desktop/) |
| **Minikube** | v1.30+ | Local Kubernetes | [Install Minikube](https://minikube.sigs.k8s.io/docs/start/) |
| **kubectl** | v1.28+ | Kubernetes CLI | [Install kubectl](https://kubernetes.io/docs/tasks/tools/) |
| **Helm** | v3.12+ | Package manager | [Install Helm](https://helm.sh/docs/intro/install/) |
| **Dapr CLI** | v1.11+ | Service mesh | [Install Dapr](https://docs.dapr.io/getting-started/install-dapr-cli/) |
| **doctl** (Phase V) | Latest | DigitalOcean CLI | [Install doctl](https://docs.digitalocean.com/reference/doctl/how-to/install/) |

### Windows-Specific Installation

For **Windows 10/11** users:

```powershell
# Install Dapr CLI
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Install Helm (using Chocolatey)
choco install kubernetes-helm

# OR install Helm manually
# Download from: https://github.com/helm/helm/releases
# Extract helm.exe and add to PATH
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=YOUR_API_KEY_HERE

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/todo_chatbot

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=info
CORS_ORIGINS=http://localhost:5173,http://localhost

# Phase V - Cloud (optional for local)
# DOCKER_REGISTRY=registry.digitalocean.com/your-registry
# DO_REGION=nyc1
```

---

## Project Structure

```
phase3/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── api/               # API routes
│   │   │   ├── app.py
│   │   │   └── chatbot_routes.py
│   │   └── services/          # Business logic
│   │       ├── chatbot.py     # OpenAI integration
│   │       └── tasks.py
│   ├── requirements.txt
│   └── run.py
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/
│   │   └── services/
│   │       └── chatbotService.ts
│   └── package.json
├── docker/                     # Docker files
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── nginx.conf
│   └── docker-compose.yml
├── k8s/                        # Kubernetes manifests
│   ├── base/                  # Base configurations
│   │   ├── backend/
│   │   ├── frontend/
│   │   ├── postgres/
│   │   └── dapr/
│   ├── local/                 # Minikube configs
│   │   └── kustomization.yaml
│   └── cloud/                 # Cloud configs
│       ├── kafka/
│       └── kustomization.yaml
├── helm/                       # Helm charts
│   └── todo-chatbot/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-local.yaml
│       ├── values-cloud.yaml
│       └── templates/
├── scripts/                    # Automation scripts
│   ├── build/
│   │   ├── build-images.sh
│   │   └── load-to-minikube.sh
│   ├── deploy/
│   │   ├── deploy-local.sh
│   │   ├── deploy-cloud.sh
│   │   └── cleanup.sh
│   └── test/
│       └── verify-deployment.sh
└── docs/
    ├── PHASE3_CHATBOT_GUIDE.md
    └── KUBERNETES_DEPLOYMENT.md (this file)
```

---

## Phase III: Local Development

### Step 1: Set Up OpenAI API Key

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add to `.env`:
   ```bash
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

### Step 2: Run with Docker Compose

```bash
# Build and start all services
docker-compose -f docker/docker-compose.yml up --build

# Or run in detached mode
docker-compose -f docker/docker-compose.yml up -d
```

### Step 3: Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Step 4: Test the Chatbot

```bash
# Test chatbot endpoint
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries",
    "conversation_history": [],
    "use_tools": true
  }'
```

### Phase III Documentation

See detailed guide: [docs/PHASE3_CHATBOT_GUIDE.md](./docs/PHASE3_CHATBOT_GUIDE.md)

---

## Phase IV: Local Kubernetes (Minikube)

### Prerequisites Check

```bash
# Verify installations
docker --version
minikube version
kubectl version --client
helm version
dapr --version
```

### Quick Start (Automated)

```bash
# Run the automated deployment script
chmod +x scripts/deploy/deploy-local.sh
./scripts/deploy/deploy-local.sh
```

This script will:
1. Start Minikube
2. Initialize Dapr
3. Build Docker images
4. Load images to Minikube
5. Deploy with Helm
6. Show access URLs

### Manual Deployment Steps

#### Step 1: Start Minikube

```bash
# Start with recommended resources
minikube start --memory=4096 --cpus=2

# Verify cluster is running
minikube status
```

#### Step 2: Initialize Dapr

```bash
# Install Dapr runtime in Kubernetes
dapr init -k

# Verify Dapr installation
kubectl get pods -n dapr-system

# Expected output: dapr-operator, dapr-sidecar-injector, dapr-sentry
```

#### Step 3: Build Docker Images

```bash
# Build backend and frontend images
chmod +x scripts/build/build-images.sh
./scripts/build/build-images.sh latest

# Verify images
docker images | grep todo-chatbot
```

#### Step 4: Load Images to Minikube

```bash
# Load images into Minikube's Docker daemon
chmod +x scripts/build/load-to-minikube.sh
./scripts/build/load-to-minikube.sh

# Verify in Minikube
minikube ssh -- docker images | grep todo-chatbot
```

#### Step 5: Update Secrets

Edit `helm/todo-chatbot/values-local.yaml`:

```yaml
backend:
  secrets:
    databaseUrl: "postgresql://postgres:postgres@postgres:5432/todo_chatbot"
    openaiApiKey: "sk-proj-your-actual-key-here"  # REPLACE THIS
```

#### Step 6: Deploy with Helm

```bash
# Create namespace
kubectl create namespace todo-chatbot

# Install with Helm
helm install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-local.yaml \
  -n todo-chatbot \
  --wait

# Watch deployment
kubectl get pods -n todo-chatbot -w
```

#### Step 7: Access the Application

```bash
# Get service URL
minikube service frontend -n todo-chatbot --url

# Or use port forwarding
kubectl port-forward svc/frontend 8080:80 -n todo-chatbot
# Access at: http://localhost:8080
```

### Verification

```bash
# Run verification script
chmod +x scripts/test/verify-deployment.sh
./scripts/test/verify-deployment.sh todo-chatbot

# Check all resources
kubectl get all -n todo-chatbot

# View logs
kubectl logs -f deployment/backend -n todo-chatbot
kubectl logs -f deployment/frontend -n todo-chatbot
```

### Dapr Dashboard

```bash
# Launch Dapr dashboard
dapr dashboard -k

# Access at: http://localhost:8080
```

### Troubleshooting Phase IV

**Pods not starting?**
```bash
kubectl describe pod <pod-name> -n todo-chatbot
kubectl logs <pod-name> -n todo-chatbot
```

**Images not found?**
```bash
# Check images in Minikube
minikube ssh -- docker images

# Reload images
./scripts/build/load-to-minikube.sh
```

**Database connection issues?**
```bash
# Check PostgreSQL pod
kubectl logs deployment/postgres -n todo-chatbot

# Test connection
kubectl exec -it deployment/backend -n todo-chatbot -- \
  env | grep DATABASE_URL
```

---

## Phase V: Cloud Deployment (DOKS)

### Prerequisites

1. **DigitalOcean Account**
2. **Container Registry** (DigitalOcean or Docker Hub)
3. **Domain Name** (optional, for ingress)

### Step 1: Install doctl

```bash
# Windows (Chocolatey)
choco install doctl

# Or download from:
# https://github.com/digitalocean/doctl/releases

# Authenticate
doctl auth init
```

### Step 2: Create DOKS Cluster

```bash
# List available Kubernetes versions
doctl kubernetes options versions

# Create cluster
doctl kubernetes cluster create todo-chatbot-cluster \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=3"

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-chatbot-cluster
```

### Step 3: Set Up Container Registry

```bash
# Create registry
doctl registry create todo-chatbot-registry

# Login to registry
doctl registry login

# Set registry environment variable
export DOCKER_REGISTRY=registry.digitalocean.com/todo-chatbot-registry
```

### Step 4: Update Cloud Configuration

Edit `helm/todo-chatbot/values-cloud.yaml`:

```yaml
global:
  environment: production
  imageRegistry: "registry.digitalocean.com/todo-chatbot-registry/"

backend:
  replicaCount: 3
  secrets:
    # Use managed PostgreSQL database URL
    databaseUrl: "postgresql://user:pass@db-host:25060/dbname?sslmode=require"
    openaiApiKey: "sk-proj-your-production-key"

frontend:
  service:
    type: LoadBalancer

kafka:
  enabled: true

ingress:
  enabled: true
  hosts:
    - host: todo-chatbot.yourdomain.com
      paths:
        - path: /
          service: frontend
          port: 80
```

### Step 5: Deploy to Cloud (Automated)

```bash
# Run cloud deployment script
export DOCKER_REGISTRY=registry.digitalocean.com/todo-chatbot-registry
export CLUSTER_NAME=todo-chatbot-cluster

chmod +x scripts/deploy/deploy-cloud.sh
./scripts/deploy/deploy-cloud.sh
```

### Step 6: Manual Cloud Deployment

```bash
# Build and push images
./scripts/build/build-images.sh latest
docker push $DOCKER_REGISTRY/todo-chatbot-backend:latest
docker push $DOCKER_REGISTRY/todo-chatbot-frontend:latest

# Initialize Dapr
dapr init -k

# Deploy with Helm
helm install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-cloud.yaml \
  -n production \
  --create-namespace \
  --set global.imageRegistry=$DOCKER_REGISTRY/ \
  --wait

# Watch deployment
kubectl get pods -n production -w
```

### Step 7: Get External IP

```bash
# Get LoadBalancer external IP
kubectl get svc frontend -n production

# If using Ingress
kubectl get ingress -n production
```

### Step 8: Configure DNS

Point your domain to the LoadBalancer IP:

```
Type: A Record
Name: todo-chatbot (or @)
Value: <LoadBalancer-External-IP>
TTL: 300
```

### Step 9: Enable HTTPS (Optional)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Update ingress in values-cloud.yaml with TLS
```

### Monitoring and Logging

```bash
# View application logs
kubectl logs -f deployment/backend -n production
kubectl logs -f deployment/frontend -n production

# View Kafka logs (if enabled)
kubectl logs -f deployment/kafka-broker -n production

# Dapr dashboard
dapr dashboard -k -n production
```

---

## Troubleshooting

### Common Issues

#### 1. ImagePullBackOff

**Problem**: Pods can't pull Docker images

**Solution**:
```bash
# For Minikube: Load images manually
minikube image load todo-chatbot-backend:latest
minikube image load todo-chatbot-frontend:latest

# For Cloud: Check registry authentication
doctl registry login
kubectl create secret docker-registry regcred \
  --docker-server=$DOCKER_REGISTRY \
  --docker-username=your-username \
  --docker-password=your-password
```

#### 2. CrashLoopBackOff

**Problem**: Pods keep restarting

**Solution**:
```bash
# Check logs
kubectl logs <pod-name> -n <namespace>

# Check events
kubectl describe pod <pod-name> -n <namespace>

# Common causes:
# - Missing environment variables
# - Database connection issues
# - Invalid OpenAI API key
```

#### 3. Database Connection Failed

**Problem**: Backend can't connect to database

**Solution**:
```bash
# Check PostgreSQL is running
kubectl get pods -n <namespace> | grep postgres

# Check connection string
kubectl get secret backend-secrets -n <namespace> -o yaml
# Decode: echo "base64-string" | base64 -d

# Test connection from backend pod
kubectl exec -it deployment/backend -n <namespace> -- \
  psql $DATABASE_URL -c "SELECT 1;"
```

#### 4. Dapr Sidecar Issues

**Problem**: Dapr sidecar not injecting

**Solution**:
```bash
# Check Dapr installation
kubectl get pods -n dapr-system

# Verify annotations
kubectl get pod <pod-name> -n <namespace> -o yaml | grep dapr.io

# Restart deployment
kubectl rollout restart deployment/backend -n <namespace>
```

### Debugging Commands

```bash
# Get all resources
kubectl get all -n <namespace>

# Describe resource
kubectl describe <resource-type> <resource-name> -n <namespace>

# View logs
kubectl logs -f <pod-name> -n <namespace>
kubectl logs -f <pod-name> -c <container-name> -n <namespace>

# Execute commands in pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/sh

# Port forward for debugging
kubectl port-forward <pod-name> 8000:8000 -n <namespace>

# Check events
kubectl get events -n <namespace> --sort-by='.lastTimestamp'
```

---

## Maintenance

### Updating the Application

```bash
# Build new version
./scripts/build/build-images.sh v1.1.0

# For Minikube
./scripts/build/load-to-minikube.sh

# For Cloud
docker push $DOCKER_REGISTRY/todo-chatbot-backend:v1.1.0
docker push $DOCKER_REGISTRY/todo-chatbot-frontend:v1.1.0

# Upgrade with Helm
helm upgrade todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-<local|cloud>.yaml \
  -n <namespace> \
  --set backend.image.tag=v1.1.0 \
  --set frontend.image.tag=v1.1.0
```

### Scaling

```bash
# Scale backend replicas
kubectl scale deployment backend --replicas=5 -n <namespace>

# Or update Helm values and upgrade
helm upgrade todo-chatbot ./helm/todo-chatbot \
  -f values-cloud.yaml \
  --set backend.replicaCount=5
```

### Backup Database

```bash
# For PostgreSQL in Kubernetes
kubectl exec deployment/postgres -n <namespace> -- \
  pg_dump -U postgres todo_chatbot > backup.sql

# For managed database, use provider's backup tools
```

### Cleanup

```bash
# Remove local deployment
./scripts/deploy/cleanup.sh todo-chatbot

# Remove cloud deployment
./scripts/deploy/cleanup.sh production

# Or manually
helm uninstall todo-chatbot -n <namespace>
kubectl delete namespace <namespace>

# Delete DOKS cluster
doctl kubernetes cluster delete todo-chatbot-cluster
```

---

## Next Steps

After successful deployment:

1. ✅ **Set up monitoring**: Prometheus + Grafana
2. ✅ **Configure CI/CD**: GitHub Actions or GitLab CI
3. ✅ **Enable auto-scaling**: HPA (Horizontal Pod Autoscaler)
4. ✅ **Set up alerting**: PagerDuty or Slack integration
5. ✅ **Implement backup strategy**: Velero for Kubernetes backups

---

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Dapr Documentation](https://docs.dapr.io/)
- [DigitalOcean Kubernetes](https://docs.digitalocean.com/products/kubernetes/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

---

## Support

For issues or questions:
- Check logs: `kubectl logs -f <pod-name> -n <namespace>`
- Review events: `kubectl get events -n <namespace>`
- Verify configuration: `kubectl describe <resource> -n <namespace>`
- See troubleshooting section above

**Happy Deploying! 🚀**
