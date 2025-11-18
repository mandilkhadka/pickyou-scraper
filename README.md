# PickYou Scraper

A Python scraper for fetching all products from pickyou.co.jp using the Shopify API.

## 🚀 Quick Start

**Just want to run it?** See [QUICK_START.md](QUICK_START.md) for simple step-by-step instructions!

```bash
cd /Users/m/code/mandilkhadka/pickyou-scraper
source venv/bin/activate
python -m src.cli
```

## Features

- ✅ Fetches all products from pickyou.co.jp via Shopify API
- ✅ Automatic pagination (handles all pages automatically)
- ✅ Transforms Shopify product format to custom JSON format
- ✅ Rate limiting and error handling
- ✅ Retry logic for failed requests
- ✅ Comprehensive unit tests
- ✅ **Pipeline-ready API** for easy integration
- ✅ **CLI interface** with flexible options
- ✅ **Configuration file support** (JSON)
- ✅ **Metadata tracking** in output
- ✅ **Progress callbacks** for monitoring
- ✅ **Professional logging** system
- ✅ **Data validation** before saving

## Project Structure

```
pickyou-scraper/
├── src/
│   ├── scraper.py      # Main scraper with pagination logic
│   ├── parser.py       # Transform Shopify format to custom format
│   ├── utils.py        # HTTP requests and file I/O helpers
│   └── __init__.py
├── tests/
│   ├── test_scraper.py # Unit tests
│   └── __init__.py
├── data/
│   └── pickyou_products.json  # Output file (generated)
├── requirements.txt
├── RULES.md
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pickyou-scraper
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface (Recommended)

**Basic usage:**
```bash
python -m src.cli
```

**With options:**
```bash
python -m src.cli --output data/products.json --delay 2.0 --verbose
```

**With config file:**
```bash
python -m src.cli --config config.json
```

**See all options:**
```bash
python -m src.cli --help
```

### Python API (For Pipeline Integration)

**Simple integration:**
```python
from src.pipeline import scrape_products

result = scrape_products(output_file="data/products.json")
```

**Advanced integration:**
```python
from src.pipeline import PipelineScraper
from src.config import Config

config = Config()
pipeline = PipelineScraper(config=config)
result = pipeline.scrape_with_metadata()
```

See [PIPELINE_INTEGRATION.md](PIPELINE_INTEGRATION.md) for complete integration guide.

### Legacy Usage

Run the scraper directly:
```bash
python -m src.scraper
```

The scraper will:
1. Fetch all products from `https://pickyou.co.jp/products.json`
2. Paginate through all pages automatically
3. Transform products to custom JSON format
4. Save results to `data/pickyou_products.json`

### Custom Configuration

You can customize the scraper in code:

```python
from src.scraper import Scraper

scraper = Scraper(
    base_url="https://pickyou.co.jp",
    limit=250,  # Products per page (max 250)
    delay=1.0   # Delay between requests (seconds)
)

success = scraper.scrape_and_save("data/pickyou_products.json")
```

## Output Format

The scraper outputs JSON in the following format:

```json
{
  "items": [
    {
      "platform": "pickyou",
      "id": "123456789",
      "name": "Product Name",
      "price": 2999,
      "sizes": [
        {
          "id": "S",
          "row": "S",
          "size": "S"
        }
      ],
      "brand": {
        "id": null,
        "name": "Brand Name",
        "sub_name": null
      },
      "category": "tops",
      "gender": "womens",
      "s3_image_url": "https://...",
      "platform_url": "https://pickyou.co.jp/products/product-handle",
      "image_count": 3,
      "item_images": [
        "https://...",
        "https://..."
      ]
    }
  ]
}
```

## Testing

Run tests with pytest:

```bash
pytest tests/
```

Run with verbose output:

```bash
pytest tests/ -v
```

## Configuration

### Rate Limiting

The scraper includes a default 1-second delay between requests to respect rate limits. You can adjust this:

```python
scraper = Scraper(delay=2.0)  # 2 seconds between requests
```

### Error Handling

The scraper includes:
- Automatic retries (3 attempts) for failed requests
- Exponential backoff for rate limit errors
- Graceful error handling that continues scraping even if individual products fail

## Requirements

- Python 3.7+
- requests >= 2.31.0
- urllib3 >= 2.0.0
- pytest >= 7.4.0 (for testing)

## Notes

- The scraper fetches products using Shopify's public API endpoint
- No authentication is required for the products.json endpoint
- Image URLs are original Shopify URLs (not S3) - S3 upload will be handled in a later pipeline
- Brand, category, and gender are extracted from product tags and product_type fields
- If fields cannot be extracted, sensible defaults are used

