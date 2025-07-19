# defreyssi.net

Hugo static site for defreyssi.net, automatically deployed to Linode Object Storage.

## Setup

This site uses Hugo with the Ananke theme. To run locally:

```bash
# Install Hugo (if not already installed)
sudo pacman -S hugo

# Start development server
hugo server --buildDrafts

# Create new content
hugo new content posts/my-post.md
```

## Deployment

The site automatically deploys to Linode Object Storage when:
- Changes are pushed to the `main` branch
- Pull requests are merged into `main`

### Required GitHub Secrets

Configure these secrets in your GitHub repository settings:

- `LINODE_ACCESS_KEY` - Your Linode Object Storage access key
- `LINODE_SECRET_KEY` - Your Linode Object Storage secret key  
- `LINODE_CLUSTER` - Your Linode cluster (e.g., `us-east-1`)
- `LINODE_BUCKET` - Your bucket name for the website

### Setting up Linode Object Storage

1. Create a bucket in Linode Object Storage
2. Generate access keys in the Linode Cloud Manager
3. Add the secrets to your GitHub repository
4. The workflow will automatically configure the bucket for static website hosting

## Theme

This site uses the [Ananke theme](https://github.com/theNewDynamic/gohugo-theme-ananke) as a git submodule.