# Pipeline Integration Guide

This guide shows you how to integrate the PickYou scraper into your extraction pipeline.

## Quick Start

### Simple Integration

```python
from src.pipeline import scrape_products

result = scrape_products(
    output_file="data/products.json",
    base_url="https://pickyou.co.jp"
)

if result['success']:
    print(f"Scraped {result['statistics']['products_transformed']} products")
```

### With Configuration

```python
from src.pipeline import PipelineScraper
from src.config import Config

config = Config()
config['delay'] = 2.0  # Custom delay
config['output_file'] = 'data/custom_output.json'

pipeline = PipelineScraper(config=config)
result = pipeline.scrape()

print(f"Duration: {result['duration_seconds']:.2f} seconds")
```

## API Reference

### `PipelineScraper` Class

Main class for pipeline integration.

#### Methods

##### `scrape(output_file=None, include_metadata=True, return_data=False)`

Scrape products and return results.

**Parameters:**
- `output_file` (str, optional): Output file path
- `include_metadata` (bool): Include metadata in output
- `return_data` (bool): Return data in addition to saving

**Returns:**
```python
{
    "success": bool,
    "timestamp": str,  # ISO format
    "duration_seconds": float,
    "output_file": str,
    "statistics": {
        "pages_fetched": int,
        "products_fetched": int,
        "products_transformed": int,
        "products_failed": int,
        "errors": list
    },
    "data": dict  # Only if return_data=True
}
```

##### `scrape_with_metadata(output_file=None)`

Scrape products and save with metadata included in output file.

**Returns:**
```python
{
    "success": bool,
    "output_file": str,
    "metadata": {
        "timestamp": str,
        "duration_seconds": float,
        "scraper_version": str,
        "platform": str,
        "base_url": str,
        "statistics": dict
    }
}
```

##### `get_status()`

Get current scraper status.

**Returns:**
```python
{
    "config": dict,
    "statistics": dict,
    "ready": bool
}
```

## Output Format

### Standard Output

```json
{
  "items": [
    {
      "platform": "pickyou",
      "id": "123456789",
      "name": "Product Name",
      "price": 2999,
      "sizes": [...],
      "brand": {...},
      "category": "tops",
      "gender": "womens",
      "s3_image_url": "https://...",
      "platform_url": "https://...",
      "image_count": 3,
      "item_images": [...]
    }
  ]
}
```

### With Metadata

```json
{
  "scraping_metadata": {
    "timestamp": "2024-01-01T12:00:00",
    "duration_seconds": 123.45,
    "scraper_version": "1.0.0",
    "platform": "pickyou",
    "base_url": "https://pickyou.co.jp",
    "statistics": {
      "pages_fetched": 100,
      "products_fetched": 25000,
      "products_transformed": 24950,
      "products_failed": 50
    }
  },
  "items": [...]
}
```

## Integration Patterns

### Pattern 1: Simple Scraping

```python
from src.pipeline import scrape_products

result = scrape_products()
# Data saved to data/pickyou_products.json
```

### Pattern 2: With Error Handling

```python
from src.pipeline import PipelineScraper

pipeline = PipelineScraper()

try:
    result = pipeline.scrape()
    if result['success']:
        # Continue with pipeline
        process_data(result['output_file'])
    else:
        # Handle failure
        handle_error(result)
except Exception as e:
    # Handle exception
    log_error(e)
```

### Pattern 3: With Progress Tracking

```python
from src.pipeline import PipelineScraper

def on_progress(stats):
    print(f"Progress: {stats['products_transformed']}/{stats['products_fetched']}")

pipeline = PipelineScraper(on_progress=on_progress)
result = pipeline.scrape()
```

### Pattern 4: Full Pipeline Integration

```python
from src.pipeline import PipelineScraper

# Step 1: Scrape
pipeline = PipelineScraper()
scrape_result = pipeline.scrape(return_data=True)

if scrape_result['success']:
    products = scrape_result['data']['items']
    
    # Step 2: Feature extraction
    features = extract_features(products)
    
    # Step 3: Upload to S3
    upload_to_s3(features)
    
    # Step 4: Update database
    update_database(features)
```

## Command Line Usage

### Basic

```bash
python -m src.cli
```

### With Options

```bash
python -m src.cli --output data/products.json --delay 2.0 --verbose
```

### With Config File

```bash
python -m src.cli --config config.json
```

## Configuration

Create a `config.json` file:

```json
{
  "base_url": "https://pickyou.co.jp",
  "limit": 250,
  "delay": 1.0,
  "output_file": "data/pickyou_products.json",
  "max_retries": 3,
  "timeout": 30,
  "log_level": "INFO"
}
```

## Error Handling

The scraper provides detailed error information:

```python
result = pipeline.scrape()

if not result['success']:
    stats = result['statistics']
    print(f"Failed products: {stats['products_failed']}")
    print(f"Errors: {stats['errors']}")
```

## Best Practices

1. **Always check success**: Verify `result['success']` before proceeding
2. **Use metadata**: Include metadata for tracking and debugging
3. **Handle errors**: Check statistics for failed products
4. **Use callbacks**: Implement progress tracking for long-running scrapes
5. **Save checkpoints**: Use checkpoint functionality for resumable scraping
6. **Monitor statistics**: Track success rates and performance metrics

## Next Steps

After scraping, you can:

1. **Feature Extraction**: Extract features from product data
2. **Data Enrichment**: Add additional data from other sources
3. **Upload to S3**: Store data in cloud storage
4. **Update Database**: Save to your database
5. **Trigger Pipeline**: Continue with your extraction pipeline

See `examples/pipeline_integration.py` for complete examples.

