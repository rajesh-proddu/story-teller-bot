# Quick Start Guide

## System Requirements

- **Docker**: Latest version installed and running
- **Docker Compose**: Latest version
- **OS**: Linux, macOS, or Windows (with Docker Desktop)
- **RAM**: 4GB minimum (8GB+ recommended)
- **Disk**: 2GB for Docker image and logs
- **Audio** (optional): Microphone and speaker for audio mode

## Installation (Docker - Recommended)

### Option 1: Docker Compose (Easiest)

```bash
# From project root
docker-compose -f deployment/docker-compose.yml up -d

# View logs
docker-compose -f deployment/docker-compose.yml logs -f

# Stop
docker-compose -f deployment/docker-compose.yml down
```

### Option 2: Direct Docker

```bash
# Build image
docker build -t story-teller-bot:latest -f deployment/Dockerfile .

# Run container
docker run -it \
  -v $(pwd)/audio_output:/app/audio_output \
  --device /dev/snd:/dev/snd \
  story-teller-bot:latest
```

### Option 3: Using Convenience Script

```bash
# Build and run the image
make docker-compose-up

# View logs
make docker-compose-logs

# Stop
make docker-compose-down
```

## First Run

1. **Choose input mode**:
   - Option 1: Audio Input (speak your requirements)
   - Option 2: Text Input (type your requirements)

2. **Describe your story**:
   - Example: "Tell me a story with a brave knight and a magic sword"
   - Be clear and descriptive

3. **Listen to your story**:
   - The bot will generate and narrate a unique story
   - Use pause/stop controls if needed

## Common Commands

### Running & Managing the Bot

```bash
# Start the bot
docker-compose -f deployment/docker-compose.yml up -d

# View logs
docker-compose -f deployment/docker-compose.yml logs -f

# Stop the bot
docker-compose -f deployment/docker-compose.yml down

# Run interactive shell in container
docker-compose -f deployment/docker-compose.yml exec story-teller-bot bash
```

### Testing & Quality

```bash
# Run tests in container
./scripts/test_in_container.sh

# Run tests with Docker Compose
docker-compose -f deployment/docker-compose.extended.yml run tests

# View test coverage
open test_results/coverage/index.html
```

### Building & Images

```bash
# Build fresh image (no cache)
docker build --no-cache -t story-teller-bot:latest -f deployment/Dockerfile .

# List Docker images
docker images | grep story-teller

# Remove old images
docker system prune
```

## Troubleshooting

### Docker container won't start

```bash
# Check Docker is running
docker ps

# Check container logs
docker-compose -f deployment/docker-compose.yml logs story-teller-bot

# Rebuild the image
docker build --no-cache -t story-teller-bot:latest -f deployment/Dockerfile .
```

### Audio device not found

```bash
# Check available devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# For Linux, ensure ALSA is working
alsamixer
```

### Out of memory

```bash
# Use smaller models in config/settings.py
WHISPER_MODEL="tiny"
TEXT_GENERATION_MODEL="distilgpt2"
```

### Models not downloading

```bash
# Check internet connection
# Manually trigger download:
python -c "import whisper; whisper.load_model('base')"
```

## Next Steps

1. **Read Documentation**:
   - [README.md](../README.md) - Overview
   - [DEVELOPMENT.md](DEVELOPMENT.md) - Developer guide
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [GITHUB_SETUP.md](GITHUB_SETUP.md) - Git setup

2. **Customize**:
   - Edit `.env` for settings
   - Explore `config/settings.py` for advanced options
   - Try different models

3. **Integrate**:
   - Use Systemd for auto-start
   - Deploy with Docker
   - Create REST API (advanced)

4. **Extend**:
   - Add new features
   - Improve story generation
   - Support more languages

## Getting Help

- Check [DEVELOPMENT.md](DEVELOPMENT.md) for debugging
- Review logs in `logs/story_teller_bot.log`
- Open an issue on GitHub

## Tips & Tricks

✨ **Pro Tips**:
- Use descriptive inputs for better stories
- Try different Whisper model sizes for balance
- Adjust temperature in settings for more/less creativity
- Store favorite stories in `audio_output/`
- Check logs to understand what's happening

🎯 **Story Ideas**:
- "Adventures with a pirate and a treasure map"
- "Fantasy realm with dragons and knights"
- "Magical forest with talking animals"
- "Space journey with aliens and robots"

---

**Enjoy storytelling with AI! 🎭✨**
