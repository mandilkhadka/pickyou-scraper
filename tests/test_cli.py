"""Unit tests for CLI functionality"""

import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.cli import create_parser, main


class TestCLI:
    """Test cases for CLI functions"""
    
    def test_create_parser(self):
        """Test parser creation"""
        parser = create_parser()
        
        assert parser is not None
        # Test that parser has expected arguments
        args = parser.parse_args([])
        assert args.base_url == "https://pickyou.co.jp"
        assert args.output == "data/pickyou_products.json"
        assert args.limit == 250
        assert args.delay == 1.0
    
    def test_parser_base_url_argument(self):
        """Test --base-url argument"""
        parser = create_parser()
        args = parser.parse_args(["--base-url", "https://custom.com"])
        
        assert args.base_url == "https://custom.com"
    
    def test_parser_output_argument(self):
        """Test --output argument"""
        parser = create_parser()
        args = parser.parse_args(["--output", "custom.json"])
        
        assert args.output == "custom.json"
    
    def test_parser_output_short_argument(self):
        """Test -o short argument"""
        parser = create_parser()
        args = parser.parse_args(["-o", "short.json"])
        
        assert args.output == "short.json"
    
    def test_parser_limit_argument(self):
        """Test --limit argument"""
        parser = create_parser()
        args = parser.parse_args(["--limit", "100"])
        
        assert args.limit == 100
    
    def test_parser_delay_argument(self):
        """Test --delay argument"""
        parser = create_parser()
        args = parser.parse_args(["--delay", "2.5"])
        
        assert args.delay == 2.5
    
    def test_parser_config_argument(self):
        """Test --config argument"""
        parser = create_parser()
        args = parser.parse_args(["--config", "config.json"])
        
        assert args.config == "config.json"
    
    def test_parser_config_short_argument(self):
        """Test -c short argument"""
        parser = create_parser()
        args = parser.parse_args(["-c", "config.json"])
        
        assert args.config == "config.json"
    
    def test_parser_verbose_argument(self):
        """Test --verbose argument"""
        parser = create_parser()
        args = parser.parse_args(["--verbose"])
        
        assert args.verbose is True
    
    def test_parser_verbose_short_argument(self):
        """Test -v short argument"""
        parser = create_parser()
        args = parser.parse_args(["-v"])
        
        assert args.verbose is True
    
    def test_parser_quiet_argument(self):
        """Test --quiet argument"""
        parser = create_parser()
        args = parser.parse_args(["--quiet"])
        
        assert args.quiet is True
    
    def test_parser_quiet_short_argument(self):
        """Test -q short argument"""
        parser = create_parser()
        args = parser.parse_args(["-q"])
        
        assert args.quiet is True
    
    def test_parser_log_file_argument(self):
        """Test --log-file argument"""
        parser = create_parser()
        args = parser.parse_args(["--log-file", "app.log"])
        
        assert args.log_file == "app.log"
    
    @patch('src.cli.setup_logger')
    @patch('src.cli.Config')
    @patch('src.cli.Scraper')
    @patch('sys.exit')
    def test_main_success(self, mock_exit, mock_scraper_class, mock_config_class, mock_setup_logger):
        """Test main function with successful scraping"""
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        
        mock_config = MagicMock()
        mock_config.__getitem__ = Mock(side_effect=lambda key: {
            "base_url": "https://pickyou.co.jp",
            "output_file": "data/pickyou_products.json",
            "limit": 250,
            "delay": 1.0
        }[key])
        mock_config.get = Mock(side_effect=lambda key, default=None: {
            "base_url": "https://pickyou.co.jp",
            "output_file": "data/pickyou_products.json",
            "limit": 250,
            "delay": 1.0,
            "batch_size": 1000,
            "save_checkpoints": True,
            "checkpoint_dir": "data/checkpoints",
            "checkpoint_interval": 1000,
            "circuit_breaker_enabled": True,
            "circuit_breaker_failure_threshold": 10,
            "circuit_breaker_timeout": 60,
            "stream_to_disk": True
        }.get(key, default))
        mock_config_class.return_value = mock_config
        
        mock_scraper = Mock()
        mock_scraper.scrape_and_save.return_value = True
        mock_scraper_class.return_value = mock_scraper
        
        with patch('sys.argv', ['cli.py']):
            main()
        
        mock_exit.assert_called_once_with(0)
    
    @patch('src.cli.setup_logger')
    @patch('src.cli.Config')
    @patch('src.cli.Scraper')
    @patch('sys.exit')
    def test_main_failure(self, mock_exit, mock_scraper_class, mock_config_class, mock_setup_logger):
        """Test main function with failed scraping"""
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        
        mock_config = MagicMock()
        mock_config.__getitem__ = Mock(side_effect=lambda key: {
            "base_url": "https://pickyou.co.jp",
            "output_file": "data/pickyou_products.json",
            "limit": 250,
            "delay": 1.0
        }[key])
        mock_config.get = Mock(side_effect=lambda key, default=None: {
            "base_url": "https://pickyou.co.jp",
            "output_file": "data/pickyou_products.json",
            "limit": 250,
            "delay": 1.0,
            "batch_size": 1000,
            "save_checkpoints": True,
            "checkpoint_dir": "data/checkpoints",
            "checkpoint_interval": 1000,
            "circuit_breaker_enabled": True,
            "circuit_breaker_failure_threshold": 10,
            "circuit_breaker_timeout": 60,
            "stream_to_disk": True
        }.get(key, default))
        mock_config_class.return_value = mock_config
        
        mock_scraper = Mock()
        mock_scraper.scrape_and_save.return_value = False
        mock_scraper.shutdown_requested = False  # Mock the shutdown_requested attribute
        mock_scraper_class.return_value = mock_scraper
        
        with patch('sys.argv', ['cli.py']):
            main()
        
        # Exit should be called with code 1 for failure
        assert mock_exit.called
        # Check if exit(1) was called (may be called multiple times)
        exit_calls = [call[0][0] for call in mock_exit.call_args_list]
        assert 1 in exit_calls
        mock_logger.error.assert_called()
    
    @patch('src.cli.setup_logger')
    @patch('src.cli.Config')
    @patch('src.cli.Scraper')
    def test_main_verbose_logging(self, mock_scraper_class, mock_config_class, mock_setup_logger):
        """Test main function with verbose logging"""
        import logging
        
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        
        mock_config = MagicMock()
        mock_config.__getitem__ = Mock(side_effect=lambda key: {
            "base_url": "https://pickyou.co.jp",
            "output_file": "data/pickyou_products.json",
            "limit": 250,
            "delay": 1.0
        }[key])
        mock_config.get = Mock(side_effect=lambda key, default=None: {
            "base_url": "https://pickyou.co.jp",
            "output_file": "data/pickyou_products.json",
            "limit": 250,
            "delay": 1.0,
            "batch_size": 1000,
            "save_checkpoints": True,
            "checkpoint_dir": "data/checkpoints",
            "checkpoint_interval": 1000,
            "circuit_breaker_enabled": True,
            "circuit_breaker_failure_threshold": 10,
            "circuit_breaker_timeout": 60,
            "stream_to_disk": True
        }.get(key, default))
        mock_config_class.return_value = mock_config
        
        mock_scraper = Mock()
        mock_scraper.scrape_and_save.return_value = True
        mock_scraper_class.return_value = mock_scraper
        
        with patch('sys.argv', ['cli.py', '--verbose']):
            with patch('sys.exit'):
                main()
        
        # Verify logger was set up with DEBUG level
        mock_setup_logger.assert_called_once()
        call_args = mock_setup_logger.call_args
        assert call_args[1]['level'] == logging.DEBUG
    
    @patch('src.cli.setup_logger')
    @patch('src.cli.Config')
    @patch('src.cli.Scraper')
    def test_main_quiet_logging(self, mock_scraper_class, mock_config_class, mock_setup_logger):
        """Test main function with quiet logging"""
        import logging
        
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        
        mock_config = MagicMock()
        mock_config.__getitem__ = Mock(side_effect=lambda key: {
            "base_url": "https://pickyou.co.jp",
            "output_file": "data/pickyou_products.json",
            "limit": 250,
            "delay": 1.0
        }[key])
        mock_config.get = Mock(side_effect=lambda key, default=None: {
            "base_url": "https://pickyou.co.jp",
            "output_file": "data/pickyou_products.json",
            "limit": 250,
            "delay": 1.0,
            "batch_size": 1000,
            "save_checkpoints": True,
            "checkpoint_dir": "data/checkpoints",
            "checkpoint_interval": 1000,
            "circuit_breaker_enabled": True,
            "circuit_breaker_failure_threshold": 10,
            "circuit_breaker_timeout": 60,
            "stream_to_disk": True
        }.get(key, default))
        mock_config_class.return_value = mock_config
        
        mock_scraper = Mock()
        mock_scraper.scrape_and_save.return_value = True
        mock_scraper_class.return_value = mock_scraper
        
        with patch('sys.argv', ['cli.py', '--quiet']):
            with patch('sys.exit'):
                main()
        
        # Verify logger was set up with WARNING level
        mock_setup_logger.assert_called_once()
        call_args = mock_setup_logger.call_args
        assert call_args[1]['level'] == logging.WARNING
    
    @patch('src.cli.setup_logger')
    @patch('src.cli.Config')
    @patch('src.cli.Scraper')
    def test_main_config_override(self, mock_scraper_class, mock_config_class, mock_setup_logger):
        """Test that CLI arguments override config"""
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        
        mock_config = MagicMock()
        mock_config.__getitem__ = Mock(side_effect=lambda key: {
            "base_url": "https://pickyou.co.jp",
            "output_file": "data/pickyou_products.json",
            "limit": 250,
            "delay": 1.0
        }[key])
        mock_config.get = Mock(side_effect=lambda key, default=None: {
            "base_url": "https://pickyou.co.jp",
            "output_file": "data/pickyou_products.json",
            "limit": 250,
            "delay": 1.0,
            "batch_size": 1000,
            "save_checkpoints": True,
            "checkpoint_dir": "data/checkpoints",
            "checkpoint_interval": 1000,
            "circuit_breaker_enabled": True,
            "circuit_breaker_failure_threshold": 10,
            "circuit_breaker_timeout": 60,
            "stream_to_disk": True
        }.get(key, default))
        mock_config_class.return_value = mock_config
        
        mock_scraper = Mock()
        mock_scraper.scrape_and_save.return_value = True
        mock_scraper_class.return_value = mock_scraper
        
        with patch('sys.argv', ['cli.py', '--delay', '5.0', '--limit', '100']):
            with patch('sys.exit'):
                main()
        
        # Verify config was updated
        assert mock_config.__setitem__.call_count >= 2

