#!/bin/bash
# ============================================================================
# Cleanup Kubernetes Deployment
# ============================================================================
# Remove all deployed resources
# Usage: ./scripts/deploy/cleanup.sh [namespace]
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

NAMESPACE="${1:-todo-chatbot}"

echo -e "${YELLOW}=================================${NC}"
echo -e "${YELLOW}Cleanup Deployment${NC}"
echo -e "${YELLOW}Namespace: ${RED}${NAMESPACE}${NC}"
echo -e "${YELLOW}=================================${NC}\n"

read -p "Are you sure you want to delete all resources? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo -e "${GREEN}Cancelled${NC}"
  exit 0
fi

# Uninstall Helm release
echo -e "${YELLOW}Uninstalling Helm release...${NC}"
helm uninstall todo-chatbot -n $NAMESPACE 2>/dev/null || echo "No Helm release found"

# Delete namespace
echo -e "${YELLOW}Deleting namespace...${NC}"
kubectl delete namespace $NAMESPACE --wait=false 2>/dev/null || echo "Namespace not found"

echo ""
echo -e "${GREEN}✓ Cleanup initiated${NC}"
echo -e "${YELLOW}Note: Namespace deletion may take a few moments${NC}"
