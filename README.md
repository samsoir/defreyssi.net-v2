# defreyssi.net

Hugo static site for defreyssi.net with social media integration, automatically deployed to Linode Object Storage.

## Features

- **Custom Hugo Theme** - "Maison de Freyssinet" theme designed for personal branding
- **YouTube Integration** - Automatically fetches and displays latest videos from configured channels
- **Bluesky Integration** - Shows recent posts from Bluesky using AT Protocol
- **Automated Deployment** - GitHub Actions workflow with testing and deployment to Linode Object Storage
- **Comprehensive Testing** - Unit tests for all social media integrations

## Setup

This site uses Hugo with a custom theme called "Maison de Freyssinet". 

### Quick Start with Makefile

```bash
# Set up development environment
make setup

# Activate virtual environment  
source venv/bin/activate

# Set your API keys and credentials
export YOUTUBE_API_KEY="your-youtube-api-key"
export BLUESKY_USERNAME="your-handle.bsky.social"
export BLUESKY_APP_PASSWORD="your-bluesky-app-password"

# Run development server with all social media data
make dev

# Or run individual commands
make test              # Run tests
make fetch-youtube     # Update YouTube data
make fetch-bluesky     # Update Bluesky data
make fetch-all         # Update all social media data
make serve             # Start Hugo server
make build             # Build production site
```

### Manual Setup

```bash
# Install Hugo (if not already installed)
sudo pacman -S hugo

# Install Python dependencies
pip install -r requirements.txt

# Start development server
hugo server --buildDrafts

# Create new content
hugo new content posts/my-post.md
```

## Deployment

The site automatically deploys to Linode Object Storage when:
- Changes are pushed to the `main` branch
- Pull requests are merged into `main`

The deployment process includes:
1. **Testing** - Runs comprehensive unit tests for all social media integrations
2. **Social media data fetch** - Pulls latest videos from YouTube and posts from Bluesky
3. **Hugo build** - Generates static site with custom theme and minification
4. **Upload to Linode** - Syncs files to object storage with public ACL

### Required GitHub Secrets

Configure these secrets in your GitHub repository settings:

- `LINODE_ACCESS_KEY` - Your Linode Object Storage access key
- `LINODE_SECRET_KEY` - Your Linode Object Storage secret key  
- `YOUTUBE_API_KEY` - Your YouTube Data API v3 key
- `BLUESKY_USERNAME` - Your Bluesky handle (e.g., `yourname.bsky.social`)
- `BLUESKY_APP_PASSWORD` - Your Bluesky App Password (NOT your main password)

### Required GitHub Variables

Configure these variables in your GitHub repository settings:

- `LINODE_CLUSTER` - Your Linode cluster (e.g., `us-east-1`)
- `LINODE_BUCKET` - Your bucket name for the website

### Setting up Linode Object Storage

1. Create a bucket in Linode Object Storage
2. Generate access keys in the Linode Cloud Manager
3. Add the secrets to your GitHub repository
4. The workflow will automatically configure the bucket for static website hosting

## YouTube Integration

The site automatically fetches and displays videos from configured YouTube channels during the build process.

### Setup YouTube Integration

1. **Get a YouTube Data API key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the YouTube Data API v3
   - Create credentials (API key)
   - Add the API key as `YOUTUBE_API_KEY` secret in GitHub

2. **Configure your channels:**
   - Edit `config/youtube-channels.yaml`
   - Replace the placeholder channel IDs with your actual YouTube channel IDs
   - Find your channel ID in YouTube Studio → Settings → Channel → Advanced settings

