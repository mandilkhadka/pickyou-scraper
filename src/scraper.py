"""
Main scraper for fetching products from pickyou.co.jp Shopify API.
pickyou.co.jp Shopify APIから商品を取得するメインスクレイパー

This module provides the core scraping functionality including:
このモジュールは以下のコアスクレイピング機能を提供します：
- Pagination through all product pages
  - すべての商品ページのページネーション
- Data transformation to custom format
  - カスタム形式へのデータ変換
- Error handling and retry logic
  - エラーハンドリングとリトライロジック
- Statistics tracking
  - 統計情報の追跡
- Batch processing for memory optimization
  - メモリ最適化のためのバッチ処理
- Progress checkpoints for resumability
  - 再開可能な進捗チェックポイント
- Circuit breaker for failure handling
  - 障害処理のためのサーキットブレーカー
- Graceful shutdown support
  - グレースフルシャットダウンサポート
"""

import time
import signal
import os
from typing import List, Dict, Any, Optional
from .utils import (
    make_request, save_json, ensure_data_dir,
    save_checkpoint, load_checkpoint,
    stream_json_line, finalize_streamed_json
)
from .parser import parse_shopify_product
from .logger import setup_logger
from .validator import validate_product
from .circuit_breaker import CircuitBreaker


# Constants / 定数
# Maximum products per page allowed by Shopify API / Shopify APIで許可される1ページあたりの最大商品数
SHOPIFY_MAX_LIMIT = 250
# Log progress every N products / N商品ごとに進捗をログに記録
PROGRESS_LOG_INTERVAL = 1000


