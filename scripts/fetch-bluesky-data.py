#!/usr/bin/env python3
"""
Fetch Bluesky posts and generate Hugo content files.
"""

import os
import sys
import json
import yaml
import re
from datetime import datetime, timezone
from pathlib import Path

try:
    from atproto import Client
except ImportError:
    print("Error: atproto package not installed. Install with: pip install atproto")
    sys.exit(1)


class BlueskyFetcher:
    def __init__(self, username, app_password):
        """
        Initialize Bluesky fetcher.
        
        Args:
            username: Your Bluesky handle (e.g., user.bsky.social)
            app_password: Your Bluesky App Password (NOT your main password)
        """
        self.username = username
        self.app_password = app_password
        self.client = None
        
    def connect(self):
        """Connect to Bluesky API."""
        try:
            self.client = Client()
            self.client.login(self.username, self.app_password)
            print(f"Successfully connected to Bluesky as {self.username}")
            return True
        except Exception as e:
            print(f"Error connecting to Bluesky: {e}")
            print("Make sure you're using an App Password, not your main password!")
            print("Generate one at: https://bsky.app/settings/app-passwords")
            return False
    
    def get_user_posts(self, handle, limit=10):
        """Fetch recent posts from a user."""
        if not self.client:
            if not self.connect():
                return []
                
        try:
            # Get author feed with posts only (no replies by default)
            response = self.client.get_author_feed(
                actor=handle, 
                filter='posts_no_replies',  # Only original posts, no replies
                limit=limit
            )
            
            posts = []
            for feed_item in response.feed:
                post = feed_item.post
                record = post.record
                
                # Skip reposts - only include original posts
                if feed_item.reason:
                    continue
                    
                post_data = {
                    'uri': post.uri,
                    'cid': post.cid,
                    'text': record.text,
                    'created_at': record.created_at,
                    'author': {
                        'handle': post.author.handle,
                        'display_name': post.author.display_name or post.author.handle,
                        'avatar': post.author.avatar
                    },
                    'like_count': post.like_count or 0,
                    'repost_count': post.repost_count or 0,
                    'reply_count': post.reply_count or 0,
                    'url': f"https://bsky.app/profile/{post.author.handle}/post/{post.uri.split('/')[-1]}"
                }
                
                # Extract links and mentions from text
                post_data['links'] = self.extract_links(record.text)
                post_data['mentions'] = self.extract_mentions(record.text)
                
                # Handle embedded content (images, external links, etc.)
                if hasattr(record, 'embed') and record.embed:
                    post_data['embed'] = self.process_embed(record.embed)
                
                posts.append(post_data)
                
            # Sort by creation date (newest first)
            posts.sort(key=lambda x: x['created_at'], reverse=True)
            
            return posts
            
        except Exception as e:
            print(f"Error fetching posts for {handle}: {e}")
            return []
    
    def extract_links(self, text):
        """Extract HTTP/HTTPS links from post text."""
        url_pattern = r'https?://[^\s]+'
        return re.findall(url_pattern, text)
    
    def extract_mentions(self, text):
        """Extract @mentions from post text."""
        mention_pattern = r'@([a-zA-Z0-9._-]+\.bsky\.social|[a-zA-Z0-9._-]+)'
        return re.findall(mention_pattern, text)
    
    def process_embed(self, embed):
        """Process embedded content in posts."""
        embed_data = {
            'type': embed.__class__.__name__,
            'data': {}
        }
        
        # Handle different embed types
        if hasattr(embed, 'external') and embed.external:
            # External link embed
            external = embed.external
            embed_data['data'] = {
                'uri': external.uri,
                'title': external.title,
                'description': external.description,
                'thumb': external.thumb
            }
        elif hasattr(embed, 'images') and embed.images:
            # Image embed
            embed_data['data'] = {
                'images': [
                    {
                        'alt': img.alt,
                        'thumb': img.thumb,
                        'fullsize': img.fullsize
                    } for img in embed.images
                ]
            }
        elif hasattr(embed, 'record') and embed.record:
            # Quote post embed
            quoted = embed.record
            embed_data['data'] = {
                'uri': quoted.uri,
                'author': quoted.author.handle if hasattr(quoted, 'author') else None,
                'text': quoted.value.text if hasattr(quoted, 'value') else None
            }
            
        return embed_data
    
    def save_data(self, posts, output_file='data/bluesky.json'):
        """Generate Hugo data file from Bluesky posts."""
        if not posts:
            print("No posts to generate data for")
            return
            
        # Create data directory
        data_file = Path(output_file)
        data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare data structure
        bluesky_data = {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'post_count': len(posts),
            'posts': posts
        }
        
        # Write data file
        with open(data_file, 'w') as f:
            json.dump(bluesky_data, f, indent=2, default=str)
            
        print(f"Generated Bluesky data: {len(posts)} posts saved to {output_file}")


def main():
    # Get credentials from environment
    username = os.getenv('BLUESKY_USERNAME')
    app_password = os.getenv('BLUESKY_APP_PASSWORD')
    
    if not username or not app_password:
        print("Error: BLUESKY_USERNAME and BLUESKY_APP_PASSWORD environment variables not set")
        print("Set them with:")
        print("  export BLUESKY_USERNAME=\"your-handle.bsky.social\"")
        print("  export BLUESKY_APP_PASSWORD=\"your-app-password\"")
        print("\nIMPORTANT: Use an App Password, NOT your main password!")
        print("Generate an App Password at: https://bsky.app/settings/app-passwords")
        sys.exit(1)
    
    # Read configuration
    config_file = Path('config') / 'bluesky-config.yaml'
    if not config_file.exists():
        print(f"Error: {config_file} not found")
        print("Create this file with your Bluesky configuration:")
        print("handle: your-handle.bsky.social")
        print("max_posts: 10")
        sys.exit(1)
        
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    handle = config.get('handle')
    max_posts = config.get('max_posts', 10)
    
    if not handle or handle == 'your-handle.bsky.social':
        print("Error: Please update 'handle' in bluesky-config.yaml with your actual Bluesky handle")
        print("Example: handle: yourname.bsky.social")
        sys.exit(1)
    
    # Fetch posts
    fetcher = BlueskyFetcher(username, app_password)
    
    print(f"Fetching latest {max_posts} posts from @{handle}...")
    posts = fetcher.get_user_posts(handle, limit=max_posts)
    
    if posts:
        fetcher.save_data(posts)
        print(f"✓ Successfully fetched {len(posts)} posts from Bluesky")
    else:
        print("No posts retrieved")


if __name__ == '__main__':
    main()