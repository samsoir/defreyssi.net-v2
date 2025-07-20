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
    
    def get_user_posts(self, handle, limit=10, enable_pagination=False):
        """
        Fetch recent posts from a user.
        
        Args:
            handle: User handle to fetch posts from
            limit: Maximum number of posts per request (default: 10)
            enable_pagination: If True, fetch all available posts up to limit using pagination
        """
        if not self.client:
            if not self.connect():
                return []
                
        try:
            posts = []
            cursor = None
            seen_cursors = set()  # Track cursors to prevent infinite loops
            max_requests = 10  # Safety limit for pagination requests
            request_count = 0
            
            while True:
                # Safety check: prevent infinite pagination
                if request_count >= max_requests:
                    print(f"Warning: Reached maximum pagination requests ({max_requests}), stopping")
                    break
                    
                # Validate cursor hasn't been seen before (infinite loop prevention)
                if cursor and cursor in seen_cursors:
                    print(f"Warning: Detected cursor loop, stopping pagination")
                    break
                    
                if cursor:
                    seen_cursors.add(cursor)
                
                # Get author feed with posts only (no replies by default)
                response = self.client.get_author_feed(
                    actor=handle, 
                    filter='posts_no_replies',  # Only original posts, no replies
                    limit=min(limit - len(posts), 100) if enable_pagination else limit,
                    cursor=cursor
                )
                
                # Validate response structure
                if not hasattr(response, 'feed') or response.feed is None:
                    print("Warning: Invalid API response")
                    break
                    
                for feed_item in response.feed:
                    # Validate feed item structure
                    if not hasattr(feed_item, 'post') or not feed_item.post:
                        continue
                        
                    post = feed_item.post
                    
                    # Validate post structure
                    if not hasattr(post, 'record') or not post.record:
                        continue
                        
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
                        post_data['embed'] = self.process_embed(record.embed, max_depth=3)
                    
                    posts.append(post_data)
                    
                    # Stop if we've reached the desired limit
                    if len(posts) >= limit:
                        break
                
                request_count += 1
                
                # Check if we should continue pagination
                if not enable_pagination or len(posts) >= limit:
                    break
                    
                # Get next cursor for pagination
                next_cursor = getattr(response, 'cursor', None)
                if not next_cursor or next_cursor == cursor:
                    break  # No more pages or same cursor (API issue)
                    
                cursor = next_cursor
                
            # Sort by creation date (newest first)
            posts.sort(key=lambda x: x['created_at'], reverse=True)
            
            return posts[:limit]  # Ensure we don't exceed requested limit
            
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
    
    def process_embed(self, embed, max_depth=3, current_depth=0):
        """
        Process embedded content in posts with recursion depth limits.
        
        Args:
            embed: The embed object to process
            max_depth: Maximum recursion depth to prevent infinite loops (default: 3)
            current_depth: Current recursion depth (internal use)
        """
        # Prevent infinite recursion
        if current_depth >= max_depth:
            return {
                'type': 'DepthLimitExceeded',
                'data': {'message': f'Maximum embed depth ({max_depth}) exceeded'}
            }
        
        # Validate embed object
        if not embed or not hasattr(embed, '__class__'):
            return {
                'type': 'InvalidEmbed',
                'data': {'message': 'Invalid or missing embed object'}
            }
        
        embed_data = {
            'type': embed.__class__.__name__,
            'data': {}
        }
        
        try:
            # Handle different embed types
            if hasattr(embed, 'external') and embed.external:
                # External link embed
                external = embed.external
                embed_data['data'] = {
                    'uri': getattr(external, 'uri', None),
                    'title': getattr(external, 'title', None),
                    'description': getattr(external, 'description', None),
                    'thumb': getattr(external, 'thumb', None)
                }
            elif hasattr(embed, 'images') and embed.images:
                # Image embed
                embed_data['data'] = {
                    'images': [
                        {
                            'alt': getattr(img, 'alt', ''),
                            'thumb': getattr(img, 'thumb', None),
                            'fullsize': getattr(img, 'fullsize', None)
                        } for img in embed.images if img
                    ]
                }
            elif hasattr(embed, 'record') and embed.record:
                # Quote post embed - handle with recursion limit
                quoted = embed.record
                embed_data['data'] = {
                    'uri': getattr(quoted, 'uri', None),
                    'author': getattr(quoted.author, 'handle', None) if hasattr(quoted, 'author') else None,
                    'text': getattr(quoted.value, 'text', None) if hasattr(quoted, 'value') else None
                }
                
                # Recursively process nested embeds with depth tracking
                if hasattr(quoted, 'embeds') and quoted.embeds and current_depth < max_depth:
                    nested_embeds = []
                    for nested_embed in quoted.embeds[:3]:  # Limit to 3 nested embeds
                        nested_result = self.process_embed(
                            nested_embed, 
                            max_depth=max_depth, 
                            current_depth=current_depth + 1
                        )
                        nested_embeds.append(nested_result)
                    embed_data['data']['nested_embeds'] = nested_embeds
            else:
                # Unknown embed type
                embed_data['data'] = {
                    'message': f'Unknown embed type: {embed.__class__.__name__}'
                }
                
        except Exception as e:
            # Handle any processing errors gracefully
            embed_data = {
                'type': 'ProcessingError',
                'data': {
                    'message': f'Error processing embed: {str(e)}',
                    'original_type': getattr(embed.__class__, '__name__', 'Unknown') if hasattr(embed, '__class__') else 'Unknown'
                }
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