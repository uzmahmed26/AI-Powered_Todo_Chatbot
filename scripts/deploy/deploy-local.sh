#!/bin/bash
# ============================================================================
# Deploy Todo Chatbot to Local Minikube (Phase IV)
# ============================================================================
# This script deploys the application using Helm to Minikube
# Usage: ./scripts/deploy/deploy-local.sh
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Local Kubernetes Deployment${NC}"
echo -e "${GREEN}Phase IV - Minikube${NC}"
echo -e "${GREEN}=================================${NC}\n"

# Step 1: Check prerequisites
echo -e "${BLUE}[1/7] Checking prerequisites...${NC}"
command -v minikube >/dev/null 2>&1 || { echo -e "${RED}Error: minikube not found${NC}"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}Error: kubectl not found${NC}"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}Error: helm not found${NC}"; exit 1; }
command -v dapr >/dev/null 2>&1 || { echo -e "${RED}Error: dapr CLI not found${NC}"; exit 1; }
echo -e "${GREEN}✓ All prerequisites satisfied${NC}\n"

# Step 2: Start Minikube if not running
echo -e "${BLUE}[2/7] Ensuring Minikube is running...${NC}"
if ! minikube status | grep -q "Running"; then
  echo -e "${YELLOW}Starting Minikube...${NC}"
  minikube start --memory=4096 --cpus=2
else
  echo -e "${GREEN}✓ Minikube is already running${NC}"
fi
echo ""

# Step 3: Initialize Dapr
echo -e "${BLUE}[3/7] Initializing Dapr in Kubernetes...${NC}"
if ! kubectl get namespace dapr-system >/dev/null 2>&1; then
  echo -e "${YELLOW}Installing Dapr...${NC}"
  dapr init -k
else
  echo -e "${GREEN}✓ Dapr is already initialized${NC}"
fi
echo ""

# Step 4: Build and load Docker images
echo -e "${BLUE}[4/7] Building Docker images...${NC}"
./scripts/build/build-images.sh latest
echo ""

echo -e "${BLUE}[4/7] Loading images to Minikube...${NC}"
./scripts/build/load-to-minikube.sh
echo ""

# Step 5: Create namespace
echo -e "${BLUE}[5/7] Creating namespace...${NC}"
kubectl create namespace todo-chatbot --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Namespace ready${NC}\n"

# Step 6: Deploy with Helm
echo -e "${BLUE}[6/7] Deploying with Helm...${NC}"
helm upgrade --install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-local.yaml \
  --namespace todo-chatbot \
  --create-namespace \
  --wait \
  --timeout 5m

echo -e "${GREEN}✓ Helm deployment successful${NC}\n"

# Step 7: Wait for pods to be ready
echo -e "${BLUE}[7/7] Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=todo-chatbot -n todo-chatbot --timeout=300s

echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}=================================${NC}\n"

# Get service URLs
echo -e "${YELLOW}Service Information:${NC}"
echo ""
echo -e "${GREEN}Frontend URL:${NC}"
minikube service frontend -n todo-chatbot --url
echo ""
echo -e "${GREEN}Backend URL:${NC}"
minikube service backend -n todo-chatbot --url
echo ""

echo -e "${YELLOW}Useful Commands:${NC}"
echo -e "  View pods:     ${BLUE}kubectl get pods -n todo-chatbot${NC}"
echo -e "  View logs:     ${BLUE}kubectl logs -f <pod-name> -n todo-chatbot${NC}"
echo -e "  Port forward:  ${BLUE}kubectl port-forward svc/frontend 8080:80 -n todo-chatbot${NC}"
echo -e "  Dapr dashboard: ${BLUE}dapr dashboard -k${NC}"
echo ""