3. **Local development:**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Set your API key
   export YOUTUBE_API_KEY="your-api-key-here"
   
   # Run tests (optional)
   python -m pytest tests/ -v
   
   # Fetch YouTube data
   python scripts/fetch-youtube-data.py
   
   # Build site
   hugo server --buildDrafts
   ```

### YouTube Features

- **Duplicate filtering** - Removes duplicate videos automatically
- **Live stream detection** - Shows badges for live/upcoming/completed streams  
- **Smart filtering** - Removes old abandoned "upcoming" streams (>7 days)
- **Clean URLs** - Uses channel names instead of IDs (`/youtube/channel-name/`)
- **Responsive design** - Mobile-friendly video cards with thumbnails
- **SEO optimized** - Static content for search engine indexing

## Bluesky Integration

The site automatically fetches and displays your latest Bluesky posts on the homepage using the AT Protocol.

### Setup Bluesky Integration

1. **Generate a Bluesky App Password:**
   - Go to [Bluesky Settings → App Passwords](https://bsky.app/settings/app-passwords)
   - Create a new App Password (give it a descriptive name like "Website Integration")
   - **Important**: Use the App Password, NOT your main account password

2. **Configure your Bluesky handle:**
   - Edit `config/bluesky-config.yaml`
   - Replace `your-actual-handle.bsky.social` with your real Bluesky handle
   - Adjust `max_posts` if you want more or fewer posts displayed

3. **Local development:**
   ```bash
   # Set your credentials
   export BLUESKY_USERNAME="your-handle.bsky.social"
   export BLUESKY_APP_PASSWORD="your-app-password"
   
   # Fetch Bluesky data
   make fetch-bluesky
   
   # Or use the Python script directly
   python scripts/fetch-bluesky-data.py
   
   # Build site with all social media data
   make serve-with-all
   ```

4. **Add GitHub secrets:**
   - Add `BLUESKY_USERNAME` and `BLUESKY_APP_PASSWORD` to your GitHub repository secrets
   - The deployment workflow will automatically fetch your latest posts

### Bluesky Features

- **App Password security** - Uses Bluesky App Passwords for secure API access
- **Smart filtering** - Shows only original posts (filters out reposts and replies)
- **Rich content support** - Displays embedded links, images, and quote posts
- **Infinite loop prevention** - Robust pagination with cursor validation and recursion limits
- **Response validation** - Handles malformed API responses gracefully
- **Responsive design** - Mobile-friendly post cards with Bluesky branding
- **Real-time stats** - Shows likes, reposts, and reply counts
- **Direct links** - Links back to original posts on Bluesky

## Theme

This site uses a custom Hugo theme called **"Maison de Freyssinet"** located in `themes/maison-de-freyssinet/`.

### Theme Features

- **Custom design** tailored for personal branding and social media integration
- **Responsive layout** optimized for mobile and desktop
- **YouTube integration** with dedicated channel pages and video cards
- **Bluesky integration** with styled post cards and embedded content support
- **Clean typography** using modern system fonts
- **Modular structure** with reusable partials and layouts
- **Performance optimized** with minimal CSS and JavaScript

### Theme Development

To customize the theme:

```bash
# Edit styles
themes/maison-de-freyssinet/static/css/style.css

# Modify layouts
themes/maison-de-freyssinet/layouts/

# Update partials
themes/maison-de-freyssinet/layouts/partials/

# Add assets
themes/maison-de-freyssinet/static/
```

The theme is designed to be easily customizable while maintaining all social media integration functionality.

## Testing

The project includes comprehensive unit tests for all integrations with **93% code coverage**:

```bash
# Run all tests
make test

# Run tests with coverage report
make test-coverage

# Run tests with coverage validation (fails if below 85%)
make test-coverage-ci

# Run tests verbosely  
make test-verbose

# Run tests for specific file
make test-file FILE=test_bluesky_fetcher.py

# Run tests matching a pattern (most flexible)
make test-match PATTERN=bluesky      # All Bluesky tests
make test-match PATTERN=youtube      # All YouTube tests  
make test-match PATTERN=pagination   # Pagination-related tests
make test-match PATTERN=embed        # Embed processing tests
```

### Test Coverage

- **Current Coverage**: 93% (maintained automatically via CI)
- **Minimum Required**: 85% (builds fail below this threshold)
- **YouTube Integration**: 14 tests covering API parsing, duplicate filtering, live stream detection, error handling
- **Bluesky Integration**: 20 tests covering AT Protocol API, post filtering, embed processing, infinite loop prevention
- **Configuration**: Tests for proper config file handling and error cases
- **Infinite Loop Prevention**: Tests for cursor validation, recursion limits, and malformed response handling
- **Data Generation**: Tests for Hugo data file creation and validation

### Continuous Integration

The project uses GitHub Actions with automatic coverage validation:
- **All pushes and PRs** trigger comprehensive test suites
- **Coverage below 85%** fails the build automatically
- **Multiple Python versions** (3.11, 3.12) tested for compatibility

## Development Workflow

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