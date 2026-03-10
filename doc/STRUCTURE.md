# Project Directory Structure

```
story_teller_bot/
│
├── 📄 Core Documentation
│   ├── README.md                      # Main project overview and guide
│   ├── PROJECT_COMPLETION.md          # Comprehensive completion summary
│   ├── QUICKSTART.md                  # Quick start guide (3 methods)
│   ├── ARCHITECTURE.md                # System design and architecture
│   ├── DEVELOPMENT.md                 # Developer guide and best practices
│   ├── WINDOWS.md                     # Windows-specific setup guide
│   ├── GITHUB_SETUP.md                # GitHub repository setup guide
│   └── prd.md                         # Original product requirements document
│
├── 🐍 Source Code (src/)
│   ├── __init__.py
│   ├── bot.py                         # Main orchestrator and state machine
│   ├── audio_handler.py               # Audio input/output handling
│   ├── speech_recognizer.py           # Speech-to-text (Whisper)
│   └── story_generator.py             # Story generation (transformers/GPT-2)
│
├── 🧪 Test Suite (tests/)
│   ├── __init__.py
│   ├── test_audio_handler.py          # Audio handler tests
│   ├── test_speech_recognizer.py      # Speech recognizer tests
│   ├── test_story_generator.py        # Story generator tests
│   └── test_bot.py                    # Main bot tests
│
├── ⚙️ Configuration (config/)
│   ├── __init__.py
│   └── settings.py                    # Pydantic-based settings
│
├── 🚀 Deployment (deployment/)
│   ├── setup.sh                       # Automated setup script
│   └── story-teller-bot.service       # Systemd service file
│
├── 🐳 Docker & Containerization
│   ├── Dockerfile                     # Multi-stage Docker build
│   ├── docker-compose.yml             # Docker Compose orchestration
│   └── .dockerignore                  # Docker build exclusions
│
├── 🔧 Build & Automation
│   ├── Makefile                       # Task automation (make)
│   ├── pytest.ini                     # Pytest configuration
│   ├── .gitignore                     # Git exclusions
│   └── .env.example                   # Environment template
│
├── 📋 CI/CD Pipeline
│   └── .github/workflows/
│       └── ci-cd.yml                  # GitHub Actions workflow
│
├── 📦 Dependencies
│   └── requirements.txt                # Python package list
│
└── 🛠️ Scripts
    └── run.sh                         # Production container manager
```

## Directory Descriptions

### 📄 Documentation
- **README.md**: Start here for complete overview
- **PROJECT_COMPLETION.md**: Summary of what was created
- **QUICKSTART.md**: Get running in 5 minutes
- **ARCHITECTURE.md**: Deep dive into system design
- **DEVELOPMENT.md**: For developers and contributors
- **WINDOWS.md**: Windows-specific instructions
- **GITHUB_SETUP.md**: Repository management guide

### 🐍 Source Code
```
src/
├── bot.py                  # Main entry point (188 lines)
│   └── Class: StoryTellerBot
│       ├── start()
│       ├── _interactive_story_mode()
│       ├── _text_input_mode()
│       └── _play_story()
│
├── audio_handler.py        # Audio I/O (168 lines)
│   ├── Class: AudioInputHandler
│   │   ├── record_audio()
│   │   ├── save_audio()
│   │   └── stop_recording()
│   └── Class: AudioOutputHandler
│       ├── speak()
│       ├── play_audio()
│       └── stop_playback()
│
├── speech_recognizer.py    # Speech-to-text (90 lines)
│   └── Class: SpeechRecognizer
│       ├── transcribe()
│       └── transcribe_from_file()
│
└── story_generator.py      # Story generation (196 lines)
    └── Class: StoryGenerator
        ├── extract_objects()
        ├── generate_story()
        └── generate_story_from_input()
```

### 🧪 Test Suite
```
tests/
├── test_audio_handler.py       # 92 lines, 15 test cases
├── test_speech_recognizer.py   # 67 lines, 10 test cases
├── test_story_generator.py     # 101 lines, 12 test cases
└── test_bot.py                 # 46 lines, 3 test cases
Total: ~320 lines, 40+ test cases
```

### ⚙️ Configuration
```
config/
├── settings.py                 # Pydantic BaseSettings
│   └── class: Settings
│       ├── Audio config (rate, duration, channels)
│       ├── Model config (whisper, gpt2)
│       ├── Story config (length, temperature)
│       └── Logging config (level, format)
└── Environment variables from .env
```

### 🚀 Deployment
```
deployment/
├── setup.sh                    # Complete environment setup
│   ├── Python version check
│   ├── Virtual environment creation
│   ├── Dependency installation
│   ├── Model downloading
│   └── Directory initialization
│
└── story-teller-bot.service   # Systemd service
    ├── Auto-start on boot
    ├── Automatic restart
    ├── Logging to journalctl
    └── Security hardening
```

### 🐳 Containerization
```
Docker Setup:
├── Dockerfile                  # Multi-stage build
│   ├── Builder stage (compilation)
│   └── Runtime stage (optimized)
│
├── docker-compose.yml          # Orchestration
│   ├── Service configuration
│   ├── Volume management
│   ├── Device mapping
│   └── Health checks
│
└── .dockerignore              # Build optimization
```

