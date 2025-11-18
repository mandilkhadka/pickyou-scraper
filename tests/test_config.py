"""Unit tests for configuration management"""

import json
import os
import pytest
import tempfile
from src.config import Config, DEFAULT_CONFIG


class TestConfig:
    """Test cases for Config class"""
    
    def test_config_defaults(self):
        """Test that config uses default values"""
        config = Config()
        
        assert config["base_url"] == "https://pickyou.co.jp"
        assert config["limit"] == 250
        assert config["delay"] == 1.0
        assert config["output_file"] == "data/pickyou_products.json"
    
    def test_config_kwargs_override(self):
        """Test that kwargs override defaults"""
        config = Config(delay=2.0, limit=100)
        
        assert config["delay"] == 2.0
        assert config["limit"] == 100
        assert config["base_url"] == "https://pickyou.co.jp"  # Default still used
    
    def test_config_load_from_file(self):
        """Test loading configuration from JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            file_config = {
                "base_url": "https://custom.com",
                "delay": 3.0
            }
            json.dump(file_config, f)
            temp_file = f.name
        
        try:
            config = Config(config_file=temp_file)
            
            assert config["base_url"] == "https://custom.com"
            assert config["delay"] == 3.0
            assert config["limit"] == 250  # Default value
        finally:
            os.unlink(temp_file)
    
    def test_config_file_and_kwargs(self):
        """Test that kwargs override file config"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            file_config = {
                "delay": 3.0,
                "limit": 100
            }
            json.dump(file_config, f)
            temp_file = f.name
        
        try:
            config = Config(config_file=temp_file, delay=5.0)
            
            assert config["delay"] == 5.0  # kwargs override file
            assert config["limit"] == 100  # From file
        finally:
            os.unlink(temp_file)
    
    def test_config_nonexistent_file(self):
        """Test that nonexistent config file doesn't cause error"""
        config = Config(config_file="nonexistent.json")
        
        # Should use defaults
        assert config["base_url"] == "https://pickyou.co.jp"
    
    def test_config_invalid_json_file(self):
        """Test that invalid JSON file raises error"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json {")
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError):
                Config(config_file=temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_config_get_method(self):
        """Test get method with default value"""
        config = Config()
        
        assert config.get("base_url") == "https://pickyou.co.jp"
        assert config.get("nonexistent", "default") == "default"
        assert config.get("nonexistent") is None
    
    def test_config_bracket_access(self):
        """Test dictionary-like bracket access"""
        config = Config()
        
        assert config["base_url"] == "https://pickyou.co.jp"
        
        # Test setting
        config["delay"] = 5.0
        assert config["delay"] == 5.0
    
    def test_config_bracket_access_missing_key(self):
        """Test that missing key raises KeyError"""
        config = Config()
        
        with pytest.raises(KeyError):
            _ = config["nonexistent_key"]
    
    def test_config_update(self):
        """Test update method"""
        config = Config()
        config.update({"delay": 10.0, "limit": 50})
        
        assert config["delay"] == 10.0
        assert config["limit"] == 50
        assert config["base_url"] == "https://pickyou.co.jp"  # Unchanged
    
    def test_config_to_dict(self):
        """Test to_dict method returns a copy"""
        config = Config(delay=5.0)
        config_dict = config.to_dict()
        
        assert config_dict["delay"] == 5.0
        assert isinstance(config_dict, dict)
        
        # Modify dict, should not affect config
        config_dict["delay"] = 10.0
        assert config["delay"] == 5.0
    
    def test_config_save_to_file(self):
        """Test saving configuration to file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "test_config.json")
            config = Config(delay=7.0, limit=150)
            config.save_to_file(config_file)
            
            assert os.path.exists(config_file)
            
            # Load and verify
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            assert loaded_config["delay"] == 7.0
            assert loaded_config["limit"] == 150
    
    def test_config_save_creates_directory(self):
        """Test that save_to_file creates parent directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "subdir", "test_config.json")
            config = Config()
            config.save_to_file(config_file)
            
            assert os.path.exists(config_file)
    
    def test_config_all_default_keys(self):
        """Test that all default config keys are present"""
        config = Config()
        
        for key in DEFAULT_CONFIG.keys():
            assert key in config.config
            assert config[key] == DEFAULT_CONFIG[key]
    
    def test_config_unicode_values(self):
        """Test config with unicode values"""
        config = Config()
        config["output_file"] = "data/产品.json"
        
        assert config["output_file"] == "data/产品.json"
        
        # Test saving and loading unicode
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "test_config.json")
            config.save_to_file(config_file)
            
            loaded_config = Config(config_file=config_file)
            assert loaded_config["output_file"] == "data/产品.json"

