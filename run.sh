#!/bin/bash

##############################################################################
# Story Teller Bot - Docker Run Wrapper
# Starts the bot using Docker Compose
##############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Story Teller Bot - Docker Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo -e "${YELLOW}Please install Docker from https://www.docker.com/${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed!${NC}"
    echo -e "${YELLOW}Please install Docker Compose from https://docs.docker.com/compose/install/${NC}"
    exit 1
fi

# Check if Docker daemon is running
if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running!${NC}"
    echo -e "${YELLOW}Please start Docker daemon${NC}"
    exit 1
fi

# Get the project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

cd "$PROJECT_ROOT"

echo -e "${YELLOW}Starting Story Teller Bot with Docker Compose...${NC}"
echo ""

# Start Docker Compose
docker-compose -f deployment/docker-compose.yml up -d

echo ""
echo -e "${GREEN}✓ Bot started successfully!${NC}"
echo ""
echo -e "${BLUE}Commands:${NC}"
echo -e "  View logs:     ${GREEN}docker-compose -f deployment/docker-compose.yml logs -f${NC}"
echo -e "  Stop bot:      ${GREEN}docker-compose -f deployment/docker-compose.yml down${NC}"
echo -e "  Shell access:  ${GREEN}docker-compose -f deployment/docker-compose.yml exec story-teller-bot bash${NC}"
echo ""
