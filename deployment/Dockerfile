# Multi-stage build for Story Teller Bot

# Stage 1: Builder
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libsndfile1 \
    libsndfile1-dev \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download models from HuggingFace
COPY scripts/download_models.py /tmp/download_models.py
RUN mkdir -p /models_cache && \
    HF_HOME=/models_cache \
    HUGGINGFACE_HUB_CACHE=/models_cache/hub \
    python /tmp/download_models.py && \
    rm /tmp/download_models.py

# Stage 2: Runtime
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    HOME=/app \
    HF_HOME=/app/models_cache \
    HUGGINGFACE_HUB_CACHE=/app/models_cache/hub \
    TRANSFORMERS_CACHE=/app/models_cache/hub

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy pre-downloaded models from builder
COPY --from=builder /models_cache /app/models_cache

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p logs models_cache audio_output && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "from src.bot import StoryTellerBot; StoryTellerBot()" || exit 1

# Expose port for API (optional)
EXPOSE 8000

# Run the bot
CMD ["python", "-m", "src.bot"]
