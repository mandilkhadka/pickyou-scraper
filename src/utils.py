"""Utility functions for HTTP requests and file I/O"""

import json
import os
import time
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def make_request(
    url: str,
    max_retries: int = 3,
    retry_backoff: float = 1.0,
    timeout: int = 30
) -> Optional[Dict[str, Any]]:
    """
    Make HTTP request with retry logic and error handling.
    
    Args:
        url: URL to fetch
        max_retries: Maximum number of retry attempts
        retry_backoff: Backoff multiplier for retries
        timeout: Request timeout in seconds
        
    Returns:
        JSON response as dictionary, or None if request fails
    """
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=retry_backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Error fetching {url}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response from {url}: {e}")
        return None


def ensure_data_dir(data_dir: str = "data") -> None:
    """
    Create data directory if it doesn't exist.
    
    Args:
        data_dir: Path to data directory
    """
    os.makedirs(data_dir, exist_ok=True)


def save_json(data: Dict[str, Any], filepath: str, indent: int = 2) -> bool:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save (dictionary)
        filepath: Path to output file
        indent: JSON indentation level
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists (only if filepath has a directory component)
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        print(f"Successfully saved {len(data.get('items', []))} items to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving JSON to {filepath}: {e}")
        return False

