# Contributing Guide

Thank you for your interest in contributing to defreyssi.net! This guide will help you get started with development and contributions.

## Quick Start for Contributors

```bash
# 1. Clone and setup
git clone https://github.com/samsoir/defreyssi.net-v2.git
cd defreyssi.net-v2
make setup

# 2. Set up environment variables (optional for development)
export YOUTUBE_API_KEY="your-youtube-api-key"
export BLUESKY_USERNAME="your-handle.bsky.social"
export BLUESKY_APP_PASSWORD="your-bluesky-app-password"

# 3. Run tests to ensure everything works
make test

# 4. Start development server
make dev
```

## Development Workflow

### Development Environment Setup

The project uses a Makefile-based workflow for consistency:

```bash
# Full development setup
make setup                    # Set up virtual environment
make test                    # Run all tests
make fetch-all               # Fetch all social media data
make serve                   # Start development server

# Quick development cycle
make quick-test              # Fast test run
make dev                     # Fetch data and serve
make check                   # Run tests + build

# Cleanup
make clean                   # Clean build artifacts
make clean-test-data         # Clean any test data leaks
make clean-all               # Clean everything including venv
```

### Code Quality Standards

#### Required Before Submitting PRs:

1. **Tests must pass**: `make test`
2. **Coverage must be ≥85%**: `make test-coverage-ci`
3. **Code should be clean**: Follow existing patterns
4. **Documentation updated**: If adding features

#### Testing Requirements:

- **Write tests** for new functionality
- **Test edge cases** and error conditions
- **Use mocks** for external API calls
- **Maintain coverage** above 85%

### Making Changes

#### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

#### 2. Development Loop
```bash
# Make changes to code
# Run tests frequently
make quick-test

# Check coverage before committing
make test-coverage-ci

# Test with real data (optional)
make dev
```

#### 3. Commit Guidelines

Use clear, descriptive commit messages:
```bash
git commit -m "Add infinite loop prevention to Bluesky pagination

- Add cursor validation to prevent infinite loops
- Add maximum request limits for safety
- Add comprehensive tests for edge cases"
```

#### 4. Submit Pull Request

- **Base branch**: `main`
- **Include**: Description of changes and testing performed
- **Ensure**: All CI checks pass

## Project Structure

```
defreyssi.net/
├── scripts/                    # Data fetching scripts
│   ├── fetch-bluesky-data.py   # Bluesky integration
│   └── fetch-youtube-data.py   # YouTube integration
├── tests/                      # Test suite
│   ├── test_bluesky_fetcher.py
│   └── test_youtube_fetcher.py
├── themes/maison-de-freyssinet/ # Custom Hugo theme
├── content/                    # Hugo content
├── config/                     # Configuration files
├── data/                       # Generated data files
├── .github/workflows/          # CI/CD pipelines
├── Makefile                    # Development commands
├── requirements.txt            # Python dependencies
└── hugo.toml                   # Hugo configuration
```

## Key Components

### Social Media Integration

#### Bluesky Fetcher (`scripts/fetch-bluesky-data.py`)
- **Purpose**: Fetch posts from Bluesky using AT Protocol
- **Features**: Infinite loop prevention, embed processing, pagination
- **Config**: `config/bluesky-config.yaml`

#### YouTube Fetcher (`scripts/fetch-youtube-data.py`)
- **Purpose**: Fetch video data from YouTube Data API
- **Features**: Duplicate filtering, live stream detection, smart filtering
- **Config**: `config/youtube-channels.yaml`

### Testing Framework

- **Framework**: pytest with coverage reporting
- **Coverage Target**: 85% minimum, 93% current
- **Approach**: Comprehensive unit tests with mocked external dependencies

### CI/CD Pipeline

- **Test Workflow**: Runs on all PRs and pushes
- **Deploy Workflow**: Deploys to Linode Object Storage
- **Coverage Enforcement**: Builds fail if coverage < 85%

## Adding New Features

### 1. Social Media Integrations

When adding a new social media platform:

1. **Create fetcher script** in `scripts/`
2. **Add configuration** in `config/`
3. **Write comprehensive tests** in `tests/`
4. **Update Makefile** with new targets
5. **Add to CI/CD pipeline**
6. **Document in README**

### 2. Hugo Theme Changes

When modifying the theme:

1. **Edit files** in `themes/maison-de-freyssinet/`
2. **Test locally** with `make serve`
3. **Ensure responsive design**
4. **Test with real data** using `make dev`

### 3. Build Process Changes

When modifying the build:

1. **Update Makefile** targets
2. **Test locally** with `make check`
3. **Update CI/CD workflows** if needed
4. **Document changes**

## Coding Standards

### Python Code

- **Style**: Follow existing code patterns
- **Imports**: Use absolute imports where possible
- **Error Handling**: Use try/catch with meaningful messages
- **Documentation**: Add docstrings for public methods
- **Type Hints**: Add type hints for new functions

### Test Code

- **Naming**: Use descriptive test names
- **Structure**: Follow Arrange-Act-Assert pattern
- **Mocking**: Mock external dependencies consistently
- **Coverage**: Ensure new code is tested

### Configuration

- **Format**: Use YAML for configuration files
- **Documentation**: Comment complex configurations
- **Validation**: Add error handling for missing configs

## Common Tasks

### Adding a Test

```python
@patch.object(module_name, 'ExternalDependency')
def test_descriptive_name(self, mock_dependency):
    """Test description explaining what this validates."""
    # Arrange
    mock_dependency.return_value = expected_result
    
    # Act
    result = function_under_test()
    
    # Assert
    assert result == expected_outcome
    mock_dependency.assert_called_once()
```

### Adding a Makefile Target

```makefile
new-target: ## Description of what this target does
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(RED)Error: Virtual environment not found. Run 'make setup' first.$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Running new target...$(NC)"
	$(PYTHON) scripts/new-script.py
```

### Debugging Issues

```bash
# Run tests with verbose output
make test-verbose

# Run specific test file
make test-file FILE=test_bluesky_fetcher.py

# Run tests matching pattern
make test-match PATTERN=pagination

# Check coverage for specific areas
make test-coverage
```

## Getting Help

### Documentation
- **Main README**: Project overview and setup
- **Testing Guide**: [TESTING.md](TESTING.md)
- **Makefile targets**: `make help`

### Common Issues

**Environment setup problems:**
```bash
make clean-all  # Clean everything
make setup      # Fresh setup
```

**Test failures:**
```bash
make clean-test-data  # Clean test data leaks
PYTHONPATH=scripts make test  # Ensure correct path
```

**Coverage issues:**
```bash
make test-coverage-ci  # See detailed coverage report
```

## Release Process

1. **All tests pass**: `make test`
2. **Coverage maintained**: `make test-coverage-ci`
3. **Documentation updated**
4. **PR reviewed and approved**
5. **Merge to main**
6. **Automatic deployment** via GitHub Actions

## Code of Conduct

- **Be respectful** in all interactions
- **Test thoroughly** before submitting changes
- **Document clearly** any new features
- **Follow established patterns** in the codebase
- **Ask questions** if anything is unclear

## Questions?

- **Check documentation** first (README, TESTING.md)
- **Search existing issues** on GitHub
- **Create new issue** if problem persists
- **Include details**: error messages, steps to reproduce, environment info