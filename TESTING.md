# Testing Guide

This document covers all testing procedures and requirements for the defreyssi.net project.

## Overview

The project includes comprehensive unit tests for all integrations with **93% code coverage**.

## Quick Testing Commands

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

## Test Coverage

### Current Status
- **Current Coverage**: 93% (maintained automatically via CI)
- **Minimum Required**: 85% (builds fail below this threshold)

### Coverage by Component

- **YouTube Integration**: 14 tests covering API parsing, duplicate filtering, live stream detection, error handling
- **Bluesky Integration**: 20 tests covering AT Protocol API, post filtering, embed processing, infinite loop prevention
- **Configuration**: Tests for proper config file handling and error cases
- **Infinite Loop Prevention**: Tests for cursor validation, recursion limits, and malformed response handling
- **Data Generation**: Tests for Hugo data file creation and validation

## Continuous Integration

The project uses GitHub Actions with automatic coverage validation:
- **All pushes and PRs** trigger comprehensive test suites
- **Coverage below 85%** fails the build automatically
- **Multiple Python versions** (3.11, 3.12) tested for compatibility

### CI Workflows

1. **`test.yml`**: Dedicated testing workflow for PRs and development
2. **`deploy.yml`**: Enhanced deployment workflow with coverage validation

## Writing New Tests

### Test Structure

Tests are organized in the `tests/` directory:
```
tests/
├── test_bluesky_fetcher.py    # Bluesky integration tests
├── test_youtube_fetcher.py    # YouTube integration tests
└── __init__.py
```

### Test Requirements

1. **Coverage**: New code must maintain 85%+ coverage
2. **Edge Cases**: Test error conditions and malformed inputs
3. **Isolation**: Tests must not affect production data
4. **Mocking**: Use mocks for external API calls

### Example Test

```python
@patch.object(fetch_bluesky_data, 'Client')
def test_pagination_cursor_loop_prevention(self, mock_client_class):
    """Test that pagination stops when cursors repeat (infinite loop prevention)"""
    mock_client = Mock()
    
    # Mock responses that would create a cursor loop
    mock_response1 = Mock()
    mock_response1.feed = []
    mock_response1.cursor = "cursor1"
    
    mock_response2 = Mock() 
    mock_response2.feed = []
    mock_response2.cursor = "cursor1"  # Same cursor - should trigger loop detection
    
    mock_client.get_author_feed.side_effect = [mock_response1, mock_response2]
    mock_client_class.return_value = mock_client
    
    fetcher = BlueskyFetcher('test.bsky.social', 'test-app-password')
    posts = fetcher.get_user_posts('test.bsky.social', limit=50, enable_pagination=True)
    
    # Should stop pagination due to cursor loop detection
    assert posts == []
    assert mock_client.get_author_feed.call_count == 2
```

## Running Tests Locally

### Prerequisites

```bash
# Set up development environment
make setup

# Activate virtual environment  
source venv/bin/activate
```

### Development Testing Workflow

```bash
# Quick test run during development
make quick-test

# Watch for changes and run tests automatically (requires entr)
make watch-tests

# Full validation before committing
make test-coverage-ci
```

## Test Categories

### Unit Tests
- Individual function and method testing
- Mocked external dependencies
- Fast execution (< 3 seconds total)

### Integration Tests
- End-to-end workflow testing
- Configuration file handling
- Error scenario validation

### Coverage Tests
- Automated coverage validation
- Fails if coverage drops below 85%
- Generates detailed coverage reports

## Troubleshooting

### Common Issues

**Tests failing with import errors:**
```bash
# Ensure PYTHONPATH is set correctly
PYTHONPATH=scripts python -m pytest tests/ -v
```

**Coverage reports not generating:**
```bash
# Install coverage dependencies
pip install pytest-cov
```

**Tests interfering with production data:**
```bash
# Clean up any test data leaks
make clean-test-data
```

### Test Environment

Tests run in isolated temporary directories and use mocked external services to prevent:
- Production data pollution
- Network dependencies
- API rate limiting
- Authentication requirements

## Performance

- **Test Suite Runtime**: ~2-3 seconds
- **Coverage Generation**: ~3-4 seconds  
- **CI Pipeline**: ~30-60 seconds (including setup)

## Best Practices

1. **Test Names**: Use descriptive names explaining what is being tested
2. **Assertions**: Use specific assertions with clear error messages
3. **Setup/Teardown**: Clean up resources in teardown methods
4. **Mocking**: Mock external services consistently
5. **Edge Cases**: Test boundary conditions and error scenarios
6. **Documentation**: Document complex test scenarios

## Coverage Targets

| Component | Target Coverage | Current |
|-----------|----------------|---------|
| Bluesky Fetcher | 90%+ | 94% |
| YouTube Fetcher | 90%+ | 93% |
| Overall Project | 85%+ | 93% |

## Related Documentation

- [Contributing Guide](CONTRIBUTING.md) - Development workflow
- [README](README.md) - Main project documentation
- [GitHub Actions](.github/workflows/) - CI/CD configuration