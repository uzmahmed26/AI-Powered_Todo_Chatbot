# Phase V: Cloud Deployment Guide - DigitalOcean DOKS

Complete guide for deploying the AI-Powered Todo Chatbot to DigitalOcean Kubernetes (DOKS) with Kafka, Dapr, and production-grade features.

---

## Prerequisites

### 1. DigitalOcean Account
- Create account at https://cloud.digitalocean.com
- Add billing information
- Generate API token: Settings → API → Personal Access Tokens

### 2. Required Tools
- `kubectl` (Kubernetes CLI) ✅ Already installed
- `helm` (Kubernetes package manager) ✅ Already installed
- `dapr` (Dapr CLI) ✅ Already installed
- `doctl` (DigitalOcean CLI) ⚠️ **Need to install**

### 3. Estimated Monthly Costs
- **DOKS Cluster**: $12-48/month (1-3 nodes)
- **LoadBalancer**: $12/month
- **Container Registry**: $5/month
- **Managed Database** (optional): $15-60/month
- **Block Storage**: $1-5/month
- **Total**: ~$50-150/month depending on configuration

---

## Step-by-Step Deployment

### Step 1: Install DigitalOcean CLI (doctl)

**For Windows:**
```powershell
# Download from GitHub releases
https://github.com/digitalocean/doctl/releases/latest

# Or using Chocolatey
choco install doctl
```

**Verify installation:**
```bash
doctl version
```

### Step 2: Authenticate with DigitalOcean

```bash
# Initialize doctl with your API token
doctl auth init

# Verify authentication
doctl account get
```

### Step 3: Create Container Registry

```bash
# Create registry
doctl registry create todo-chatbot-registry

# Login to registry
doctl registry login

# Get registry URL (save this!)
doctl registry get todo-chatbot-registry
# Example output: registry.digitalocean.com/todo-chatbot-registry
```

### Step 4: Tag and Push Docker Images

```bash
# Set registry URL
export DOCKER_REGISTRY=registry.digitalocean.com/todo-chatbot-registry

# Tag images
docker tag todo-chatbot-backend:latest $DOCKER_REGISTRY/todo-chatbot-backend:latest
docker tag todo-chatbot-frontend:latest $DOCKER_REGISTRY/todo-chatbot-frontend:latest

# Push to registry
docker push $DOCKER_REGISTRY/todo-chatbot-backend:latest
docker push $DOCKER_REGISTRY/todo-chatbot-frontend:latest

# Verify images
doctl registry repository list-v2
```

### Step 5: Create DOKS Cluster

**Option A: Via CLI (Recommended)**
```bash
# Create cluster (basic - 2 nodes, 2GB RAM each)
doctl kubernetes cluster create todo-chatbot-cluster \
  --region nyc1 \
  --version 1.31.1-do.5 \
  --node-pool "name=worker;size=s-2vcpu-4gb;count=2;auto-scale=true;min-nodes=2;max-nodes=4"

# This takes 5-10 minutes
```

**Option B: Via DigitalOcean Dashboard**
1. Go to https://cloud.digitalocean.com/kubernetes/clusters
2. Click "Create Cluster"
3. Choose:
   - Region: New York (NYC1) or closest to you
   - Kubernetes version: Latest stable
   - Node pool: Basic nodes, 2x 4GB / 2 vCPUs ($24/month)
   - Cluster name: `todo-chatbot-cluster`
4. Click "Create Cluster"

### Step 6: Connect kubectl to DOKS

```bash
# Download cluster credentials
doctl kubernetes cluster kubeconfig save todo-chatbot-cluster

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### Step 7: Initialize Dapr on DOKS

```bash
# Initialize Dapr
dapr init -k

# Wait for Dapr components to be ready
dapr status -k

# All components should show "True" in HEALTHY column
```

### Step 8: Update Cloud Configuration

Edit `helm/todo-chatbot/values-cloud.yaml`:

```yaml
global:
  environment: production
  imageRegistry: "registry.digitalocean.com/todo-chatbot-registry/"

backend:
  replicaCount: 2
  secrets:
    # IMPORTANT: Update these values
    databaseUrl: "postgresql+asyncpg://user:pass@your-db-host:5432/todo_chatbot"
    openaiApiKey: "sk-proj-YOUR-ACTUAL-KEY-HERE"
  env:
    ENVIRONMENT: production
    APP_ENV: production

# Optional: Use DigitalOcean Managed PostgreSQL
postgresql:
  enabled: false  # Set to false if using managed database

kafka:
  enabled: true  # Enable for Phase V features
```

**Option: Use DigitalOcean Managed Database** (Recommended for production)
```bash
# Create managed PostgreSQL database
doctl databases create todo-chatbot-db \
  --engine pg \
  --region nyc1 \
  --size db-s-1vcpu-1gb \
  --version 15

# Get connection details
doctl databases connection todo-chatbot-db

# Update databaseUrl in values-cloud.yaml with the connection string
```

### Step 9: Create Production Namespace

```bash
kubectl create namespace production
```

### Step 10: Deploy with Helm

```bash
# Navigate to project root
cd "C:\Users\laptop world\Desktop\phase3"

