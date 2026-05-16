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

### Running on Windows with pyenv-win (Native, No Docker)

For running the bot directly on Windows using [pyenv-win](https://github.com/pyenv-win/pyenv-win)
to manage the Python version. The project pins Python **3.10.11** in `.python-version`.

#### 1. Install pyenv-win

Open **PowerShell** (as your normal user, not admin) and run:

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"
&"./install-pyenv-win.ps1"
```

Close and reopen PowerShell, then verify:

```powershell
pyenv --version
```

If `pyenv` is not recognized, add these to your user `PATH` environment variable
(System Properties -> Environment Variables):

```
%USERPROFILE%\.pyenv\pyenv-win\bin
%USERPROFILE%\.pyenv\pyenv-win\shims
```

#### 2. Install Python 3.10.11

```powershell
pyenv update
pyenv install 3.10.11
```

#### 3. Clone and pin the Python version

```powershell
git clone https://github.com/YOUR_USERNAME/story-teller-bot.git
cd story-teller-bot

# .python-version already pins 3.10.11; this just confirms pyenv picks it up
pyenv local 3.10.11
python --version    # should print: Python 3.10.11
```

#### 4. Create a virtual environment and install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

# Required by spaCy NER entity extraction
python -m spacy download en_core_web_sm
```

Notes:
- `bitsandbytes` (4-bit LLM quantization) is **skipped automatically on Windows**
  via a marker in `requirements.txt`. The bot falls back to fp32 — slower but works.
- If `Activate.ps1` is blocked, allow scripts for the current user once:
  `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

#### 5. Install espeak-ng (required by Kokoro TTS)

Kokoro is the primary TTS engine and uses **espeak-ng** for English grapheme-to-phoneme.
Download the latest Windows installer from
https://github.com/espeak-ng/espeak-ng/releases and run it. Then either add
`C:\Program Files\eSpeak NG` to your `PATH`, or set this env var so the
`phonemizer` library can find the DLL:

```powershell
$env:PHONEMIZER_ESPEAK_LIBRARY = "C:\Program Files\eSpeak NG\libespeak-ng.dll"
```

If you skip this step, Kokoro will fail to initialize and the bot will fall back
to **Piper** then **pyttsx3** automatically (the chain is configured in
`config/settings.py`).

#### 6. Configure environment (optional)

Create a `.env` file in the project root to override defaults:

```env
# Use a CPU-friendly GGUF model via llama-cpp-python (recommended on Windows
# without a CUDA GPU — e.g. Intel Core Ultra). ~2 GB RAM, ~5-15s per generation.
STORY_BACKEND=llama_cpp

# Alternative: use Anthropic Claude (fastest, needs API key)
# STORY_BACKEND=anthropic
# ANTHROPIC_API_KEY=sk-ant-...

# Print every LLM call's prompt + response to stdout (debugging)
LOG_LLM_CALLS=true

# Run the critique-revise loop N times after the first draft
STORY_REFINEMENT_ROUNDS=1
```

The `llama_cpp` backend auto-downloads `Phi-3-mini-4k-instruct-q4.gguf` (~2.3 GB)
from HuggingFace on first run and caches it under
`%USERPROFILE%\.cache\huggingface\`. To use a different GGUF, set
`LLAMA_CPP_MODEL_PATH=C:\path\to\model.gguf` in `.env`.

#### 7. Run the bot

From the project root with the venv activated:

```powershell
# Interactive menu (audio / text / continue / exit)
python -m src.bot

# One-shot, non-interactive
python -m src.bot --text "a brave knight and a friendly dragon"

# Generate without speaking the result
python -m src.bot --text "a brave knight and a friendly dragon" --no-play
```

First run downloads model weights (Phi-3-mini ~2.3 GB, distil-whisper ~250 MB,
Kokoro ~330 MB) into `models_cache/` and the HuggingFace cache under
`%USERPROFILE%\.cache\huggingface`. Subsequent runs start in seconds.

#### Windows native — common gotchas

- **Microphone permission**: Windows may prompt the first time `sounddevice`
  opens the mic. Allow it under Settings -> Privacy -> Microphone.
- **WSL note**: If you are on WSL and want native audio, run from PowerShell
  using pyenv-win as above. Audio passthrough from WSL is finicky.
- **Faster startup**: Set `STORY_BACKEND=anthropic` to skip loading the
  local 3.8B-parameter LLM entirely.

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
