# Deployment - Docker Configuration and Scripts

This folder contains all deployment-related files for the Story Teller Bot.

## Files

### Docker Files
- **Dockerfile** - Production Docker image definition with pre-downloaded models
- **Dockerfile.test** - Testing Docker image with pytest and coverage tools

### Docker Compose Files
- **docker-compose.yml** - Main orchestration file for running the bot
- **docker-compose.extended.yml** - Extended compose file with both bot and test services

### Scripts
- **setup.sh** - Production setup script for host system
- **story-teller-bot.service** - Systemd service file for production deployment

## Quick Start

### From project root directory:

```bash
# Build and run bot
docker-compose -f deployment/docker-compose.yml up -d

# View logs
docker-compose -f deployment/docker-compose.yml logs -f

# Stop bot
docker-compose -f deployment/docker-compose.yml down
```

### Run tests in container:

```bash
# From project root
docker-compose -f deployment/docker-compose.extended.yml run tests

# Or use the convenience script
./scripts/test_in_container.sh
```

### Or from deployment directory:

```bash
# From deployment directory
cd deployment
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## How Docker Build Works

### Build Context

When running docker-compose from the project root with:
```bash
docker-compose -f deployment/docker-compose.yml up
```

- **context: ..** - Points to the project root (where source code is)
- **dockerfile: deployment/Dockerfile** - Path to the Dockerfile relative to project root
- Result: Docker can access all source files and dependencies

### Multi-Stage Build

The Dockerfile uses a multi-stage build:

1. **Builder stage** - Creates intermediate image with:
   - Python environment
   - All dependencies from requirements.txt
   - Downloads models from HuggingFace
   - Caches models in `/models_cache`

2. **Runtime stage** - Final production image with:
   - Python runtime
   - Only necessary files
   - Pre-downloaded models copied from builder
   - Application ready to run immediately
   - Much smaller image size (~1.5GB vs 2GB+)

### Models Pre-cached

Models are downloaded during image build:
- Whisper Base (~140MB) for speech recognition
- GPT-2 (~540MB) for story generation
- DistilGPT-2 (~160MB) as alternative

Result: No network calls needed at runtime, instant model loading.

## Volumes

### Persistent Volumes

Files created in these directories are preserved:
- `./logs/` - Application logs
- `./audio_output/` - Generated audio files
- `./models_cache/` - HuggingFace model cache
- `./test_results/` - Test coverage reports

Location in container → Host mapping:
- `/app/logs` → `logs/`
- `/app/audio_output` → `audio_output/`
- `/app/models_cache` → `models_cache/`
- `/app/test_results` → `test_results/`

## Environment Variables

Configured in docker-compose files:
- `LOG_LEVEL` - Logging level (INFO, DEBUG, WARNING)
- `PYTHONUNBUFFERED=1` - Real-time Python output
- `HF_HOME=/app/models_cache` - HuggingFace cache directory
- `HUGGINGFACE_HUB_CACHE=/app/models_cache/hub` - Hub models location
- `WHISPER_MODEL=base` - Whisper model to use
- `TEXT_GENERATION_MODEL=gpt2` - Text generation model

## Audio Support

For audio input/output to work:
```bash
# Linux: Device mapping already configured in docker-compose
device: /dev/snd:/dev/snd

# macOS/Windows: Audio forwarding via Docker Desktop
# May need additional configuration for USB audio devices
```

## Production Deployment

### Option 1: Using systemd service

```bash
# Setup (requires sudo)
sudo cp story-teller-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable story-teller-bot
sudo systemctl start story-teller-bot

# Check status
sudo systemctl status story-teller-bot

# View logs
sudo journalctl -u story-teller-bot -f
```

### Option 2: Using docker-compose

```bash
# Run in background
docker-compose -f deployment/docker-compose.yml up -d

# Check status
docker-compose -f deployment/docker-compose.yml ps

# View logs
docker-compose -f deployment/docker-compose.yml logs -f

# Stop
docker-compose -f deployment/docker-compose.yml down
```

### Option 3: Cloud deployment

```bash
# Build and push to registry
docker build -t your-registry/story-teller-bot:latest \
  -f deployment/Dockerfile .
docker push your-registry/story-teller-bot:latest

# Deploy on cloud (AWS, GCP, Azure, Kubernetes, etc.)
# Use the pushed image in your deployment configuration
```

## Troubleshooting

### Issue: Docker daemon not running
```bash
# Linux
sudo systemctl start docker

# macOS
open /Applications/Docker.app

# Windows
# Start Docker Desktop from Start menu
```

### Issue: Port already in use
```bash
# Change port in docker-compose.yml
# From: ports: - "8000:8000"
# To:   ports: - "8001:8000"
nano deployment/docker-compose.yml
docker-compose -f deployment/docker-compose.yml up -d
```

### Issue: Out of memory during build
```bash
# Use smaller models or increase Docker memory
# Docker preferences → Resources → Memory

# Or build with memory limit
docker build --memory=2g -t story-teller-bot:latest \
  -f deployment/Dockerfile .
```

### Issue: Models won't download
```bash
# Check internet connectivity
ping huggingface.co

# Check disk space
docker system df

# Try building with verbose output
docker build --progress=plain -t story-teller-bot:latest \
  -f deployment/Dockerfile .
```

## Performance

### Build Time
- First build (downloads models): 5-10 minutes
- Subsequent builds (cached): 1-2 minutes

### Image Size
- Final image: ~1.5-1.6 GB
- Breakdown:
  - Base OS: ~150 MB
  - Dependencies: ~500 MB
  - Models: ~900 MB
  - Application: ~5 MB

### Runtime
- Container startup: 2-5 seconds
- Model loading: 1-2 seconds (from cache)
- Bot ready: ~5-7 seconds total

## Advanced Usage

### Build without cache
```bash
docker build --no-cache -t story-teller-bot:latest \
  -f deployment/Dockerfile .
```

### Build for specific Python version
```bash
# Edit Dockerfile to use different base image
# FROM python:3.10-slim
docker build -t story-teller-bot:py310 \
  -f deployment/Dockerfile .
```

### Run with custom environment
```bash
docker run -it \
  -e LOG_LEVEL=DEBUG \
  -e WHISPER_MODEL=small \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/audio_output:/app/audio_output \
  --device /dev/snd:/dev/snd \
  story-teller-bot:latest
```

### Multi-platform builds
```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -t your-registry/story-teller-bot:latest \
  -f deployment/Dockerfile .
```

## CI/CD Integration

### GitHub Actions

Uses `.github/workflows/ci-cd.yml`:
1. Runs linting checks
2. Executes unit tests
3. Builds Docker image
4. Runs security scanner

Triggered on:
- Push to main/develop branches
- Pull requests to main/develop

### GitLab CI

Similar pipeline available in `.gitlab-ci.yml` if needed

## See Also

- [README.md](../README.md) - Project overview
- See [QUICKSTART.md](../doc/QUICKSTART.md) for quick start instructions
- See [DOCKER_TESTING.md](../doc/DOCKER_TESTING.md) - Detailed Docker testing guide
- See [DEVELOPMENT.md](../doc/DEVELOPMENT.md) - Development guide with setup instructions
- See [DEPLOYMENT.md](../doc/DEPLOYMENT.md) - Production deployment guide

---

**Questions?** See the main documentation files in the project root.
