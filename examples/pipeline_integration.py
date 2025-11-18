"""
Example: How to integrate the scraper into an extraction pipeline.

This demonstrates various ways to use the scraper programmatically.
"""

from src.pipeline import PipelineScraper, scrape_products
from src.config import Config
from src.logger import setup_logger


def example_simple_integration():
    """Simplest way to use the scraper in a pipeline."""
    print("Example 1: Simple Integration")
    print("-" * 50)
    
    result = scrape_products(
        output_file="data/products.json",
        base_url="https://pickyou.co.jp"
    )
    
    print(f"Success: {result['success']}")
    print(f"Output: {result['output_file']}")
    print(f"Statistics: {result['statistics']}")
    print()


def example_with_config():
    """Using configuration file for customization."""
    print("Example 2: With Configuration")
    print("-" * 50)
    
    # Create config
    config = Config()
    config['delay'] = 2.0  # Slower requests
    config['output_file'] = 'data/custom_output.json'
    
    # Use pipeline scraper
    pipeline = PipelineScraper(config=config)
    result = pipeline.scrape()
    
    print(f"Success: {result['success']}")
    print(f"Duration: {result['duration_seconds']:.2f} seconds")
    print()


def example_with_callbacks():
    """Using callbacks for progress tracking."""
    print("Example 3: With Progress Callbacks")
    print("-" * 50)
    
    def progress_callback(stats):
        print(f"Progress: {stats['products_transformed']} products transformed")
    
    def batch_callback(batch):
        print(f"Processed batch of {len(batch)} products")
    
    pipeline = PipelineScraper(
        on_progress=progress_callback,
        on_batch=batch_callback
    )
    
    result = pipeline.scrape()
    print(f"Final result: {result['success']}")
    print()


def example_with_metadata():
    """Including metadata in output for pipeline tracking."""
    print("Example 4: With Metadata")
    print("-" * 50)
    
    pipeline = PipelineScraper()
    result = pipeline.scrape_with_metadata(output_file="data/products_with_metadata.json")
    
    if result['success']:
        print(f"Metadata included in output file")
        print(f"Timestamp: {result['metadata']['timestamp']}")
        print(f"Statistics: {result['metadata']['statistics']}")
    print()


def example_in_extraction_pipeline():
    """Example of how to use in a full extraction pipeline."""
    print("Example 5: Full Pipeline Integration")
    print("-" * 50)
    
    # Step 1: Scrape products
    pipeline = PipelineScraper()
    scrape_result = pipeline.scrape(return_data=True)
    
    if not scrape_result['success']:
        print("Scraping failed, aborting pipeline")
        return
    
    # Step 2: Process data (example)
    products = scrape_result['data']['items']
    print(f"Scraped {len(products)} products")
    
    # Step 3: Filter/transform (example)
    valid_products = [p for p in products if p.get('price', 0) > 0]
    print(f"Found {len(valid_products)} products with valid prices")
    
    # Step 4: Continue with your pipeline...
    # - Feature extraction
    # - Data enrichment
    # - Upload to S3
    # etc.
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Pipeline Integration Examples")
    print("=" * 60)
    print()
    
    # Uncomment the example you want to run:
    # example_simple_integration()
    # example_with_config()
    # example_with_callbacks()
    # example_with_metadata()
    # example_in_extraction_pipeline()
    
    print("Uncomment examples in the code to run them")

