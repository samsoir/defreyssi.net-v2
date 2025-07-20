"""Tests for Bluesky data fetcher"""

import json
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import pytest

# Import the Bluesky fetcher
import sys
import importlib.util
script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'fetch-bluesky-data.py')
spec = importlib.util.spec_from_file_location("fetch_bluesky_data", script_path)
fetch_bluesky_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch_bluesky_data)
BlueskyFetcher = fetch_bluesky_data.BlueskyFetcher


class TestBlueskyFetcher:
    """Test cases for BlueskyFetcher class"""
    
    def setup_method(self):
        """Set up test environment with temporary directory"""
        self.original_cwd = os.getcwd()
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)
        
        # Create necessary directories
        os.makedirs('data', exist_ok=True)
        os.makedirs('config', exist_ok=True)
        
        # Create config file
        self.config_content = {
            'bluesky': {
                'username': 'test.bsky.social',
                'password': 'test-password',
                'posts_limit': 3
            }
        }
        
        with open('config/bluesky-config.yaml', 'w') as f:
            import yaml
            yaml.dump(self.config_content, f)
    
    def teardown_method(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch.object(fetch_bluesky_data, 'Client')
    def test_connect_creates_client(self, mock_client_class):
        """Test that BlueskyFetcher connects to AT Protocol client"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        fetcher = BlueskyFetcher('test.bsky.social', 'test-app-password')
        result = fetcher.connect()
        
        mock_client_class.assert_called_once()
        mock_client.login.assert_called_once_with('test.bsky.social', 'test-app-password')
        assert result is True
        assert fetcher.client == mock_client
    
    @patch.object(fetch_bluesky_data, 'Client')
    def test_get_user_posts_success(self, mock_client_class):
        """Test successful retrieval of user posts"""
        # Mock AT Protocol response
        mock_response = Mock()
        mock_post = Mock()
        mock_post.uri = 'at://did:plc:test123/app.bsky.feed.post/abc123'
        mock_post.cid = 'test-cid-1'
        mock_post.author = Mock()
        mock_post.author.handle = 'test.bsky.social'
        mock_post.author.display_name = 'Test User'
        mock_post.author.avatar = 'https://example.com/avatar.jpg'
        mock_post.record = Mock()
        mock_post.record.text = 'This is a test post'
        mock_post.record.created_at = '2024-01-15T10:30:00Z'
        mock_post.record.embed = None
        mock_post.like_count = 25
        mock_post.repost_count = 10
        mock_post.reply_count = 5
        
        mock_feed_item = Mock()
        mock_feed_item.post = mock_post
        mock_feed_item.reason = None  # Not a repost
        
        mock_response.feed = [mock_feed_item]
        
        mock_client = Mock()
        mock_client.get_author_feed.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        fetcher = BlueskyFetcher('test.bsky.social', 'test-app-password')
        posts = fetcher.get_user_posts('test.bsky.social', limit=10)
        
        assert len(posts) == 1
        post = posts[0]
        assert post['text'] == 'This is a test post'
        assert post['author']['handle'] == 'test.bsky.social'
        assert post['like_count'] == 25
        mock_client.get_author_feed.assert_called_once_with(
            actor='test.bsky.social',
            filter='posts_no_replies',
            limit=10
        )
    
    @patch.object(fetch_bluesky_data, 'Client')
    def test_get_user_posts_filters_reposts(self, mock_client_class):
        """Test that reposts are filtered out"""
        mock_response = Mock()
        
        # Create regular post
        mock_post1 = Mock()
        mock_post1.uri = 'at://did:plc:test123/app.bsky.feed.post/abc123'
        mock_post1.cid = 'test-cid-1'
        mock_post1.author = Mock()
        mock_post1.author.handle = 'test.bsky.social'
        mock_post1.author.display_name = 'Test User'
        mock_post1.author.avatar = None
        mock_post1.record = Mock()
        mock_post1.record.text = 'Regular post'
        mock_post1.record.created_at = '2024-01-15T10:30:00Z'
        mock_post1.record.embed = None
        mock_post1.like_count = 0
        mock_post1.repost_count = 0
        mock_post1.reply_count = 0
        
        mock_feed_item1 = Mock()
        mock_feed_item1.post = mock_post1
        mock_feed_item1.reason = None  # Not a repost
        
        # Create repost (should be filtered out)
        mock_post2 = Mock()
        mock_feed_item2 = Mock()
        mock_feed_item2.post = mock_post2
        mock_feed_item2.reason = Mock()  # This is a repost
        
        mock_response.feed = [mock_feed_item1, mock_feed_item2]
        
        mock_client = Mock()
        mock_client.get_author_feed.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        fetcher = BlueskyFetcher('test.bsky.social', 'test-app-password')
        posts = fetcher.get_user_posts('test.bsky.social')
        
        # Should only return the non-repost
        assert len(posts) == 1
        assert posts[0]['text'] == 'Regular post'
    
    @patch.object(fetch_bluesky_data, 'Client')
    def test_process_embed_external_link(self, mock_client_class):
        """Test processing of external link embeds"""
        # Create mock with specific attributes only
        mock_embed = Mock(spec=['external'])
        mock_embed.__class__.__name__ = 'External'
        mock_embed.external = Mock()
        mock_embed.external.uri = 'https://example.com/article'
        mock_embed.external.title = 'Test Article'
        mock_embed.external.description = 'A test article description'
        mock_embed.external.thumb = 'https://example.com/thumb.jpg'
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        fetcher = BlueskyFetcher('test.bsky.social', 'test-app-password')
        result = fetcher.process_embed(mock_embed)
        
        assert result['type'] == 'External'
        assert result['data']['uri'] == 'https://example.com/article'
        assert result['data']['title'] == 'Test Article'
        assert result['data']['description'] == 'A test article description'
        assert result['data']['thumb'] == 'https://example.com/thumb.jpg'
    
    @patch.object(fetch_bluesky_data, 'Client')
    def test_process_embed_images(self, mock_client_class):
        """Test processing of image embeds"""
        # Create mock with specific attributes only
        mock_embed = Mock(spec=['images'])
        mock_embed.__class__.__name__ = 'Images'
        
        mock_img1 = Mock()
        mock_img1.fullsize = 'https://example.com/image1.jpg'
        mock_img1.thumb = 'https://example.com/thumb1.jpg'
        mock_img1.alt = 'Test image 1'
        
        mock_img2 = Mock()
        mock_img2.fullsize = 'https://example.com/image2.jpg'
        mock_img2.thumb = 'https://example.com/thumb2.jpg'
        mock_img2.alt = 'Test image 2'
        
        mock_embed.images = [mock_img1, mock_img2]
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        fetcher = BlueskyFetcher('test.bsky.social', 'test-app-password')
        result = fetcher.process_embed(mock_embed)
        
        assert result['type'] == 'Images'
        assert len(result['data']['images']) == 2
        assert result['data']['images'][0]['fullsize'] == 'https://example.com/image1.jpg'
        assert result['data']['images'][1]['alt'] == 'Test image 2'
    
    @patch.object(fetch_bluesky_data, 'Client')
    def test_process_embed_quote_post(self, mock_client_class):
        """Test processing of quote post embeds"""
        # Create mock with specific attributes only
        mock_embed = Mock(spec=['record'])
        mock_embed.__class__.__name__ = 'Record'
        mock_embed.record = Mock()
        mock_embed.record.uri = 'at://did:plc:other/app.bsky.feed.post/xyz789'
        mock_embed.record.author = Mock()
        mock_embed.record.author.handle = 'other.bsky.social'
        mock_embed.record.value = Mock()
        mock_embed.record.value.text = 'Original quoted post'
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        fetcher = BlueskyFetcher('test.bsky.social', 'test-app-password')
        result = fetcher.process_embed(mock_embed)
        
        assert result['type'] == 'Record'
        assert result['data']['uri'] == 'at://did:plc:other/app.bsky.feed.post/xyz789'
        assert result['data']['author'] == 'other.bsky.social'
        assert result['data']['text'] == 'Original quoted post'
    
    @patch.object(fetch_bluesky_data, 'Client')
    def test_save_data_creates_json_file(self, mock_client_class):
        """Test that save_data creates proper JSON file"""
        mock_posts = [
            {
                'text': 'Test post',
                'author': {'handle': 'test.bsky.social'},
                'created_at': '2024-01-15T10:30:00Z',
                'url': 'https://bsky.app/profile/test.bsky.social/post/abc123'
            }
        ]
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        fetcher = BlueskyFetcher('test.bsky.social', 'test-password')
        fetcher.save_data(mock_posts)
        
        # Check that the file was created
        assert os.path.exists('data/bluesky.json')
        
        # Check the content
        with open('data/bluesky.json', 'r') as f:
            data = json.load(f)
        
        assert 'posts' in data
        assert len(data['posts']) == 1
        assert data['posts'][0]['text'] == 'Test post'
    
    @patch.object(fetch_bluesky_data, 'Client')
    def test_empty_posts_skips_file_creation(self, mock_client_class):
        """Test handling of empty posts list"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        fetcher = BlueskyFetcher('test.bsky.social', 'test-app-password')
        fetcher.save_data([])
        
        # Empty posts should not create file
        assert not os.path.exists('data/bluesky.json')
    
    @patch.object(fetch_bluesky_data, 'BlueskyFetcher')
    @patch('yaml.safe_load')
    @patch('builtins.open')
    @patch('pathlib.Path.exists')
    def test_main_function_success(self, mock_exists, mock_open, mock_yaml_load, mock_fetcher_class):
        """Test main function execution"""
        # Mock file operations
        mock_exists.return_value = True
        mock_yaml_load.return_value = {'handle': 'test.bsky.social', 'max_posts': 3}
        
        # Mock fetcher
        mock_fetcher = Mock()
        mock_posts = [{'text': 'Test post', 'author': {'handle': 'test.bsky.social'}}]
        mock_fetcher.get_user_posts.return_value = mock_posts
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'BLUESKY_USERNAME': 'test.bsky.social',
            'BLUESKY_APP_PASSWORD': 'test-app-password'
        }):
            fetch_bluesky_data.main()
        
        mock_fetcher_class.assert_called_once_with('test.bsky.social', 'test-app-password')
        mock_fetcher.get_user_posts.assert_called_once_with('test.bsky.social', limit=3)
        mock_fetcher.save_data.assert_called_once_with(mock_posts)
    
    def test_main_function_missing_env_vars(self):
        """Test main function with missing environment variables"""
        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit):
                fetch_bluesky_data.main()
    
    @patch.object(fetch_bluesky_data, 'Client')
    def test_api_error_handling(self, mock_client_class):
        """Test handling of AT Protocol API errors"""
        mock_client = Mock()
        mock_client.get_author_feed.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        fetcher = BlueskyFetcher('test.bsky.social', 'test-app-password')
        
        # The method should return empty list when API fails, not raise exception
        posts = fetcher.get_user_posts('test.bsky.social')
        assert posts == []