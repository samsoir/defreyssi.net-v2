#!/usr/bin/env python3
"""
Fetch YouTube channel data and generate Hugo content files.
"""

import os
import sys
import json
import yaml
import requests
import re
from datetime import datetime
from pathlib import Path

class YouTubeFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    def get_channel_videos(self, channel_id, max_results=50):
        """Fetch videos from a YouTube channel."""
        try:
            # Get channel's uploads playlist ID
            channel_url = f"{self.base_url}/channels"
            channel_params = {
                'part': 'contentDetails,snippet',
                'id': channel_id,
                'key': self.api_key
            }
            
            response = requests.get(channel_url, params=channel_params)
            response.raise_for_status()
            channel_data = response.json()
            
            if not channel_data['items']:
                print(f"Channel {channel_id} not found")
                return []
                
            channel_info = channel_data['items'][0]
            uploads_playlist_id = channel_info['contentDetails']['relatedPlaylists']['uploads']
            channel_title = channel_info['snippet']['title']
            
            # Get videos from uploads playlist
            playlist_url = f"{self.base_url}/playlistItems"
            playlist_params = {
                'part': 'snippet',
                'playlistId': uploads_playlist_id,
                'maxResults': max_results,
                'order': 'date',
                'key': self.api_key
            }
            
            response = requests.get(playlist_url, params=playlist_params)
            response.raise_for_status()
            playlist_data = response.json()
            
            # Get video IDs for detailed info
            video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_data['items']]
            
            # Get detailed video information including live stream status
            videos_url = f"{self.base_url}/videos"
            videos_params = {
                'part': 'snippet,liveStreamingDetails',
                'id': ','.join(video_ids),
                'key': self.api_key
            }
            
            response = requests.get(videos_url, params=videos_params)
            response.raise_for_status()
            videos_data = response.json()
            
            # Use set to track video IDs and prevent duplicates
            seen_video_ids = set()
            videos = []
            
            for video in videos_data['items']:
                video_id = video['id']
                
                # Skip if we've already seen this video
                if video_id in seen_video_ids:
                    continue
                seen_video_ids.add(video_id)
                
                # Determine if this is a live stream
                is_live_stream = 'liveStreamingDetails' in video
                live_status = None
                if is_live_stream:
                    live_details = video['liveStreamingDetails']
                    if 'actualEndTime' in live_details:
                        live_status = 'completed'
                    elif 'actualStartTime' in live_details:
                        live_status = 'live'
                    else:
                        live_status = 'upcoming'
                        
                        # Filter out old upcoming streams (likely canceled/never happened)
                        from datetime import datetime, timezone
                        published_date = datetime.fromisoformat(video['snippet']['publishedAt'].replace('Z', '+00:00'))
                        days_old = (datetime.now(timezone.utc) - published_date).days
                        
                        # Skip upcoming streams older than 7 days (likely canceled)
                        if days_old > 7:
                            print(f"Skipping old upcoming stream: {video['snippet']['title']}")
                            continue
                
                video_data = {
                    'id': video_id,
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'published_at': video['snippet']['publishedAt'],
                    'thumbnail': video['snippet']['thumbnails']['maxres']['url'] if 'maxres' in video['snippet']['thumbnails'] else video['snippet']['thumbnails']['high']['url'],
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'is_live_stream': is_live_stream,
                    'live_status': live_status
                }
                videos.append(video_data)
                
            # Sort by published date (newest first)
            videos.sort(key=lambda x: x['published_at'], reverse=True)
                
            return {
                'channel_title': channel_title,
                'channel_id': channel_id,
                'videos': videos
            }
            
        except requests.RequestException as e:
            print(f"Error fetching data for channel {channel_id}: {e}")
            return []
        except KeyError as e:
            print(f"Unexpected API response structure: {e}")
            return []

    def generate_hugo_content(self, channel_data, output_dir, channel_slug):
        """Generate Hugo content files from YouTube data."""
        if not channel_data or not channel_data.get('videos'):
            print(f"No data to generate content for channel")
            return
            
        channel_title = channel_data['channel_title']
        channel_id = channel_data['channel_id']
        videos = channel_data['videos']
        
        # Create channel directory using slug
        channel_dir = Path(output_dir) / 'youtube' / channel_slug
        channel_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate channel index page
        channel_frontmatter = {
            'title': f"{channel_title} - YouTube Videos",
            'date': datetime.now().isoformat(),
            'type': 'youtube-channel',
            'channel_id': channel_id,
            'channel_title': channel_title,
            'channel_slug': channel_slug,
            'video_count': len(videos)
        }
        
        channel_content = f"""---
{yaml.dump(channel_frontmatter, default_flow_style=False)}---

# {channel_title}

Latest videos from my YouTube channel.

{{{{< youtube-channel "{channel_id}" >}}}}
"""
        
        with open(channel_dir / '_index.md', 'w') as f:
            f.write(channel_content)
            
        # Generate video data file for Hugo to use (still use channel_id for data file)
        data_dir = Path('data') / 'youtube'
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Add channel_slug to the data for template use
        channel_data['channel_slug'] = channel_slug
        
        with open(data_dir / f'{channel_id}.json', 'w') as f:
            json.dump(channel_data, f, indent=2)
            
        print(f"Generated content for {channel_title} ({len(videos)} videos)")

def main():
    # Get API key from environment
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set")
        sys.exit(1)
        
    # Read channel configuration
    config_file = Path('config') / 'youtube-channels.yaml'
    if not config_file.exists():
        print(f"Error: {config_file} not found")
        print("Create this file with your channel IDs:")
        print("channels:")
        print("  - channel_id: UCxxxxxxxxxxxxxxxxxxxxx")
        print("    name: My First Channel")
        print("  - channel_id: UCxxxxxxxxxxxxxxxxxxxxx") 
        print("    name: My Second Channel")
        sys.exit(1)
        
    with open(config_file) as f:
        config = yaml.safe_load(f)
        
    fetcher = YouTubeFetcher(api_key)
    
    def create_slug(name):
        """Create URL-friendly slug from channel name."""
        # Convert to lowercase, replace spaces and special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    # Process each channel
    for channel_config in config['channels']:
        channel_id = channel_config['channel_id']
        channel_name = channel_config.get('name', 'Unknown Channel')
        channel_slug = create_slug(channel_name)
        
        print(f"Fetching data for channel: {channel_name} (/{channel_slug}/)")
        
        channel_data = fetcher.get_channel_videos(channel_id)
        if channel_data:
            fetcher.generate_hugo_content(channel_data, 'content', channel_slug)

if __name__ == '__main__':
    main()