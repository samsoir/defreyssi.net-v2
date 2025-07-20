# defreyssi.net

Hugo static site for defreyssi.net with social media integration, automatically deployed to Linode Object Storage.

[![Test Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)](TESTING.md)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](#continuous-integration)
[![Hugo](https://img.shields.io/badge/hugo-0.148.1-blue)](https://gohugo.io/)

## Table of Contents

- [🚀 Quick Start](#-quick-start)
- [✨ Features](#-features)
- [🔧 Setup](#-setup)
- [🏗️ Development](#️-development)
- [🚀 Deployment](#-deployment)
- [📚 Documentation](#-documentation)

## 🚀 Quick Start

```bash
# One-time setup
make setup

# Activate virtual environment  
source venv/bin/activate

# Set your API keys (optional for development)
export YOUTUBE_API_KEY="your-youtube-api-key"
export BLUESKY_USERNAME="your-handle.bsky.social"
export BLUESKY_APP_PASSWORD="your-bluesky-app-password"

# Start development server with all features
make dev
```

Visit `http://localhost:1313` to see your site!

## ✨ Features

### 🎨 Custom Hugo Theme
- **"Maison de Freyssinet"** theme designed for personal branding
- **Responsive design** optimized for mobile and desktop
- **Performance optimized** with minimal CSS and JavaScript

### 📺 YouTube Integration
- **Automatic video fetching** from configured channels
- **Duplicate filtering** and smart content management
- **Live stream detection** with status badges
- **SEO optimized** static content generation

### 🦋 Bluesky Integration  
- **AT Protocol support** with App Password security
- **Smart filtering** (original posts only, no reposts/replies)
- **Rich content support** (links, images, quote posts)
- **Infinite loop prevention** with robust pagination

### 🛡️ Quality Assurance
- **93% test coverage** with automated validation
- **CI/CD pipeline** with quality gates
- **Multiple Python versions** tested (3.11, 3.12)

## 🔧 Setup

### Prerequisites

- **Hugo** (0.148.1+)
- **Python** (3.11+)
- **Make** (for development commands)

### Basic Setup

<details>
<summary>📖 Detailed Setup Instructions (click to expand)</summary>

#### Manual Installation

```bash
# Install Hugo (Arch Linux)
sudo pacman -S hugo

# Install Python dependencies
pip install -r requirements.txt

# Start development server
hugo server --buildDrafts
```

#### API Configuration

1. **YouTube Setup:**
   - Get API key from [Google Cloud Console](https://console.cloud.google.com/)
   - Enable YouTube Data API v3
   - Configure channels in `config/youtube-channels.yaml`

2. **Bluesky Setup:**
   - Generate App Password at [Bluesky Settings](https://bsky.app/settings/app-passwords)
   - Configure handle in `config/bluesky-config.yaml`

</details>

### Environment Variables

```bash
# Required for fetching live data
export YOUTUBE_API_KEY="your-youtube-api-key"
export BLUESKY_USERNAME="your-handle.bsky.social"
export BLUESKY_APP_PASSWORD="your-bluesky-app-password"
```

## 🏗️ Development

### Common Commands

```bash
# Development workflow
make setup           # Initial setup
make test           # Run tests
make dev            # Fetch data + serve
make build          # Production build

# Testing
make test-coverage  # Coverage report
make test-match PATTERN=bluesky  # Specific tests

# Cleanup
make clean          # Clean build artifacts
```

See the [Contributing Guide](CONTRIBUTING.md) for detailed development workflow.

## 🚀 Deployment

### Automatic Deployment

The site automatically deploys to Linode Object Storage when:
- ✅ Changes pushed to `main` branch
- ✅ All tests pass (≥85% coverage required)
- ✅ Social media data updated
- ✅ Site built and optimized

### Required Secrets

Configure in GitHub repository settings:

**Secrets:**
- `LINODE_ACCESS_KEY` / `LINODE_SECRET_KEY` 
- `YOUTUBE_API_KEY`
- `BLUESKY_USERNAME` / `BLUESKY_APP_PASSWORD`

**Variables:**
- `LINODE_CLUSTER` (e.g., `us-east-1`)
- `LINODE_BUCKET` (your bucket name)

<details>
<summary>🔧 Manual Deployment Setup (click to expand)</summary>

### Linode Object Storage Setup

1. Create bucket in Linode Object Storage
2. Generate access keys in Linode Cloud Manager  
3. Add secrets to GitHub repository
4. Workflow automatically configures static website hosting

### Local Deployment Testing

```bash
# Test full build process
make check          # Tests + build

# Test with real data
make fetch-all      # Fetch all social media
make build          # Build production site
```

</details>

## 📚 Documentation

### Quick Links

- **[Testing Guide](TESTING.md)** - Comprehensive testing documentation
- **[Contributing Guide](CONTRIBUTING.md)** - Development workflow and standards
- **[Makefile Commands](#development)** - `make help` for full list

### Project Structure

```
defreyssi.net/
├── scripts/                    # Data fetching scripts
├── themes/maison-de-freyssinet/ # Custom Hugo theme  
├── content/                    # Hugo content
├── config/                     # Configuration files
├── tests/                      # Test suite (93% coverage)
└── .github/workflows/          # CI/CD pipelines
```

### Key Features Deep Dive

<details>
<summary>📺 YouTube Integration Details</summary>

- **Channel Management:** Configure multiple channels in `config/youtube-channels.yaml`
- **Content Filtering:** Automatic duplicate removal and smart filtering
- **Live Streams:** Detection and status tracking for live/upcoming streams
- **URL Generation:** Clean URLs using channel names (`/youtube/channel-name/`)
- **SEO Optimization:** Static content generation for search engines

</details>

<details>
<summary>🦋 Bluesky Integration Details</summary>

- **AT Protocol:** Native integration with Bluesky's AT Protocol
- **Security:** App Password authentication (not main password)
- **Content Processing:** Rich embed support for links, images, quotes
- **Reliability:** Infinite loop prevention with cursor validation
- **Performance:** Efficient pagination with safety limits

</details>

### Continuous Integration

- **Automated Testing:** All pushes/PRs trigger comprehensive test suites
- **Coverage Enforcement:** Builds fail if coverage drops below 85%
- **Multi-Python Testing:** Compatibility tested across Python 3.11 and 3.12
- **Quality Gates:** Code must pass all checks before deployment

---

## Getting Help

- **📖 Documentation:** Check [TESTING.md](TESTING.md) and [CONTRIBUTING.md](CONTRIBUTING.md)
- **🐛 Issues:** [Create an issue](https://github.com/samsoir/defreyssi.net-v2/issues) 
- **💡 Questions:** Include error messages and steps to reproduce

Built with ❤️ using [Hugo](https://gohugo.io/) and deployed to [Linode Object Storage](https://www.linode.com/products/object-storage/).