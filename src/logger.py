"""
Logging configuration for the scraper.
スクレイパーのログ設定

This module provides a centralized logging setup that can be used throughout
the application. It supports both console and file logging with configurable
log levels.
このモジュールは、アプリケーション全体で使用できる集中型ログ設定を提供します。
設定可能なログレベルでコンソールとファイルの両方のログをサポートします。
"""

import logging
import sys
import getpass
from typing import Optional


# Default logger user / デフォルトのロガーユーザー
DEFAULT_LOGGER_NAME = "pickyou_scraper"

# Default log format / デフォルトのログ形式
LOG_FORMAT = '%(asctime)s - %(user)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class UserFormatter(logging.Formatter):
    """Custom formatter that adds user information to log records."""
    
    def format(self, record):
        # Add user to the log record
        record.user = getpass.getuser()
        return super().format(record)


def setup_logger(
    user: str = DEFAULT_LOGGER_NAME,
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up and configure logger with console and optional file handlers.
    
    This function creates a logger with:
    - Console output (stdout) for real-time monitoring
    - Optional file output for persistent logging
    - Formatted messages with timestamps
    - UTF-8 encoding for international characters
    
    Args:
        user: Logger user (default: "pickyou_scraper")
        level: Logging level (default: logging.INFO)
               Use logging.DEBUG for verbose, logging.WARNING for quiet
        log_file: Optional file path for file logging (default: None)
                  If provided, logs will also be written to this file
        
    Returns:
        Configured logger instance ready to use.
        
    Example:
        >>> logger = setup_logger(level=logging.DEBUG)
        >>> logger.info("This is an info message")
        >>> logger.error("This is an error message")
        
        >>> # With file logging
        >>> logger = setup_logger(log_file="logs/scraper.log")
        >>> logger.info("This will be logged to both console and file")
    """
    # Get or create logger
    logger = logging.getLogger(user)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    # This is important if setup_logger is called multiple times
    logger.handlers.clear()
    
    # Create formatter for log messages with user support
    formatter = UserFormatter(
        LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    
    # Console handler - always add this for real-time output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler - only add if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
