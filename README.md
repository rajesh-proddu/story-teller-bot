# Story Teller Bot 🎭

An AI-powered storytelling bot for kids that accepts audio input and generates creative stories with user-specified characters and objects, then narrates them back using text-to-speech.

## Features ✨

- **Audio Input**: Kids can speak their story requirements in audio format
- **AI Story Generation**: Generates creative stories based on user input using transformer models
- **Audio Output**: Narrates generated stories using text-to-speech
- **Playback Controls**: Pause and stop controls during story playback
- **Open Source**: Built entirely with open-source models and libraries
- **Production Ready**: Follows Python best practices, includes comprehensive tests and deployment scripts
- **Containerized**: Full Docker support for easy deployment anywhere
- **Local Execution**: Runs entirely on local machine with no cloud dependencies

## Requirements

- Python 3.8+
- 4GB+ RAM recommended
- Audio input/output device (microphone and speaker)
- Linux/macOS/Windows with Linux subsystem

## Installation

### Quick Start (Recommended - Docker)

The easiest way to get started is with Docker:

```bash
# From project root
docker-compose -f deployment/docker-compose.yml up -d
```

This will:
- Build the Docker image with all dependencies
- Pre-download required ML models (Whisper, GPT-2)
- Start the bot container
- Create necessary directories

That's it! The bot is ready to use.

## Usage

### Running the Bot with Docker (Recommended)

```bash
# View logs
docker-compose -f deployment/docker-compose.yml logs -f story-teller-bot

# Stop the bot
docker-compose -f deployment/docker-compose.yml down

# Run tests
./scripts/test_in_container.sh
```

### Interactive Modes

#### 1. Audio Input Mode
- Select option 1 from the menu
- Speak your story requirements clearly
- The bot will transcribe, generate, and narrate the story

#### 2. Text Input Mode
- Select option 2 from the menu
- Type your story requirements
- The bot will generate and narrate the story

### Example Inputs

- "Tell me a story with a brave knight and a dragon"
- "I want a story about a princess, a unicorn, and a magical castle"
- "Story with a funny rabbit and a wise owl in the forest"

## Project Structure

```
story_teller_bot/
├── src/                          # Source code
│   ├── __init__.py
│   ├── audio_handler.py         # Audio input/output handling
│   ├── speech_recognizer.py     # Speech-to-text (Whisper)
│   ├── story_generator.py       # Story generation (GPT-2)
│   └── bot.py                   # Main bot orchestrator
├── config/                       # Configuration
│   ├── __init__.py
│   └── settings.py              # Settings and environment config
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_audio_handler.py
│   ├── test_speech_recognizer.py
│   ├── test_story_generator.py
│   └── test_bot.py
├── deployment/                   # Deployment scripts
│   ├── setup.sh                 # Setup script
│   └── story-teller-bot.service # Systemd service
├── deployment/                    # Deployment configuration
│   ├── Dockerfile                 # Docker containerization
│   ├── Dockerfile.test            # Test image definition
│   ├── docker-compose.yml         # Docker Compose orchestration
│   ├── docker-compose.extended.yml# Extended compose (with tests)
│   ├── setup.sh                   # Production setup script
│   ├── story-teller-bot.service   # Systemd service
│   └── README.md                  # Deployment guide
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── doc/                         # Documentation
    ├── QUICKSTART.md            # Quick start guide
    ├── ARCHITECTURE.md          # System architecture
    ├── DEVELOPMENT.md           # Development guide
    ├── prd.md                   # Product requirements document
```

## Configuration

### Environment Variables (.env)

```env
LOG_LEVEL=INFO
SAMPLE_RATE=16000
AUDIO_DURATION_SECONDS=30
WHISPER_MODEL=base
TEXT_GENERATION_MODEL=gpt2
TTS_ENGINE=pyttsx3
```

### Adjusting Settings

Edit `config/settings.py` to customize:
- Audio sample rate and duration
- Model choices (Whisper model size, text generation model)
- Story generation parameters (temperature, length)
- Logging levels

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Suite

