# GitHub Repository Setup Guide

## Initialize GitHub Repository

### Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Enter repository name: `story_teller_bot`
3. Enter description: "AI-powered storytelling bot for kids with audio input/output"
4. Choose public or private
5. Do NOT initialize with README (we have one)
6. Click "Create repository"

### Step 2: Initialize Local Repository

```bash
cd /home/rajesh/ai_projects/story_teller_bot

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Story Teller Bot project structure

- Core bot implementation with audio I/O
- Speech recognition using Whisper
- Story generation with transformers
- Comprehensive test suite
- Docker containerization
- Deployment scripts"

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/story_teller_bot.git

# Rename branch to main if needed
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 3: Configure GitHub

1. **Enable Issues**: Settings → Features → Issues (enable)
2. **Enable Discussions**: Settings → Features → Discussions (enable)
3. **Set up Branch Protection**:
   - Settings → Branches
   - Add rule for `main`
   - Require status checks to pass (CI/CD)
4. **Configure Secrets** (if using workflows):
   - Settings → Secrets → Add repository secret

### Step 4: Setup CI/CD

The project includes GitHub Actions workflow. Commit and push:

```bash
git add .github/workflows/ci-cd.yml
git commit -m "Add GitHub Actions CI/CD workflow"
git push
```

Actions will automatically run on push and pull request.

## Working with the Repository

### Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/story_teller_bot.git
cd story_teller_bot

# Build the Docker image
docker build -t story-teller-bot:latest -f deployment/Dockerfile .

# Or use Docker Compose to build and run
docker-compose -f deployment/docker-compose.yml up --build
```

### Development Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test**:
   ```bash
   make test
   make lint
   ```

3. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: Description of feature"
   ```

4. **Push to GitHub**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**:
   - Go to GitHub repository
   - Click "New Pull Request"
   - Select your branch
   - Add description
   - Request reviewers
   - Submit PR

6. **Merge PR**:
   - After review and CI passes
   - Click "Merge Pull Request"
   - Delete branch

### Branching Strategy

```
main (production)
├── develop (development)
│   ├── feature/audio-enhancement
│   ├── feature/better-stories
│   └── fix/bug-fix
└── hotfix/critical-fix
```

### Conventional Commits

Use conventional commit messages:

```
feat: Add new feature
fix: Fix a bug
docs: Update documentation
test: Add or update tests
refactor: Code refactoring
perf: Performance improvements
ci: CI/CD changes
chore: Maintenance tasks
```

## Release Management

### Creating a Release

1. **Create release branch**:
   ```bash
   git checkout -b release/v1.0.0
   ```

2. **Update version numbers**:
   - Update version in `setup.py` (if exists)
   - Update `README.md`
   - Update `CHANGELOG.md`

3. **Commit**:
   ```bash
   git commit -m "chore: Prepare release v1.0.0"
   git push origin release/v1.0.0
   ```

4. **Create Pull Request** to `main`

5. **Tag Release**:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

6. **GitHub Release**:
   - Go to Releases
   - Click "Create Release"
   - Select tag
   - Add release notes
   - Attach binaries if needed
   - Publish

### Version Numbering

Use semantic versioning: `MAJOR.MINOR.PATCH`

- `MAJOR`: Breaking changes
- `MINOR`: New features
- `PATCH`: Bug fixes

Example: `v1.2.3`

## Documentation

### Update Documentation

1. **README.md**: User-facing documentation
2. **DEVELOPMENT.md**: Developer guide
3. **CHANGELOG.md**: Release notes (create if needed)
4. **GitHub Wiki**: More detailed documentation (optional)
5. **GitHub Pages**: Project website (optional)

### Create CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] - 2024-03-09

### Added
- Initial release
- Audio input/output handling
- Speech recognition with Whisper
- Story generation with transformers
- Docker support
- Comprehensive test suite

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A
```

## Collaboration

### Adding Collaborators

1. Settings → Manage access → Invite a collaborator
2. Enter GitHub username
3. Select role (pull request: read, develop: write, admin)
4. Send invitation

### Code Review Checklist

Before merging PR, check:

- [ ] Tests pass (CI/CD successful)
- [ ] Code follows style guidelines (`make lint`)
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Commit messages are clear
- [ ] At least one review approval

## Useful Commands

```bash
# View git history
git log --oneline -10

# See current changes
git status

# View diff
git diff

# Stash changes
git stash

# Check branches
git branch -a

# Delete local branch
git branch -d branch-name

# Delete remote branch
git push origin --delete branch-name

# Sync with main
git fetch origin
git rebase origin/main

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

## GitHub Issues & Projects

### Using Issues

1. **Create Issue**:
   - Title: Clear and concise
   - Description: Detailed explanation
   - Labels: bug, feature, documentation, etc.
   - Assignee: Who's working on it
   - Milestone: Release/version

2. **Link to PR**:
   ```markdown
   Fixes #123
   ```

### Using Projects

1. Go to Projects tab
2. Create new project
3. Link issues and PRs
4. Organize as Kanban board

## Best Practices

✅ **Do:**
- Write clear commit messages
- Create small, focused PRs
- Update documentation
- Write tests for new features
- Review code thoroughly
- Use issues for discussion

❌ **Don't:**
- Commit directly to main
- Large commits mixing changes
- Forget to test locally
- Ignore CI/CD failures
- Force push to main

## Support & Contact

- Create an issue for bug reports
- Use discussions for general questions
- Email: rajesh@example.com
