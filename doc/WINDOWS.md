# Windows Installation Guide

## Prerequisites

### 1. Install Docker Desktop

1. Download from https://www.docker.com/products/docker-desktop
2. Run installer and follow prompts
3. Restart your computer
4. Verify installation:
   ```cmd
   docker --version
   docker-compose --version
   ```

### 2. Install Git

1. Download from https://git-scm.com/download/win
2. Use default options
3. Verify:
   ```cmd
   git --version
   ```

### 3. Audio Setup (Optional)

For audio input/output:
- Ensure microphone and speakers/headphones connected
- Test audio in Windows Settings → Sound
- Docker Desktop will handle audio passthrough

## Installation Steps

### Option 1: Docker Desktop (Recommended)

1. **Ensure Docker Desktop is running**:
   - Click Docker icon in system tray
   - Verify it shows "Docker Desktop is running"

2. **Clone project**:
   ```cmd
   git clone https://github.com/YOUR_USERNAME/story_teller_bot.git
   cd story_teller_bot
   ```

3. **Build the bot**:
   ```cmd
   docker build -t story-teller-bot:latest -f deployment/Dockerfile .
   ```

4. **Run with Docker Compose**:
   ```cmd
   docker-compose -f deployment/docker-compose.yml up
   ```

   Or manually with docker run:
   ```cmd
   docker run -it --device=/dev/snd story-teller-bot:latest
   ```

### Option 2: Using WSL2 + Docker

For best compatibility with WSL2:

1. **Enable WSL2**:
   ```cmd
   wsl --install
   # Restart computer
   ```

2. **Install Ubuntu**:
   ```cmd
   wsl --install -d Ubuntu
   ```

3. **Setup Docker in WSL**:
   ```bash
   # In WSL terminal
   sudo apt update
   sudo apt install docker.io docker-compose
   ```

4. **Clone and setup**:
   ```bash
   cd ~/projects
   git clone https://github.com/YOUR_USERNAME/story_teller_bot.git
   cd story_teller_bot
   
   # Build and run
   docker-compose -f deployment/docker-compose.yml up
   ```

### Option 3: Quick Start with Docker Compose

Fastest way to get running:

```cmd
# Clone
git clone https://github.com/YOUR_USERNAME/story_teller_bot.git
cd story_teller_bot

# Build and run (all in one)
docker-compose -f deployment/docker-compose.yml up --build
```

The bot will be running in a container with all dependencies already installed!

## Troubleshooting (Windows)

### Issue: Docker not running

```cmd
# Start Docker Desktop
# Click the Docker icon in system tray, or run:
"C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### Issue: Docker Compose error

```cmd
# Ensure Docker is fully started (may take a minute)
# Verify installation:
docker-compose --version

# If not found, reinstall Docker Desktop or upgrade
```

### Issue: Container won't start

```cmd
# Check logs:
docker-compose -f deployment/docker-compose.yml logs

# Rebuild without cache:
docker build --no-cache -t story-teller-bot:latest -f deployment/Dockerfile .
```

### Issue: Audio not working in Docker

1. Ensure speakers/microphone connected
2. Check Windows Sound Settings
3. In Docker Desktop:
   - Settings → Resources → File Sharing → ensure project added
   - Restart Docker

### Issue: Port already in use

If port 5000 is already in use:
```cmd
# Edit deployment/docker-compose.yml:
# Change "5000:5000" to "5001:5000" for a different port
```

### Issue: Out of memory

Docker containers may need more memory:
1. Open Docker Desktop Settings
2. Go to Resources
3. Increase available memory (e.g., 4GB → 8GB)
4. Restart Docker

## Using PowerShell

### Docker Compose from PowerShell

Running commands via PowerShell:

```powershell
# Start the bot
docker-compose -f deployment/docker-compose.yml up

# Start in background
docker-compose -f deployment/docker-compose.yml up -d

# Run tests
docker-compose -f deployment/docker-compose.yml exec story-teller-bot pytest tests/ -v

# Run linting
docker-compose -f deployment/docker-compose.yml exec story-teller-bot flake8 src

# Stop the bot
docker-compose -f deployment/docker-compose.yml down
```

## IDE Setup

### Visual Studio Code (Recommended)

1. **Install Extensions**:
   - Docker (Microsoft)
   - Dev Containers (Microsoft)
   - Python (Microsoft) - optional, for editing
   - Remote - Containers (Microsoft) - optional

2. **Open Project in Container**:
   - Click Remote icon (bottom-left corner)
   - Select "Reopen in Container"
   - VS Code will develop inside the container

3. **Or run in terminal**:
   ```cmd
   docker-compose -f deployment/docker-compose.yml up
   ```

### PyCharm

1. **Install PyCharm**:
   - Community Edition is free
   - Download from https://www.jetbrains.com/pycharm/

2. **Configure Docker as Interpreter**:
   - File → Settings → Project → Python Interpreter
   - Click ⚙️ → Add
   - Select "Docker Compose"
   - Set service: `story-teller-bot`

3. **Run**:
   - Right-click `src/bot.py`
   - Select "Run" (will execute in container)

## Command Reference (Windows)

### Docker Compose

```cmd
# Start bot
docker-compose -f deployment/docker-compose.yml up

# Start in background
docker-compose -f deployment/docker-compose.yml up -d

# Stop bot
docker-compose -f deployment/docker-compose.yml down

# View logs
docker-compose -f deployment/docker-compose.yml logs

# Rebuild image
docker build --no-cache -t story-teller-bot:latest -f deployment/Dockerfile .
```

### Running Commands in Container

```cmd
# Run tests
docker-compose -f deployment/docker-compose.yml exec story-teller-bot pytest tests/ -v

# Run linting
docker-compose -f deployment/docker-compose.yml exec story-teller-bot flake8 src

# Interactive shell
docker-compose -f deployment/docker-compose.yml exec story-teller-bot bash
```

### Git

```cmd
# Clone
git clone <repository-url>

# Add changes
git add .

# Commit
git commit -m "message"

# Push
git push origin main
```

## Performance Tips

- **Use Docker Desktop** for seamless Windows integration
- **Allocate sufficient resources**:
  - Minimum: 2 CPU cores, 2GB memory
  - Recommended: 4 CPU cores, 4-8GB memory
- **Models cache**: Docker volume stores downloaded models for reuse
- **WSL2 backend**: For better performance, Docker Desktop uses WSL2

## Getting Help

1. Check project [README.md](../README.md)
2. Read [DEVELOPMENT.md](DEVELOPMENT.md) for debugging
3. Check Docker logs: `docker-compose -f deployment/docker-compose.yml logs`
4. Check container shell:
   ```cmd
   docker-compose -f deployment/docker-compose.yml exec story-teller-bot bash
   ```
5. Open GitHub issue if stuck

## Next Steps

1. Complete installation using your chosen method
2. Read [QUICKSTART.md](QUICKSTART.md)
3. Read [README.md](../README.md)
4. Try running the bot!

---

**Happy storytelling on Windows! 🎭🚀**