class Scraper:
    """
    Scraper for pickyou.co.jp Shopify products.
    pickyou.co.jp Shopify商品のスクレイパー
    
    Handles fetching, transforming, and saving products from the Shopify API.
    Includes automatic pagination, error handling, and statistics tracking.
    Shopify APIからの商品の取得、変換、保存を処理します。
    自動ページネーション、エラーハンドリング、統計情報の追跡を含みます。
    
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
        logger: Optional[Any] = None,
        batch_size: int = 1000,
        save_checkpoints: bool = True,
        checkpoint_dir: str = "data/checkpoints",
        checkpoint_interval: int = 1000,
        circuit_breaker_enabled: bool = True,
        circuit_breaker_failure_threshold: int = 10,
        circuit_breaker_timeout: int = 60,
        stream_to_disk: bool = True
    ):
        """
        Initialize scraper with configuration.
        設定でスクレイパーを初期化
        
        Args:
            base_url: Base URL of the Shopify store / ShopifyストアのベースURL
            limit: Number of products per page (max 250, enforced automatically) / 1ページあたりの商品数（最大250、自動的に強制）
            delay: Delay between requests in seconds (for rate limiting) / リクエスト間の遅延（秒）（レート制限のため）
            logger: Optional logger instance (creates default if None) / オプションのロガーインスタンス（Noneの場合はデフォルトを作成）
            batch_size: Batch size for processing products (default: 1000) / 商品処理のバッチサイズ（デフォルト: 1000）
            save_checkpoints: Enable progress checkpoint saving (default: True) / 進捗チェックポイント保存を有効化（デフォルト: True）
            checkpoint_dir: Directory for checkpoint files (default: "data/checkpoints") / チェックポイントファイルのディレクトリ（デフォルト: "data/checkpoints"）
            checkpoint_interval: Save checkpoint every N products (default: 1000) / N商品ごとにチェックポイントを保存（デフォルト: 1000）
            circuit_breaker_enabled: Enable circuit breaker pattern (default: True) / サーキットブレーカーパターンを有効化（デフォルト: True）
            circuit_breaker_failure_threshold: Failures before opening circuit (default: 10) / サーキットを開くまでの失敗数（デフォルト: 10）
            circuit_breaker_timeout: Seconds before attempting to close circuit (default: 60) / サーキットを閉じる試行までの秒数（デフォルト: 60）
            stream_to_disk: Stream products to disk instead of keeping in memory (default: True) / メモリに保持せずディスクにストリーム（デフォルト: True）
            
        Note:
            The limit parameter is automatically capped at 250 (Shopify's maximum).
            limitパラメータは自動的に250（Shopifyの最大値）に制限されます。
        """
        self.base_url = base_url
        # Enforce Shopify's maximum / Shopifyの最大値を強制
        self.limit = min(limit, SHOPIFY_MAX_LIMIT)
        self.delay = delay
        # API endpoints / APIエンドポイント
        self.api_endpoint = f"{base_url}/products.json"
        self.collections_endpoint = f"{base_url}/collections.json"
        self.logger = logger or setup_logger()
        
        # Production-ready features / 本番環境対応機能
        self.batch_size = batch_size
        self.save_checkpoints = save_checkpoints
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_interval = checkpoint_interval
        self.stream_to_disk = stream_to_disk
        
        # Circuit breaker for API failure handling / API障害処理のためのサーキットブレーカー
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_failure_threshold,
            timeout=circuit_breaker_timeout,
            enabled=circuit_breaker_enabled
        )
        
        # Graceful shutdown support / グレースフルシャットダウンサポート
        self.shutdown_requested = False
        self._setup_signal_handlers()
        
        # Initialize statistics tracking / 統計情報の追跡を初期化
        self.stats = {
            "pages_fetched": 0,  # Number of pages fetched / 取得したページ数
            "products_fetched": 0,  # Number of products fetched / 取得した商品数
            "products_transformed": 0,  # Number of products successfully transformed / 正常に変換された商品数
            "products_failed": 0,  # Number of products that failed transformation / 変換に失敗した商品数
            "collections_fetched": 0,  # Number of collections fetched / 取得したコレクション数
            "errors": []  # List of error details / エラー詳細のリスト
        }
    
    def _setup_signal_handlers(self) -> None:
        """
        Setup signal handlers for graceful shutdown.
        グレースフルシャットダウンのためのシグナルハンドラーを設定
        """
        def signal_handler(signum, frame):
            """
            Handle shutdown signals gracefully.
            シャットダウンシグナルを適切に処理
            """
            signal_name = signal.Signals(signum).name
            self.logger.warning(f"\nReceived {signal_name} signal. Initiating graceful shutdown...")
            self.shutdown_requested = True
        
        # Register handlers for SIGTERM and SIGINT / SIGTERMとSIGINTのハンドラーを登録
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    def fetch_page(self, page: int) -> List[Dict[str, Any]]:
        """
        Fetch a single page of products from the Shopify API.
        Shopify APIから1ページの商品を取得
        
        Args:
            page: Page number (1-indexed, not 0-indexed) / ページ番号（1から始まる、0からではない）
            
        Returns:
            List of Shopify product objects from the API response.
            Returns empty list if request fails or no products found.
            APIレスポンスからのShopify商品オブジェクトのリスト。
            リクエストが失敗したか商品が見つからない場合は空のリストを返す。
            
        Example:
            >>> scraper = Scraper()
            >>> products = scraper.fetch_page(1)
            >>> print(f"Found {len(products)} products on page 1")
        """
        # Check circuit breaker before making request / リクエスト前にサーキットブレーカーをチェック
        if not self.circuit_breaker.can_proceed():
            circuit_state = self.circuit_breaker.get_state()
            self.logger.warning(
                f"Circuit breaker is {circuit_state}. Skipping page {page}. "
                f"Waiting for recovery timeout..."
            )
            return []
        
        url = f"{self.api_endpoint}?limit={self.limit}&page={page}"
        self.logger.info(f"Fetching page {page}...")
        
        # Make HTTP request with retry logic / リトライロジック付きHTTPリクエストを実行
        response = make_request(url, logger=self.logger)
        
        # Record success or failure for circuit breaker / サーキットブレーカーの成功または失敗を記録
        if response and "products" in response:
            self.circuit_breaker.record_success()
            products = response["products"]
            self.logger.info(f"  Found {len(products)} products on page {page}")
            
            # Update statistics / 統計情報を更新
            self.stats["pages_fetched"] += 1
            self.stats["products_fetched"] += len(products)
            
            return products
        else:
            # Record failure for circuit breaker
            self.circuit_breaker.record_failure()
            failure_count = self.circuit_breaker.get_failure_count()
            if failure_count >= self.circuit_breaker.failure_threshold:
                self.logger.error(
                    f"Circuit breaker opened after {failure_count} failures. "
                    "API may be experiencing issues."
                )
        
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
            
            # Check for graceful shutdown
            if self.shutdown_requested:
                self.logger.warning("Shutdown requested during fetch. Stopping...")
                break
        
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
            
            # Check for graceful shutdown
            if self.shutdown_requested:
                self.logger.warning("Shutdown requested during collection fetch. Stopping...")
                break
        
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
        2. Transforms each product to custom format (with checkpoint support)
        3. Validates transformed products
        4. Saves to JSON file (with streaming support)
        5. Logs statistics
        
        Supports production-ready features:
        - Progress checkpoints for resumability
        - Streaming to disk for memory optimization
        - Batch processing
        - Graceful shutdown
        
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
        if self.stream_to_disk:
            self.logger.info("Mode: Streaming to disk (memory optimized)")
        if self.save_checkpoints:
            self.logger.info("Checkpoints: Enabled")
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
        
        # Setup checkpoint system
        checkpoint_file = None
        processed_ids = set()
        if self.save_checkpoints:
            ensure_data_dir(self.checkpoint_dir)
            checkpoint_file = os.path.join(
                self.checkpoint_dir,
                os.path.basename(output_file) + ".checkpoint"
            )
            processed_ids = load_checkpoint(checkpoint_file, self.logger)
            if processed_ids:
                self.logger.info(f"Resuming from checkpoint: {len(processed_ids)} products already processed")
        
        # Step 1: Fetch all products from API
        shopify_products = self.fetch_all_products()
        
        if not shopify_products:
            self.logger.error("No products found. Exiting.")
            return False
        
        # Filter out already processed products if resuming from checkpoint
        if processed_ids:
            original_count = len(shopify_products)
            shopify_products = [
                p for p in shopify_products
                if str(p.get("id", "")) not in processed_ids
            ]
            skipped = original_count - len(shopify_products)
            if skipped > 0:
                self.logger.info(f"Skipping {skipped} already processed products")
        
        # Step 2: Transform products to custom format
        self.logger.info(f"\nTransforming {len(shopify_products)} products to custom format...")
        start_time = time.time()
        
        # Prepare output structure based on streaming mode
        if self.stream_to_disk:
            # Streaming mode: write directly to disk
            ensure_data_dir(os.path.dirname(output_file) or ".")
            transformed_products = []  # Only keep current batch in memory
            items_written = 0
            is_first_item = True
        else:
            # Traditional mode: keep all in memory
            transformed_products = []
            items_written = 0
        
        # Process products in batches for memory optimization
        batch_count = 0
        for batch_start in range(0, len(shopify_products), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(shopify_products))
            batch = shopify_products[batch_start:batch_end]
            batch_count += 1
            
            self.logger.debug(f"Processing batch {batch_count}: products {batch_start+1}-{batch_end}")
            
            # Process each product in batch
            for idx, product in enumerate(batch, batch_start + 1):
                # Check for graceful shutdown
                if self.shutdown_requested:
                    self.logger.warning("Shutdown requested. Saving progress and exiting...")
                    if self.save_checkpoints:
                        save_checkpoint(processed_ids, checkpoint_file, self.logger)
                    if self.stream_to_disk and items_written > 0:
                        finalize_streamed_json(output_file, self.logger)
                    return False
                
                try:
                    product_id = str(product.get("id", ""))
                    
                    # Skip if already processed (checkpoint)
                    if product_id in processed_ids:
                        continue
                    
                    # Transform Shopify format to our custom format
                    transformed = parse_shopify_product(product, self.base_url)
                    
                    # Validate the transformed product before adding
                    if validate_product(transformed):
                        if self.stream_to_disk:
                            # Stream directly to disk
                            stream_json_line(transformed, output_file, is_first=is_first_item, logger=self.logger)
                            is_first_item = False
                            items_written += 1
                        else:
                            # Keep in memory
                            transformed_products.append(transformed)
                        
                        processed_ids.add(product_id)
                        self.stats["products_transformed"] += 1
                        
                        # Save checkpoint periodically
                        if self.save_checkpoints and self.stats["products_transformed"] % self.checkpoint_interval == 0:
                            save_checkpoint(processed_ids, checkpoint_file, self.logger)
                    else:
                        # Log validation failure but continue processing
                        self.logger.warning(
                            f"Product {product_id} failed validation, skipping"
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
                        f"({rate:.2f} products/sec, {self.stats['products_transformed']} transformed)"
                    )
            
            # Log batch completion
            if self.stream_to_disk:
                self.logger.debug(f"Batch {batch_count} completed: {len(batch)} products processed")
        
        # Finalize streaming if used
        if self.stream_to_disk:
            finalize_streamed_json(output_file, self.logger)
            total_products = items_written
        else:
            total_products = len(transformed_products)
        
        # Log transformation completion with metrics
        elapsed_time = time.time() - start_time
        rate = total_products / elapsed_time if elapsed_time > 0 else 0
        self.logger.info(
            f"Transformation completed: {total_products} products in "
            f"{elapsed_time:.2f} seconds ({rate:.2f} products/sec)"
        )
        
        # Final checkpoint save
        if self.save_checkpoints:
            save_checkpoint(processed_ids, checkpoint_file, self.logger)
        
        # Step 3: Log detailed statistics
        self._log_statistics()
        
        # Step 4: Save to JSON file (if not streaming)
        success = True
        if not self.stream_to_disk:
            output_data = {
                "items": transformed_products
            }
            ensure_data_dir()
            success = save_json(output_data, output_file, logger=self.logger)
        else:
            # Streaming mode - file already written
            self.logger.info(f"Successfully streamed {total_products} products to {output_file}")
        
        # Store final statistics for programmatic access
        self.final_stats = {
            "total_products": total_products,
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
            self.logger.info(f"Total products saved: {total_products}")
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
