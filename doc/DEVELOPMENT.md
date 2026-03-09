# Development Guide

## Getting Started

### Prerequisites
- Docker & Docker Compose installed
- Git
- 4GB+ RAM
- Text editor or IDE (VS Code recommended)

### Quick Start

1. **Clone repository**:
```bash
git clone <repo-url>
cd story_teller_bot
```

2. **Start development environment**:
```bash
docker-compose -f deployment/docker-compose.yml up -d
```

3. **Verify setup**:
```bash
./scripts/test_in_container.sh
```

All dependencies are containerized!

## Development Workflow

### Running Tests

```bash
# Run tests in container (main method)
./scripts/test_in_container.sh

# Or using Docker Compose
docker-compose -f deployment/docker-compose.extended.yml run tests

# Run specific test file
docker-compose -f deployment/docker-compose.extended.yml run tests pytest tests/test_audio_handler.py -v

# View coverage
open test_results/coverage/index.html
```

### Code Quality

```bash
# Run linting in container
docker run --rm -v $(pwd):/app story-teller-bot:test flake8 src tests

# Run type checking
docker run --rm -v $(pwd):/app story-teller-bot:test mypy src --ignore-missing-imports

# Run all checks
docker run --rm -v $(pwd):/app story-teller-bot:test bash -c \
  "flake8 src tests && mypy src --ignore-missing-imports"
```

### Running the Bot

```bash
# Start with Docker Compose
docker-compose -f deployment/docker-compose.yml up -d

# View logs
docker-compose -f deployment/docker-compose.yml logs -f

# Or run interactive session
docker-compose -f deployment/docker-compose.yml exec story-teller-bot bash
```

### Editing Code

```bash
# Code is mounted as a volume - edit locally with your IDE
# Changes are immediately visible in the container

# To rebuild image after changing dependencies:
docker build --no-cache -t story-teller-bot:latest -f deployment/Dockerfile .
```

## Code Structure

### Core Modules

#### `src/audio_handler.py`
- `AudioInputHandler`: Record audio from microphone
- `AudioOutputHandler`: Play audio and text-to-speech

#### `src/speech_recognizer.py`
- `SpeechRecognizer`: Transcribe audio to text using Whisper

#### `src/story_generator.py`
- `StoryGenerator`: Generate stories based on input objects

#### `src/bot.py`
- `StoryTellerBot`: Main orchestrator combining all modules
- `BotState`: State machine for bot lifecycle

#### `config/settings.py`
- `Settings`: Configuration management using Pydantic

## Adding New Features

### 1. Add New Audio Feature

```python
# In src/audio_handler.py
class AudioOutputHandler:
    def new_feature(self, param: str) -> None:
        """Description of new feature."""
        logger.info(f"New feature called with {param}")
        # Implementation
```

### 2. Add Tests

```python
# In tests/test_audio_handler.py
def test_new_feature():
    handler = AudioOutputHandler()
    result = handler.new_feature("test")
    assert result is not None
```

### 3. Update Main Bot

Update `src/bot.py` to integrate new feature into the workflow.

## Debugging

### Enable Debug Logging

Edit `.env`:
```env
LOG_LEVEL=DEBUG
```

### View Logs

```bash
# While running
tail -f logs/story_teller_bot.log

# Docker Container
docker logs -f story_teller_bot

# Systemd Service
journalctl -u story-teller-bot -f
```

### Test Specific Component

```python
# Test audio recording
python -c "from src.audio_handler import AudioInputHandler; h = AudioInputHandler(); h.record_audio(duration=3)"

# Test speech recognition
python -c "from src.speech_recognizer import SpeechRecognizer; r = SpeechRecognizer(); text = r.transcribe_from_file('audio.wav'); print(text)"

# Test story generation
python -c "from src.story_generator import StoryGenerator; g = StoryGenerator(); story = g.generate_story_from_input('king and lion'); print(story)"
```

## Performance Optimization

### Reduce Model Size

In `config/settings.py`:
```python
WHISPER_MODEL = "tiny"  # Smaller model, faster
TEXT_GENERATION_MODEL = "distilgpt2"  # Smaller than gpt2
```

### Memory Optimization

- Cache models: `models_cache/`
- Use CPU-optimized operations
- Batch process audio if processing multiple files

## Extending Models

### Use Different Models

#### Speech Recognition
- `tiny`: 39M parameters (fastest)
- `base`: 140M parameters (default)
- `small`: 244M parameters
- `medium`: 769M parameters
- `large`: 1550M parameters

#### Text Generation
- `distilgpt2`: Lighter version of GPT-2
- `gpt2`: Standard GPT-2
- `EleutherAI/gpt-neo-125M`: Open alternative
- `EleutherAI/gpt-j-6B`: Larger model (requires more resources)

## Deployment

### Local Deployment

```bash
# Using Systemd
sudo cp deployment/story-teller-bot.service /etc/systemd/system/
sudo systemctl enable story-teller-bot
sudo systemctl start story-teller-bot
```

### Docker Deployment

```bash
# Build and push to registry
docker build -t username/story-teller-bot:latest -f deployment/Dockerfile .
docker push username/story-teller-bot:latest

# Deploy with Docker Compose (from project root)
docker-compose -f deployment/docker-compose.yml up -d

# Or with Makefile target
make docker-compose-up
```

## Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all functions
- Keep functions focused and small

### Testing Requirements

- Minimum 80% code coverage
- All public methods must have tests
- Mock external dependencies

### Commit Messages

```
feat: Add new feature description
fix: Fix bug description
docs: Update documentation
test: Add test cases
refactor: Code refactoring
```

## Troubleshooting Common Issues

### Import Errors

```bash
# Rebuild the Docker image to ensure dependencies are installed
docker build --no-cache -t story-teller-bot:latest -f deployment/Dockerfile .

# Or reinstall via Docker Compose
docker-compose -f deployment/docker-compose.yml up --build
```

### Audio Device Not Found

```bash
# List audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Check PulseAudio
pulseaudio --check && echo "Running" || echo "Not running"
```

### Model Download Failures

```bash
# Set download directory
export HF_HOME=./models_cache

# Manually download model
python -c "import whisper; whisper.load_model('base')"
```

### Memory Issues

Reduce model size or process audio in chunks:
```python
# In config/settings.py
WHISPER_MODEL = "tiny"
TEXT_GENERATION_MODEL = "distilgpt2"
```

## Resources

- [Hugging Face Models](https://huggingface.co/models)
- [Whisper Documentation](https://github.com/openai/whisper)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)
- [PyTest Documentation](https://docs.pytest.org/)
- [Docker Documentation](https://docs.docker.com/)

## Support

For issues or questions:
1. Check existing issues on GitHub
2. Review logs in `logs/`
3. Run tests to identify problems
4. Open a new issue with:
   - Python version
   - OS and version
   - Error message and logs
   - Steps to reproduce
