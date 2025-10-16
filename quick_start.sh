#!/bin/bash

# AutoPublisher AI - Quick Start Script
# This script helps you get started quickly

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}AutoPublisher AI - Quick Start${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed!${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed!${NC}"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Please edit .env file and add your API keys!${NC}"
    echo ""
    echo "Required keys:"
    echo "  - OPENAI_API_KEY (required for content generation)"
    echo "  - POSTGRES_PASSWORD (set a strong password)"
    echo "  - JWT_SECRET_KEY (set a strong secret key, min 32 chars)"
    echo ""
    read -p "Press Enter after you've edited the .env file..."
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""

# Ask user what to do
echo "What would you like to do?"
echo ""
echo "1) Start all services"
echo "2) Start services with health checks"
echo "3) Stop all services"
echo "4) View logs"
echo "5) Run tests"
echo "6) Clean up (remove all containers and volumes)"
echo "7) Exit"
echo ""
read -p "Enter your choice (1-7): " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}Starting all services...${NC}"
        docker-compose up -d
        echo ""
        echo -e "${GREEN}✓ All services started!${NC}"
        echo ""
        echo "Services running:"
        docker-compose ps
        echo ""
        echo "Access points:"
        echo "  - Auth Service: http://localhost:8005/docs"
        echo "  - Content Service: http://localhost:8001/docs"
        echo "  - Publishing Service: http://localhost:8002/docs"
        echo "  - Orchestrator Service: http://localhost:8003/docs"
        echo "  - Strategy Service: http://localhost:8004/docs"
        echo "  - Flower (Celery): http://localhost:5555"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop: docker-compose down"
        ;;
    
    2)
        echo ""
        echo -e "${BLUE}Starting services with health checks...${NC}"
        docker-compose -f docker-compose.healthchecks.yml up -d
        echo ""
        echo -e "${GREEN}✓ All services started with health checks!${NC}"
        echo ""
        echo "Monitoring health status..."
        docker-compose ps
        ;;
    
    3)
        echo ""
        echo -e "${BLUE}Stopping all services...${NC}"
        docker-compose down
        echo ""
        echo -e "${GREEN}✓ All services stopped!${NC}"
        ;;
    
    4)
        echo ""
        echo -e "${BLUE}Viewing logs (Ctrl+C to exit)...${NC}"
        docker-compose logs -f
        ;;
    
    5)
        echo ""
        echo -e "${BLUE}Running tests...${NC}"
        echo ""
        
        # Check if services are running
        if ! docker-compose ps | grep -q "Up"; then
            echo -e "${YELLOW}Services are not running. Starting them first...${NC}"
            docker-compose up -d
            echo "Waiting for services to be ready..."
            sleep 10
        fi
        
        ./test_system.sh
        ;;
    
    6)
        echo ""
        echo -e "${RED}⚠️  WARNING: This will remove all containers, volumes, and data!${NC}"
        read -p "Are you sure? (yes/no): " confirm
        
        if [ "$confirm" = "yes" ]; then
            echo ""
            echo -e "${BLUE}Cleaning up...${NC}"
            docker-compose down -v --rmi local
            echo ""
            echo -e "${GREEN}✓ Cleanup complete!${NC}"
        else
            echo "Cleanup cancelled."
        fi
        ;;
    
    7)
        echo "Goodbye!"
        exit 0
        ;;
    
    *)
        echo -e "${RED}Invalid choice!${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Done!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

