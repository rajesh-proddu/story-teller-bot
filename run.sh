#!/bin/bash

##############################################################################
# Story Teller Bot - Production Container Manager
# Starts, stops, and manages production containers
##############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get command
COMMAND="${1:-help}"

# Get the project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

cd "$PROJECT_ROOT"

##############################################################################
# Helper Functions
##############################################################################

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed!${NC}"
        echo -e "${YELLOW}Please install Docker from https://www.docker.com/${NC}"
        exit 1
    fi
}

check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed!${NC}"
        echo -e "${YELLOW}Please install Docker Compose${NC}"
        exit 1
    fi
}

check_docker_running() {
    if ! docker ps &> /dev/null; then
        echo -e "${RED}❌ Docker daemon is not running!${NC}"
        echo -e "${YELLOW}Please start Docker${NC}"
        exit 1
    fi
}

show_help() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Story Teller Bot - Container Manager${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Usage: ./run.sh [command]${NC}"
    echo ""
    echo -e "${GREEN}Commands:${NC}"
    echo -e "  ${BLUE}start${NC}      - Start bot containers"
    echo -e "  ${BLUE}stop${NC}       - Stop bot containers"
    echo -e "  ${BLUE}restart${NC}    - Restart bot containers"
    echo -e "  ${BLUE}logs${NC}       - View container logs (follow mode)"
    echo -e "  ${BLUE}logs-all${NC}   - View all logs without following"
    echo -e "  ${BLUE}status${NC}     - Show container status"
    echo -e "  ${BLUE}shell${NC}      - Interactive shell in running container"
    echo -e "  ${BLUE}help${NC}       - Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  ./run.sh start         # Start the bot"
    echo -e "  ./run.sh logs          # View live logs"
    echo -e "  ./run.sh stop          # Stop the bot"
    echo ""
}

##############################################################################
# Commands
##############################################################################

cmd_start() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Starting Story Teller Bot${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    check_docker
    check_docker_compose
    check_docker_running
    
    echo -e "${YELLOW}Building and starting containers...${NC}"
    docker-compose -f deployment/docker-compose.yml up -d --build
    
    sleep 2
    
    echo ""
    echo -e "${GREEN}✓ Bot started successfully!${NC}"
    echo ""
    echo -e "${BLUE}Common commands:${NC}"
    echo -e "  View logs:     ${GREEN}./run.sh logs${NC}"
    echo -e "  Stop bot:      ${GREEN}./run.sh stop${NC}"
    echo -e "  Get shell:     ${GREEN}./run.sh shell${NC}"
    echo ""
}

cmd_stop() {
    echo -e "${YELLOW}Stopping containers...${NC}"
    docker-compose -f deployment/docker-compose.yml down
    echo -e "${GREEN}✓ Containers stopped${NC}"
    echo ""
}

cmd_restart() {
    echo -e "${YELLOW}Restarting containers...${NC}"
    docker-compose -f deployment/docker-compose.yml restart
    echo -e "${GREEN}✓ Containers restarted${NC}"
    echo ""
}

cmd_logs() {
    check_docker
    check_docker_compose
    echo -e "${BLUE}Showing live logs (Ctrl+C to exit)...${NC}"
    echo ""
    docker-compose -f deployment/docker-compose.yml logs -f story-teller-bot
}

cmd_logs_all() {
    check_docker
    check_docker_compose
    docker-compose -f deployment/docker-compose.yml logs story-teller-bot
}

cmd_status() {
    echo -e "${BLUE}Container Status:${NC}"
    echo ""
    docker-compose -f deployment/docker-compose.yml ps
    echo ""
}

cmd_shell() {
    check_docker
    check_docker_compose
    
    # Check if container is running
    if ! docker-compose -f deployment/docker-compose.yml ps story-teller-bot | grep -q "running"; then
        echo -e "${RED}❌ Container is not running!${NC}"
        echo -e "${YELLOW}Start it first: ./run.sh start${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Opening shell in running container...${NC}"
    echo -e "${YELLOW}Type 'exit' to quit${NC}"
    echo ""
    docker-compose -f deployment/docker-compose.yml exec story-teller-bot bash
}

##############################################################################
# Main
##############################################################################

case "$COMMAND" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    logs)
        cmd_logs
        ;;
    logs-all)
        cmd_logs_all
        ;;
    status)
        cmd_status
        ;;
    shell)
        cmd_shell
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
