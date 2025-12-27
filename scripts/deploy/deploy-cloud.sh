#!/bin/bash
# ============================================================================
# Deploy Todo Chatbot to Cloud (Phase V)
# ============================================================================
# This script deploys the application to DigitalOcean DOKS
# Usage: ./scripts/deploy/deploy-cloud.sh
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CLUSTER_NAME="${CLUSTER_NAME:-todo-chatbot-cluster}"
REGION="${DO_REGION:-nyc1}"
REGISTRY="${DOCKER_REGISTRY:-}"

echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Cloud Kubernetes Deployment${NC}"
echo -e "${GREEN}Phase V - DigitalOcean DOKS${NC}"
echo -e "${GREEN}=================================${NC}\n"

# Step 1: Check prerequisites
echo -e "${BLUE}[1/8] Checking prerequisites...${NC}"
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}Error: kubectl not found${NC}"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}Error: helm not found${NC}"; exit 1; }
command -v dapr >/dev/null 2>&1 || { echo -e "${RED}Error: dapr CLI not found${NC}"; exit 1; }
command -v doctl >/dev/null 2>&1 || { echo -e "${RED}Error: doctl not found. Install from: https://docs.digitalocean.com/reference/doctl/${NC}"; exit 1; }

# Check if registry is set
if [ -z "$REGISTRY" ]; then
  echo -e "${RED}Error: DOCKER_REGISTRY environment variable not set${NC}"
  echo -e "${YELLOW}Set it with: export DOCKER_REGISTRY=registry.digitalocean.com/your-registry${NC}"
  exit 1
fi

echo -e "${GREEN}✓ All prerequisites satisfied${NC}\n"

# Step 2: Build and push images
echo -e "${BLUE}[2/8] Building and pushing Docker images...${NC}"
export DOCKER_REGISTRY=$REGISTRY
./scripts/build/build-images.sh latest

echo -e "${YELLOW}Pushing images to registry...${NC}"
docker push ${REGISTRY}/todo-chatbot-backend:latest
docker push ${REGISTRY}/todo-chatbot-frontend:latest
echo -e "${GREEN}✓ Images pushed successfully${NC}\n"

# Step 3: Connect to DOKS cluster
echo -e "${BLUE}[3/8] Connecting to DOKS cluster...${NC}"
doctl kubernetes cluster kubeconfig save $CLUSTER_NAME
echo -e "${GREEN}✓ Connected to cluster${NC}\n"

# Step 4: Create production namespace
echo -e "${BLUE}[4/8] Creating production namespace...${NC}"
kubectl create namespace production --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Namespace ready${NC}\n"

# Step 5: Initialize Dapr
echo -e "${BLUE}[5/8] Initializing Dapr in Kubernetes...${NC}"
if ! kubectl get namespace dapr-system >/dev/null 2>&1; then
  echo -e "${YELLOW}Installing Dapr...${NC}"
  dapr init -k
else
  echo -e "${GREEN}✓ Dapr is already initialized${NC}"
fi
echo ""

# Step 6: Create secrets (prompt user)
echo -e "${BLUE}[6/8] Setting up secrets...${NC}"
read -p "Have you updated the secrets in values-cloud.yaml? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo -e "${RED}Please update secrets in helm/todo-chatbot/values-cloud.yaml first${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Secrets configured${NC}\n"

# Step 7: Deploy with Helm
echo -e "${BLUE}[7/8] Deploying with Helm...${NC}"
helm upgrade --install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-cloud.yaml \
  --namespace production \
  --create-namespace \
  --set global.imageRegistry=${REGISTRY}/ \
  --wait \
  --timeout 10m

echo -e "${GREEN}✓ Helm deployment successful${NC}\n"

# Step 8: Wait for LoadBalancer IP
echo -e "${BLUE}[8/8] Waiting for LoadBalancer IP...${NC}"
kubectl wait --for=condition=ready pod -l app=todo-chatbot -n production --timeout=600s

echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}=================================${NC}\n"

# Get LoadBalancer IP
echo -e "${YELLOW}Getting service information...${NC}"
EXTERNAL_IP=$(kubectl get svc frontend -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

if [ -n "$EXTERNAL_IP" ]; then
  echo -e "${GREEN}Frontend URL: ${BLUE}http://${EXTERNAL_IP}${NC}"
else
  echo -e "${YELLOW}Waiting for LoadBalancer IP assignment...${NC}"
  kubectl get svc frontend -n production -w
fi

echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo -e "  View pods:     ${BLUE}kubectl get pods -n production${NC}"
echo -e "  View services: ${BLUE}kubectl get svc -n production${NC}"
echo -e "  View logs:     ${BLUE}kubectl logs -f <pod-name> -n production${NC}"
echo -e "  Dapr dashboard: ${BLUE}dapr dashboard -k -n production${NC}"
echo ""
