# Deploy Flow Forecaster no Contabo VPS

Guia completo para implantar o Flow Forecaster em um VPS Contabo.

## 💰 Custo Estimado: ~$11.25/mês (plano anual)

```yaml
Contabo Cloud VPS 30:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 8 vCPU
✅ 24 GB RAM
✅ 200 GB NVMe (ou 400 GB SSD)
✅ 32 TB Transfer
✅ ~R$ 65/mês (plano anual)
```

---

## 📁 Estrutura de Arquivos Criados

```
infrastructure/contabo/
├── docker-compose.yml          # Orquestração de containers
├── .env.example                # Template de variáveis de ambiente
├── init-db/
│   └── 01-init.sql            # Inicialização do PostgreSQL
├── nginx/
│   ├── conf.d/
│   │   └── flow-forecaster.conf  # Configuração Nginx
│   ├── ssl/
│   │   └── .gitkeep           # Certificados SSL aqui
│   └── logs/
│       └── .gitkeep           # Logs do Nginx
└── scripts/
    ├── setup.sh               # Setup inicial do servidor
    ├── backup.sh              # Backup automático
    ├── deploy.sh              # Deploy automatizado
    └── restore.sh             # Restauração de backup

backend/
├── Dockerfile                 # Container da aplicação Flask
├── wsgi.py                    # Entry point WSGI
├── celery_app.py             # Configuração Celery
└── tasks/
    └── __init__.py           # Tarefas em background

frontend/
├── Dockerfile                # Container React/Vite
└── nginx.conf               # Nginx interno do frontend

Procfile                      # Para Heroku/Fly.io
runtime.txt                   # Versão Python 3.11
```

---

## 🚀 Parte 1: Provisionar VPS no Contabo

### 1.1 Acessar Painel Contabo

1. Login em: https://my.contabo.com/
2. Vá para **Your Services** → **VPS**
3. Aguarde o VPS ficar **Active**

### 1.2 Anotar Credenciais (recebidas por email)

- **IP Address**: `xxx.xxx.xxx.xxx`
- **Username**: `root`
- **Password**: `(senha inicial)`

### 1.3 Primeiro Acesso SSH

```bash
# Conectar (aceite o fingerprint)
ssh root@<IP_DO_VPS>
```

### 1.4 Criar Usuário de Deploy (Recomendado)

```bash
# Criar usuário
adduser deploy

# Dar permissões sudo
usermod -aG sudo deploy

# No seu computador local, copiar SSH key:
ssh-copy-id deploy@<IP_DO_VPS>

# Testar login sem senha
ssh deploy@<IP_DO_VPS>
```

---

## 🔧 Parte 2: Setup do Servidor

### 2.1 Executar Script de Setup

```bash
# Login como deploy
ssh deploy@<IP_DO_VPS>

# Clonar repositório
sudo mkdir -p /opt/flow-forecaster
sudo chown $USER:$USER /opt/flow-forecaster
cd /opt/flow-forecaster
git clone https://github.com/SEU_USUARIO/flow-forecaster.git .

# Executar setup
chmod +x infrastructure/contabo/scripts/*.sh
sudo ./infrastructure/contabo/scripts/setup.sh

# IMPORTANTE: Logout e login novamente (para grupos Docker)
exit
ssh deploy@<IP_DO_VPS>

# Verificar Docker
docker --version
docker compose version
```

---

## 📦 Parte 3: Deploy da Aplicação

### 3.1 Configurar Variáveis de Ambiente

```bash
cd /opt/flow-forecaster/infrastructure/contabo

# Copiar template
cp .env.example .env

# Gerar senhas fortes
echo "POSTGRES_PASSWORD: $(openssl rand -base64 24)"
echo "SECRET_KEY: $(openssl rand -base64 32)"
echo "JWT_SECRET_KEY: $(openssl rand -base64 32)"

# Editar .env com os valores gerados
nano .env
```

### 3.2 Build e Start

```bash
# Build (primeira vez: 3-5 minutos)
docker compose build

# Iniciar todos os serviços
docker compose up -d

# Verificar status
docker compose ps
```

### 3.3 Executar Migrações do Banco

```bash
docker exec flow-forecaster-app flask db upgrade
```

### 3.4 Verificar Health

```bash
# Backend
curl http://localhost:8000/health

# Via Nginx
curl http://localhost/health

# Logs
docker compose logs -f
```

---

## 🌐 Parte 4: Configurar Domínio e SSL

### 4.1 Configurar DNS

No seu provedor de domínio, adicione:

```
Type: A
Name: @ (ou www)
Value: <IP_DO_CONTABO>
TTL: 300
```

### 4.2 Editar Nginx

```bash
nano infrastructure/contabo/nginx/conf.d/flow-forecaster.conf
```

