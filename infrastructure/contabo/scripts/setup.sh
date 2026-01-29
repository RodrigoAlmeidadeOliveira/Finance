#!/bin/bash
# ===========================================
# Flow Forecaster - Server Setup Script
# For Contabo VPS (Ubuntu/Debian)
# ===========================================

set -e

echo "=========================================="
echo "Flow Forecaster - Server Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

echo -e "${YELLOW}[1/8] Updating system packages...${NC}"
apt-get update && apt-get upgrade -y

echo -e "${YELLOW}[2/8] Installing essential packages...${NC}"
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
    nano \
    wget \
    unzip \
    ufw \
    fail2ban

echo -e "${YELLOW}[3/8] Installing Docker...${NC}"
# Remove old versions
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Add repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable and start Docker
systemctl enable docker
systemctl start docker

echo -e "${YELLOW}[4/8] Configuring Docker for non-root user...${NC}"
# Add current user to docker group (if not root)
if [ -n "$SUDO_USER" ]; then
    usermod -aG docker $SUDO_USER
    echo -e "${GREEN}Added $SUDO_USER to docker group${NC}"
fi

echo -e "${YELLOW}[5/8] Configuring firewall (UFW)...${NC}"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo -e "${GREEN}Firewall configured: SSH, HTTP, HTTPS allowed${NC}"

echo -e "${YELLOW}[6/8] Configuring Fail2ban...${NC}"
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
echo -e "${GREEN}Fail2ban configured${NC}"

echo -e "${YELLOW}[7/8] Creating application directories...${NC}"
mkdir -p /opt/flow-forecaster
mkdir -p /opt/backups
mkdir -p /var/log/flow-forecaster

# Set permissions
if [ -n "$SUDO_USER" ]; then
    chown -R $SUDO_USER:$SUDO_USER /opt/flow-forecaster
    chown -R $SUDO_USER:$SUDO_USER /opt/backups
fi

echo -e "${YELLOW}[8/8] Setting up automatic backups...${NC}"
# Add backup cron job
BACKUP_SCRIPT="/opt/flow-forecaster/infrastructure/contabo/scripts/backup.sh"
CRON_JOB="0 2 * * * $BACKUP_SCRIPT >> /var/log/flow-forecaster/backup.log 2>&1"

# Add to crontab if not already present
(crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT"; echo "$CRON_JOB") | crontab -
echo -e "${GREEN}Daily backup scheduled for 2 AM${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Log out and log back in (for Docker group changes)"
echo "2. Clone your repository to /opt/flow-forecaster"
echo "3. Copy and configure .env file"
echo "4. Run docker compose up -d"
echo ""
echo "Useful commands:"
echo "  docker --version"
echo "  docker compose version"
echo "  ufw status"
echo "  fail2ban-client status"
echo ""
