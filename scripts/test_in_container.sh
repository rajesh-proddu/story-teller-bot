#!/bin/bash

##############################################################################
# Story Teller Bot - Test Runner in Container
# Builds and runs tests inside Docker container
##############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Story Teller Bot - Docker Test Runner                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

# Parse arguments
BUILD_ONLY=false
KEEP_CONTAINER=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --keep)
            KEEP_CONTAINER=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --build-only    Only build the test image, don't run tests"
            echo "  --keep          Keep the test container running"
            echo "  -h, --help      Show this help message"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# Build test image
echo -e "${YELLOW}[1/3] Building test Docker image...${NC}"
if docker build -t story-teller-bot:test -f "$PROJECT_ROOT/deployment/Dockerfile.test" "$PROJECT_ROOT"; then
    echo -e "${GREEN}✓ Test image built successfully${NC}"
else
    echo -e "${RED}✗ Failed to build test image${NC}"
    exit 1
fi

if [ "$BUILD_ONLY" = true ]; then
    echo -e "${GREEN}✓ Build complete. To run tests: docker run -it story-teller-bot:test${NC}"
    exit 0
fi

# Create results directory
mkdir -p "$PROJECT_ROOT/test_results"

# Run tests
echo -e "${YELLOW}[2/3] Running tests in container...${NC}"
echo ""

CONTAINER_NAME="story-teller-bot-test-$(date +%s)"

if docker run \
    --rm \
    --name "$CONTAINER_NAME" \
    -v "$PROJECT_ROOT/test_results:/app/test_results" \
    -v "$PROJECT_ROOT/models_cache:/app/models_cache" \
    story-teller-bot:test; then
    
    echo -e "${GREEN}✓ Tests completed successfully${NC}"
    TEST_RESULT=0
else
    echo -e "${RED}✗ Tests failed${NC}"
    TEST_RESULT=1
fi

# Report results
echo -e "${YELLOW}[3/3] Test Results${NC}"
echo ""

if [ -d "$PROJECT_ROOT/test_results/coverage" ]; then
    echo -e "${GREEN}✓ Coverage report generated${NC}"
    echo "  Location: test_results/coverage/index.html"
fi

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ ALL TESTS PASSED                                           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ✗ SOME TESTS FAILED                                          ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
fi

exit $TEST_RESULT
