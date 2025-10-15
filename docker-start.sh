#!/bin/bash

# Docker Quick Start Script for FastAPI Application

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  FastAPI Docker Quick Start${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"

# Stop any existing containers
echo -e "\n${BLUE}Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Build and start services
echo -e "\n${BLUE}Building and starting services...${NC}"
docker-compose up -d --build

# Wait for services to be healthy
echo -e "\n${BLUE}Waiting for services to be ready...${NC}"
sleep 5

# Check service status
echo -e "\n${BLUE}Checking service status...${NC}"
docker-compose ps

# Display logs
echo -e "\n${BLUE}Recent logs:${NC}"
docker-compose logs --tail=20

# Show access information
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Application is running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""
echo -e "Access the application at:"
echo -e "  • API:        ${BLUE}http://localhost:8000${NC}"
echo -e "  • Swagger:    ${BLUE}http://localhost:8000/docs${NC}"
echo -e "  • ReDoc:      ${BLUE}http://localhost:8000/redoc${NC}"
echo -e "  • PostgreSQL: ${BLUE}localhost:5432${NC}"
echo -e "  • Redis:      ${BLUE}localhost:6379${NC}"
echo -e ""
echo -e "Useful commands:"
echo -e "  • View logs:     ${BLUE}docker-compose logs -f${NC}"
echo -e "  • Stop all:      ${BLUE}docker-compose down${NC}"
echo -e "  • Restart app:   ${BLUE}docker-compose restart app${NC}"
echo -e "  • Access shell:  ${BLUE}docker-compose exec app bash${NC}"
echo -e ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
