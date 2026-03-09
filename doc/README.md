# Documentation

This folder contains all the project documentation files organized for easy navigation.

## Getting Started

| File | Purpose | Best For |
|------|---------|----------|
| [../README.md](../README.md) | 📖 Main project overview | Quick overview of the project |
| [QUICKSTART.md](QUICKSTART.md) | ⚡ 5-minute setup guide | Getting up and running quickly |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 🏗️ System design and architecture | Understanding how it works |
| [DEVELOPMENT.md](DEVELOPMENT.md) | 👨‍💻 Development guide | Contributing code and debugging |

## Deployment & Operations

| File | Purpose | Best For |
|------|---------|----------|
| [../deployment/README.md](../deployment/README.md) | 🐳 Docker deployment guide | Running with Docker/Docker Compose |
| [DOCKER_TESTING.md](DOCKER_TESTING.md) | 🧪 Docker testing guide | Running tests in containers |
| [DOCKER_MIGRATION.md](DOCKER_MIGRATION.md) | 📦 Docker files organization | Understanding Docker file structure |
| [DOCKER_MODELS_IMPLEMENTATION.md](DOCKER_MODELS_IMPLEMENTATION.md) | 🤖 Model download feature | How models are pre-cached in Docker |
| [QUICK_START_DOCKER_MODELS.md](QUICK_START_DOCKER_MODELS.md) | 🚀 Docker models quick reference | Quick Docker workflow with models |

## Platform-Specific Guides

| File | Purpose | Best For |
|------|---------|----------|
| [WINDOWS.md](WINDOWS.md) | 🪟 Windows setup guide | Setting up on Windows/WSL2 |
| [GITHUB_SETUP.md](GITHUB_SETUP.md) | 🔧 GitHub integration guide | Setting up GitHub repository |

## Reference

| File | Purpose | Best For |
|------|---------|----------|
| [STRUCTURE.md](STRUCTURE.md) | 📋 Detailed project structure | Understanding folder organization |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | ✅ Project completion status | Reviewing what's implemented |
| [PROJECT_COMPLETION.md](PROJECT_COMPLETION.md) | 📊 Project statistics and features | Detailed project metrics |
| [prd.md](prd.md) | 📝 Product requirements document | Original project specification |

## Quick Navigation

### By Role

**User/Team Lead:**
1. Start with [../README.md](../README.md)
2. Run with [QUICKSTART.md](QUICKSTART.md)
3. Deploy with [../deployment/README.md](../deployment/README.md)

**Developer:**
1. Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. Follow [DEVELOPMENT.md](DEVELOPMENT.md)
3. Reference [STRUCTURE.md](STRUCTURE.md)

**DevOps/Operations:**
1. Review [../deployment/README.md](../deployment/README.md)
2. Study [DOCKER_TESTING.md](DOCKER_TESTING.md)
3. Check [DOCKER_MIGRATION.md](DOCKER_MIGRATION.md)

**Data Scientist:**
1. Understand [DOCKER_MODELS_IMPLEMENTATION.md](DOCKER_MODELS_IMPLEMENTATION.md)
2. Reference [QUICK_START_DOCKER_MODELS.md](QUICK_START_DOCKER_MODELS.md)
3. Check [prd.md](prd.md) for requirements

### By Task

**I want to...**

| Task | Start Here |
|------|-----------|
| Get running in 5 minutes | [QUICKSTART.md](QUICKSTART.md) |
| Deploy to production | [../deployment/README.md](../deployment/README.md) |
| Run tests in Docker | [DOCKER_TESTING.md](DOCKER_TESTING.md) |
| Understand the architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Set up on Windows | [WINDOWS.md](WINDOWS.md) |
| Configure GitHub Actions | [GITHUB_SETUP.md](GITHUB_SETUP.md) |
| Contribute code | [DEVELOPMENT.md](DEVELOPMENT.md) |
| See project statistics | [PROJECT_STATUS.md](PROJECT_STATUS.md) |

## File Organization

```
doc/
├── README.md                            ← You are here
├── QUICKSTART.md                        # Quick start (5 min)
├── ARCHITECTURE.md                      # System design  
├── DEVELOPMENT.md                       # Dev guide
├── prd.md                               # Requirements
├── STRUCTURE.md                         # Project structure
├── WINDOWS.md                           # Windows setup
├── GITHUB_SETUP.md                      # GitHub setup
├── DEPLOYMENT.md                        # [Reference in deployment/README.md]
├── DOCKER_TESTING.md                    # Docker tests
├── DOCKER_MIGRATION.md                  # Docker files org
├── DOCKER_MODELS_IMPLEMENTATION.md      # Model download feature
├── QUICK_START_DOCKER_MODELS.md         # Docker quick ref
├── PROJECT_STATUS.md                    # Project status
└── PROJECT_COMPLETION.md                # Project stats
```

## Documentation Stats

| Category | Files | Lines |
|----------|-------|-------|
| Quick Start | 2 | ~350 |
| Architecture & Design | 2 | ~850 |
| Deployment | 4 | ~1,200 |
| Development | 1 | ~300 |
| Platform-Specific | 2 | ~600 |
| Reference | 3 | ~1,500 |
| **Total** | **~14** | **~4,800** |

## Search Tips

Looking for something specific?

- **Audio setup**: QUICKSTART.md, WINDOWS.md
- **Docker**: DOCKER_*.md files, ../deployment/README.md
- **Testing**: DOCKER_TESTING.md
- **Models & HuggingFace**: DOCKER_MODELS_IMPLEMENTATION.md, QUICK_START_DOCKER_MODELS.md
- **API & Code**: ARCHITECTURE.md, DEVELOPMENT.md
- **GitHub Actions**: GITHUB_SETUP.md
- **Project info**: PROJECT_STATUS.md, PROJECT_COMPLETION.md

## Updates & Maintenance

Last organized: March 9, 2026

This documentation is maintained alongside the codebase and updated with each release. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the latest project status.

---

**Start here:** [../README.md](../README.md) → [QUICKSTART.md](QUICKSTART.md)
