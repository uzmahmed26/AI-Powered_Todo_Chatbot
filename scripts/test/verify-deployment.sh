#!/bin/bash
# ============================================================================
# Verify Kubernetes Deployment
# ============================================================================
# Check if all components are running correctly
# Usage: ./scripts/test/verify-deployment.sh [namespace]
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE="${1:-todo-chatbot}"

echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Deployment Verification${NC}"
echo -e "${GREEN}Namespace: ${YELLOW}${NAMESPACE}${NC}"
echo -e "${GREEN}=================================${NC}\n"

# Check pods
echo -e "${BLUE}[1/5] Checking pods...${NC}"
kubectl get pods -n $NAMESPACE
echo ""

PODS_READY=$(kubectl get pods -n $NAMESPACE -o json | jq -r '.items[] | select(.status.phase == "Running") | .metadata.name' | wc -l)
TOTAL_PODS=$(kubectl get pods -n $NAMESPACE -o json | jq -r '.items | length')

if [ "$PODS_READY" -eq "$TOTAL_PODS" ]; then
  echo -e "${GREEN}✓ All pods are running ($PODS_READY/$TOTAL_PODS)${NC}\n"
else
  echo -e "${RED}⚠ Some pods are not running ($PODS_READY/$TOTAL_PODS)${NC}\n"
fi

# Check services
echo -e "${BLUE}[2/5] Checking services...${NC}"
kubectl get svc -n $NAMESPACE
echo -e "${GREEN}✓ Services listed${NC}\n"

# Check Dapr components
echo -e "${BLUE}[3/5] Checking Dapr components...${NC}"
kubectl get components -n $NAMESPACE 2>/dev/null || echo -e "${YELLOW}No Dapr components found${NC}"
echo ""

# Test backend health
echo -e "${BLUE}[4/5] Testing backend health...${NC}"
BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l component=backend -o jsonpath='{.items[0].metadata.name}')
if [ -n "$BACKEND_POD" ]; then
  kubectl exec -n $NAMESPACE $BACKEND_POD -- curl -s http://localhost:8000/health > /dev/null && \
    echo -e "${GREEN}✓ Backend health check passed${NC}" || \
    echo -e "${RED}⚠ Backend health check failed${NC}"
else
  echo -e "${RED}⚠ Backend pod not found${NC}"
fi
echo ""

# Test frontend health
echo -e "${BLUE}[5/5] Testing frontend health...${NC}"
FRONTEND_POD=$(kubectl get pods -n $NAMESPACE -l component=frontend -o jsonpath='{.items[0].metadata.name}')
if [ -n "$FRONTEND_POD" ]; then
  kubectl exec -n $NAMESPACE $FRONTEND_POD -- curl -s http://localhost/health > /dev/null && \
    echo -e "${GREEN}✓ Frontend health check passed${NC}" || \
    echo -e "${RED}⚠ Frontend health check failed${NC}"
else
  echo -e "${RED}⚠ Frontend pod not found${NC}"
fi
echo ""

# Summary
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Verification Summary${NC}"
echo -e "${GREEN}=================================${NC}"
echo -e "Pods Running: ${GREEN}$PODS_READY${NC}/${TOTAL_PODS}"
echo ""
echo -e "${YELLOW}Access your application:${NC}"
if [ "$NAMESPACE" == "todo-chatbot" ]; then
  echo -e "  ${BLUE}minikube service frontend -n $NAMESPACE${NC}"
else
  EXTERNAL_IP=$(kubectl get svc frontend -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
  if [ -n "$EXTERNAL_IP" ]; then
    echo -e "  ${BLUE}http://${EXTERNAL_IP}${NC}"
  else
    echo -e "  ${YELLOW}Waiting for LoadBalancer IP...${NC}"
  fi
fi
echo ""
