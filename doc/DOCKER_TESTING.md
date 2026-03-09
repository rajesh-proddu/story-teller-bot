# Running Tests in Docker Container

## Overview

The Story Teller Bot includes comprehensive Docker-based testing infrastructure. Models are automatically downloaded from HuggingFace during the Docker build process, ensuring all dependencies are pre-configured.

## Quick Start

### Option 1: Using Test Script (Recommended)

```bash
# Run tests in Docker container
./scripts/test_in_container.sh

# Build test image only (don't run tests)
./scripts/test_in_container.sh --build-only

# Keep container running after tests
./scripts/test_in_container.sh --keep
```

### Option 2: Using Docker Compose

```bash
# Run tests with extended compose file
docker-compose -f docker-compose.extended.yml run tests

# Start both bot and test services
docker-compose -f docker-compose.extended.yml up
```

### Option 3: Direct Docker Commands

```bash
# Build test image with models pre-downloaded
docker build -t story-teller-bot:test -f Dockerfile.test .

# Run tests
docker run -it \
  -v $(pwd)/test_results:/app/test_results \
  -v $(pwd)/models_cache:/app/models_cache \
  story-teller-bot:test

# Run specific test file
docker run -it story-teller-bot:test pytest tests/test_bot.py -v

# Run with coverage
docker run -it story-teller-bot:test \
  pytest tests/ -v --cov=src --cov-report=html
```

## Model Download Strategy

### During Build Time

Models are downloaded automatically when building the image:

```dockerfile
# In deployment/Dockerfile (Build Stage)
RUN python scripts/download_models.py
```

**Models Downloaded:**
- **Whisper Base** (~140MB) - Speech recognition
- **GPT-2** (~540MB) - Story generation  
- **DistilGPT-2** (~160MB) - Smaller alternative

### Cache Management

```
Image Structure:
├── /app/models_cache/
│   ├── hub/
│   │   ├── models--openai--whisper-base/
│   │   ├── models--gpt2/
│   │   └── models--distilgpt2/
│   └── [other HuggingFace artifacts]
```

### Runtime Environment

```bash
# Container environment variables for model caching
HF_HOME=/app/models_cache
HUGGINGFACE_HUB_CACHE=/app/models_cache/hub
TRANSFORMERS_CACHE=/app/models_cache/hub
```

## Docker Files Included

### Dockerfile (Main)
- Multi-stage build for production
- Optimized size
- Models pre-downloaded
- Non-root user
- Health checks

### Dockerfile.test
- Includes pytest and test tools
- Larger image (development focused)
- Models pre-downloaded
- Test coverage reporting

## Test Execution Details

### What Gets Tested

```
Unit Tests:
✓ Audio handler - Recording, playback, controls
✓ Speech recognizer - Model loading, transcription
✓ Story generator - Object extraction, story generation
✓ Bot orchestrator - State machine, workflow

Test Coverage:
- 29+ test cases
- 80%+ code coverage
- Mock-based dependency testing
- Error path testing
```

### Test Output

Tests generate multiple reports:

```
test_results/
├── coverage/
│   ├── index.html          # Coverage report (open in browser)
│   ├── status.json
│   └── [detailed coverage files]
├── junit.xml               # Test results XML
└── [test logs]
```

## Environment Configuration

### Build-Time Environment

```dockerfile
ENV HF_HOME=/models_cache \
    HUGGINGFACE_HUB_CACHE=/models_cache/hub \
    TRANSFORMERS_CACHE=/models_cache/hub
```

### Runtime Environment

```bash
# In docker-compose.yml or command line
environment:
  - HF_HOME=/app/models_cache
  - HUGGINGFACE_HUB_CACHE=/app/models_cache/hub
  - TRANSFORMERS_CACHE=/app/models_cache/hub
  - LOG_LEVEL=INFO
```

## Volume Management

### Docker Compose Volumes

```yaml
volumes:
  - ./logs:/app/logs              # Persistent logs
  - ./audio_output:/app/audio_output    # Generated audio
  - ./models_cache:/app/models_cache    # Downloaded models
  - ./test_results:/app/test_results    # Test reports
```

### Sharing Models Between Runs

```bash
# First build (downloads models)
docker build -t story-teller-bot:test -f Dockerfile.test .

# Subsequent runs reuse cached models
docker run -v $(pwd)/models_cache:/app/models_cache story-teller-bot:test
```

## Troubleshooting

### Issue: "Model download failed"

