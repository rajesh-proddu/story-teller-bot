#!/bin/bash

##############################################################################
# Story Teller Bot - Docker Setup Script
# This script prepares the environment for Docker-based development
##############################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}Story Teller Bot - Docker Setup${NC}"
echo -e "${BLUE}===================================================${NC}"
echo ""

# Check if Docker is installed
echo -e "${YELLOW}Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo -e "${YELLOW}Please install Docker from https://www.docker.com/${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

# Check if Docker Compose is installed
echo -e "${YELLOW}Checking Docker Compose installation...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed!${NC}"
    echo -e "${YELLOW}Please install Docker Compose${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose found${NC}"

# Create necessary directories for volumes
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/models_cache"
mkdir -p "$PROJECT_ROOT/audio_output"
mkdir -p "$PROJECT_ROOT/test_results"

echo -e "${GREEN}Directories created successfully!${NC}"

# Create .env file if it doesn't exist
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > "$PROJECT_ROOT/.env" << 'EOF'
# Story Teller Bot Configuration
LOG_LEVEL=INFO
SAMPLE_RATE=16000
AUDIO_DURATION_SECONDS=30
WHISPER_MODEL=base
TEXT_GENERATION_MODEL=gpt2
TTS_ENGINE=pyttsx3
EOF
    echo -e "${GREEN}.env file created${NC}"
fi

# Build Docker image
echo -e "${YELLOW}Building Docker image (this may take a few minutes)...${NC}"
docker build -t story-teller-bot:latest -f "$SCRIPT_DIR/Dockerfile" "$PROJECT_ROOT"

echo -e "${BLUE}===================================================${NC}"
echo -e "${GREEN}✓ Setup completed successfully!${NC}"
echo -e "${BLUE}===================================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "${GREEN}1. Run the bot:${NC}"
echo -e "   docker-compose -f deployment/docker-compose.yml up -d"
echo ""
echo -e "${GREEN}2. View logs:${NC}"
echo -e "   docker-compose -f deployment/docker-compose.yml logs -f"
echo ""
echo -e "${GREEN}3. Or use the run script:${NC}"
echo -e "   ./run.sh"
echo ""
echo -e "${GREEN}4. Run tests:${NC}"
echo -e "   ./scripts/test_in_container.sh"
echo ""
