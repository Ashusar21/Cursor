# ☁️ DoChat+ Cloud Deployment Guide

Deploy DoChat+ on popular cloud platforms with these configurations.

## 🚀 **AWS EC2 Deployment**

### Launch EC2 Instance
```bash
# Recommended instance types:
# - t3.large (2 vCPU, 8GB RAM) - Minimum
# - t3.xlarge (4 vCPU, 16GB RAM) - Recommended
# - c5.2xlarge (8 vCPU, 16GB RAM) - High performance

# Security Group Rules:
# - SSH (22) from your IP
# - HTTP (80) from anywhere
# - HTTPS (443) from anywhere
# - Custom TCP (7860) from anywhere (for direct access)
```

### Deploy on EC2
```bash
# 1. Connect to your instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 2. Clone the repository
git clone https://github.com/yourusername/dochat-plus.git
cd dochat-plus

# 3. Run production deployment
chmod +x deploy_production.sh
./deploy_production.sh

# 4. Configure domain (optional)
sudo nano /etc/nginx/sites-available/dochat-plus
# Replace server_name _ with your domain

# 5. Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### AWS Application Load Balancer Setup
```bash
# Create target group pointing to port 7860
# Configure health checks on /
# Add SSL certificate via ACM
# Update security groups accordingly
```

## 🔵 **Google Cloud Platform (GCP) Deployment**

### Compute Engine VM
```bash
# Create VM instance
gcloud compute instances create dochat-plus-vm \
    --machine-type=e2-standard-4 \
    --boot-disk-size=50GB \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --tags=dochat-server

# Configure firewall
gcloud compute firewall-rules create allow-dochat \
    --allow tcp:80,tcp:443,tcp:7860 \
    --source-ranges 0.0.0.0/0 \
    --target-tags dochat-server

# SSH and deploy
gcloud compute ssh dochat-plus-vm
git clone https://github.com/yourusername/dochat-plus.git
cd dochat-plus
./deploy_production.sh
```

### Cloud Run Deployment
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/dochat-plus', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/dochat-plus']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: [
      'run', 'deploy', 'dochat-plus',
      '--image', 'gcr.io/$PROJECT_ID/dochat-plus',
      '--platform', 'managed',
      '--region', 'us-central1',
      '--memory', '8Gi',
      '--cpu', '4',
      '--timeout', '3600',
      '--max-instances', '10',
      '--allow-unauthenticated'
    ]
```

## 🔷 **Microsoft Azure Deployment**

### Azure Container Instances
```bash
# Create resource group
az group create --name dochat-rg --location eastus

# Deploy container
az container create \
    --resource-group dochat-rg \
    --name dochat-plus \
    --image your-registry/dochat-plus:latest \
    --cpu 4 \
    --memory 8 \
    --ports 7860 \
    --dns-name-label dochat-plus \
    --environment-variables \
        DOCHAT_OLLAMA_MODEL=llama3.1:8b-instruct-q5_K_M \
        DOCHAT_LOG_LEVEL=INFO
```

### Azure App Service
```yaml
# azure-pipelines.yml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: Docker@2
  inputs:
    containerRegistry: 'your-acr'
    repository: 'dochat-plus'
    command: 'buildAndPush'
    Dockerfile: '**/Dockerfile'

- task: AzureWebAppContainer@1
  inputs:
    azureSubscription: 'your-subscription'
    appName: 'dochat-plus-app'
    containers: 'your-acr.azurecr.io/dochat-plus:latest'
```

## 🟠 **DigitalOcean Droplet Deployment**

```bash
# Create droplet (4GB RAM minimum)
doctl compute droplet create dochat-plus \
    --size s-2vcpu-4gb \
    --image ubuntu-22-04-x64 \
    --region nyc1 \
    --ssh-keys your-ssh-key-id

# Get droplet IP
doctl compute droplet list

# Connect and deploy
ssh root@your-droplet-ip
git clone https://github.com/yourusername/dochat-plus.git
cd dochat-plus
./deploy_production.sh
```

## 🟣 **Heroku Deployment**

### Heroku Configuration
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-dochat-app

