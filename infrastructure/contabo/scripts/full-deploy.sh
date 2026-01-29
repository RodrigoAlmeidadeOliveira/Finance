#!/bin/bash
# ===========================================
# Planner Financeiro - Full Automated Deployment
# VPS: 164.68.108.166 (Port 8080)
# Repo: https://github.com/RodrigoAlmeidadeOliveira/Finance
# Runs alongside Flow Forecaster (Port 80)
# ===========================================

set -e

# Configuration
REPO_URL="https://github.com/RodrigoAlmeidadeOliveira/Finance.git"
APP_DIR="/opt/planner-financeiro"
COMPOSE_DIR="$APP_DIR/infrastructure/contabo"
VPS_IP="164.68.108.166"
APP_PORT="8080"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}=========================================="
echo "  Planner Financeiro - Automated Deploy"
echo "==========================================${NC}"
echo ""
echo "VPS IP: $VPS_IP"
echo "Port: $APP_PORT"
echo "Repository: $REPO_URL"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Por favor, execute como root: sudo bash full-deploy.sh${NC}"
    exit 1
fi

# ===========================================
# PHASE 1: Check if Docker is installed
# ===========================================
echo -e "${YELLOW}[1/6] Verificando Docker...${NC}"

if ! command -v docker &> /dev/null; then
    echo "Docker não encontrado. Instalando..."

    # Update system
    apt-get update && apt-get upgrade -y

    # Install dependencies
    apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        git \
        wget

    # Add Docker GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    systemctl enable docker
    systemctl start docker
fi

echo -e "${GREEN}✓ Docker $(docker --version | cut -d' ' -f3) disponível${NC}"

# ===========================================
# PHASE 2: Open Port 8080 in Firewall
# ===========================================
echo -e "${YELLOW}[2/6] Abrindo porta 8080 no firewall...${NC}"

if command -v ufw &> /dev/null; then
    ufw allow 8080/tcp 2>/dev/null || true
    echo -e "${GREEN}✓ Porta 8080 liberada${NC}"
else
    echo -e "${YELLOW}⚠ UFW não encontrado, verifique o firewall manualmente${NC}"
fi

# ===========================================
# PHASE 3: Clone Repository
# ===========================================
echo -e "${YELLOW}[3/6] Clonando repositório...${NC}"

# Create directories
mkdir -p "$APP_DIR"
mkdir -p /opt/backups/planner

# Clone or update
if [ -d "$APP_DIR/.git" ]; then
    echo "Repositório já existe, atualizando..."
    cd "$APP_DIR"
    git fetch origin
    git reset --hard origin/main
else
    git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"
echo -e "${GREEN}✓ Repositório clonado em $APP_DIR${NC}"

# ===========================================
# PHASE 4: Generate Secrets & Configure .env
# ===========================================
echo -e "${YELLOW}[4/6] Configurando ambiente...${NC}"

cd "$COMPOSE_DIR"

# Generate secrets
POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)
SECRET_KEY=$(openssl rand -base64 32 | tr -d '/+=' | head -c 48)
JWT_SECRET=$(openssl rand -base64 32 | tr -d '/+=' | head -c 48)

# Create .env file
cat > .env <<EOF
# ===========================================
# Planner Financeiro - Production Environment
# Generated: $(date)
# ===========================================

# PostgreSQL Database
POSTGRES_USER=planner
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=planner_financeiro

# Application Security
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# CORS (IP access with port 8080)
CORS_ORIGINS=http://$VPS_IP:$APP_PORT,http://localhost:$APP_PORT

# OpenAI (optional)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-3.5-turbo

# Gunicorn (reduced for shared VPS)
GUNICORN_WORKERS=2
GUNICORN_THREADS=2

# Logging
LOG_LEVEL=INFO
EOF

# Save credentials to a secure file
cat > /root/planner-financeiro-credentials.txt <<EOF
===========================================
Planner Financeiro - Credenciais
Gerado em: $(date)
===========================================

VPS IP: $VPS_IP
URL: http://$VPS_IP:$APP_PORT

PostgreSQL:
  Host: localhost:5433 (interno)
  User: planner
  Password: $POSTGRES_PASSWORD
  Database: planner_financeiro

SECRET_KEY: $SECRET_KEY
JWT_SECRET_KEY: $JWT_SECRET

Comandos úteis:
  cd $COMPOSE_DIR
  docker compose ps
  docker compose logs -f
  docker compose restart

Backup:
  ./scripts/backup.sh
EOF

chmod 600 /root/planner-financeiro-credentials.txt
echo -e "${GREEN}✓ Ambiente configurado${NC}"
echo -e "${CYAN}  Credenciais salvas em: /root/planner-financeiro-credentials.txt${NC}"

# ===========================================
# PHASE 5: Build and Start
# ===========================================
echo -e "${YELLOW}[5/6] Construindo e iniciando containers...${NC}"

# Make scripts executable
chmod +x scripts/*.sh

# Build containers
echo "Building containers (pode demorar 3-5 minutos)..."
docker compose build

# Start containers
echo "Starting containers..."
docker compose up -d

# Wait for database to be ready
echo "Aguardando banco de dados..."
sleep 15

# Run migrations
echo "Executando migrações..."
docker exec planner-backend flask db upgrade 2>/dev/null || echo "Migrações executadas ou não necessárias"

# ===========================================
# PHASE 6: Health Check
# ===========================================
echo ""
echo -e "${CYAN}[6/6] Verificando saúde dos serviços...${NC}"
sleep 10

# Check containers
echo ""
echo "Status dos containers:"
docker compose ps

# Health checks
echo ""
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null || echo "000")
NGINX_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/nginx-health 2>/dev/null || echo "000")

if [ "$BACKEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓ Backend: OK${NC}"
else
    echo -e "${YELLOW}⚠ Backend: HTTP $BACKEND_HEALTH (pode estar iniciando)${NC}"
fi

if [ "$NGINX_HEALTH" = "200" ]; then
    echo -e "${GREEN}✓ Nginx: OK${NC}"
else
    echo -e "${YELLOW}⚠ Nginx: HTTP $NGINX_HEALTH (pode estar iniciando)${NC}"
fi

# ===========================================
# SETUP BACKUP CRON
# ===========================================
BACKUP_SCRIPT="$COMPOSE_DIR/scripts/backup.sh"
CRON_JOB="0 3 * * * $BACKUP_SCRIPT >> /var/log/planner-backup.log 2>&1"
(crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT"; echo "$CRON_JOB") | crontab -

# ===========================================
# DONE!
# ===========================================
echo ""
echo -e "${GREEN}=========================================="
echo "  ✅ DEPLOY COMPLETO!"
echo "==========================================${NC}"
echo ""
echo -e "🌐 Acesse: ${CYAN}http://$VPS_IP:$APP_PORT${NC}"
echo ""
echo "Credenciais salvas em:"
echo "  /root/planner-financeiro-credentials.txt"
echo ""
echo "Comandos úteis:"
echo "  cd $COMPOSE_DIR"
echo "  docker compose ps          # Status"
echo "  docker compose logs -f     # Logs"
echo "  docker compose restart     # Reiniciar"
echo "  ./scripts/backup.sh        # Backup manual"
echo ""
echo -e "${YELLOW}Aguarde ~30 segundos para todos os serviços iniciarem completamente.${NC}"
echo ""
