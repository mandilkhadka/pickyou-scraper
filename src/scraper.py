"""
Main scraper for fetching products from pickyou.co.jp Shopify API.

This module provides the core scraping functionality including:
- Pagination through all product pages
- Data transformation to custom format
- Error handling and retry logic
- Statistics tracking
"""

import time
from typing import List, Dict, Any, Optional
from .utils import make_request, save_json, ensure_data_dir
from .parser import parse_shopify_product
from .logger import setup_logger
from .validator import validate_product


# Constants
SHOPIFY_MAX_LIMIT = 250  # Maximum products per page allowed by Shopify API
PROGRESS_LOG_INTERVAL = 1000  # Log progress every N products


class Scraper:
    """
    Scraper for pickyou.co.jp Shopify products.
    
    Handles fetching, transforming, and saving products from the Shopify API.
    Includes automatic pagination, error handling, and statistics tracking.
    
    Example:
        >>> scraper = Scraper()
        >>> success = scraper.scrape_and_save("data/products.json")
        >>> if success:
        ...     print(f"Scraped {scraper.stats['products_transformed']} products")
    """
    
    def __init__(
        self,
        base_url: str = "https://pickyou.co.jp",
        limit: int = 250,
        delay: float = 1.0,
        logger: Optional[Any] = None
    ):
        """
        Initialize scraper with configuration.
        
        Args:
            base_url: Base URL of the Shopify store
            limit: Number of products per page (max 250, enforced automatically)
            delay: Delay between requests in seconds (for rate limiting)
            logger: Optional logger instance (creates default if None)
            
        Note:
            The limit parameter is automatically capped at 250 (Shopify's maximum).
        """
        self.base_url = base_url
        self.limit = min(limit, SHOPIFY_MAX_LIMIT)  # Enforce Shopify's maximum
        self.delay = delay
        self.api_endpoint = f"{base_url}/products.json"
        self.logger = logger or setup_logger()
        
        # Initialize statistics tracking
        self.stats = {
            "pages_fetched": 0,
            "products_fetched": 0,
            "products_transformed": 0,
            "products_failed": 0,
            "errors": []
        }
    
    def fetch_page(self, page: int) -> List[Dict[str, Any]]:
        """
        Fetch a single page of products from the Shopify API.
        
        Args:
            page: Page number (1-indexed, not 0-indexed)
            
        Returns:
            List of Shopify product objects from the API response.
            Returns empty list if request fails or no products found.
            
        Example:
            >>> scraper = Scraper()
            >>> products = scraper.fetch_page(1)
            >>> print(f"Found {len(products)} products on page 1")
        """
        url = f"{self.api_endpoint}?limit={self.limit}&page={page}"
        self.logger.info(f"Fetching page {page}...")
        
        # Make HTTP request with retry logic
        response = make_request(url, logger=self.logger)
        
        # Extract products from response
        if response and "products" in response:
            products = response["products"]
            self.logger.info(f"  Found {len(products)} products on page {page}")
            
            # Update statistics
            self.stats["pages_fetched"] += 1
            self.stats["products_fetched"] += len(products)
            
            return products
        
        # Return empty list if no products or request failed
        return []
    
    def fetch_all_products(self) -> List[Dict[str, Any]]:
        """
        Fetch all products by automatically paginating through all pages.
        
        The method continues fetching pages until:
        - An empty response is received
        - Fewer products than the limit are returned (indicating last page)
        
        Returns:
            List of all Shopify product objects from all pages.
            
        Example:
            >>> scraper = Scraper()
            >>> all_products = scraper.fetch_all_products()
            >>> print(f"Total products: {len(all_products)}")
        """
        all_products = []
        page = 1
        start_time = time.time()
        
        self.logger.info("Starting product fetch...")
        
        # Paginate through all pages
        while True:
            products = self.fetch_page(page)
            
            # Stop if no products returned (end of catalog or error)
            if not products:
                self.logger.info(f"No more products found. Stopping at page {page}")
                break
            
            # Add products from this page to our collection
            all_products.extend(products)
            
            # If we got fewer products than the limit, we've reached the last page
            # This is more efficient than making an extra request to check
            if len(products) < self.limit:
                self.logger.info(
                    f"Reached last page (got {len(products)} products, limit is {self.limit})"
                )
                break
            
            # Move to next page
            page += 1
            
            # Rate limiting: delay between requests to be respectful to the API
            if self.delay > 0:
                time.sleep(self.delay)
        
        # Log performance metrics
        elapsed_time = time.time() - start_time
        rate = len(all_products) / elapsed_time if elapsed_time > 0 else 0
        self.logger.info(
            f"Fetch completed: {len(all_products)} products in {elapsed_time:.2f} seconds "
            f"({rate:.2f} products/sec)"
        )
        
        return all_products
    
    def scrape_and_save(self, output_file: str = "data/pickyou_products.json") -> bool:
        """
        Complete scraping workflow: fetch, transform, validate, and save.
        
        This is the main method that orchestrates the entire scraping process:
        1. Fetches all products from the API
        2. Transforms each product to custom format
        3. Validates transformed products
        4. Saves to JSON file
        5. Logs statistics
        
        Args:
            output_file: Path to output JSON file (default: "data/pickyou_products.json")
            
        Returns:
            True if scraping completed successfully, False otherwise.
            
        Example:
            >>> scraper = Scraper()
            >>> if scraper.scrape_and_save("data/products.json"):
            ...     print("Scraping successful!")
            ...     print(f"Stats: {scraper.stats}")
        """
        # Log start of scraping session
        self.logger.info("=" * 60)
        self.logger.info("Starting scraper")
        self.logger.info(f"Target: {self.base_url}")
        self.logger.info(f"Output: {output_file}")
        self.logger.info("=" * 60)
        
        # Reset statistics for this scraping session
        self.stats = {
            "pages_fetched": 0,
            "products_fetched": 0,
            "products_transformed": 0,
            "products_failed": 0,
            "errors": []
        }
        
        # Step 1: Fetch all products from API
        shopify_products = self.fetch_all_products()
        
        if not shopify_products:
            self.logger.error("No products found. Exiting.")
            return False
        
        # Step 2: Transform products to custom format
        self.logger.info(f"\nTransforming {len(shopify_products)} products to custom format...")
        transformed_products = []
        start_time = time.time()
        
        # Process each product
        for idx, product in enumerate(shopify_products, 1):
            try:
                # Transform Shopify format to our custom format
                transformed = parse_shopify_product(product, self.base_url)
                
                # Validate the transformed product before adding
                if validate_product(transformed):
                    transformed_products.append(transformed)
                    self.stats["products_transformed"] += 1
                else:
                    # Log validation failure but continue processing
                    self.logger.warning(
                        f"Product {product.get('id', 'unknown')} failed validation, skipping"
                    )
                    self.stats["products_failed"] += 1
                    
            except Exception as e:
                # Log transformation errors but continue with other products
                product_id = product.get('id', 'unknown')
                error_msg = f"Error transforming product {product_id}: {e}"
                self.logger.error(error_msg)
                self.stats["products_failed"] += 1
                self.stats["errors"].append({
                    "product_id": product_id,
                    "error": str(e)
                })
                continue
            
            # Log progress periodically to show activity
            if idx % PROGRESS_LOG_INTERVAL == 0:
                elapsed = time.time() - start_time
                rate = idx / elapsed if elapsed > 0 else 0
                self.logger.info(
                    f"Progress: {idx}/{len(shopify_products)} products "
                    f"({rate:.2f} products/sec)"
                )
        
        # Log transformation completion with metrics
        elapsed_time = time.time() - start_time
        rate = len(transformed_products) / elapsed_time if elapsed_time > 0 else 0
        self.logger.info(
            f"Transformation completed: {len(transformed_products)} products in "
            f"{elapsed_time:.2f} seconds ({rate:.2f} products/sec)"
        )
        
        # Step 3: Log detailed statistics
        self._log_statistics()
        
        # Step 4: Prepare output data structure
        output_data = {
            "items": transformed_products
        }
        
        # Step 5: Ensure output directory exists
        ensure_data_dir()
        
        # Step 6: Save to JSON file
        success = save_json(output_data, output_file, logger=self.logger)
        
        # Store final statistics for programmatic access
        self.final_stats = {
            "total_products": len(transformed_products),
            "success_rate": (
                self.stats["products_transformed"] / self.stats["products_fetched"] * 100
                if self.stats["products_fetched"] > 0 else 0
            ),
            **self.stats
        }
        
        # Log completion
        if success:
            self.logger.info("=" * 60)
            self.logger.info("Scraping completed successfully!")
            self.logger.info(f"Total products saved: {len(transformed_products)}")
            self.logger.info("=" * 60)
        
        return success
    
    def _log_statistics(self) -> None:
        """
        Log detailed scraping statistics.
        
        This is a private method called internally to display statistics
        about the scraping session including success rates and errors.
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Scraping Statistics")
        self.logger.info("=" * 60)
        self.logger.info(f"Pages fetched: {self.stats['pages_fetched']}")
        self.logger.info(f"Products fetched: {self.stats['products_fetched']}")
        self.logger.info(f"Products transformed: {self.stats['products_transformed']}")
        self.logger.info(f"Products failed: {self.stats['products_failed']}")
        
        # Calculate and log success rate
        if self.stats['products_fetched'] > 0:
            success_rate = (
                self.stats['products_transformed'] / self.stats['products_fetched'] * 100
            )
            self.logger.info(f"Success rate: {success_rate:.2f}%")
        
        # Log error summary if there were any errors
        if self.stats['errors']:
            self.logger.warning(f"Total errors: {len(self.stats['errors'])}")
            # Show first 5 errors as examples (to avoid log spam)
            for error in self.stats['errors'][:5]:
                self.logger.warning(f"  - Product {error['product_id']}: {error['error']}")
        
        self.logger.info("=" * 60 + "\n")


def main():
    """
    Main entry point for running the scraper as a standalone script.
    
    This function is called when the module is run directly (not imported).
    It sets up logging and runs the scraper with default settings.
    """
    logger = setup_logger()
    scraper = Scraper(logger=logger)
    success = scraper.scrape_and_save()
    
    if not success:
        logger.error("Scraping failed!")
        exit(1)


if __name__ == "__main__":
    main()
