"""Unit tests for logger functionality"""

import logging
import os
import pytest
import tempfile
from src.logger import setup_logger, UserFormatter, DEFAULT_LOGGER_NAME


class TestLogger:
    """Test cases for logger setup"""
    
    def test_setup_logger_default(self):
        """Test logger setup with default parameters"""
        logger = setup_logger()
        
        assert logger is not None
        assert logger.name == DEFAULT_LOGGER_NAME
        assert logger.level == logging.INFO
        assert len(logger.handlers) >= 1  # At least console handler
    
    def test_setup_logger_custom_level(self):
        """Test logger setup with custom level"""
        logger = setup_logger(level=logging.DEBUG)
        
        assert logger.level == logging.DEBUG
    
    def test_setup_logger_with_file(self):
        """Test logger setup with file handler"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name
        
        try:
            logger = setup_logger(log_file=log_file)
            
            assert len(logger.handlers) >= 2  # Console + file handler
            assert os.path.exists(log_file)
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    def test_setup_logger_custom_user(self):
        """Test logger setup with custom user"""
        logger = setup_logger(user="test_user")
        
        assert logger.name == "test_user"
    
    def test_setup_logger_multiple_calls(self):
        """Test that multiple calls don't duplicate handlers"""
        logger1 = setup_logger()
        handler_count1 = len(logger1.handlers)
        
        logger2 = setup_logger()
        handler_count2 = len(logger2.handlers)
        
        # Should have same number of handlers (handlers cleared and re-added)
        assert handler_count1 == handler_count2
    
    def test_setup_logger_logging_levels(self):
        """Test logger with different logging levels"""
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
        
        for level in levels:
            logger = setup_logger(level=level)
            assert logger.level == level
    
    def test_setup_logger_file_encoding(self):
        """Test that file handler uses UTF-8 encoding"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name
        
        try:
            logger = setup_logger(log_file=log_file)
            
            # Log a message with unicode characters
            logger.info("Test message with 日本語 characters")
            
            # Verify file was created and contains the message
            assert os.path.exists(log_file)
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "日本語" in content
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    def test_setup_logger_console_output(self):
        """Test that console handler is always added"""
        logger = setup_logger()
        
        # Should have at least one StreamHandler (console)
        stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(stream_handlers) >= 1


class TestUserFormatter:
    """Test cases for UserFormatter class"""
    
    def test_user_formatter_adds_user(self):
        """Test that UserFormatter adds user to log record"""
        formatter = UserFormatter('%(user)s - %(message)s')
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        # Should contain user information
        assert formatted is not None
        assert len(formatted) > 0
    
    def test_user_formatter_format(self):
        """Test UserFormatter format method"""
        formatter = UserFormatter('%(levelname)s - %(message)s')
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        assert "INFO" in formatted
        assert "Test" in formatted

