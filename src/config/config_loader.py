#!/usr/bin/env python3
"""
Configuration loader for the Movie Search Application.
Handles loading configuration from JSON files and environment variables.
"""

import json
import os
from typing import Dict, Any, Optional

class ConfigLoader:
    """Configuration loader with environment variable override support."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_path (str): Path to the configuration file
        """
        if config_path is None:
            # Default to config.json in the same directory as this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, 'config.json')
        
        self.config_path = config_path
        self._config = None
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            print(f"✅ Configuration loaded from: {self.config_path}")
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {self.config_path}")
            self._config = self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in configuration file: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file loading fails."""
        return {
            "api": {
                "omdb_api_key": "your-api-key-here",
                "omdb_base_url": "http://www.omdbapi.com/",
                "timeout": 10,
                "max_retries": 3
            },
            "app": {
                "name": "Movie Search App",
                "version": "1.0.0",
                "debug": False,
                "host": "127.0.0.1",
                "port": 5000,
                "secret_key": "change-this-secret-key"
            },
            "features": {
                "enable_popular_movies": True,
                "enable_api_endpoints": True,
                "enable_sharing": True,
                "cache_duration": 3600
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path (str): Dot-separated path to the configuration key (e.g., 'api.omdb_api_key')
            default (Any): Default value if key is not found
            
        Returns:
            Any: Configuration value or default
        """
        # Check environment variable first (convert dots to underscores and uppercase)
        env_key = key_path.replace('.', '_').upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        # Navigate through the config dictionary
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_api_key(self) -> str:
        """Get the OMDb API key."""
        return self.get('api.omdb_api_key', '')
    
    def get_api_url(self) -> str:
        """Get the OMDb API base URL."""
        return self.get('api.omdb_base_url', 'http://www.omdbapi.com/')
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get Flask app configuration."""
        return {
            'DEBUG': self.get('app.debug', False),
            'SECRET_KEY': self.get('app.secret_key', 'change-this-secret-key'),
            'HOST': self.get('app.host', '127.0.0.1'),
            'PORT': self.get('app.port', 5000)
        }
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        return self.get(f'features.{feature}', False)
    
    def get_popular_movies(self) -> list:
        """Get the list of popular movies."""
        return self.get('popular_movies', [])
    
    def get_search_suggestions(self) -> list:
        """Get search suggestions for the UI."""
        return self.get('ui.search_suggestions', [])
    
    def update_config(self, key_path: str, value: Any) -> None:
        """
        Update configuration value and save to file.
        
        Args:
            key_path (str): Dot-separated path to the configuration key
            value (Any): New value to set
        """
        keys = key_path.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save to file
        self.save_config()
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuration saved to: {self.config_path}")
        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")

# Global configuration instance
config = ConfigLoader()

# Convenience functions
def get_config(key_path: str, default: Any = None) -> Any:
    """Get configuration value using dot notation."""
    return config.get(key_path, default)

def get_api_key() -> str:
    """Get the OMDb API key."""
    return config.get_api_key()

def get_api_url() -> str:
    """Get the OMDb API base URL."""
    return config.get_api_url()

def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled."""
    return config.is_feature_enabled(feature)
