"""
Utility functions for HTTP requests and file I/O operations.

This module provides reusable functions for:
- Making HTTP requests with retry logic
- File system operations
- JSON file handling
"""

import json
import os
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Constants
DEFAULT_TIMEOUT = 30  # Default HTTP request timeout in seconds
DEFAULT_MAX_RETRIES = 3  # Default number of retry attempts
DEFAULT_RETRY_BACKOFF = 1.0  # Default backoff multiplier for retries
DEFAULT_JSON_INDENT = 2  # Default JSON indentation for pretty printing

# HTTP status codes that should trigger a retry
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]  # Rate limit and server errors

# User agent string to identify our scraper
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def make_request(
    url: str,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_backoff: float = DEFAULT_RETRY_BACKOFF,
    timeout: int = DEFAULT_TIMEOUT,
    logger: Optional[Any] = None
) -> Optional[Dict[str, Any]]:
    """
    Make HTTP GET request with automatic retry logic and error handling.
    
    This function implements robust HTTP request handling with:
    - Automatic retries for transient failures
    - Exponential backoff between retries
    - Proper error logging
    - JSON response parsing
    
    Args:
        url: URL to fetch
        max_retries: Maximum number of retry attempts (default: 3)
        retry_backoff: Backoff multiplier for exponential backoff (default: 1.0)
        timeout: Request timeout in seconds (default: 30)
        logger: Optional logger instance for error logging
        
    Returns:
        JSON response parsed as dictionary, or None if request fails.
        
    Example:
        >>> response = make_request("https://api.example.com/data")
        >>> if response:
        ...     print(response["key"])
    """
    # Create a session for connection pooling and retry configuration
    session = requests.Session()
    
    # Configure retry strategy
    # This automatically retries on specific HTTP status codes
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=retry_backoff,  # Exponential backoff: 1s, 2s, 4s, etc.
        status_forcelist=RETRY_STATUS_CODES,  # Retry on these status codes
        allowed_methods=["GET"]  # Only retry GET requests (safe to retry)
    )
    
    # Mount the adapter to handle retries
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set user agent to identify our scraper
    headers = {
        "User-Agent": USER_AGENT
    }
    
    try:
        # Make the HTTP GET request
        response = session.get(url, headers=headers, timeout=timeout)
        
        # Raise an exception for bad status codes (4xx, 5xx)
        response.raise_for_status()
        
        # Parse and return JSON response
        return response.json()
        
    except (requests.exceptions.RequestException, Exception) as e:
        # Handle all request-related exceptions
        error_msg = f"Error fetching {url}: {e}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        return None
        
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors (response wasn't valid JSON)
        error_msg = f"Error parsing JSON response from {url}: {e}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        return None


def ensure_data_dir(data_dir: str = "data") -> None:
    """
    Create data directory if it doesn't exist.
    
    This is a convenience function to ensure the output directory exists
    before attempting to save files. Uses os.makedirs with exist_ok=True
    to avoid errors if directory already exists.
    
    Args:
        data_dir: Path to data directory (default: "data")
        
    Example:
        >>> ensure_data_dir("output/data")
        >>> # Now safe to save files to output/data/
    """
    os.makedirs(data_dir, exist_ok=True)


def save_json(
    data: Dict[str, Any], 
    filepath: str, 
    indent: int = DEFAULT_JSON_INDENT,
    logger: Optional[Any] = None
) -> bool:
    """
    Save data dictionary to JSON file with proper error handling.
    
    This function handles:
    - Creating parent directories if needed
    - UTF-8 encoding for international characters
    - Pretty printing with indentation
    - Error logging
    
    Args:
        data: Data dictionary to save
        filepath: Path to output JSON file
        indent: JSON indentation level for pretty printing (default: 2)
        logger: Optional logger instance for logging
        
    Returns:
        True if file was saved successfully, False otherwise.
        
    Example:
        >>> data = {"items": [{"id": 1, "name": "Product"}]}
        >>> success = save_json(data, "output/products.json")
        >>> if success:
        ...     print("File saved successfully")
    """
    try:
        # Create parent directory if filepath includes directories
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # Write JSON file with UTF-8 encoding and pretty printing
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        # Log success message
        item_count = len(data.get('items', []))
        success_msg = f"Successfully saved {item_count} items to {filepath}"
        if logger:
            logger.info(success_msg)
        else:
            print(success_msg)
        
        return True
        
    except Exception as e:
        # Log error and return False on failure
        error_msg = f"Error saving JSON to {filepath}: {e}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        return False
