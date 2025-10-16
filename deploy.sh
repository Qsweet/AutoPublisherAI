#!/bin/bash

###############################################################################
# AutoPublisherAI - VPS Deployment Script
###############################################################################
#
# This script automates the deployment of AutoPublisherAI on a VPS.
# It handles:
# - System dependencies installation
# - Docker and Docker Compose setup
# - SSL certificate configuration
# - Firewall setup
# - Application deployment
#
# Usage:
#   chmod +x deploy.sh
#   ./deploy.sh
#
# Requirements:
# - Ubuntu 22.04 LTS
# - Root or sudo access
# - Internet connection
#
###############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root or with sudo"
        exit 1
    fi
}

# Update system packages
update_system() {
    log_info "Updating system packages..."
    apt-get update -y
    apt-get upgrade -y
    log_success "System packages updated"
}

# Install Docker
install_docker() {
    if command -v docker &> /dev/null; then
        log_info "Docker is already installed"
        docker --version
        return
    fi
    
    log_info "Installing Docker..."
    
    # Install prerequisites
    apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up the repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    log_success "Docker installed successfully"
    docker --version
}

# Install Docker Compose
install_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose is already installed"
        docker-compose --version
        return
    fi
    
    log_info "Installing Docker Compose..."
    
    # Docker Compose is now included with Docker
    # But we'll create an alias for compatibility
    echo 'alias docker-compose="docker compose"' >> /root/.bashrc
    
    log_success "Docker Compose installed successfully"
}

# Setup firewall
setup_firewall() {
    log_info "Setting up firewall..."
    
    # Install UFW if not installed
    apt-get install -y ufw
    
    # Allow SSH
    ufw allow 22/tcp
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Enable firewall
    echo "y" | ufw enable
    
    log_success "Firewall configured"
    ufw status
}

# Install additional tools
install_tools() {
    log_info "Installing additional tools..."
    
    apt-get install -y \
        git \
        curl \
        wget \
        vim \
        htop \
        net-tools \
        certbot \
        python3-certbot-nginx
    
    log_success "Additional tools installed"
}

# Clone or update repository
setup_repository() {
    local REPO_URL="https://github.com/Qsweet/AutoPublisherAI.git"
    local INSTALL_DIR="/opt/autopublisher"
    
    log_info "Setting up repository..."
    
    if [ -d "$INSTALL_DIR" ]; then
        log_info "Repository already exists, pulling latest changes..."
        cd "$INSTALL_DIR"
        git pull
    else
        log_info "Cloning repository..."
        git clone "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi
    
    log_success "Repository setup complete"
}

# Setup environment file
setup_env_file() {
    local INSTALL_DIR="/opt/autopublisher"
    local ENV_FILE="$INSTALL_DIR/.env"
    
    log_info "Setting up environment file..."
    
    if [ -f "$ENV_FILE" ]; then
        log_warning ".env file already exists, skipping..."
        return
    fi
    
    # Copy example file
    cp "$INSTALL_DIR/.env.example" "$ENV_FILE"
    
    # Generate random passwords
    local POSTGRES_PASSWORD=$(openssl rand -base64 32)
    local JWT_SECRET=$(openssl rand -hex 32)
    local API_SECRET=$(openssl rand -hex 32)
    
    # Update .env file
    sed -i "s/POSTGRES_PASSWORD=CHANGE_THIS_TO_STRONG_PASSWORD/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" "$ENV_FILE"
    sed -i "s/JWT_SECRET_KEY=CHANGE_THIS_TO_RANDOM_SECRET_KEY_IN_PRODUCTION/JWT_SECRET_KEY=$JWT_SECRET/" "$ENV_FILE"
    sed -i "s/API_SECRET_KEY=CHANGE_THIS_TO_RANDOM_API_KEY_IN_PRODUCTION/API_SECRET_KEY=$API_SECRET/" "$ENV_FILE"
    
    log_success "Environment file created with secure passwords"
    log_warning "IMPORTANT: Edit /opt/autopublisher/.env and add your OPENAI_API_KEY"
}

# Start application
start_application() {
    local INSTALL_DIR="/opt/autopublisher"
    
    log_info "Starting application..."
    
    cd "$INSTALL_DIR"
    
    # Stop existing containers
    docker compose down
    
    # Build and start containers
    docker compose up -d --build
    
    log_success "Application started successfully"
    
    # Show running containers
    docker compose ps
}

# Setup SSL certificate
setup_ssl() {
    local DOMAIN="$1"
    
    if [ -z "$DOMAIN" ]; then
        log_warning "No domain provided, skipping SSL setup"
        log_info "To setup SSL later, run: certbot --nginx -d yourdomain.com"
        return
    fi
    
    log_info "Setting up SSL certificate for $DOMAIN..."
    
    # Install Nginx if not installed
    apt-get install -y nginx
    
    # Get SSL certificate
    certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email admin@"$DOMAIN"
    
    log_success "SSL certificate installed for $DOMAIN"
}

# Display completion message
show_completion_message() {
    echo ""
    echo "=========================================="
    log_success "AutoPublisherAI deployed successfully!"
    echo "=========================================="
    echo ""
    log_info "Next steps:"
    echo "  1. Edit /opt/autopublisher/.env and add your OPENAI_API_KEY"
    echo "  2. Configure WordPress and Instagram credentials in .env"
    echo "  3. Restart services: cd /opt/autopublisher && docker compose restart"
    echo ""
    log_info "Access points:"
    echo "  - Dashboard: http://$(curl -s ifconfig.me):8080"
    echo "  - Content Service API: http://$(curl -s ifconfig.me):8001/docs"
    echo "  - Publishing Service API: http://$(curl -s ifconfig.me):8002/docs"
    echo "  - Orchestrator Service API: http://$(curl -s ifconfig.me):8003/docs"
    echo "  - Flower (Celery Monitor): http://$(curl -s ifconfig.me):5555"
    echo ""
    log_info "Useful commands:"
    echo "  - View logs: cd /opt/autopublisher && docker compose logs -f"
    echo "  - Restart services: cd /opt/autopublisher && docker compose restart"
    echo "  - Stop services: cd /opt/autopublisher && docker compose down"
    echo "  - Update code: cd /opt/autopublisher && git pull && docker compose up -d --build"
    echo ""
}

# Main deployment function
main() {
    echo ""
    echo "=========================================="
    echo "  AutoPublisherAI VPS Deployment Script"
    echo "=========================================="
    echo ""
    
    # Check if running as root
    check_root
    
    # Ask for domain (optional)
    read -p "Enter your domain name (press Enter to skip SSL setup): " DOMAIN
    
    # Run deployment steps
    update_system
    install_docker
    install_docker_compose
    install_tools
    setup_firewall
    setup_repository
    setup_env_file
    start_application
    
    # Setup SSL if domain provided
    if [ -n "$DOMAIN" ]; then
        setup_ssl "$DOMAIN"
    fi
    
    # Show completion message
    show_completion_message
}

# Run main function
main

