"""
Pipeline integration module for easy programmatic use.
簡単なプログラム使用のためのパイプライン統合モジュール

This module provides a clean, production-ready API for integrating the scraper
into extraction pipelines. It includes:
このモジュールは、スクレイパーを抽出パイプラインに統合するための
クリーンで本番環境対応のAPIを提供します。以下を含みます：
- Callback support for progress tracking
  - 進捗追跡のためのコールバックサポート
- Metadata inclusion in output
  - 出力へのメタデータの含め
- Batch processing support
  - バッチ処理サポート
- Easy error handling
  - 簡単なエラーハンドリング
- Status monitoring
  - ステータス監視
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import json
from .scraper import Scraper
from .logger import setup_logger
from .config import Config


# Constants
DEFAULT_SCRAPER_VERSION = "1.0.0"  # Scraper version for metadata
DEFAULT_PLATFORM = "pickyou"  # Platform identifier


class PipelineScraper:
    """
    Pipeline-friendly scraper wrapper.
    
    Provides a clean API for integration into extraction pipelines with:
    - Callback support for progress tracking
    - Metadata inclusion in output
    - Batch processing support
    - Easy error handling
    - Status monitoring
    
    Example:
        >>> from src.pipeline import PipelineScraper
        >>> from src.config import Config
        >>> 
        >>> config = Config(delay=2.0)
        >>> pipeline = PipelineScraper(config=config)
        >>> result = pipeline.scrape_with_metadata()
        >>> 
        >>> if result['success']:
        ...     print(f"Scraped {result['metadata']['statistics']['products_transformed']} products")
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        logger=None,
        on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_batch: Optional[Callable[[List[Dict[str, Any]]], None]] = None
    ):
        """
        Initialize pipeline scraper with configuration and callbacks.
        
        Args:
            config: Configuration object (uses defaults if None)
            logger: Logger instance (creates default if None)
            on_progress: Optional callback function called with progress updates
                        Receives dictionary with statistics
            on_batch: Optional callback function called with each batch of products
                     Receives list of transformed products
        """
        self.config = config or Config()
        self.logger = logger or setup_logger()
        self.on_progress = on_progress
        self.on_batch = on_batch
        
        # Initialize the underlying scraper with configuration
        self.scraper = Scraper(
            base_url=self.config['base_url'],
            limit=self.config['limit'],
            delay=self.config['delay'],
            logger=self.logger
        )
    
    def scrape(
        self,
        output_file: Optional[str] = None,
        include_metadata: bool = True,
        return_data: bool = False
    ) -> Dict[str, Any]:
        """
        Scrape products and return results with metadata.
        
        This is the main scraping method that returns a comprehensive result
        dictionary with success status, timing information, and statistics.
        
        Args:
            output_file: Output file path (uses config default if None)
            include_metadata: Whether to include metadata (currently always True)
            return_data: If True, includes the full data in the result dictionary
                        (useful for in-memory processing without re-reading file)
        
        Returns:
            Dictionary with structure:
            {
                "success": bool,
                "timestamp": str (ISO format),
                "duration_seconds": float,
                "output_file": str,
                "statistics": dict,
                "data": dict (only if return_data=True)
            }
            
        Example:
            >>> pipeline = PipelineScraper()
            >>> result = pipeline.scrape(return_data=True)
            >>> if result['success']:
            ...     products = result['data']['items']
            ...     print(f"Scraped {len(products)} products in {result['duration_seconds']:.2f}s")
        """
        output_file = output_file or self.config['output_file']
        start_time = datetime.now()
        
        # Run the scraper
        success = self.scraper.scrape_and_save(output_file)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Prepare result dictionary
        result = {
            "success": success,
            "timestamp": end_time.isoformat(),
            "duration_seconds": duration,
            "output_file": output_file,
            "statistics": self.scraper.stats.copy()
        }
        
        # Optionally load and include data in result
        if return_data:
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    result["data"] = data
            except Exception as e:
                self.logger.error(f"Error loading output file: {e}")
                result["data"] = None
        
        return result
    
    def scrape_with_metadata(
        self,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scrape products and save with metadata included in output file.
        
        This method saves the scraped data with metadata embedded in the JSON file.
        The metadata includes timestamp, duration, statistics, and version information.
        This is useful for tracking when data was scraped and how the scraping performed.
        
        Args:
            output_file: Output file path (uses config default if None)
            
        Returns:
            Dictionary with structure:
            {
                "success": bool,
                "output_file": str,
                "metadata": dict (if successful)
                "error": str (if failed)
            }
            
        Example:
            >>> pipeline = PipelineScraper()
            >>> result = pipeline.scrape_with_metadata("data/products.json")
            >>> if result['success']:
            ...     print(f"Metadata: {result['metadata']}")
        """
        output_file = output_file or self.config['output_file']
        start_time = datetime.now()
        
        # Run the scraper
        success = self.scraper.scrape_and_save(output_file)
        
        if not success:
            return {"success": False, "error": "Scraping failed"}
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Load the scraped data
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading output file: {e}")
            return {"success": False, "error": str(e)}
        
        # Prepare metadata to embed in the file
        metadata = {
            "scraping_metadata": {
                "timestamp": end_time.isoformat(),
                "duration_seconds": duration,
                "scraper_version": DEFAULT_SCRAPER_VERSION,
                "platform": DEFAULT_PLATFORM,
                "base_url": self.config['base_url'],
                "statistics": self.scraper.stats.copy()
            }
        }
        
        # Merge metadata with data (metadata first so it appears at top of JSON)
        output_data = {**metadata, **data}
        
        # Save file with embedded metadata
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved data with metadata to {output_file}")
        except Exception as e:
            self.logger.error(f"Error saving file with metadata: {e}")
            return {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "output_file": output_file,
            "metadata": metadata["scraping_metadata"]
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current scraper status and configuration.
        
        Useful for monitoring and health checks in production pipelines.
        
        Returns:
            Dictionary with structure:
            {
                "config": dict,
                "statistics": dict,
                "ready": bool
            }
            
        Example:
            >>> pipeline = PipelineScraper()
            >>> status = pipeline.get_status()
            >>> print(f"Ready: {status['ready']}")
            >>> print(f"Config: {status['config']}")
        """
        return {
            "config": self.config.to_dict(),
            "statistics": self.scraper.stats.copy(),
            "ready": True
        }


def scrape_products(
    output_file: str = "data/pickyou_products.json",
    base_url: str = "https://pickyou.co.jp",
    **kwargs
) -> Dict[str, Any]:
    """
    Quick function to scrape products (for simple integrations).
    
    This is a convenience function for simple use cases where you don't need
    the full PipelineScraper class. It creates a scraper, runs it, and
    returns the result.
    
    Args:
        output_file: Output file path
        base_url: Base URL of Shopify store
        **kwargs: Additional scraper configuration options
                 (e.g., delay=2.0, limit=100)
        
    Returns:
        Dictionary with scraping results (same format as PipelineScraper.scrape())
        
    Example:
        >>> from src.pipeline import scrape_products
        >>> result = scrape_products(
        ...     output_file="data/products.json",
        ...     delay=2.0
        ... )
        >>> if result['success']:
        ...     print(f"Success! Scraped {result['statistics']['products_transformed']} products")
    """
    # Create configuration with provided values
    config = Config()
    config['output_file'] = output_file
    config['base_url'] = base_url
    config.update(kwargs)
    
    # Create and run pipeline scraper
    pipeline_scraper = PipelineScraper(config=config)
    return pipeline_scraper.scrape(return_data=False)