Altere `server_name` para seu domínio:
```nginx
server_name seudominio.com www.seudominio.com;
```

### 4.3 Reiniciar Nginx

```bash
docker compose restart nginx
```

### 4.4 SSL com Let's Encrypt

```bash
# Instalar certbot
sudo apt install certbot

# Parar Nginx temporariamente
docker compose stop nginx

# Obter certificado
sudo certbot certonly --standalone -d seudominio.com -d www.seudominio.com

# Copiar certificados
sudo cp /etc/letsencrypt/live/seudominio.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/seudominio.com/privkey.pem nginx/ssl/
sudo chown -R $USER:$USER nginx/ssl/

# Editar nginx config - descomentar seção HTTPS
nano nginx/conf.d/flow-forecaster.conf

# Reiniciar
docker compose up -d nginx
```

### 4.5 Renovação Automática SSL

```bash
# Adicionar ao crontab
crontab -e

# Adicionar linha:
0 3 1 * * certbot renew --quiet --post-hook "docker compose -f /opt/flow-forecaster/infrastructure/contabo/docker-compose.yml restart nginx"
```

---

## 🔍 Comandos Úteis

### Status e Logs

```bash
cd /opt/flow-forecaster/infrastructure/contabo

# Status de todos containers
docker compose ps

# Logs em tempo real
docker compose logs -f

# Logs específicos
docker compose logs -f flow-forecaster
docker compose logs -f celery-worker
docker compose logs -f postgres
docker compose logs -f nginx
```

### Reiniciar Serviços

```bash
# Tudo
docker compose restart

# Específico
docker compose restart flow-forecaster
```

### Database

```bash
# Conectar ao PostgreSQL
docker exec -it forecaster-postgres psql -U forecaster -d flow_forecaster

# Redis CLI
docker exec -it forecaster-redis redis-cli
```

### Backup e Restore

```bash
# Backup manual
./scripts/backup.sh

# Listar backups
ls -lh /opt/backups/

# Restaurar
./scripts/restore.sh
```

### Deploy de Atualizações

```bash
./scripts/deploy.sh main
```

---

## 💾 Backups

### Automático
Configurado para rodar **diariamente às 2 AM**.

### Manual
```bash
/opt/flow-forecaster/infrastructure/contabo/scripts/backup.sh
```

### Restaurar
```bash
# Interativo (lista backups disponíveis)
./scripts/restore.sh

# Direto
./scripts/restore.sh flow_forecaster_20240101_020000.sql.gz
```

---

## 🆘 Troubleshooting

### Container não inicia
```bash
docker compose logs <service>
docker compose restart <service>
```

### 502 Bad Gateway
```bash
# Verificar se app está rodando
docker compose ps flow-forecaster

# Testar diretamente
docker exec flow-forecaster-app curl http://localhost:8000/health
```

### Erro de memória
```bash
# Ver uso
docker stats

# Reduzir workers no .env
# GUNICORN_WORKERS=2
docker compose restart flow-forecaster
```

### Disco cheio
```bash
# Ver uso
df -h

# Limpar Docker
docker system prune -f

# Limpar backups antigos
find /opt/backups -name "*.sql.gz" -mtime +30 -delete
```

---

## 📊 Monitoramento

### Recursos
```bash
# Containers
docker stats

# Sistema
htop
```

### Health Checks
```bash
# Flow Forecaster
curl http://localhost/health

# Nginx
curl http://localhost/nginx-health

# PostgreSQL
docker exec forecaster-postgres pg_isready

# Redis
docker exec forecaster-redis redis-cli ping
```

---

## 🔐 Segurança Checklist

- [ ] Senha forte no PostgreSQL
- [ ] SECRET_KEY única e aleatória
- [ ] JWT_SECRET_KEY diferente do SECRET_KEY
- [ ] Firewall (ufw) ativo
- [ ] Fail2ban configurado
- [ ] SSL/HTTPS habilitado
- [ ] Usuário não-root para deploy
- [ ] SSH key ao invés de senha

### Desabilitar login root por senha (opcional):
```bash
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no
sudo systemctl restart sshd
```

---

## ✅ Checklist Final

Antes de considerar deploy completo:

- [ ] VPS provisionado no Contabo
- [ ] Setup executado com sucesso
- [ ] Repositório clonado
- [ ] .env configurado com senhas fortes
- [ ] Docker compose rodando
- [ ] Migrações executadas
- [ ] Health check funcionando (http://IP/health)
- [ ] Domínio apontado
- [ ] SSL configurado
- [ ] Backups automáticos funcionando
- [ ] Firewall ativo

---

**Pronto!** Flow Forecaster rodando por **~$11/mês** 🎉
