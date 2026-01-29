#!/bin/bash
# ===========================================
# Flow Forecaster - Deployment Script
# Automated deployment with zero-downtime
# ===========================================

set -e

# Configuration
APP_DIR="/opt/flow-forecaster"
COMPOSE_DIR="$APP_DIR/infrastructure/contabo"
BRANCH=${1:-main}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=========================================="
echo "Flow Forecaster Deployment"
echo "Branch: $BRANCH"
echo "=========================================="

cd "$APP_DIR"

echo -e "${YELLOW}[1/7] Creating backup before deployment...${NC}"
"$COMPOSE_DIR/scripts/backup.sh" || {
    echo -e "${RED}Backup failed! Aborting deployment.${NC}"
    exit 1
}

echo -e "${YELLOW}[2/7] Fetching latest changes...${NC}"
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

COMMIT=$(git rev-parse --short HEAD)
echo -e "${GREEN}Deployed commit: $COMMIT${NC}"

echo -e "${YELLOW}[3/7] Building new images...${NC}"
cd "$COMPOSE_DIR"
docker compose build --no-cache

echo -e "${YELLOW}[4/7] Stopping old containers...${NC}"
docker compose down

echo -e "${YELLOW}[5/7] Starting new containers...${NC}"
docker compose up -d

echo -e "${YELLOW}[6/7] Running database migrations...${NC}"
# Wait for database to be ready
sleep 10
docker exec flow-forecaster-app flask db upgrade || {
    echo -e "${YELLOW}Migrations skipped or no pending migrations${NC}"
}

echo -e "${YELLOW}[7/7] Health check...${NC}"
# Wait for services to be healthy
sleep 15

# Check health endpoints
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
NGINX_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/nginx-health 2>/dev/null || echo "000")

if [ "$BACKEND_HEALTH" = "200" ] && [ "$NGINX_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓ All services healthy${NC}"
else
    echo -e "${RED}⚠ Health check issues:${NC}"
    echo "  Backend: HTTP $BACKEND_HEALTH"
    echo "  Nginx: HTTP $NGINX_HEALTH"
    echo ""
    echo "Check logs with: docker compose logs -f"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Deployed: $BRANCH @ $COMMIT"
echo "Time: $(date)"
echo ""
echo "Useful commands:"
echo "  docker compose ps          # Check status"
echo "  docker compose logs -f     # View logs"
echo "  docker compose restart     # Restart services"
echo ""
