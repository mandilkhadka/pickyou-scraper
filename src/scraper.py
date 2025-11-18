"""Main scraper for fetching products from pickyou.co.jp Shopify API"""

import time
from typing import List, Dict, Any
from .utils import make_request, save_json, ensure_data_dir
from .parser import parse_shopify_product


class Scraper:
    """Scraper for pickyou.co.jp Shopify products"""
    
    def __init__(
        self,
        base_url: str = "https://pickyou.co.jp",
        limit: int = 250,
        delay: float = 1.0
    ):
        """
        Initialize scraper.
        
        Args:
            base_url: Base URL of the Shopify store
            limit: Number of products per page (max 250)
            delay: Delay between requests in seconds
        """
        self.base_url = base_url
        self.limit = min(limit, 250)  # Shopify max is 250
        self.delay = delay
        self.api_endpoint = f"{base_url}/products.json"
    
    def fetch_page(self, page: int) -> List[Dict[str, Any]]:
        """
        Fetch a single page of products.
        
        Args:
            page: Page number (1-indexed)
            
        Returns:
            List of Shopify product objects, or empty list on error
        """
        url = f"{self.api_endpoint}?limit={self.limit}&page={page}"
        print(f"Fetching page {page}...")
        
        response = make_request(url)
        
        if response and "products" in response:
            products = response["products"]
            print(f"  Found {len(products)} products on page {page}")
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
        
        while True:
            products = self.fetch_page(page)
            
            if not products:
                print(f"No more products found. Stopping at page {page}")
                break
            
            all_products.extend(products)
            
            # If we got fewer products than the limit, we've reached the last page
            if len(products) < self.limit:
                print(f"Reached last page (got {len(products)} products, limit is {self.limit})")
                break
            
            page += 1
            
            # Rate limiting: delay between requests
            if self.delay > 0:
                time.sleep(self.delay)
        
        print(f"\nTotal products fetched: {len(all_products)}")
        return all_products
    
    def scrape_and_save(self, output_file: str = "data/pickyou_products.json") -> bool:
        """
        Scrape all products, transform to custom format, and save to JSON.
        
        Args:
            output_file: Path to output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        print("Starting scraper...")
        print(f"Target: {self.base_url}")
        print(f"Output: {output_file}\n")
        
        # Fetch all products
        shopify_products = self.fetch_all_products()
        
        if not shopify_products:
            print("No products found. Exiting.")
            return False
        
        # Transform to custom format
        print(f"\nTransforming {len(shopify_products)} products to custom format...")
        transformed_products = []
        
        for product in shopify_products:
            try:
                transformed = parse_shopify_product(product, self.base_url)
                transformed_products.append(transformed)
            except Exception as e:
                print(f"Error transforming product {product.get('id', 'unknown')}: {e}")
                continue
        
        print(f"Successfully transformed {len(transformed_products)} products")
        
        # Prepare output structure
        output_data = {
            "items": transformed_products
        }
        
        # Ensure data directory exists
        ensure_data_dir()
        
        # Save to file
        return save_json(output_data, output_file)


def main():
    """Main entry point for running the scraper"""
    scraper = Scraper()
    success = scraper.scrape_and_save()
    
    if success:
        print("\n✓ Scraping completed successfully!")
    else:
        print("\n✗ Scraping failed!")
        exit(1)


if __name__ == "__main__":
    main()