# Deploy using Helm
helm install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-cloud.yaml \
  --namespace production \
  --create-namespace \
  --wait \
  --timeout 10m

# Or use the automated script
chmod +x scripts/deploy/deploy-cloud.sh
export DOCKER_REGISTRY=registry.digitalocean.com/todo-chatbot-registry
./scripts/deploy/deploy-cloud.sh
```

### Step 11: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n production

# Check services
kubectl get svc -n production

# Check Dapr components
dapr status -k

# View logs
kubectl logs -f deployment/backend -c backend -n production
kubectl logs -f deployment/frontend -c frontend -n production
```

### Step 12: Get External IP

```bash
# Wait for LoadBalancer IP assignment (2-5 minutes)
kubectl get svc frontend -n production -w

# Get the EXTERNAL-IP once assigned
kubectl get svc frontend -n production

# Example output:
# NAME       TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)
# frontend   LoadBalancer   10.245.0.123    138.197.123.45   80:30080/TCP
```

### Step 13: Access Your Application

```
http://EXTERNAL-IP

Example: http://138.197.123.45
```

---

## Optional: Configure Custom Domain

### 1. Install Nginx Ingress Controller

```bash
# Install nginx ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/do/deploy.yaml

# Wait for external IP
kubectl get svc -n ingress-nginx ingress-nginx-controller -w
```

### 2. Configure DNS

1. Go to your domain registrar (Namecheap, GoDaddy, etc.)
2. Add an A record:
   - **Name**: `@` or `todo-chatbot`
   - **Type**: A
   - **Value**: LoadBalancer EXTERNAL-IP
   - **TTL**: 3600

### 3. Install Cert-Manager (for HTTPS)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create Let's Encrypt issuer
cat <<EOF | kubectl apply -f -
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
```

### 4. Update values-cloud.yaml

```yaml
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: todo-chatbot.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
          service: frontend
          port: 80
  tls:
    - secretName: todo-chatbot-tls
      hosts:
        - todo-chatbot.yourdomain.com
```

### 5. Upgrade Deployment

```bash
helm upgrade todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-cloud.yaml \
  -n production \
  --wait
```

---

## Monitoring & Troubleshooting

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/backend -c backend -n production

# Frontend logs
kubectl logs -f deployment/frontend -c frontend -n production

# Dapr sidecar logs
kubectl logs -f deployment/backend -c daprd -n production

# Kafka logs (if enabled)
kubectl logs -f deployment/kafka-broker -n production
```

### Check Pod Status

```bash
# All resources
kubectl get all -n production

# Pod details
kubectl describe pod <pod-name> -n production

# Events
kubectl get events -n production --sort-by='.lastTimestamp'
```

### Dapr Dashboard

```bash
# Forward Dapr dashboard
dapr dashboard -k -n production

# Access at: http://localhost:8080
```

### Scale Deployments

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n production

# Scale frontend
kubectl scale deployment frontend --replicas=3 -n production

# Or update values-cloud.yaml and run helm upgrade
```

---

## Cost Optimization Tips

### 1. Use Autoscaling

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

### 2. Use Managed Services

- **Managed PostgreSQL**: Instead of running in cluster
- **Managed Redis**: DigitalOcean Managed Redis
- **Managed Kafka**: Consider Confluent Cloud or AWS MSK

### 3. Resource Limits

Set appropriate resource requests/limits to avoid over-provisioning:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### 4. Use Smaller Node Sizes

Start with basic nodes and scale up as needed:
- Development: `s-2vcpu-2gb` ($18/month)
- Production: `s-2vcpu-4gb` ($24/month)

---

## Cleanup (Destroy Resources)

**WARNING: This will delete all cloud resources and data!**

```bash
# Delete Helm release
helm uninstall todo-chatbot -n production

# Delete namespace
kubectl delete namespace production

# Delete DOKS cluster
doctl kubernetes cluster delete todo-chatbot-cluster

# Delete container registry
doctl registry delete todo-chatbot-registry

# Delete managed database (if created)
doctl databases delete todo-chatbot-db
```

---

## Production Checklist

Before going live:

- [ ] Updated all secrets in `values-cloud.yaml`
- [ ] Using managed PostgreSQL database
- [ ] Configured custom domain with HTTPS
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configured log aggregation
- [ ] Set up automated backups
- [ ] Configured resource limits
- [ ] Enabled autoscaling
- [ ] Set up alerting
- [ ] Reviewed security settings
- [ ] Load tested the application
- [ ] Documented runbooks

---

## Support

- **DigitalOcean Docs**: https://docs.digitalocean.com/products/kubernetes/
- **Dapr Docs**: https://docs.dapr.io/
- **Helm Docs**: https://helm.sh/docs/
- **Kafka Docs**: https://kafka.apache.org/documentation/

---

**Phase V Cloud Deployment Complete!**

Your AI-Powered Todo Chatbot is now running in production on DigitalOcean with:
- Kubernetes orchestration
- Dapr service mesh
- Kafka event streaming
- LoadBalancer with external IP
- Autoscaling
- Production-grade configuration
