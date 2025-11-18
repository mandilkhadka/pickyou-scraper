# Changelog

## [1.1.0] - Pipeline Integration Update

### Added

#### 🚀 Pipeline Integration Module (`src/pipeline.py`)
- **`PipelineScraper` class**: Clean API for programmatic use
- **`scrape_products()` function**: Quick integration function
- **Metadata support**: Automatic metadata inclusion in output
- **Progress callbacks**: Track scraping progress
- **Batch callbacks**: Process products in batches

#### 🎯 CLI Interface (`src/cli.py`)
- Full command-line interface with argparse
- Support for all configuration options via CLI
- Verbose/quiet modes
- Config file support
- Help documentation

#### ⚙️ Configuration Management (`src/config.py`)
- JSON-based configuration files
- Default configuration with sensible defaults
- Easy override mechanism
- Config file loading and saving

#### 📚 Documentation
- **PIPELINE_INTEGRATION.md**: Complete integration guide
- **examples/pipeline_integration.py**: Working examples
- **config.example.json**: Example configuration file
- Updated README with new features

#### 📊 Enhanced Features
- Metadata tracking in output files
- Final statistics accessible via API
- Better error reporting structure
- Status endpoint for monitoring

### Improved

- Better separation of concerns
- More modular architecture
- Enhanced error handling
- Professional logging throughout
- Better documentation

### Usage Examples

**Simple Integration:**
```python
from src.pipeline import scrape_products
result = scrape_products()
```

**Advanced Integration:**
```python
from src.pipeline import PipelineScraper
pipeline = PipelineScraper()
result = pipeline.scrape_with_metadata()
```

**CLI Usage:**
```bash
python -m src.cli --output data/products.json --verbose
```

## [1.0.0] - Initial Release

### Features
- Shopify API scraping
- Automatic pagination
- Data transformation
- Error handling and retry logic
- Logging system
- Data validation
- Unit tests