# Set environment variables
heroku config:set DOCHAT_OLLAMA_MODEL=llama3.1:8b-instruct-q5_K_M
heroku config:set DOCHAT_LOG_LEVEL=INFO
heroku config:set PORT=7860

# Deploy
git push heroku main
```

### Heroku Dockerfile
```dockerfile
# Use heroku/heroku:20 base image for Heroku
FROM heroku/heroku:20

# Install dependencies
RUN apt-get update && apt-get install -y python3 python3-pip

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE $PORT

# Start command
CMD gunicorn --bind 0.0.0.0:$PORT app:app
```

## 🐙 **Kubernetes Deployment**

### Kubernetes Manifests
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dochat-plus
spec:
  replicas: 2
  selector:
    matchLabels:
      app: dochat-plus
  template:
    metadata:
      labels:
        app: dochat-plus
    spec:
      containers:
      - name: dochat-plus
        image: your-registry/dochat-plus:latest
        ports:
        - containerPort: 7860
        env:
        - name: DOCHAT_OLLAMA_MODEL
          value: "llama3.1:8b-instruct-q5_K_M"
        - name: DOCHAT_LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
---
apiVersion: v1
kind: Service
metadata:
  name: dochat-plus-service
spec:
  selector:
    app: dochat-plus
  ports:
  - port: 80
    targetPort: 7860
  type: LoadBalancer
```

## 🔧 **Environment-Specific Configurations**

### Production Environment Variables
```bash
# Core settings
DOCHAT_OLLAMA_MODEL=llama3.1:8b-instruct-q5_K_M
DOCHAT_EMBEDDING_MODEL=all-MiniLM-L6-v2
DOCHAT_HOST=0.0.0.0
DOCHAT_PORT=7860
DOCHAT_LOG_LEVEL=INFO

# Performance tuning
DOCHAT_CHUNK_SIZE=800
DOCHAT_RETRIEVAL_K=4
DOCHAT_BATCH_SIZE=32
DOCHAT_MAX_CONCURRENT_REQUESTS=4

# Security
DOCHAT_MAX_FILE_SIZE_MB=50
DOCHAT_ENABLE_QUEUE=true
```

### Resource Requirements
```yaml
Minimum:
  CPU: 2 cores
  RAM: 4GB
  Storage: 20GB
  Network: 1Gbps

Recommended:
  CPU: 4 cores
  RAM: 8GB
  Storage: 50GB
  Network: 1Gbps

High Performance:
  CPU: 8 cores
  RAM: 16GB
  Storage: 100GB
  Network: 10Gbps
```

## 🔒 **Security Best Practices**

### SSL/TLS Configuration
```nginx
# /etc/nginx/sites-available/dochat-plus
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/private.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    location / {
        proxy_pass http://127.0.0.1:7860;
        # ... other proxy settings
    }
}
```

### Firewall Configuration
```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw deny 7860  # Block direct access, force through Nginx
sudo ufw enable

# iptables (alternative)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 7860 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 7860 -j DROP
```

## 📊 **Monitoring and Logging**

### Health Checks
```bash
# Application health check endpoint
curl -f http://localhost:7860/health || exit 1

# Docker health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1
```

### Log Aggregation
```yaml
# docker-compose with logging
version: '3.8'
services:
  dochat:
    # ... other config
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 🚀 **Deployment Checklist**

### Pre-deployment
- [ ] Choose appropriate instance size
- [ ] Configure security groups/firewall
- [ ] Set up domain name (optional)
- [ ] Prepare SSL certificates
- [ ] Review environment variables

### Deployment
- [ ] Clone repository
- [ ] Run deployment script
- [ ] Verify application starts
- [ ] Test PDF upload and processing
- [ ] Configure reverse proxy
- [ ] Set up SSL/TLS

### Post-deployment
- [ ] Configure monitoring
- [ ] Set up log rotation
- [ ] Create backup strategy
- [ ] Test auto-restart on failure
- [ ] Document access credentials
- [ ] Set up maintenance schedule

---

**Choose the deployment method that best fits your infrastructure and requirements!**