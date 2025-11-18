"""
Pipeline integration module for easy programmatic use.

This module provides a clean API for integrating the scraper into extraction pipelines.
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import json
from .scraper import Scraper
from .logger import setup_logger
from .config import Config


class PipelineScraper:
    """
    Pipeline-friendly scraper wrapper.
    
    Provides a clean API for integration into extraction pipelines with:
    - Callback support for progress tracking
    - Metadata inclusion in output
    - Batch processing support
    - Easy error handling
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        logger=None,
        on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_batch: Optional[Callable[[List[Dict[str, Any]]], None]] = None
    ):
        """
        Initialize pipeline scraper.
        
        Args:
            config: Configuration object (optional)
            logger: Logger instance (optional)
            on_progress: Callback function called with progress updates
            on_batch: Callback function called with each batch of products
        """
        self.config = config or Config()
        self.logger = logger or setup_logger()
        self.on_progress = on_progress
        self.on_batch = on_batch
        
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
        
        Args:
            output_file: Output file path (uses config default if None)
            include_metadata: Include scraping metadata in output
            return_data: Return data in addition to saving to file
            
        Returns:
            Dictionary with scraping results and metadata
        """
        output_file = output_file or self.config['output_file']
        start_time = datetime.now()
        
        # Run scraper
        success = self.scraper.scrape_and_save(output_file)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Prepare result
        result = {
            "success": success,
            "timestamp": end_time.isoformat(),
            "duration_seconds": duration,
            "output_file": output_file,
            "statistics": self.scraper.stats.copy()
        }
        
        # Load data if requested
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
        
        Args:
            output_file: Output file path (uses config default if None)
            
        Returns:
            Dictionary with scraping results
        """
        output_file = output_file or self.config['output_file']
        start_time = datetime.now()
        
        # Run scraper
        success = self.scraper.scrape_and_save(output_file)
        
        if not success:
            return {"success": False, "error": "Scraping failed"}
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Load existing data
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading output file: {e}")
            return {"success": False, "error": str(e)}
        
        # Add metadata
        metadata = {
            "scraping_metadata": {
                "timestamp": end_time.isoformat(),
                "duration_seconds": duration,
                "scraper_version": "1.0.0",
                "platform": "pickyou",
                "base_url": self.config['base_url'],
                "statistics": self.scraper.stats.copy()
            }
        }
        
        # Merge metadata with data
        output_data = {**metadata, **data}
        
        # Save with metadata
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
        Get current scraper status.
        
        Returns:
            Dictionary with scraper status information
        """
        return {
            "config": self.config.to_dict(),
            "statistics": self.scraper.stats.copy(),
            "ready": True
        }


# Convenience function for quick integration
def scrape_products(
    output_file: str = "data/pickyou_products.json",
    base_url: str = "https://pickyou.co.jp",
    **kwargs
) -> Dict[str, Any]:
    """
    Quick function to scrape products (for simple integrations).
    
    Args:
        output_file: Output file path
        base_url: Base URL of Shopify store
        **kwargs: Additional scraper configuration options
        
    Returns:
        Dictionary with scraping results
    """
    config = Config()
    config['output_file'] = output_file
    config['base_url'] = base_url
    config.update(kwargs)
    
    pipeline_scraper = PipelineScraper(config=config)
    return pipeline_scraper.scrape(return_data=False)

