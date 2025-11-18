"""
Configuration management for the scraper.

This module provides a flexible configuration system that supports:
- Default configuration values
- Loading from JSON files
- Runtime overrides
- Easy access via dictionary-like interface
"""

import json
import os
from typing import Dict, Any, Optional


# Default configuration values
# These are used when no config file or overrides are provided
DEFAULT_CONFIG = {
    "base_url": "https://pickyou.co.jp",
    "limit": 250,  # Products per page (Shopify maximum)
    "delay": 1.0,  # Delay between requests in seconds
    "output_file": "data/pickyou_products.json",
    "max_retries": 3,  # HTTP request retry attempts
    "timeout": 30,  # HTTP request timeout in seconds
    "batch_size": 1000,  # For future batch processing features
    "save_checkpoints": True,  # For future checkpoint/resume features
    "checkpoint_dir": "data/checkpoints",  # For future checkpoint features
    "include_metadata": True,  # Include metadata in output
    "log_level": "INFO"  # Logging level
}


class Config:
    """
    Configuration manager for scraper settings.
    
    Provides a dictionary-like interface for accessing configuration values
    with support for defaults, file loading, and runtime overrides.
    
    Example:
        >>> # Use defaults
        >>> config = Config()
        >>> print(config['base_url'])  # "https://pickyou.co.jp"
        
        >>> # Load from file
        >>> config = Config(config_file="config.json")
        
        >>> # Override values
        >>> config = Config(delay=2.0, limit=100)
        >>> print(config['delay'])  # 2.0
    """
    
    def __init__(self, config_file: Optional[str] = None, **kwargs):
        """
        Initialize configuration with defaults, file, and overrides.
        
        Configuration is loaded in this order (later overrides earlier):
        1. Default values
        2. Values from config file (if provided)
        3. Values from kwargs (if provided)
        
        Args:
            config_file: Optional path to JSON configuration file
            **kwargs: Configuration values to override
        
        Raises:
            ValueError: If config file exists but cannot be loaded
        """
        # Start with default configuration
        self.config = DEFAULT_CONFIG.copy()
        
        # Load from file if provided
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        
        # Override with kwargs (highest priority)
        self.config.update(kwargs)
    
    def load_from_file(self, config_file: str) -> None:
        """
        Load configuration from JSON file.
        
        Merges file configuration with existing configuration.
        File values override defaults but can be overridden by kwargs.
        
        Args:
            config_file: Path to JSON configuration file
            
        Raises:
            ValueError: If file cannot be read or parsed
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                # Merge file config into existing config
                self.config.update(file_config)
        except Exception as e:
            raise ValueError(f"Error loading config file {config_file}: {e}")
    
    def save_to_file(self, config_file: str) -> None:
        """
        Save current configuration to JSON file.
        
        Creates parent directories if needed. Useful for creating
        example config files or saving current settings.
        
        Args:
            config_file: Path where to save the configuration file
        """
        # Create parent directory if it doesn't exist
        dir_path = os.path.dirname(config_file) or '.'
        os.makedirs(dir_path, exist_ok=True)
        
        # Write configuration to file
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with optional default.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """
        Get configuration value using bracket notation.
        
        Allows dictionary-like access: config['base_url']
        
        Args:
            key: Configuration key
            
        Returns:
            Configuration value
            
        Raises:
            KeyError: If key doesn't exist
        """
        return self.config[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set configuration value using bracket notation.
        
        Allows dictionary-like assignment: config['delay'] = 2.0
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def update(self, other: Dict[str, Any]) -> None:
        """
        Update configuration with values from dictionary.
        
        Args:
            other: Dictionary of configuration values to merge
        """
        self.config.update(other)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Return configuration as dictionary (copy).
        
        Returns:
            Copy of current configuration dictionary
        """
        return self.config.copy()
