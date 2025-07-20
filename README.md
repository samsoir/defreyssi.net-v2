# defreyssi.net

Hugo static site for defreyssi.net, automatically deployed to Linode Object Storage.

## Setup

This site uses Hugo with a custom theme called "Maison de Freyssinet". 

### Quick Start with Makefile

```bash
# Set up development environment
make setup

# Activate virtual environment  
source venv/bin/activate

# Set your YouTube API key
export YOUTUBE_API_KEY="your-api-key-here"

# Run development server with latest YouTube data
make dev

# Or run individual commands
make test              # Run tests
make fetch-youtube     # Update YouTube data
make serve            # Start Hugo server
make build            # Build production site
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
1. **Testing** - Runs comprehensive unit tests for YouTube integration
2. **YouTube data fetch** - Pulls latest videos from configured channels
3. **Hugo build** - Generates static site with custom theme and minification
4. **Upload to Linode** - Syncs files to object storage with public ACL

### Required GitHub Secrets

Configure these secrets in your GitHub repository settings:

- `LINODE_ACCESS_KEY` - Your Linode Object Storage access key
- `LINODE_SECRET_KEY` - Your Linode Object Storage secret key  
- `YOUTUBE_API_KEY` - Your YouTube Data API v3 key

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

## Theme

This site uses a custom Hugo theme called **"Maison de Freyssinet"** located in `themes/maison-de-freyssinet/`.

### Theme Features

- **Custom design** tailored for personal branding and YouTube integration
- **Responsive layout** optimized for mobile and desktop
- **YouTube integration** with dedicated channel pages and video cards
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

The theme is designed to be easily customizable while maintaining the YouTube integration functionality.