```bash
pytest tests/test_audio_handler.py -v
pytest tests/test_story_generator.py -v
pytest tests/test_speech_recognizer.py -v
pytest tests/test_bot.py -v
```

### Generate Coverage Report

```bash
pytest tests/ --cov=src --cov-report=html
```

## Deployment

### Systemd Service (Linux)

1. Copy service file:
```bash
sudo cp deployment/story-teller-bot.service /etc/systemd/system/
```

2. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable story-teller-bot
sudo systemctl start story-teller-bot
```

3. Check status:
```bash
sudo systemctl status story-teller-bot
```

4. View logs:
```bash
journalctl -u story-teller-bot -f
```

### Docker Deployment

#### Build Image

```bash
docker build -t story-teller-bot:latest .
```

#### Run Container

```bash
docker run -it --device /dev/snd story-teller-bot:latest
```

#### Using Docker Compose

```bash
docker-compose up -d
```

Check logs:
```bash
docker-compose logs -f story-teller-bot
```

Stop:
```bash
docker-compose down
```

## Models Used

### Speech Recognition
- **Whisper (OpenAI)**: Robust multilingual speech-to-text
- Model size: `base` (140M parameters)
- Available sizes: `tiny`, `base`, `small`, `medium`, `large`

### Story Generation
- **GPT-2 (OpenAI)**: Text generation for creative storytelling
- Alternative models: DistilGPT-2 (smaller), GPT-Neo (larger)

### Text-to-Speech
- **pyttsx3**: Cross-platform TTS engine
- Works offline without API calls

## Architecture

```
User Input (Audio) 
    ↓
[AudioInputHandler] - Records audio from microphone
    ↓
[SpeechRecognizer] - Transcribes audio to text using Whisper
    ↓
[StoryGenerator] - Extracts objects and generates story using GPT-2
    ↓
[AudioOutputHandler] - Converts story to speech and plays audio
    ↓
User Output (Audio Story)
```

## Best Practices Implemented

✅ **Code Quality**
- Type hints throughout
- Comprehensive docstrings
- Modular, single-responsibility functions
- Error handling and logging

✅ **Testing**
- Unit tests for all modules
- Mock-based testing for external dependencies
- Pytest framework with fixtures

✅ **Configuration**
- Environment-based settings
- Pydantic for validation
- Configurable parameters

✅ **Logging**
- Structured logging with loguru
- Log rotation and management
- File and console output

✅ **Security**
- Non-root Docker user
- Environment variable management
- No hardcoded secrets

✅ **Performance**
- Model caching
- Efficient memory usage
- CPU-optimized (no GPU required)

## Troubleshooting

### Audio Issues
- Ensure microphone is working in Docker: `--device /dev/snd:/dev/snd`
- Check volume levels inside container
- For WSL2: Enable USB audio passthrough

### Docker Issues
- Ensure Docker daemon is running
- Check container logs: `docker-compose -f deployment/docker-compose.yml logs story-teller-bot`
- Rebuild image: `docker build --no-cache -t story-teller-bot:latest -f deployment/Dockerfile .`

### Model Download Issues
- Check internet connection in container
- Rebuild with fresh models: `docker build --no-cache -t story-teller-bot:latest -f deployment/Dockerfile .`
- Verify disk space: models need ~2GB

### Memory Issues
- Increase Docker memory allocation
- Use smaller model: Edit `scripts/download_models.py` to use `tiny` Whisper
- Reduce model size in docker-compose environment variables
- Reinstall dependencies: `pip install -r requirements.txt`

## Contributing

Feel free to fork, modify, and improve this project. Suggested areas:
- Add more language support
- Implement streaming audio
- Add web UI
- Optimize for ARM devices
- Add story history/persistence

## License

MIT License - See LICENSE file

## Contact

For issues, questions, or suggestions, please open an issue in the repository.

---

**Enjoy storytelling with AI! 🚀📖✨**
