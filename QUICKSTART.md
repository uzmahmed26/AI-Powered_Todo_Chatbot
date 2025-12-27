# AI-Powered Todo Chatbot - Quick Start Guide

**Get your application running in minutes!**

---

## 🚀 Phase III: Local Development (Docker Compose)

### Prerequisites
- Docker Desktop installed and running
- OpenAI API key

### Steps

```bash
# 1. Clone and navigate to project
cd phase3

# 2. Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Start all services
docker-compose -f docker/docker-compose.yml up -d

# 4. Access the application
# Frontend: http://localhost
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**That's it! You're running Phase III! 🎉**

---

## 🎯 Phase IV: Local Kubernetes (Minikube)

### Prerequisites
- All Phase III prerequisites
- Minikube, kubectl, Helm, Dapr installed

### One-Command Deployment

```bash
# Deploy everything automatically
./scripts/deploy/deploy-local.sh
```

### Manual Steps (if needed)

```bash
# 1. Start Minikube
minikube start --memory=4096 --cpus=2

# 2. Initialize Dapr
dapr init -k

# 3. Build images
./scripts/build/build-images.sh

# 4. Load to Minikube
./scripts/build/load-to-minikube.sh

# 5. Update secrets in helm/todo-chatbot/values-local.yaml
# Replace OPENAI_API_KEY with your actual key

# 6. Deploy with Helm
helm install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-local.yaml \
  -n todo-chatbot \
  --create-namespace

# 7. Get URL
minikube service frontend -n todo-chatbot --url
```

**Phase IV Complete! Access via Minikube URL 🎉**

---

## ☁️ Phase V: Cloud Deployment (DigitalOcean)

### Prerequisites
- DigitalOcean account
- doctl installed
- Container registry (DigitalOcean or Docker Hub)

### Steps

```bash
# 1. Authenticate with DigitalOcean
doctl auth init

# 2. Create DOKS cluster
doctl kubernetes cluster create todo-chatbot-cluster \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --node-pool "name=worker;size=s-2vcpu-4gb;count=3"

# 3. Create and login to registry
doctl registry create todo-chatbot-registry
doctl registry login

# 4. Set environment variables
export DOCKER_REGISTRY=registry.digitalocean.com/todo-chatbot-registry
export CLUSTER_NAME=todo-chatbot-cluster

# 5. Update helm/todo-chatbot/values-cloud.yaml
# - Set global.imageRegistry
# - Update backend.secrets with production values
# - Set your domain in ingress.hosts

# 6. Deploy to cloud
./scripts/deploy/deploy-cloud.sh

# 7. Get external IP
kubectl get svc frontend -n production
```

**Phase V Complete! Your app is in the cloud! 🎉**

---

## 📋 Essential Commands Cheat Sheet

### Docker Commands

```bash
# Build images
./scripts/build/build-images.sh [tag]

# View images
docker images | grep todo-chatbot

# Stop Docker Compose
docker-compose -f docker/docker-compose.yml down
```

### Minikube Commands

```bash
# Start/Stop Minikube
minikube start
minikube stop

# Load images
minikube image load todo-chatbot-backend:latest

# Get service URL
minikube service <service-name> -n <namespace> --url

# SSH into Minikube
minikube ssh
```

### kubectl Commands

```bash
# View resources
kubectl get all -n <namespace>
kubectl get pods -n <namespace>
kubectl get svc -n <namespace>

# View logs
kubectl logs -f <pod-name> -n <namespace>
kubectl logs -f deployment/<name> -n <namespace>

# Describe resources
kubectl describe pod <pod-name> -n <namespace>

# Execute in pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/sh

# Port forward
kubectl port-forward svc/<service-name> 8080:80 -n <namespace>

# Delete resources
kubectl delete pod <pod-name> -n <namespace>
kubectl delete namespace <namespace>
```

### Helm Commands

```bash
# Install
helm install <release-name> <chart-path> -f values.yaml

# Upgrade
helm upgrade <release-name> <chart-path> -f values.yaml

# List releases
helm list -n <namespace>

# Uninstall
helm uninstall <release-name> -n <namespace>

# View values
helm get values <release-name> -n <namespace>
```

### Dapr Commands

```bash
# Initialize Dapr
dapr init -k

# Check status
dapr status -k

# Dashboard
dapr dashboard -k

# Uninstall
dapr uninstall -k
```

### Debugging

```bash
# Verify deployment
./scripts/test/verify-deployment.sh <namespace>

# Check events
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Check pod status
kubectl get pods -n <namespace> -o wide

# Watch pods
kubectl get pods -n <namespace> -w
```

---

## 🔧 Common Fixes

### Problem: Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n <namespace>

# Check logs
kubectl logs <pod-name> -n <namespace>

# Restart deployment
kubectl rollout restart deployment/<name> -n <namespace>
```

### Problem: Can't access application

```bash
# For Minikube
minikube service list -n <namespace>
minikube service <service-name> -n <namespace>

# For Cloud
kubectl get svc -n <namespace>
# Check EXTERNAL-IP column
```

### Problem: Images not found

```bash
# For Minikube: Reload images
./scripts/build/load-to-minikube.sh

# For Cloud: Check registry
doctl registry login
docker push $DOCKER_REGISTRY/todo-chatbot-backend:latest
```

### Problem: Database connection failed

```bash
# Check PostgreSQL
kubectl get pods -n <namespace> | grep postgres
kubectl logs deployment/postgres -n <namespace>

# Check secrets
kubectl get secret backend-secrets -n <namespace> -o yaml
```

---

## 📖 Documentation Links

- **Full Deployment Guide**: [KUBERNETES_DEPLOYMENT.md](./KUBERNETES_DEPLOYMENT.md)
- **Phase III Chatbot Guide**: [docs/PHASE3_CHATBOT_GUIDE.md](./docs/PHASE3_CHATBOT_GUIDE.md)
- **Getting Started**: [docs/GETTING_STARTED.md](./docs/GETTING_STARTED.md)

---

## 🆘 Need Help?

1. Check logs: `kubectl logs -f <pod-name> -n <namespace>`
2. Verify resources: `kubectl get all -n <namespace>`
3. Run verification: `./scripts/test/verify-deployment.sh <namespace>`
4. Review full guide: `KUBERNETES_DEPLOYMENT.md`

---

**Happy Coding! 🚀**
