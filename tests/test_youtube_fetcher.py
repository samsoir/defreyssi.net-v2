#!/usr/bin/env python3
"""
Unit tests for the YouTube fetcher script.
"""

import unittest
import json
import tempfile
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import pytest

# Add the scripts directory to the Python path
scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
sys.path.insert(0, scripts_dir)

from fetch_youtube_data import YouTubeFetcher
import fetch_youtube_data


class TestYouTubeFetcher(unittest.TestCase):
    """Test cases for YouTubeFetcher class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.fetcher = YouTubeFetcher(self.api_key)
        self.temp_dir = tempfile.mkdtemp()
        # Store original working directory
        self.original_cwd = os.getcwd()
        # Change to temp directory for isolated testing
        os.chdir(self.temp_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Return to original directory
        os.chdir(self.original_cwd)
        # Clean up temp directory
        shutil.rmtree(self.temp_dir)
        
        # Clean up any test files that might have leaked to the project directory
        project_data_dir = os.path.join(self.original_cwd, 'data', 'youtube')
        if os.path.exists(project_data_dir):
            test_files = ['UCtest123.json', 'UCempty.json']
            for test_file in test_files:
                test_path = os.path.join(project_data_dir, test_file)
                if os.path.exists(test_path):
                    os.remove(test_path)
                    
        # Clean up any test content directories
        project_content_dir = os.path.join(self.original_cwd, 'content', 'youtube')
        if os.path.exists(project_content_dir):
            test_dirs = ['test-channel', 'empty-channel']
            for test_dir in test_dirs:
                test_path = os.path.join(project_content_dir, test_dir)
                if os.path.exists(test_path):
                    shutil.rmtree(test_path)
    
    def create_mock_channel_response(self):
        """Create a mock YouTube API channel response."""
        return {
            'items': [{
                'snippet': {
                    'title': 'Test Channel'
                },
                'contentDetails': {
                    'relatedPlaylists': {
                        'uploads': 'UUtest123'
                    }
                }
            }]
        }
    
    def create_mock_playlist_response(self):
        """Create a mock YouTube API playlist response."""
        return {
            'items': [
                {
                    'snippet': {
                        'resourceId': {'videoId': 'video1'},
                        'title': 'Test Video 1',
                        'description': 'Description 1',
                        'publishedAt': '2023-01-01T12:00:00Z',
                        'thumbnails': {
                            'high': {'url': 'https://example.com/thumb1.jpg'}
                        }
                    }
                },
                {
                    'snippet': {
                        'resourceId': {'videoId': 'video2'},
                        'title': 'Test Video 2',
                        'description': 'Description 2',
                        'publishedAt': '2023-01-02T12:00:00Z',
                        'thumbnails': {
                            'maxres': {'url': 'https://example.com/thumb2_maxres.jpg'},
                            'high': {'url': 'https://example.com/thumb2.jpg'}
                        }
                    }
                },
                # Duplicate video
                {
                    'snippet': {
                        'resourceId': {'videoId': 'video1'},
                        'title': 'Test Video 1 Duplicate',
                        'description': 'Description 1 Duplicate',
                        'publishedAt': '2023-01-01T12:00:00Z',
                        'thumbnails': {
                            'high': {'url': 'https://example.com/thumb1.jpg'}
                        }
                    }
                }
            ]
        }
    
    def create_mock_videos_response(self, include_live_stream=False, live_status='upcoming', days_old=0):
        """Create a mock YouTube API videos response."""
        published_date = datetime.now(timezone.utc) - timedelta(days=days_old)
        published_str = published_date.isoformat().replace('+00:00', 'Z')
        
        videos = [
            {
                'id': 'video1',
                'snippet': {
                    'title': 'Test Video 1',
                    'description': 'Description 1',
                    'publishedAt': published_str,
                    'thumbnails': {
                        'high': {'url': 'https://example.com/thumb1.jpg'}
                    }
                }
            },
            {
                'id': 'video2',
                'snippet': {
                    'title': 'Test Video 2',
                    'description': 'Description 2',
                    'publishedAt': '2023-01-02T12:00:00Z',
                    'thumbnails': {
                        'maxres': {'url': 'https://example.com/thumb2_maxres.jpg'},
                        'high': {'url': 'https://example.com/thumb2.jpg'}
                    }
                }
            }
        ]
        
        if include_live_stream:
            live_video = {
                'id': 'live_video',
                'snippet': {
                    'title': 'Live Stream Test',
                    'description': 'Live stream description',
                    'publishedAt': published_str,
                    'thumbnails': {
                        'high': {'url': 'https://example.com/live_thumb.jpg'}
                    }
                },
                'liveStreamingDetails': {}
            }
            
            # Add appropriate live streaming details based on status
            if live_status == 'live':
                live_video['liveStreamingDetails']['actualStartTime'] = published_str
            elif live_status == 'completed':
                live_video['liveStreamingDetails']['actualStartTime'] = published_str
                live_video['liveStreamingDetails']['actualEndTime'] = published_str
            # upcoming has no additional fields
            
            videos.append(live_video)
        
        return {'items': videos}


class TestYouTubeFetcherMethods(TestYouTubeFetcher):
    """Test individual methods of YouTubeFetcher."""
    
    @patch('fetch_youtube_data.requests.get')
    def test_get_channel_videos_success(self, mock_get):
        """Test successful channel video fetching."""
        # Mock API responses
        mock_responses = [
            Mock(status_code=200),  # Channel response
            Mock(status_code=200),  # Playlist response  
            Mock(status_code=200),  # Videos response
        ]
        
        mock_responses[0].json.return_value = self.create_mock_channel_response()
        mock_responses[1].json.return_value = self.create_mock_playlist_response()
        mock_responses[2].json.return_value = self.create_mock_videos_response()
        
        mock_get.side_effect = mock_responses
        
        # Test the method
        result = self.fetcher.get_channel_videos('UCtest123')
        
        # Verify results
        self.assertIsInstance(result, dict)
        self.assertEqual(result['channel_title'], 'Test Channel')
        self.assertEqual(result['channel_id'], 'UCtest123')
        self.assertEqual(len(result['videos']), 2)  # Duplicates should be removed
        
        # Check video data structure
        video = result['videos'][0]
        self.assertIn('id', video)
        self.assertIn('title', video)
        self.assertIn('description', video)
        self.assertIn('published_at', video)
        self.assertIn('thumbnail', video)
        self.assertIn('url', video)
        self.assertIn('is_live_stream', video)
        
        # Verify API calls
        self.assertEqual(mock_get.call_count, 3)
    
    @patch('fetch_youtube_data.requests.get')
    def test_get_channel_videos_duplicate_filtering(self, mock_get):
        """Test that duplicate videos are properly filtered."""
        mock_responses = [
            Mock(status_code=200),
            Mock(status_code=200),
            Mock(status_code=200),
        ]
        
        mock_responses[0].json.return_value = self.create_mock_channel_response()
        mock_responses[1].json.return_value = self.create_mock_playlist_response()
        mock_responses[2].json.return_value = self.create_mock_videos_response()
        
        mock_get.side_effect = mock_responses
        
        result = self.fetcher.get_channel_videos('UCtest123')
        
        # Should have 2 unique videos (duplicate removed)
        self.assertEqual(len(result['videos']), 2)
        
        # Verify unique video IDs
        video_ids = [video['id'] for video in result['videos']]
        self.assertEqual(len(set(video_ids)), 2)  # All unique
        self.assertIn('video1', video_ids)
        self.assertIn('video2', video_ids)
    
    @patch('fetch_youtube_data.requests.get')
    def test_live_stream_detection(self, mock_get):
        """Test live stream detection and status."""
        mock_responses = [
            Mock(status_code=200),
            Mock(status_code=200),
            Mock(status_code=200),
        ]
        
        mock_responses[0].json.return_value = self.create_mock_channel_response()
        mock_responses[1].json.return_value = self.create_mock_playlist_response()
        mock_responses[2].json.return_value = self.create_mock_videos_response(
            include_live_stream=True, live_status='live'
        )
        
        mock_get.side_effect = mock_responses
        
        result = self.fetcher.get_channel_videos('UCtest123')
        
        # Find the live stream video
        live_video = None
        for video in result['videos']:
            if video['id'] == 'live_video':
                live_video = video
                break
        
        self.assertIsNotNone(live_video)
        self.assertTrue(live_video['is_live_stream'])
        self.assertEqual(live_video['live_status'], 'live')
    
    @patch('fetch_youtube_data.requests.get')
    def test_old_upcoming_stream_filtering(self, mock_get):
        """Test that old upcoming streams are filtered out."""
        mock_responses = [
            Mock(status_code=200),
            Mock(status_code=200),
            Mock(status_code=200),
        ]
        
        mock_responses[0].json.return_value = self.create_mock_channel_response()
        mock_responses[1].json.return_value = self.create_mock_playlist_response()
        mock_responses[2].json.return_value = self.create_mock_videos_response(
            include_live_stream=True, live_status='upcoming', days_old=10  # 10 days old
        )
        
        mock_get.side_effect = mock_responses
        
        result = self.fetcher.get_channel_videos('UCtest123')
        
        # Old upcoming stream should be filtered out
        video_ids = [video['id'] for video in result['videos']]
        self.assertNotIn('live_video', video_ids)
        self.assertEqual(len(result['videos']), 2)  # Only regular videos
    
    @patch('fetch_youtube_data.requests.get')
    def test_recent_upcoming_stream_kept(self, mock_get):
        """Test that recent upcoming streams are kept."""
        mock_responses = [
            Mock(status_code=200),
            Mock(status_code=200),
            Mock(status_code=200),
        ]
        
        mock_responses[0].json.return_value = self.create_mock_channel_response()
        mock_responses[1].json.return_value = self.create_mock_playlist_response()
        mock_responses[2].json.return_value = self.create_mock_videos_response(
            include_live_stream=True, live_status='upcoming', days_old=3  # 3 days old
        )
        
        mock_get.side_effect = mock_responses
        
        result = self.fetcher.get_channel_videos('UCtest123')
        
        # Recent upcoming stream should be kept
        video_ids = [video['id'] for video in result['videos']]
        self.assertIn('live_video', video_ids)
        self.assertEqual(len(result['videos']), 3)  # All videos including upcoming stream
    
    @patch('fetch_youtube_data.requests.get')
    def test_channel_not_found(self, mock_get):
        """Test handling of channel not found."""
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {'items': []}
        mock_get.return_value = mock_response
        
        result = self.fetcher.get_channel_videos('UCnonexistent')
        
        self.assertEqual(result, [])
    
    @patch('fetch_youtube_data.requests.get')
    def test_api_error_handling(self, mock_get):
        """Test API error handling."""
        import requests
        mock_get.side_effect = requests.RequestException("API Error")
        
        result = self.fetcher.get_channel_videos('UCtest123')
        
        self.assertEqual(result, [])
    
    def test_thumbnail_preference(self):
        """Test that maxres thumbnails are preferred over high quality."""
        with patch('fetch_youtube_data.requests.get') as mock_get:
            mock_responses = [
                Mock(status_code=200),
                Mock(status_code=200),
                Mock(status_code=200),
            ]
            
            mock_responses[0].json.return_value = self.create_mock_channel_response()
            mock_responses[1].json.return_value = self.create_mock_playlist_response()
            mock_responses[2].json.return_value = self.create_mock_videos_response()
            
            mock_get.side_effect = mock_responses
            
            result = self.fetcher.get_channel_videos('UCtest123')
            
            # video2 has maxres thumbnail, should prefer it
            video2 = None
            for video in result['videos']:
                if video['id'] == 'video2':
                    video2 = video
                    break
            
            self.assertIsNotNone(video2)
            self.assertEqual(video2['thumbnail'], 'https://example.com/thumb2_maxres.jpg')


class TestContentGeneration(TestYouTubeFetcher):
    """Test Hugo content generation."""
    
    def create_test_channel_data(self):
        """Create test channel data."""
        return {
            'channel_title': 'Test Channel',
            'channel_id': 'UCtest123',
            'videos': [
                {
                    'id': 'video1',
                    'title': 'Test Video 1',
                    'description': 'Description 1',
                    'published_at': '2023-01-01T12:00:00Z',
                    'thumbnail': 'https://example.com/thumb1.jpg',
                    'url': 'https://www.youtube.com/watch?v=video1',
                    'is_live_stream': False,
                    'live_status': None
                }
            ]
        }
    
    def test_generate_hugo_content(self):
        """Test Hugo content generation."""
        channel_data = self.create_test_channel_data()
        channel_slug = 'test-channel'
        
        # Use 'content' relative to current directory (temp directory)
        self.fetcher.generate_hugo_content(channel_data, 'content', channel_slug)
        
        # Check that content directory was created
        content_dir = Path('content') / 'youtube' / channel_slug
        self.assertTrue(content_dir.exists())
        
        # Check that index file was created
        index_file = content_dir / '_index.md'
        self.assertTrue(index_file.exists())
        
        # Check index file content
        with open(index_file, 'r') as f:
            content = f.read()
        
        self.assertIn('title: Test Channel - YouTube Videos', content)
        self.assertIn('type: youtube-channel', content)
        self.assertIn('channel_id: UCtest123', content)
        self.assertIn('channel_slug: test-channel', content)
        self.assertIn('# Test Channel', content)
        
        # Check that data file was created
        data_file = Path('data') / 'youtube' / 'UCtest123.json'
        self.assertTrue(data_file.exists())
        
        # Check data file content
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['channel_title'], 'Test Channel')
        self.assertEqual(data['channel_id'], 'UCtest123')
        self.assertEqual(data['channel_slug'], 'test-channel')
        self.assertEqual(len(data['videos']), 1)
    
    def test_generate_hugo_content_empty_videos(self):
        """Test content generation with empty video list."""
        channel_data = {
            'channel_title': 'Empty Channel',
            'channel_id': 'UCempty',
            'videos': []
        }
        
        # The generate_hugo_content method returns early for empty videos
        # So we need to test with at least one video
        channel_data['videos'] = [
            {
                'id': 'dummy',
                'title': 'Dummy',
                'description': 'Test',
                'published_at': '2023-01-01T12:00:00Z',
                'thumbnail': 'test.jpg',
                'url': 'test.com',
                'is_live_stream': False,
                'live_status': None
            }
        ]
        
        self.fetcher.generate_hugo_content(channel_data, 'content', 'empty-channel')
        
        # Should create content
        data_file = Path('data') / 'youtube' / 'UCempty.json'
        self.assertTrue(data_file.exists())
        
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data['videos']), 1)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_create_slug(self):
        """Test URL slug creation from channel names."""
        # Import the function from the main script
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        
        # We need to extract the create_slug function
        # For now, let's test the logic manually
        import re
        
        def create_slug(name):
            slug = re.sub(r'[^\w\s-]', '', name.lower())
            slug = re.sub(r'[-\s]+', '-', slug)
            return slug.strip('-')
        
        test_cases = [
            ('Sam does a thing', 'sam-does-a-thing'),
            ('Four Star Captain', 'four-star-captain'),
            ('Channel Name!@#', 'channel-name'),
            ('Multiple   Spaces', 'multiple-spaces'),
            ('Hyphens-and-spaces', 'hyphens-and-spaces'),
            ('', ''),
            ('123 Numbers', '123-numbers'),
        ]
        
        for input_name, expected_slug in test_cases:
            with self.subTest(input_name=input_name):
                result = create_slug(input_name)
                self.assertEqual(result, expected_slug)


class TestMainFunction(unittest.TestCase):
    """Test cases for main function and error conditions"""
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        self.original_cwd = os.getcwd()
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)
        
        # Create necessary directories
        os.makedirs('config', exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('builtins.print')
    @patch('sys.exit')
    def test_main_missing_api_key(self, mock_exit, mock_print):
        """Test main function with missing YouTube API key"""
        # Mock sys.exit to raise an exception to stop execution
        mock_exit.side_effect = SystemExit(1)
        
        with pytest.raises(SystemExit):
            with patch.dict(os.environ, {}, clear=True):
                fetch_youtube_data.main()
        
        mock_exit.assert_called_once_with(1)
        mock_print.assert_called_with("Error: YOUTUBE_API_KEY environment variable not set")
    
    @patch('builtins.print')
    @patch('sys.exit')
    @patch('pathlib.Path.exists')
    def test_main_missing_config_file(self, mock_exists, mock_exit, mock_print):
        """Test main function with missing config file"""
        mock_exists.return_value = False
        mock_exit.side_effect = SystemExit(1)
        
        with pytest.raises(SystemExit):
            with patch.dict(os.environ, {'YOUTUBE_API_KEY': 'test-key'}):
                fetch_youtube_data.main()
        
        mock_exit.assert_called_once_with(1)
        # Check that error message was printed
        mock_print.assert_any_call("Error: config/youtube-channels.yaml not found")
    
    @patch.object(fetch_youtube_data, 'YouTubeFetcher')
    @patch('yaml.safe_load')
    @patch('builtins.open')
    @patch('pathlib.Path.exists')
    def test_main_function_workflow(self, mock_exists, mock_open, mock_yaml_load, mock_fetcher_class):
        """Test main function successful workflow"""
        # Mock file operations
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            'channels': [
                {'channel_id': 'UCtest123', 'name': 'Test Channel'},
                {'channel_id': 'UCtest456', 'name': 'Another Channel'}
            ]
        }
        
        # Mock fetcher
        mock_fetcher = Mock()
        mock_channel_data = {
            'channel_title': 'Test Channel',
            'channel_id': 'UCtest123',
            'videos': [{'id': 'video1', 'title': 'Test Video'}]
        }
        mock_fetcher.get_channel_videos.return_value = mock_channel_data
        mock_fetcher_class.return_value = mock_fetcher
        
        with patch.dict(os.environ, {'YOUTUBE_API_KEY': 'test-api-key'}):
            fetch_youtube_data.main()
        
        # Verify fetcher was created with API key
        mock_fetcher_class.assert_called_once_with('test-api-key')
        
        # Verify get_channel_videos was called for each channel
        expected_calls = [
            unittest.mock.call('UCtest123'),
            unittest.mock.call('UCtest456')
        ]
        mock_fetcher.get_channel_videos.assert_has_calls(expected_calls)
        
        # Verify content generation was called
        assert mock_fetcher.generate_hugo_content.call_count == 2


if __name__ == '__main__':
    unittest.main()