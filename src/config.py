"""Configuration management for the scraper"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for scraper settings"""
    
    DEFAULT_CONFIG = {
        "base_url": "https://pickyou.co.jp",
        "limit": 250,
        "delay": 1.0,
        "output_file": "data/pickyou_products.json",
        "max_retries": 3,
        "timeout": 30,
        "batch_size": 1000,
        "save_checkpoints": True,
        "checkpoint_dir": "data/checkpoints",
        "include_metadata": True,
        "log_level": "INFO"
    }
    
    def __init__(self, config_file: Optional[str] = None, **kwargs):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to JSON config file
            **kwargs: Override config values
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Load from file if provided
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        
        # Override with kwargs
        self.config.update(kwargs)
    
    def load_from_file(self, config_file: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                self.config.update(file_config)
        except Exception as e:
            raise ValueError(f"Error loading config file {config_file}: {e}")
    
    def save_to_file(self, config_file: str) -> None:
        """Save current configuration to JSON file."""
        os.makedirs(os.path.dirname(config_file) or '.', exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """Get configuration value using bracket notation."""
        return self.config[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self.config.copy()

