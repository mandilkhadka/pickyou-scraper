"""
Utility functions for HTTP requests and file I/O operations.
HTTPリクエストとファイルI/O操作のためのユーティリティ関数

This module provides reusable functions for:
このモジュールは以下の再利用可能な関数を提供します：
- Making HTTP requests with retry logic
  - リトライロジック付きHTTPリクエストの作成
- File system operations
  - ファイルシステム操作
- JSON file handling
  - JSONファイルの処理
"""

import json
import os
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Constants / 定数
# Default HTTP request timeout in seconds / デフォルトのHTTPリクエストタイムアウト（秒）
DEFAULT_TIMEOUT = 30
# Default number of retry attempts / デフォルトのリトライ試行回数
DEFAULT_MAX_RETRIES = 3
# Default backoff multiplier for retries / リトライのデフォルトバックオフ乗数
DEFAULT_RETRY_BACKOFF = 1.0
# Default JSON indentation for pretty printing / 整形出力のためのデフォルトJSONインデント
DEFAULT_JSON_INDENT = 2

# HTTP status codes that should trigger a retry / リトライをトリガーすべきHTTPステータスコード
# Rate limit and server errors / レート制限とサーバーエラー
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]

# User agent string to identify our scraper / スクレイパーを識別するためのユーザーエージェント文字列
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
    自動リトライロジックとエラーハンドリング付きHTTP GETリクエストを作成
    
    This function implements robust HTTP request handling with:
    この関数は以下の堅牢なHTTPリクエスト処理を実装します：
    - Automatic retries for transient failures
      - 一時的な失敗の自動リトライ
    - Exponential backoff between retries
      - リトライ間の指数バックオフ
    - Proper error logging
      - 適切なエラーログ記録
    - JSON response parsing
      - JSONレスポンスの解析
    
    Args:
        url: URL to fetch / 取得するURL
        max_retries: Maximum number of retry attempts (default: 3) / 最大リトライ試行回数（デフォルト: 3）
        retry_backoff: Backoff multiplier for exponential backoff (default: 1.0) / 指数バックオフのバックオフ乗数（デフォルト: 1.0）
        timeout: Request timeout in seconds (default: 30) / リクエストタイムアウト（秒）（デフォルト: 30）
        logger: Optional logger instance for error logging / エラーログ記録用のオプションのロガーインスタンス
        
    Returns:
        JSON response parsed as dictionary, or None if request fails.
        JSONレスポンスを辞書として解析したもの、またはリクエストが失敗した場合はNone
        
    Example:
        >>> response = make_request("https://api.example.com/data")
        >>> if response:
        ...     print(response["key"])
    """
    # Create a session for connection pooling and retry configuration
    # 接続プーリングとリトライ設定のためのセッションを作成
    session = requests.Session()
    
    # Configure retry strategy / リトライ戦略を設定
    # This automatically retries on specific HTTP status codes
    # 特定のHTTPステータスコードで自動的にリトライします
    retry_strategy = Retry(
        total=max_retries,
        # Exponential backoff: 1s, 2s, 4s, etc. / 指数バックオフ: 1秒、2秒、4秒など
        backoff_factor=retry_backoff,
        # Retry on these status codes / これらのステータスコードでリトライ
        status_forcelist=RETRY_STATUS_CODES,
        # Only retry GET requests (safe to retry) / GETリクエストのみリトライ（安全にリトライ可能）
        allowed_methods=["GET"]
    )
    
    # Mount the adapter with retry strategy and connection pool limits
    # リトライ戦略と接続プール制限付きアダプターをマウント
    # Connection pool limits prevent excessive resource usage
    # 接続プール制限により過剰なリソース使用を防止
    # pool_connections: number of connection pools to cache
    # pool_connections: キャッシュする接続プールの数
    # pool_maxsize: maximum number of connections to save in the pool
    # pool_maxsize: プールに保存する最大接続数
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,  # Cache up to 10 connection pools / 最大10個の接続プールをキャッシュ
        pool_maxsize=20  # Maximum 20 connections per pool / プールあたり最大20接続
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set user agent to identify our scraper / スクレイパーを識別するためのユーザーエージェントを設定
    headers = {
        "User-Agent": USER_AGENT
    }
    
    try:
        # Make the HTTP GET request / HTTP GETリクエストを実行
        response = session.get(url, headers=headers, timeout=timeout)
        
        # Raise an exception for bad status codes (4xx, 5xx) / 悪いステータスコード（4xx、5xx）で例外を発生
        response.raise_for_status()
        
        # Parse and return JSON response / JSONレスポンスを解析して返す
        return response.json()
        
    except (requests.exceptions.RequestException, Exception) as e:
        # Handle all request-related exceptions / すべてのリクエスト関連の例外を処理
        error_msg = f"Error fetching {url}: {e}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        return None
        
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors (response wasn't valid JSON) / JSON解析エラーを処理（レスポンスが有効なJSONではなかった）
        error_msg = f"Error parsing JSON response from {url}: {e}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        return None


def ensure_data_dir(data_dir: str = "data") -> None:
    """
    Create data directory if it doesn't exist.
    データディレクトリが存在しない場合は作成
    
    This is a convenience function to ensure the output directory exists
    before attempting to save files. Uses os.makedirs with exist_ok=True
    to avoid errors if directory already exists.
    ファイルを保存する前に出力ディレクトリが存在することを確認する便利関数。
    os.makedirsにexist_ok=Trueを使用して、ディレクトリが既に存在する場合のエラーを回避します。
    
    Args:
        data_dir: Path to data directory (default: "data") / データディレクトリのパス（デフォルト: "data"）
        
    Example:
        >>> ensure_data_dir("output/data")
        >>> # Now safe to save files to output/data/
    """
    # Create directory if it doesn't exist (exist_ok=True prevents error if it exists)
    # ディレクトリが存在しない場合は作成（exist_ok=Trueにより既に存在する場合のエラーを防止）
    os.makedirs(data_dir, exist_ok=True)


def save_checkpoint(
    processed_ids: set,
    checkpoint_file: str,
    logger: Optional[Any] = None
) -> bool:
    """
    Save progress checkpoint to file.
    
    Saves processed product IDs to allow resuming from last checkpoint.
    
    Args:
        processed_ids: Set of processed product IDs
        checkpoint_file: Path to checkpoint file
        logger: Optional logger instance for logging
        
    Returns:
        True if checkpoint was saved successfully, False otherwise.
    """
    try:
        dir_path = os.path.dirname(checkpoint_file)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        checkpoint_data = {
            "processed_ids": list(processed_ids),
            "count": len(processed_ids)
        }
        
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        
        if logger:
            logger.debug(f"Checkpoint saved: {len(processed_ids)} products")
        
        return True
        
    except Exception as e:
        error_msg = f"Error saving checkpoint to {checkpoint_file}: {e}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        return False


def load_checkpoint(checkpoint_file: str, logger: Optional[Any] = None) -> set:
    """
    Load progress checkpoint from file.
    
    Args:
        checkpoint_file: Path to checkpoint file
        logger: Optional logger instance for logging
        
    Returns:
        Set of processed product IDs, or empty set if checkpoint doesn't exist.
    """
    try:
        if not os.path.exists(checkpoint_file):
            return set()
        
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            checkpoint_data = json.load(f)
        
        processed_ids = set(checkpoint_data.get("processed_ids", []))
        
        if logger:
            logger.info(f"Checkpoint loaded: {len(processed_ids)} products already processed")
        
        return processed_ids
        
    except Exception as e:
        error_msg = f"Error loading checkpoint from {checkpoint_file}: {e}"
        if logger:
            logger.warning(error_msg)
        else:
            print(error_msg)
        return set()


def stream_json_line(
    item: Dict[str, Any],
    filepath: str,
    is_first: bool = False,
    logger: Optional[Any] = None
) -> bool:
    """
    Stream a single item as JSON line to file (for memory-efficient appending).
    
    This function appends items one at a time to avoid loading everything in memory.
    Format: Each line is a JSON object (JSONL format).
    
    Args:
        item: Item dictionary to append
        filepath: Path to output file
        is_first: Whether this is the first item (determines if we need to open array)
        logger: Optional logger instance
        
    Returns:
        True if item was written successfully, False otherwise.
    """
    try:
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        mode = "w" if is_first else "a"
        with open(filepath, mode, encoding="utf-8") as f:
            if is_first:
                # Start JSON array format
                f.write('{"items": [\n')
                json.dump(item, f, ensure_ascii=False)
            else:
                f.write(",\n")
                json.dump(item, f, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        error_msg = f"Error streaming item to {filepath}: {e}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        return False


def finalize_streamed_json(filepath: str, logger: Optional[Any] = None) -> bool:
    """
    Finalize a streamed JSON file by closing the array.
    
    Args:
        filepath: Path to output file
        logger: Optional logger instance
        
    Returns:
        True if finalized successfully, False otherwise.
    """
    try:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write("\n]}\n")
        return True
        
    except Exception as e:
        error_msg = f"Error finalizing streamed JSON {filepath}: {e}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        return False


def save_json(
    data: Dict[str, Any], 
    filepath: str, 
    indent: int = DEFAULT_JSON_INDENT,
    logger: Optional[Any] = None
) -> bool:
    """
    Save data dictionary to JSON file with proper error handling.
    適切なエラーハンドリングでデータ辞書をJSONファイルに保存
    
    This function handles:
    この関数は以下を処理します：
    - Creating parent directories if needed
      - 必要に応じて親ディレクトリを作成
    - UTF-8 encoding for international characters
      - 国際文字のためのUTF-8エンコーディング
    - Pretty printing with indentation
      - インデント付きの整形出力
    - Error logging
      - エラーログ記録
    
    Args:
        data: Data dictionary to save / 保存するデータ辞書
        filepath: Path to output JSON file / 出力JSONファイルのパス
        indent: JSON indentation level for pretty printing (default: 2) / 整形出力のためのJSONインデントレベル（デフォルト: 2）
        logger: Optional logger instance for logging / ログ記録用のオプションのロガーインスタンス
        
    Returns:
        True if file was saved successfully, False otherwise.
        ファイルが正常に保存された場合はTrue、それ以外はFalse
        
    Example:
        >>> data = {"items": [{"id": 1, "name": "Product"}]}
        >>> success = save_json(data, "output/products.json")
        >>> if success:
        ...     print("File saved successfully")
    """
    try:
        # Create parent directory if filepath includes directories
        # ファイルパスにディレクトリが含まれている場合は親ディレクトリを作成
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # Write JSON file with UTF-8 encoding and pretty printing
        # UTF-8エンコーディングと整形出力でJSONファイルを書き込み
        # ensure_ascii=False allows Unicode characters (Japanese, etc.)
        # ensure_ascii=FalseによりUnicode文字（日本語など）が使用可能
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        # Log success message / 成功メッセージをログに記録
        item_count = len(data.get('items', []))
        success_msg = f"Successfully saved {item_count} items to {filepath}"
        if logger:
            logger.info(success_msg)
        else:
            print(success_msg)
        
        return True
        
    except Exception as e:
        # Log error and return False on failure / エラーをログに記録し、失敗時はFalseを返す
        error_msg = f"Error saving JSON to {filepath}: {e}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        return False