### 🔧 Tools & Config
```
Build/Test Tools:
├── Makefile                    # 100+ lines of tasks
│   ├── setup, install, test
│   ├── lint, format
│   ├── docker, docker-compose
│   └── run
│
├── pytest.ini                  # Test discovery patterns
│   ├── Test paths
│   ├── Markers
│   └── Output options
│
├── requirements.txt            # 20 packages
│   ├── Core: transformers, whisper
│   ├── Audio: sounddevice, soundfile
│   ├── ML: torch, numpy
│   ├── Testing: pytest
│   └── Dev: black, flake8, mypy
│
├── .gitignore                  # 50+ exclusions
├── .env.example               # Configuration template
└── .dockerignore              # Docker exclusions
```

### 📋 CI/CD
```
.github/workflows/
└── ci-cd.yml                   # GitHub Actions
    ├── Test (Python 3.8-3.11)
    ├── Lint (flake8)
    ├── Type check (mypy)
    ├── Coverage report
    ├── Docker build
    └── Security scan (Trivy)
```

---

## File Statistics

### Code Files
- **Source Code**: 542 lines across 5 modules
- **Test Code**: 306 lines across 4 test files
- **Configuration**: 74 lines
- **Scripts**: 165 lines (setup + run)
- **Total Code**: ~1,087 lines

### Documentation Files
- **README.md**: ~400 lines
- **ARCHITECTURE.md**: ~450 lines
- **DEVELOPMENT.md**: ~350 lines
- **Windows.md**: ~300 lines
- **QUICKSTART.md**: ~150 lines
- **GITHUB_SETUP.md**: ~250 lines
- **PROJECT_COMPLETION.md**: ~300 lines
- **Total Documentation**: ~2,200 lines

### Configuration Files
- **Docker Files**: ~100 lines
- **GitHub Actions**: ~65 lines
- **Makefile**: ~100 lines
- **Config Code**: ~74 lines
- **Total Config**: ~339 lines

### Grand Total
- **All Files**: ~3,626 lines of content
- **Python Code**: 922 lines
- **Tests**: 306 lines
- **Configuration**: 339 lines
- **Documentation**: 2,200 lines
- **Scripts**: 165 lines

---

## Getting Started from Here

### Step 1: Choose Your Setup Method
```
Option 1: Setup + Manager → ./deployment/setup.sh → ./run.sh start
Option 2: Docker Compose  → docker-compose -f deployment/docker-compose.yml up
Option 3: Manual          → Read QUICKSTART.md
Option 4: Windows         → Read WINDOWS.md
```

### Step 2: Choose Your Reading Path
```
Beginner     → QUICKSTART.md → README.md
Developer    → DEVELOPMENT.md → ARCHITECTURE.md
Deployer     → deployment/ → GITHUB_SETUP.md
Windows User → WINDOWS.md → Others
```

### Step 3: Verify Installation
```bash
# Run tests
docker-compose -f deployment/docker-compose.yml exec story-teller-bot pytest tests/

# Start bot
./run.sh start

# View logs
./run.sh logs
```

---

## Key File Locations

| Need | File |
|------|------|
| Quick setup | QUICKSTART.md |
| Windows setup | WINDOWS.md |
| Full docs | README.md |
| How it works | ARCHITECTURE.md |
| Development | DEVELOPMENT.md |
| GitHub setup | GITHUB_SETUP.md |
| Completion summary | PROJECT_COMPLETION.md |
| Run bot | `./run.sh start` |
| Stop bot | `./run.sh stop` |
| Run tests | `docker-compose exec ... pytest` |
| View logs | `./run.sh logs` |
| Settings | config/settings.py or .env |
| Deploy | deployment/setup.sh |
The deployment folder contains all Docker and production deployment configuration:

```
deployment/
├── Dockerfile              # Production image with model pre-caching
├── Dockerfile.test         # Test image with pytest and coverage
├── docker-compose.yml      # Main orchestration (run from project root)
├── docker-compose.extended.yml  # Testing orchestration
├── setup.sh                # Host system setup script
├── story-teller-bot.service # Systemd service for Linux
└── README.md               # Deployment guide and instructions
```

### How to Use

All docker-compose commands are run from the **project root** with `-f deployment/...`:

```bash
# From project root
docker-compose -f deployment/docker-compose.yml up -d
docker-compose -f deployment/docker-compose.yml logs -f
docker-compose -f deployment/docker-compose.yml down
```

Or run from the deployment directory:

```bash
cd deployment
docker-compose up -d
docker-compose logs -f
docker-compose down
```

Build context in docker-compose automatically resolves to the project root, allowing Docker to access all source code and dependencies.

---

## Project Health Checklist

✅ Code Quality:
- Type hints throughout
- Docstrings for all functions
- Error handling
- Logging integrated

✅ Testing:
- Unit tests for all modules
- Mock-based testing
- Ready for 80%+ coverage

✅ Documentation:
- User guide (README)
- Developer guide (DEVELOPMENT)
- Architecture document
- Quick start guide
- Windows specific guide
- GitHub setup guide
- Completion summary

✅ Deployment:
- Virtual environment setup
- Systemd service
- Docker container
- Docker Compose
- GitHub Actions CI/CD

✅ Production Ready:
- Error handling
- Configuration management
- Logging
- Security
- Performance
- Scalability

---

**Next: Read QUICKSTART.md to get started! 🚀**