```bash
# Check internet connection
ping huggingface.co

# Manually build with verbose output
docker build -t story-teller-bot:test -f Dockerfile.test . --progress=plain

# Pre-download models locally
python scripts/download_models.py
```

### Issue: "Out of disk space"

Models cache can be ~1GB. If space is limited:

```bash
# Use smaller models
# Edit config/settings.py or .env:
WHISPER_MODEL=tiny        # 39MB instead of 140MB
TEXT_GENERATION_MODEL=distilgpt2  # 160MB instead of 540MB
```

### Issue: "Test container exits immediately"

```bash
# Check container logs
docker logs <container_name>

# Run in interactive mode
docker run -it story-teller-bot:test /bin/bash

# Check models were downloaded
docker run story-teller-bot:test ls -la /app/models_cache
```

## Performance Optimization

### Image Building

```bash
# Build with BuildKit for better caching
DOCKER_BUILDKIT=1 docker build -t story-teller-bot:test -f Dockerfile.test .

# Use build cache
docker build --cache-from story-teller-bot:test -f Dockerfile.test .
```

### Test Execution

```bash
# Run tests in parallel (if supported)
docker run story-teller-bot:test pytest tests/ -n auto

# Run specific test module only
docker run story-teller-bot:test pytest tests/test_bot.py -v
```

### Model Caching

```bash
# Check what models are cached
docker run story-teller-bot:test find /app/models_cache -type d

# Verify model files
docker run story-teller-bot:test du -sh /app/models_cache/*
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build test image
        run: docker build -t story-teller-bot:test -f deployment/Dockerfile.test .
      
      - name: Run tests
        run: |
          docker run -v $(pwd)/test_results:/app/test_results \
            story-teller-bot:test
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          files: ./test_results/coverage.xml
```

### GitLab CI Example

```yaml
test:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t story-teller-bot:test -f deployment/Dockerfile.test .
    - docker run -v $CI_PROJECT_DIR/test_results:/app/test_results story-teller-bot:test
  artifacts:
    paths:
      - test_results/
```

## Advanced Usage

### Running Tests with Different Python Versions

```dockerfile
# deployment/Dockerfile.test-py310
FROM python:3.10-slim
# ... rest of Dockerfile
```

```bash
docker build -t story-teller-bot:test-py310 -f deployment/Dockerfile.test-py310 .
docker run story-teller-bot:test-py310
```

### Testing with Smaller Models

```bash
docker run \
  -e WHISPER_MODEL=tiny \
  -e TEXT_GENERATION_MODEL=distilgpt2 \
  story-teller-bot:test
```

### Interactive Testing

```bash
# Enter container for manual testing
docker run -it --entrypoint /bin/bash story-teller-bot:test

# Inside container:
$ pytest tests/test_bot.py -v --pdb  # Run with debugger
$ python -m src.bot                   # Test bot directly
$ python scripts/download_models.py   # Re-download models
```

## Best Practices

✅ **Do:**
- Use volumes to persist model cache between runs
- Run tests in CI/CD pipeline
- Keep separate test and production images
- Build images locally before pushing
- Use specific model versions in production

❌ **Don't:**
- Build models into production image if they change
- Run tests without using volumes (loses results)
- Use root user in containers
- Commit large model files to git

## Model Update Instructions

### Updating Models

```bash
# Remove cached models
rm -rf models_cache/

# Rebuild image with new models
DOCKER_BUILDKIT=1 docker build --no-cache -t story-teller-bot:test -f Dockerfile.test .

# Verify new models
docker run story-teller-bot:test ls -la /app/models_cache/hub/
```

### Switching Model Versions

Edit `scripts/download_models.py`:

```python
models_to_download = [
    {
        'name': 'Whisper Small (larger model)',
        'download_fn': lambda: whisper.load_model("small", ...)
    },
    # ...
]
```

Then rebuild the image.

## Documentation References

- [Docker Documentation](https://docs.docker.com/)
- [HuggingFace Model Hub](https://huggingface.co/models)
- [Whisper Model Documentation](https://github.com/openai/whisper)
- [Transformers Library](https://huggingface.co/docs/transformers/)

## Support

For issues running tests in containers:
1. Check logs: `docker logs <container_name>`
2. Verify models: `docker run story-teller-bot:test python -c "import whisper, transformers"`
3. Check disk space: `docker exec <container_name> df -h`
4. Review this guide
5. Open an issue on GitHub

---

**Next Steps:**
- Run tests: `./scripts/test_in_container.sh`
- View coverage: Open `test_results/coverage/index.html`
- Deploy: `docker-compose -f deployment/docker-compose.yml up -d`
