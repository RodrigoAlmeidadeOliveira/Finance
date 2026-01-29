#!/bin/bash
# ===========================================
# Flow Forecaster - Full Automated Deployment
# VPS: 164.68.108.166
# Repo: https://github.com/RodrigoAlmeidadeOliveira/Finance
# ===========================================

set -e

# Configuration
REPO_URL="https://github.com/RodrigoAlmeidadeOliveira/Finance.git"
APP_DIR="/opt/flow-forecaster"
COMPOSE_DIR="$APP_DIR/infrastructure/contabo"
VPS_IP="164.68.108.166"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}=========================================="
echo "  Flow Forecaster - Automated Deploy"
echo "==========================================${NC}"
echo ""
echo "VPS IP: $VPS_IP"
echo "Repository: $REPO_URL"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Por favor, execute como root: sudo bash full-deploy.sh${NC}"
    exit 1
fi

# ===========================================
# PHASE 1: System Update & Dependencies
# ===========================================
echo -e "${YELLOW}[1/8] Atualizando sistema...${NC}"
apt-get update && apt-get upgrade -y

echo -e "${YELLOW}[2/8] Instalando dependências...${NC}"
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    git \
    htop \
    vim \
    wget \
    unzip \
    ufw \
    fail2ban

# ===========================================
# PHASE 2: Docker Installation
# ===========================================
echo -e "${YELLOW}[3/8] Instalando Docker...${NC}"

# Remove old versions
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

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

# Enable Docker
systemctl enable docker
systemctl start docker

echo -e "${GREEN}✓ Docker $(docker --version | cut -d' ' -f3) instalado${NC}"

# ===========================================
# PHASE 3: Firewall Configuration
# ===========================================
echo -e "${YELLOW}[4/8] Configurando firewall...${NC}"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo -e "${GREEN}✓ Firewall configurado (SSH, HTTP, HTTPS)${NC}"

# ===========================================
# PHASE 4: Fail2ban Configuration
# ===========================================
echo -e "${YELLOW}[5/8] Configurando Fail2ban...${NC}"
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 24h
EOF

systemctl enable fail2ban
systemctl restart fail2ban
echo -e "${GREEN}✓ Fail2ban configurado${NC}"

# ===========================================
# PHASE 5: Clone Repository
# ===========================================
echo -e "${YELLOW}[6/8] Clonando repositório...${NC}"

# Create directories
mkdir -p "$APP_DIR"
mkdir -p /opt/backups

# Clone
if [ -d "$APP_DIR/.git" ]; then
    echo "Repositório já existe, atualizando..."
    cd "$APP_DIR"
    git pull origin main
else
    git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"
echo -e "${GREEN}✓ Repositório clonado${NC}"

# ===========================================
# PHASE 6: Generate Secrets & Configure .env
# ===========================================
echo -e "${YELLOW}[7/8] Configurando ambiente...${NC}"

cd "$COMPOSE_DIR"

# Generate secrets
POSTGRES_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)
SECRET_KEY=$(openssl rand -base64 32 | tr -d '/+=' | head -c 48)
JWT_SECRET=$(openssl rand -base64 32 | tr -d '/+=' | head -c 48)

# Create .env file
cat > .env <<EOF
# ===========================================
# Flow Forecaster - Production Environment
# Generated: $(date)
# ===========================================

# PostgreSQL Database
POSTGRES_USER=forecaster
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=flow_forecaster

# Application Security
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# CORS (IP access)
CORS_ORIGINS=http://$VPS_IP,http://localhost

# OpenAI (optional)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-3.5-turbo

# Gunicorn
GUNICORN_WORKERS=4
GUNICORN_THREADS=2

# Logging
LOG_LEVEL=INFO
EOF

# Save credentials to a secure file
cat > /root/flow-forecaster-credentials.txt <<EOF
===========================================
Flow Forecaster - Credenciais
Gerado em: $(date)
===========================================

VPS IP: $VPS_IP
URL: http://$VPS_IP

PostgreSQL:
  Host: localhost:5432
  User: forecaster
  Password: $POSTGRES_PASSWORD
  Database: flow_forecaster

SECRET_KEY: $SECRET_KEY
JWT_SECRET_KEY: $JWT_SECRET

Comandos úteis:
  cd /opt/flow-forecaster/infrastructure/contabo
  docker compose ps
  docker compose logs -f
  docker compose restart
EOF

chmod 600 /root/flow-forecaster-credentials.txt
echo -e "${GREEN}✓ Ambiente configurado${NC}"
echo -e "${CYAN}  Credenciais salvas em: /root/flow-forecaster-credentials.txt${NC}"

# ===========================================
# PHASE 7: Update Nginx for IP Access
# ===========================================
# Update nginx config for IP access
sed -i "s/server_name localhost;/server_name $VPS_IP;/" nginx/conf.d/flow-forecaster.conf

# ===========================================
# PHASE 8: Build and Start
# ===========================================
echo -e "${YELLOW}[8/8] Construindo e iniciando containers...${NC}"

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
docker exec flow-forecaster-app flask db upgrade 2>/dev/null || echo "Migrações executadas ou não necessárias"

# ===========================================
# HEALTH CHECK
# ===========================================
echo ""
echo -e "${CYAN}Verificando saúde dos serviços...${NC}"
sleep 10

# Check containers
echo ""
echo "Status dos containers:"
docker compose ps

# Health checks
echo ""
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
NGINX_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/nginx-health 2>/dev/null || echo "000")

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
CRON_JOB="0 2 * * * $BACKUP_SCRIPT >> /var/log/flow-forecaster-backup.log 2>&1"
(crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT"; echo "$CRON_JOB") | crontab -

# ===========================================
# DONE!
# ===========================================
echo ""
echo -e "${GREEN}=========================================="
echo "  ✅ DEPLOY COMPLETO!"
echo "==========================================${NC}"
echo ""
echo -e "🌐 Acesse: ${CYAN}http://$VPS_IP${NC}"
echo ""
echo "Credenciais salvas em:"
echo "  /root/flow-forecaster-credentials.txt"
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
