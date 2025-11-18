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
        self.collections_endpoint = f"{base_url}/collections.json"
        self.logger = logger or setup_logger()
        
        # Initialize statistics tracking
        self.stats = {
            "pages_fetched": 0,
            "products_fetched": 0,
            "products_transformed": 0,
            "products_failed": 0,
            "collections_fetched": 0,
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
    
    def fetch_all_collections(self) -> List[Dict[str, Any]]:
        """
        Fetch all collections from the Shopify API.
        
        Returns:
            List of all collection objects from the API.
            
        Example:
            >>> scraper = Scraper()
            >>> collections = scraper.fetch_all_collections()
            >>> print(f"Found {len(collections)} collections")
        """
        all_collections = []
        page = 1
        start_time = time.time()
        
        self.logger.info("Fetching all collections...")
        
        # Paginate through all collection pages
        while True:
            url = f"{self.collections_endpoint}?limit={self.limit}&page={page}"
            self.logger.info(f"Fetching collections page {page}...")
            
            response = make_request(url, logger=self.logger)
            
            if response and "collections" in response:
                collections = response["collections"]
                if not collections:
                    break
                
                all_collections.extend(collections)
                self.logger.info(f"  Found {len(collections)} collections on page {page}")
                
                # If we got fewer collections than the limit, we've reached the last page
                if len(collections) < self.limit:
                    break
                
                page += 1
                
                # Rate limiting
                if self.delay > 0:
                    time.sleep(self.delay)
            else:
                break
        
        elapsed_time = time.time() - start_time
        self.logger.info(
            f"Collections fetch completed: {len(all_collections)} collections in "
            f"{elapsed_time:.2f} seconds"
        )
        
        self.stats["collections_fetched"] = len(all_collections)
        return all_collections
    
    def fetch_products_from_collection(
        self, 
        collection_id: str, 
        collection_handle: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all products from a specific collection with pagination.
        
        Args:
            collection_id: Collection ID (can be numeric ID or handle)
            collection_handle: Optional collection handle for URL construction
            
        Returns:
            List of all products from the collection.
            
        Example:
            >>> scraper = Scraper()
            >>> products = scraper.fetch_products_from_collection("123456")
            >>> print(f"Found {len(products)} products in collection")
        """
        all_products = []
        page = 1
        
        # Use handle if available (more reliable), otherwise use ID
        if collection_handle:
            collection_path = collection_handle
        else:
            collection_path = collection_id
        
        collection_url = f"{self.base_url}/collections/{collection_path}/products.json"
        
        # Paginate through all product pages in this collection
        while True:
            url = f"{collection_url}?limit={self.limit}&page={page}"
            
            response = make_request(url, logger=self.logger)
            
            if response and "products" in response:
                products = response["products"]
                if not products:
                    break
                
                all_products.extend(products)
                self.stats["pages_fetched"] += 1
                self.stats["products_fetched"] += len(products)
                
                # If we got fewer products than the limit, we've reached the last page
                if len(products) < self.limit:
                    break
                
                page += 1
                
                # Rate limiting
                if self.delay > 0:
                    time.sleep(self.delay)
            else:
                break
        
        return all_products
    
    def fetch_all_products(self) -> List[Dict[str, Any]]:
        """
        Fetch all products from all sources: main products endpoint and all collections.
        
        This comprehensive method:
        1. Fetches products from the main /products.json endpoint
        2. Fetches all collections
        3. Fetches products from each collection
        4. Deduplicates products by ID to ensure no duplicates
        
        Returns:
            List of all unique Shopify product objects from all sources.
            
        Example:
            >>> scraper = Scraper()
            >>> all_products = scraper.fetch_all_products()
            >>> print(f"Total unique products: {len(all_products)}")
        """
        start_time = time.time()
        all_products_dict = {}  # Use dict to deduplicate by product ID
        
        self.logger.info("=" * 60)
        self.logger.info("Starting comprehensive product fetch from all sources...")
        self.logger.info("=" * 60)
        
        # Step 1: Fetch from main products endpoint
        self.logger.info("\n[Step 1/3] Fetching products from main endpoint...")
        main_products = []
        page = 1
        
        while True:
            products = self.fetch_page(page)
            
            if not products:
                self.logger.info(f"No more products found. Stopping at page {page}")
                break
            
            main_products.extend(products)
            
            if len(products) < self.limit:
                self.logger.info(
                    f"Reached last page (got {len(products)} products, limit is {self.limit})"
                )
                break
            
            page += 1
            
            if self.delay > 0:
                time.sleep(self.delay)
        
        self.logger.info(f"Main endpoint: Found {len(main_products)} products")
        
        # Step 2: Fetch all collections
        self.logger.info("\n[Step 2/3] Fetching all collections...")
        collections = self.fetch_all_collections()
        self.logger.info(f"Found {len(collections)} collections")
        
        # Step 3: Fetch products from each collection
        self.logger.info("\n[Step 3/3] Fetching products from collections...")
        all_collection_products = []  # Store all collection products
        
        for idx, collection in enumerate(collections, 1):
            collection_id = collection.get("id", "")
            collection_handle = collection.get("handle", "")
            collection_title = collection.get("title", collection_handle or str(collection_id))
            
            self.logger.info(
                f"Collection {idx}/{len(collections)}: {collection_title} "
                f"(ID: {collection_id}, Handle: {collection_handle})"
            )
            
            products = self.fetch_products_from_collection(
                str(collection_id), 
                collection_handle
            )
            
            all_collection_products.extend(products)
            self.logger.info(f"  Found {len(products)} products in this collection")
            
            if self.delay > 0:
                time.sleep(self.delay)
        
        self.logger.info(f"Collections: Found {len(all_collection_products)} products total")
        
        # Step 4: Combine and deduplicate all products by ID
        self.logger.info("\n[Deduplication] Combining and deduplicating products...")
        
        # Add all products to dict keyed by ID (this automatically deduplicates)
        for product in main_products:
            product_id = str(product.get("id", ""))
            if product_id:
                all_products_dict[product_id] = product
        
        # Add collection products (deduplication happens automatically via dict)
        for product in all_collection_products:
            product_id = str(product.get("id", ""))
            if product_id:
                all_products_dict[product_id] = product
        
        # Convert dict back to list
        all_products = list(all_products_dict.values())
        
        # Log final statistics
        elapsed_time = time.time() - start_time
        rate = len(all_products) / elapsed_time if elapsed_time > 0 else 0
        
        self.logger.info("=" * 60)
        self.logger.info("Comprehensive fetch completed!")
        self.logger.info(f"Main endpoint products: {len(main_products)}")
        self.logger.info(f"Collection products (before dedup): {len(all_collection_products)}")
        duplicates_removed = len(main_products) + len(all_collection_products) - len(all_products)
        if duplicates_removed > 0:
            self.logger.info(f"Duplicates removed: {duplicates_removed}")
        self.logger.info(f"Total unique products: {len(all_products)}")
        self.logger.info(f"Time elapsed: {elapsed_time:.2f} seconds")
        self.logger.info(f"Rate: {rate:.2f} products/sec")
        self.logger.info("=" * 60)
        
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
            "collections_fetched": 0,
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
        self.logger.info(f"Collections fetched: {self.stats['collections_fetched']}")
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
