#!/bin/bash

# DoChat+ Production Deployment Script
# For Ubuntu/Debian servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "========================================"
echo "🚀 DoChat+ Production Deployment"
echo "========================================"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root for security reasons"
   exit 1
fi

# Update system packages
log_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
log_info "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    supervisor \
    curl \
    git \
    htop \
    ufw

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    log_info "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    log_success "Docker installed. Please log out and back in for group changes to take effect."
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log_info "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create application directory
APP_DIR="/opt/dochat-plus"
log_info "Setting up application directory: $APP_DIR"

if [ ! -d "$APP_DIR" ]; then
    sudo mkdir -p $APP_DIR
    sudo chown $USER:$USER $APP_DIR
fi

# Copy application files
log_info "Copying application files..."
cp -r . $APP_DIR/
cd $APP_DIR

# Create production environment file
log_info "Creating production environment configuration..."
cat > .env << EOF
# DoChat+ Production Configuration
DOCHAT_OLLAMA_MODEL=llama3.1:8b-instruct-q5_K_M
DOCHAT_EMBEDDING_MODEL=all-MiniLM-L6-v2
DOCHAT_HOST=0.0.0.0
DOCHAT_PORT=7860
DOCHAT_LOG_LEVEL=INFO

# Performance settings for production
DOCHAT_CHUNK_SIZE=800
DOCHAT_RETRIEVAL_K=4
DOCHAT_BATCH_SIZE=32
DOCHAT_MAX_CONCURRENT_REQUESTS=4

# Security settings
DOCHAT_MAX_FILE_SIZE_MB=50
DOCHAT_ENABLE_QUEUE=true
EOF

# Create systemd service for auto-start
log_info "Creating systemd service..."
sudo tee /etc/systemd/system/dochat-plus.service > /dev/null << EOF
[Unit]
Description=DoChat+ AI Document Intelligence Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable dochat-plus.service

# Configure Nginx reverse proxy
log_info "Configuring Nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/dochat-plus > /dev/null << EOF
server {
    listen 80;
    server_name _;  # Replace with your domain
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support for Gradio
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/dochat-plus /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Configure firewall
log_info "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Create log rotation
log_info "Setting up log rotation..."
sudo tee /etc/logrotate.d/dochat-plus > /dev/null << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

# Build and start the application
log_info "Building and starting DoChat+ application..."
docker-compose build
docker-compose up -d

# Wait for application to start
log_info "Waiting for application to start..."
sleep 30

# Check if application is running
if curl -f http://localhost:7860 >/dev/null 2>&1; then
    log_success "DoChat+ is running successfully!"
else
    log_error "Application failed to start. Check logs with: docker-compose logs"
fi

echo ""
echo "========================================"
echo "🎉 Production Deployment Complete!"
echo "========================================"
echo ""
echo "📱 Application URL: http://your-server-ip"
echo "📊 Status: sudo systemctl status dochat-plus"
echo "📋 Logs: docker-compose logs -f"
echo "🔄 Restart: sudo systemctl restart dochat-plus"
echo "🛑 Stop: sudo systemctl stop dochat-plus"
echo ""
echo "📁 Application directory: $APP_DIR"
echo "⚙️ Configuration file: $APP_DIR/.env"
echo "🌐 Nginx config: /etc/nginx/sites-available/dochat-plus"
echo ""
echo "🔒 Security Notes:"
echo "- Configure SSL/TLS with Let's Encrypt"
echo "- Update server_name in Nginx config with your domain"
echo "- Review firewall rules: sudo ufw status"
echo "- Monitor logs regularly"
echo ""
echo "🚀 DoChat+ is ready for production use!"