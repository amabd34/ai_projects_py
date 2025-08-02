"""
Comprehensive tests for ConfigLoader service.
Tests configuration loading, environment variable overrides, error handling, and validation.
"""

import os
import json
import tempfile
import pytest
from unittest.mock import patch, mock_open

from src.config.config_loader import ConfigLoader, get_config, get_api_key, get_api_url


class TestConfigLoader:
    """Test suite for ConfigLoader class."""
    
    def test_init_with_default_path(self):
        """Test ConfigLoader initialization with default config path."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='{"test": "value"}')):
            loader = ConfigLoader()
            assert loader.config_path.endswith('config.json')
            assert loader._config == {"test": "value"}
    
    def test_init_with_custom_path(self, temp_config_file):
        """Test ConfigLoader initialization with custom config path."""
        loader = ConfigLoader(temp_config_file)
        assert loader.config_path == temp_config_file
        assert loader._config is not None
    
    def test_load_config_success(self, test_config):
        """Test successful configuration loading."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            assert loader._config == test_config
        finally:
            os.unlink(temp_path)
    
    def test_load_config_file_not_found(self):
        """Test configuration loading when file doesn't exist."""
        with patch('builtins.print') as mock_print:
            loader = ConfigLoader('/nonexistent/config.json')
            assert loader._config is not None  # Should use default config
            mock_print.assert_called()
    
    def test_load_config_invalid_json(self):
        """Test configuration loading with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')  # Invalid JSON
            temp_path = f.name
        
        try:
            with patch('builtins.print') as mock_print:
                loader = ConfigLoader(temp_path)
                assert loader._config is not None  # Should use default config
                mock_print.assert_called()
        finally:
            os.unlink(temp_path)
    
    def test_get_simple_key(self, config_loader):
        """Test getting a simple configuration key."""
        result = config_loader.get('app.name')
        assert result == "Test Movie App"
    
    def test_get_nested_key(self, config_loader):
        """Test getting a nested configuration key."""
        result = config_loader.get('api.omdb_api_key')
        assert result == "test-api-key"
    
    def test_get_with_default(self, config_loader):
        """Test getting a non-existent key with default value."""
        result = config_loader.get('nonexistent.key', 'default_value')
        assert result == 'default_value'
    
    def test_get_without_default(self, config_loader):
        """Test getting a non-existent key without default value."""
        result = config_loader.get('nonexistent.key')
        assert result is None
    
    @patch.dict(os.environ, {'API_OMDB_API_KEY': 'env_api_key'})
    def test_environment_variable_override(self, config_loader):
        """Test that environment variables override config file values."""
        result = config_loader.get('api.omdb_api_key')
        assert result == 'env_api_key'
    
    @patch.dict(os.environ, {'FEATURES_ENABLE_API_ENDPOINTS': 'false'})
    def test_environment_variable_boolean_override(self, config_loader):
        """Test environment variable override for boolean values."""
        result = config_loader.get('features.enable_api_endpoints')
        assert result == 'false'  # Environment variables are strings
    
    def test_get_api_key(self, config_loader):
        """Test getting API key."""
        result = config_loader.get_api_key()
        assert result == "test-api-key"
    
    def test_get_api_url(self, config_loader):
        """Test getting API URL."""
        result = config_loader.get_api_url()
        assert result == "http://www.omdbapi.com/"
    
    def test_get_app_config(self, config_loader):
        """Test getting app configuration."""
        result = config_loader.get_app_config()
        expected_keys = ['SECRET_KEY', 'DEBUG']
        for key in expected_keys:
            assert key in result
    
    def test_get_popular_movies(self, config_loader):
        """Test getting popular movies list."""
        result = config_loader.get_popular_movies()
        assert isinstance(result, list)
        assert len(result) > 0
        assert "The Shawshank Redemption" in result
    
    def test_get_search_suggestions(self, config_loader):
        """Test getting search suggestions."""
        result = config_loader.get_search_suggestions()
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_is_feature_enabled_true(self, config_loader):
        """Test feature flag that is enabled."""
        result = config_loader.is_feature_enabled('enable_popular_movies')
        assert result is True
    
    def test_is_feature_enabled_false(self, config_loader):
        """Test feature flag that is disabled."""
        # Modify config to have a disabled feature
        config_loader._config['features']['test_disabled'] = False
        result = config_loader.is_feature_enabled('test_disabled')
        assert result is False
    
    def test_is_feature_enabled_nonexistent(self, config_loader):
        """Test feature flag that doesn't exist."""
        result = config_loader.is_feature_enabled('nonexistent_feature')
        assert result is False
    
    def test_save_config(self, config_loader):
        """Test saving configuration to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            config_loader.config_path = temp_path
            config_loader.save_config()
            
            # Verify file was written
            assert os.path.exists(temp_path)
            
            # Verify content
            with open(temp_path, 'r') as f:
                saved_config = json.load(f)
            assert saved_config == config_loader._config
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_save_config_error(self, config_loader):
        """Test save configuration with write error."""
        config_loader.config_path = '/invalid/path/config.json'
        with patch('builtins.print') as mock_print:
            config_loader.save_config()
            mock_print.assert_called()
    
    def test_get_default_config(self, config_loader):
        """Test getting default configuration."""
        default_config = config_loader._get_default_config()
        assert isinstance(default_config, dict)
        assert 'api' in default_config
        assert 'app' in default_config
        assert 'features' in default_config
    
    def test_invalid_key_path(self, config_loader):
        """Test getting configuration with invalid key path."""
        result = config_loader.get('api.nonexistent.deeply.nested')
        assert result is None
    
    def test_empty_key_path(self, config_loader):
        """Test getting configuration with empty key path."""
        result = config_loader.get('')
        assert result is None
    
    def test_none_key_path(self, config_loader):
        """Test getting configuration with None key path."""
        with pytest.raises(AttributeError):
            config_loader.get(None)


class TestConvenienceFunctions:
    """Test suite for convenience functions."""
    
    def test_get_config_function(self, config_loader):
        """Test get_config convenience function."""
        with patch('src.config.config_loader.config', config_loader):
            result = get_config('app.name')
            assert result == "Test Movie App"
    
    def test_get_api_key_function(self, config_loader):
        """Test get_api_key convenience function."""
        with patch('src.config.config_loader.config', config_loader):
            result = get_api_key()
            assert result == "test-api-key"
    
    def test_get_api_url_function(self, config_loader):
        """Test get_api_url convenience function."""
        with patch('src.config.config_loader.config', config_loader):
            result = get_api_url()
            assert result == "http://www.omdbapi.com/"


class TestConfigValidation:
    """Test suite for configuration validation."""
    
    def test_missing_required_api_key(self):
        """Test behavior when API key is missing."""
        config_data = {
            "api": {
                "omdb_base_url": "http://www.omdbapi.com/"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            api_key = loader.get_api_key()
            assert api_key is None or api_key == ""
        finally:
            os.unlink(temp_path)
    
    def test_malformed_config_structure(self):
        """Test behavior with malformed configuration structure."""
        config_data = {
            "api": "not_a_dict",
            "app": {
                "name": "Test App"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            # Should handle gracefully and return None for invalid paths
            result = loader.get('api.omdb_api_key')
            assert result is None
        finally:
            os.unlink(temp_path)
