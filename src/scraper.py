"""Main scraper for fetching products from pickyou.co.jp Shopify API"""

import time
from typing import List, Dict, Any, Optional
from .utils import make_request, save_json, ensure_data_dir
from .parser import parse_shopify_product
from .logger import setup_logger
from .validator import validate_product


class Scraper:
    """Scraper for pickyou.co.jp Shopify products"""
    
    def __init__(
        self,
        base_url: str = "https://pickyou.co.jp",
        limit: int = 250,
        delay: float = 1.0,
        logger: Optional[Any] = None
    ):
        """
        Initialize scraper.
        
        Args:
            base_url: Base URL of the Shopify store
            limit: Number of products per page (max 250)
            delay: Delay between requests in seconds
            logger: Optional logger instance
        """
        self.base_url = base_url
        self.limit = min(limit, 250)  # Shopify max is 250
        self.delay = delay
        self.api_endpoint = f"{base_url}/products.json"
        self.logger = logger or setup_logger()
        
        # Statistics tracking
        self.stats = {
            "pages_fetched": 0,
            "products_fetched": 0,
            "products_transformed": 0,
            "products_failed": 0,
            "errors": []
        }
    
    def fetch_page(self, page: int) -> List[Dict[str, Any]]:
        """
        Fetch a single page of products.
        
        Args:
            page: Page number (1-indexed)
            
        Returns:
            List of Shopify product objects, or empty list on error
        """
        url = f"{self.api_endpoint}?limit={self.limit}&page={page}"
        self.logger.info(f"Fetching page {page}...")
        
        response = make_request(url, logger=self.logger)
        
        if response and "products" in response:
            products = response["products"]
            self.logger.info(f"  Found {len(products)} products on page {page}")
            self.stats["pages_fetched"] += 1
            self.stats["products_fetched"] += len(products)
            return products
        
        return []
    
    def fetch_all_products(self) -> List[Dict[str, Any]]:
        """
        Fetch all products by paginating through all pages.
        
        Returns:
            List of all Shopify product objects
        """
        all_products = []
        page = 1
        start_time = time.time()
        
        self.logger.info("Starting product fetch...")
        
        while True:
            products = self.fetch_page(page)
            
            if not products:
                self.logger.info(f"No more products found. Stopping at page {page}")
                break
            
            all_products.extend(products)
            
            # If we got fewer products than the limit, we've reached the last page
            if len(products) < self.limit:
                self.logger.info(
                    f"Reached last page (got {len(products)} products, limit is {self.limit})"
                )
                break
            
            page += 1
            
            # Rate limiting: delay between requests
            if self.delay > 0:
                time.sleep(self.delay)
        
        elapsed_time = time.time() - start_time
        self.logger.info(
            f"Fetch completed: {len(all_products)} products in {elapsed_time:.2f} seconds "
            f"({len(all_products)/elapsed_time:.2f} products/sec)"
        )
        return all_products
    
    def scrape_and_save(self, output_file: str = "data/pickyou_products.json") -> bool:
        """
        Scrape all products, transform to custom format, and save to JSON.
        
        Args:
            output_file: Path to output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("=" * 60)
        self.logger.info("Starting scraper")
        self.logger.info(f"Target: {self.base_url}")
        self.logger.info(f"Output: {output_file}")
        self.logger.info("=" * 60)
        
        # Reset statistics
        self.stats = {
            "pages_fetched": 0,
            "products_fetched": 0,
            "products_transformed": 0,
            "products_failed": 0,
            "errors": []
        }
        
        # Fetch all products
        shopify_products = self.fetch_all_products()
        
        if not shopify_products:
            self.logger.error("No products found. Exiting.")
            return False
        
        # Transform to custom format
        self.logger.info(f"\nTransforming {len(shopify_products)} products to custom format...")
        transformed_products = []
        start_time = time.time()
        
        for idx, product in enumerate(shopify_products, 1):
            try:
                transformed = parse_shopify_product(product, self.base_url)
                
                # Validate the transformed product
                if validate_product(transformed):
                    transformed_products.append(transformed)
                    self.stats["products_transformed"] += 1
                else:
                    self.logger.warning(
                        f"Product {product.get('id', 'unknown')} failed validation, skipping"
                    )
                    self.stats["products_failed"] += 1
                    
            except Exception as e:
                product_id = product.get('id', 'unknown')
                error_msg = f"Error transforming product {product_id}: {e}"
                self.logger.error(error_msg)
                self.stats["products_failed"] += 1
                self.stats["errors"].append({
                    "product_id": product_id,
                    "error": str(e)
                })
                continue
            
            # Log progress every 1000 products
            if idx % 1000 == 0:
                elapsed = time.time() - start_time
                rate = idx / elapsed if elapsed > 0 else 0
                self.logger.info(
                    f"Progress: {idx}/{len(shopify_products)} products "
                    f"({rate:.2f} products/sec)"
                )
        
        elapsed_time = time.time() - start_time
        self.logger.info(
            f"Transformation completed: {len(transformed_products)} products in "
            f"{elapsed_time:.2f} seconds ({len(transformed_products)/elapsed_time:.2f} products/sec)"
        )
        
        # Log statistics
        self._log_statistics()
        
        # Prepare output structure
        output_data = {
            "items": transformed_products
        }
        
        # Ensure data directory exists
        ensure_data_dir()
        
        # Save to file
        success = save_json(output_data, output_file, logger=self.logger)
        
        # Store final stats for pipeline access
        self.final_stats = {
            "total_products": len(transformed_products),
            "success_rate": (
                self.stats["products_transformed"] / self.stats["products_fetched"] * 100
                if self.stats["products_fetched"] > 0 else 0
            ),
            **self.stats
        }
        
        if success:
            self.logger.info("=" * 60)
            self.logger.info("Scraping completed successfully!")
            self.logger.info(f"Total products saved: {len(transformed_products)}")
            self.logger.info("=" * 60)
        
        return success
    
    def _log_statistics(self) -> None:
        """Log scraping statistics."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Scraping Statistics")
        self.logger.info("=" * 60)
        self.logger.info(f"Pages fetched: {self.stats['pages_fetched']}")
        self.logger.info(f"Products fetched: {self.stats['products_fetched']}")
        self.logger.info(f"Products transformed: {self.stats['products_transformed']}")
        self.logger.info(f"Products failed: {self.stats['products_failed']}")
        
        if self.stats['products_fetched'] > 0:
            success_rate = (
                self.stats['products_transformed'] / self.stats['products_fetched'] * 100
            )
            self.logger.info(f"Success rate: {success_rate:.2f}%")
        
        if self.stats['errors']:
            self.logger.warning(f"Total errors: {len(self.stats['errors'])}")
            # Log first 5 errors as examples
            for error in self.stats['errors'][:5]:
                self.logger.warning(f"  - Product {error['product_id']}: {error['error']}")
        
        self.logger.info("=" * 60 + "\n")


def main():
    """Main entry point for running the scraper"""
    logger = setup_logger()
    scraper = Scraper(logger=logger)
    success = scraper.scrape_and_save()
    
    if not success:
        logger.error("Scraping failed!")
        exit(1)


if __name__ == "__main__":
    main()

