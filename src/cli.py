"""Command-line interface for the scraper"""

import argparse
import sys
from pathlib import Path
from .scraper import Scraper
from .logger import setup_logger
from .config import Config


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Shopify API scraper for pickyou.co.jp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python -m src.cli
  
  # Custom output file
  python -m src.cli --output data/products.json
  
  # Custom delay and limit
  python -m src.cli --delay 2.0 --limit 100
  
  # Use config file
  python -m src.cli --config config.json
  
  # Verbose logging
  python -m src.cli --verbose
        """
    )
    
    parser.add_argument(
        '--base-url',
        type=str,
        default='https://pickyou.co.jp',
        help='Base URL of the Shopify store (default: https://pickyou.co.jp)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='data/pickyou_products.json',
        help='Output file path (default: data/pickyou_products.json)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=250,
        help='Products per page (max 250, default: 250)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to JSON configuration file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Enable quiet mode (WARNING level only)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Path to log file (optional)'
    )
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Determine log level
    if args.verbose:
        log_level = 'DEBUG'
    elif args.quiet:
        log_level = 'WARNING'
    else:
        log_level = 'INFO'
    
    # Setup logger
    import logging
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR
    }
    logger = setup_logger(
        level=level_map.get(log_level, logging.INFO),
        log_file=args.log_file
    )
    
    # Load configuration
    config = Config(config_file=args.config)
    
    # Override with CLI arguments
    if args.base_url:
        config['base_url'] = args.base_url
    if args.output:
        config['output_file'] = args.output
    if args.limit:
        config['limit'] = min(args.limit, 250)
    if args.delay:
        config['delay'] = args.delay
    
    # Create and run scraper
    scraper = Scraper(
        base_url=config['base_url'],
        limit=config['limit'],
        delay=config['delay'],
        logger=logger
    )
    
    success = scraper.scrape_and_save(config['output_file'])
    
    if not success:
        logger.error("Scraping failed!")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()

