#!/bin/bash
# ===========================================
# Planner Financeiro - Backup Script
# Backs up database and important files
# ===========================================

set -e

# Configuration
BACKUP_DIR="/opt/backups/planner"
COMPOSE_DIR="/opt/planner-financeiro/infrastructure/contabo"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "Planner Financeiro Backup - $DATE"
echo "=========================================="

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Load environment variables
if [ -f "$COMPOSE_DIR/.env" ]; then
    source "$COMPOSE_DIR/.env"
fi

POSTGRES_USER=${POSTGRES_USER:-planner}
POSTGRES_DB=${POSTGRES_DB:-planner_financeiro}

echo -e "${YELLOW}[1/4] Backing up PostgreSQL database...${NC}"
# Database backup
DB_BACKUP_FILE="$BACKUP_DIR/${POSTGRES_DB}_${DATE}.sql.gz"

docker exec planner-postgres pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" | gzip > "$DB_BACKUP_FILE"

if [ -f "$DB_BACKUP_FILE" ]; then
    SIZE=$(ls -lh "$DB_BACKUP_FILE" | awk '{print $5}')
    echo -e "${GREEN}Database backup created: $DB_BACKUP_FILE ($SIZE)${NC}"
else
    echo -e "${RED}Database backup failed!${NC}"
    exit 1
fi

echo -e "${YELLOW}[2/4] Backing up uploaded files...${NC}"
# Uploads backup
UPLOADS_BACKUP_FILE="$BACKUP_DIR/uploads_${DATE}.tar.gz"

# Check if uploads volume has data
if docker volume inspect contabo_planner_uploads >/dev/null 2>&1; then
    docker run --rm \
        -v contabo_planner_uploads:/data:ro \
        -v "$BACKUP_DIR":/backup \
        alpine tar czf "/backup/uploads_${DATE}.tar.gz" -C /data .

    if [ -f "$UPLOADS_BACKUP_FILE" ]; then
        SIZE=$(ls -lh "$UPLOADS_BACKUP_FILE" | awk '{print $5}')
        echo -e "${GREEN}Uploads backup created: $UPLOADS_BACKUP_FILE ($SIZE)${NC}"
    fi
else
    echo -e "${YELLOW}No uploads volume found, skipping...${NC}"
fi

echo -e "${YELLOW}[3/4] Backing up ML models...${NC}"
# ML Models backup
MODELS_BACKUP_FILE="$BACKUP_DIR/ml_models_${DATE}.tar.gz"

if docker volume inspect contabo_planner_ml_models >/dev/null 2>&1; then
    docker run --rm \
        -v contabo_planner_ml_models:/data:ro \
        -v "$BACKUP_DIR":/backup \
        alpine tar czf "/backup/ml_models_${DATE}.tar.gz" -C /data .

    if [ -f "$MODELS_BACKUP_FILE" ]; then
        SIZE=$(ls -lh "$MODELS_BACKUP_FILE" | awk '{print $5}')
        echo -e "${GREEN}ML models backup created: $MODELS_BACKUP_FILE ($SIZE)${NC}"
    fi
else
    echo -e "${YELLOW}No ML models volume found, skipping...${NC}"
fi

echo -e "${YELLOW}[4/4] Cleaning old backups (older than $RETENTION_DAYS days)...${NC}"
# Clean old backups
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

DELETED=$(find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS 2>/dev/null | wc -l)
echo -e "${GREEN}Cleaned $DELETED old backup files${NC}"

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}Backup Complete!${NC}"
echo "=========================================="
echo ""
echo "Backup files created in: $BACKUP_DIR"
ls -lh "$BACKUP_DIR" | grep "$DATE" | awk '{print "  " $NF " (" $5 ")"}'
echo ""
echo "Total backup size: $(du -sh "$BACKUP_DIR" | awk '{print $1}')"
echo ""
