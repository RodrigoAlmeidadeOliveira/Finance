#!/bin/bash
# ===========================================
# Flow Forecaster - Restore Script
# Restore database from backup
# ===========================================

set -e

# Configuration
BACKUP_DIR="/opt/backups"
COMPOSE_DIR="/opt/flow-forecaster/infrastructure/contabo"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Load environment
if [ -f "$COMPOSE_DIR/.env" ]; then
    source "$COMPOSE_DIR/.env"
fi

POSTGRES_USER=${POSTGRES_USER:-forecaster}
POSTGRES_DB=${POSTGRES_DB:-flow_forecaster}

echo "=========================================="
echo "Flow Forecaster - Restore"
echo "=========================================="

# List available backups
echo -e "${YELLOW}Available database backups:${NC}"
echo ""
ls -lht "$BACKUP_DIR"/*.sql.gz 2>/dev/null | head -10 | awk '{print NR". " $NF " (" $5 ", " $6 " " $7 " " $8 ")"}'
echo ""

# Get backup file
if [ -z "$1" ]; then
    read -p "Enter backup filename (or number from list): " BACKUP_INPUT

    # Check if input is a number
    if [[ "$BACKUP_INPUT" =~ ^[0-9]+$ ]]; then
        BACKUP_FILE=$(ls -t "$BACKUP_DIR"/*.sql.gz 2>/dev/null | sed -n "${BACKUP_INPUT}p")
    else
        BACKUP_FILE="$BACKUP_DIR/$BACKUP_INPUT"
    fi
else
    if [[ "$1" == /* ]]; then
        BACKUP_FILE="$1"
    else
        BACKUP_FILE="$BACKUP_DIR/$1"
    fi
fi

# Validate backup file
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}Selected backup: $(basename $BACKUP_FILE)${NC}"
echo ""

# Confirm restore
read -p "⚠️  This will OVERWRITE the current database. Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}[1/3] Stopping application...${NC}"
cd "$COMPOSE_DIR"
docker compose stop flow-forecaster celery-worker celery-beat

echo -e "${YELLOW}[2/3] Restoring database...${NC}"
# Drop and recreate database
docker exec forecaster-postgres psql -U "$POSTGRES_USER" -c "DROP DATABASE IF EXISTS ${POSTGRES_DB};" postgres
docker exec forecaster-postgres psql -U "$POSTGRES_USER" -c "CREATE DATABASE ${POSTGRES_DB};" postgres

# Restore from backup
gunzip -c "$BACKUP_FILE" | docker exec -i forecaster-postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"

echo -e "${GREEN}Database restored successfully${NC}"

echo -e "${YELLOW}[3/3] Restarting application...${NC}"
docker compose up -d flow-forecaster celery-worker celery-beat

# Wait and check health
sleep 10
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")

if [ "$HEALTH" = "200" ]; then
    echo -e "${GREEN}✓ Application is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Application may still be starting (HTTP $HEALTH)${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Restore Complete!${NC}"
echo "=========================================="
echo ""
echo "Restored from: $(basename $BACKUP_FILE)"
echo "Time: $(date)"
echo ""
