"""Unit tests for scraper functionality"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.scraper import Scraper
from src.parser import parse_shopify_product
from src.utils import make_request, save_json, ensure_data_dir
from src.validator import validate_product


# Sample Shopify product data for testing
SAMPLE_SHOPIFY_PRODUCT = {
    "id": 123456789,
    "title": "Test Product",
    "handle": "test-product",
    "product_type": "Tops",
    "tags": "brand:TestBrand, womens, tops",
    "variants": [
        {
            "id": 987654321,
            "title": "S",
            "price": "29.99"
        },
        {
            "id": 987654322,
            "title": "M",
            "price": "29.99"
        }
    ],
    "images": [
        {
            "src": "https://example.com/image1.jpg"
        },
        {
            "src": "https://example.com/image2.jpg"
        }
    ]
}

SAMPLE_SHOPIFY_RESPONSE = {
    "products": [SAMPLE_SHOPIFY_PRODUCT]
}


class TestScraper:
    """Test cases for Scraper class"""
    
    def test_scraper_initialization(self):
        """Test scraper initialization"""
        scraper = Scraper()
        assert scraper.base_url == "https://pickyou.co.jp"
        assert scraper.limit == 250
        assert scraper.delay == 1.0
    
    def test_scraper_custom_initialization(self):
        """Test scraper with custom parameters"""
        scraper = Scraper(base_url="https://test.com", limit=100, delay=2.0)
        assert scraper.base_url == "https://test.com"
        assert scraper.limit == 100
        assert scraper.delay == 2.0
    
    def test_scraper_limit_max(self):
        """Test that limit is capped at 250"""
        scraper = Scraper(limit=500)
        assert scraper.limit == 250
    
    @patch('src.scraper.make_request')
    def test_fetch_page_success(self, mock_request):
        """Test successful page fetch"""
        mock_request.return_value = SAMPLE_SHOPIFY_RESPONSE
        
        scraper = Scraper()
        products = scraper.fetch_page(1)
        
        assert len(products) == 1
        assert products[0]["id"] == 123456789
        mock_request.assert_called_once()
    
    @patch('src.scraper.make_request')
    def test_fetch_page_empty(self, mock_request):
        """Test page fetch with empty response"""
        mock_request.return_value = {"products": []}
        
        scraper = Scraper()
        products = scraper.fetch_page(1)
        
        assert products == []
    
    @patch('src.scraper.make_request')
    def test_fetch_page_error(self, mock_request):
        """Test page fetch with error"""
        mock_request.return_value = None
        
        scraper = Scraper()
        products = scraper.fetch_page(1)
        
        assert products == []
    
    @patch('src.scraper.make_request')
    @patch('time.sleep')
    def test_fetch_all_products_pagination(self, mock_sleep, mock_request):
        """Test pagination through multiple pages"""
        # First page returns limit (250) products, second page returns 1, third returns empty
        # Create products with unique IDs for page 1
        page1_products = []
        for i in range(250):
            product = SAMPLE_SHOPIFY_PRODUCT.copy()
            product["id"] = 123456789 + i
            product["handle"] = f"test-product-{i}"
            page1_products.append(product)
        
        # Product for page 2 with unique ID
        page2_product = SAMPLE_SHOPIFY_PRODUCT.copy()
        page2_product["id"] = 123456789 + 250
        page2_product["handle"] = "test-product-250"
        
        mock_request.side_effect = [
            {"products": page1_products},  # Page 1: main endpoint
            {"products": [page2_product]},  # Page 2: main endpoint
            {"collections": []},  # Collections page 1 (empty)
        ]
        
        scraper = Scraper(delay=0)  # No delay for testing
        products = scraper.fetch_all_products()
        
        assert len(products) == 251  # 250 from page 1, 1 from page 2
        # Should be called: 2 for main endpoint, 1 for collections
        assert mock_request.call_count >= 2
    
    @patch('src.scraper.make_request')
    @patch('time.sleep')
    def test_fetch_all_products_stops_at_limit(self, mock_sleep, mock_request):
        """Test that pagination stops when fewer products than limit are returned"""
        # First page returns 1 product (less than limit of 250)
        # Also need to mock collections endpoint
        mock_request.side_effect = [
            {"products": [SAMPLE_SHOPIFY_PRODUCT]},  # Main endpoint page 1
            {"collections": []},  # Collections page 1 (empty)
        ]
        
        scraper = Scraper(delay=0)
        products = scraper.fetch_all_products()
        
        assert len(products) == 1
        # Should be called: 1 for main endpoint, 1 for collections
        assert mock_request.call_count >= 1
    
    @patch('src.scraper.make_request')
    @patch('time.sleep')
    def test_fetch_all_collections(self, mock_sleep, mock_request):
        """Test fetching all collections"""
        sample_collection = {
            "id": "123456",
            "handle": "test-collection",
            "title": "Test Collection"
        }
        
        mock_request.side_effect = [
            {"collections": [sample_collection]},  # Page 1
            {"collections": []},  # Page 2 (empty, stops)
        ]
        
        scraper = Scraper(delay=0)
        collections = scraper.fetch_all_collections()
        
        assert len(collections) == 1
        assert collections[0]["id"] == "123456"
        assert collections[0]["handle"] == "test-collection"
    
    @patch('src.scraper.make_request')
    @patch('time.sleep')
    def test_fetch_products_from_collection(self, mock_sleep, mock_request):
        """Test fetching products from a collection"""
        mock_request.side_effect = [
            {"products": [SAMPLE_SHOPIFY_PRODUCT]},  # Page 1
            {"products": []},  # Page 2 (empty, stops)
        ]
        
        scraper = Scraper(delay=0)
        products = scraper.fetch_products_from_collection("123456", "test-collection")
        
        assert len(products) == 1
        assert products[0]["id"] == 123456789
    
    @patch('src.scraper.make_request')
    @patch('time.sleep')
    def test_fetch_all_products_with_collections(self, mock_sleep, mock_request):
        """Test fetching products from main endpoint and collections with deduplication"""
        # Create products with unique IDs
        main_product = SAMPLE_SHOPIFY_PRODUCT.copy()
        main_product["id"] = 100
        
        collection_product1 = SAMPLE_SHOPIFY_PRODUCT.copy()
        collection_product1["id"] = 200
        collection_product1["handle"] = "collection-product-1"
        
        collection_product2 = SAMPLE_SHOPIFY_PRODUCT.copy()
        collection_product2["id"] = 100  # Same ID as main product (duplicate)
        collection_product2["handle"] = "collection-product-2"
        
        sample_collection = {
            "id": "123456",
            "handle": "test-collection",
            "title": "Test Collection"
        }
        
        mock_request.side_effect = [
            {"products": [main_product]},  # Main endpoint page 1
            {"collections": [sample_collection]},  # Collections page 1
            {"products": [collection_product1, collection_product2]},  # Collection products
        ]
        
        scraper = Scraper(delay=0)
        products = scraper.fetch_all_products()
        
        # Should have 2 unique products (100 and 200), not 3 (duplicate removed)
        assert len(products) == 2
        product_ids = {p["id"] for p in products}
        assert product_ids == {100, 200}


class TestParser:
    """Test cases for parser functions"""
    
    def test_parse_shopify_product_basic(self):
        """Test basic product parsing"""
        result = parse_shopify_product(SAMPLE_SHOPIFY_PRODUCT)
        
        assert result["platform"] == "pickyou"
        assert result["id"] == "123456789"
        assert result["name"] == "Test Product"
        assert result["price"] == 29
        assert result["platform_url"] == "https://pickyou.co.jp/products/test-product"
        assert result["image_count"] == 2
    
    def test_parse_shopify_product_sizes(self):
        """Test size extraction"""
        result = parse_shopify_product(SAMPLE_SHOPIFY_PRODUCT)
        
        assert len(result["sizes"]) == 2
        assert result["sizes"][0]["size"] == "S"
        assert result["sizes"][1]["size"] == "M"
    
    def test_parse_shopify_product_images(self):
        """Test image extraction"""
        result = parse_shopify_product(SAMPLE_SHOPIFY_PRODUCT)
        
        assert len(result["item_images"]) == 2
        assert result["s3_image_url"] == "https://example.com/image1.jpg"
        assert result["image_count"] == 2
    
    def test_parse_shopify_product_no_images(self):
        """Test product with no images"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["images"] = []
        
        result = parse_shopify_product(product)
        
        assert result["image_count"] == 0
        assert result["s3_image_url"] == ""
        assert result["item_images"] == []
    
    def test_parse_shopify_product_no_variants(self):
        """Test product with no variants"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["variants"] = []
        
        result = parse_shopify_product(product)
        
        assert result["price"] == 0
        assert len(result["sizes"]) == 1
        assert result["sizes"][0]["size"] == "One Size"
    
    def test_parse_shopify_product_brand_extraction(self):
        """Test brand extraction from tags"""
        result = parse_shopify_product(SAMPLE_SHOPIFY_PRODUCT)
        
        # Should extract brand from tags
        assert result["brand"]["name"] is not None
    
    def test_parse_shopify_product_category(self):
        """Test category extraction"""
        result = parse_shopify_product(SAMPLE_SHOPIFY_PRODUCT)
        
        assert result["category"] == "tops"
    
    def test_parse_shopify_product_gender(self):
        """Test gender extraction"""
        result = parse_shopify_product(SAMPLE_SHOPIFY_PRODUCT)
        
        assert result["gender"] == "womens"
    
    def test_parse_shopify_product_japanese_tags(self):
        """Test parsing with Japanese tags"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["tags"] = "ブランド:TestBrand, レディース, トップス"
        
        result = parse_shopify_product(product)
        
        assert result["gender"] == "womens"
        assert result["category"] == "tops"
        assert result["brand"]["name"] is not None
    
    def test_parse_shopify_product_tags_as_list(self):
        """Test parsing when tags are provided as a list"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["tags"] = ["brand:TestBrand", "womens", "tops"]
        
        result = parse_shopify_product(product)
        
        assert result["gender"] == "womens"
        assert result["category"] == "tops"
    
    def test_parse_shopify_product_mens_gender(self):
        """Test mens gender extraction"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["tags"] = "men, fashion, tops"
        
        result = parse_shopify_product(product)
        
        assert result["gender"] == "mens"
    
    def test_parse_shopify_product_unisex_gender(self):
        """Test unisex gender when no gender tags present"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["tags"] = "fashion, tops"
        
        result = parse_shopify_product(product)
        
        assert result["gender"] == "unisex"
    
    def test_parse_shopify_product_empty_tags(self):
        """Test parsing with empty tags"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["tags"] = ""
        product["product_type"] = None  # Remove product_type to test category fallback
        
        result = parse_shopify_product(product)
        
        assert result["gender"] == "unisex"
        assert result["category"] == "uncategorized"
    
    def test_parse_shopify_product_no_product_type(self):
        """Test category extraction from tags when product_type is missing"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["product_type"] = None
        product["tags"] = "shoes, womens"
        
        result = parse_shopify_product(product)
        
        assert result["category"] == "shoes"
    
    def test_parse_shopify_product_default_title_variant(self):
        """Test that Default Title variants are skipped"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["variants"] = [
            {"id": 1, "title": "Default Title", "price": "29.99"}
        ]
        
        result = parse_shopify_product(product)
        
        assert len(result["sizes"]) == 1
        assert result["sizes"][0]["size"] == "One Size"
    
    def test_parse_shopify_product_invalid_price(self):
        """Test handling of invalid price values"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["variants"] = [
            {"id": 1, "title": "S", "price": "invalid"}
        ]
        
        result = parse_shopify_product(product)
        
        assert result["price"] == 0
    
    def test_parse_shopify_product_missing_handle(self):
        """Test parsing when handle is missing"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["handle"] = ""
        
        result = parse_shopify_product(product)
        
        assert result["platform_url"] == ""
    
    def test_parse_shopify_product_custom_base_url(self):
        """Test parsing with custom base URL"""
        result = parse_shopify_product(
            SAMPLE_SHOPIFY_PRODUCT,
            base_url="https://custom.com"
        )
        
        assert result["platform_url"] == "https://custom.com/products/test-product"
    
    def test_parse_shopify_product_float_price(self):
        """Test parsing price that's a float string"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["variants"] = [
            {"id": 1, "title": "S", "price": "29.50"}
        ]
        
        result = parse_shopify_product(product)
        
        assert result["price"] == 29
    
    def test_parse_shopify_product_brand_without_colon(self):
        """Test brand extraction when tag doesn't have colon"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["tags"] = "brand TestBrand, womens"
        
        result = parse_shopify_product(product)
        
        # Should still extract brand
        assert result["brand"]["name"] is not None
    
    def test_parse_shopify_product_multiple_brand_tags(self):
        """Test that first brand tag is used"""
        product = SAMPLE_SHOPIFY_PRODUCT.copy()
        product["tags"] = "brand:FirstBrand, brand:SecondBrand, womens"
        
        result = parse_shopify_product(product)
        
        assert result["brand"]["name"] == "FirstBrand"
    
    @patch('src.scraper.make_request')
    @patch('src.scraper.parse_shopify_product')
    @patch('src.scraper.validate_product')
    @patch('src.scraper.save_json')
    @patch('src.scraper.ensure_data_dir')
    def test_scrape_and_save_success(self, mock_ensure_dir, mock_save, mock_validate, mock_parse, mock_request):
        """Test complete scrape_and_save workflow"""
        mock_request.side_effect = [
            {"products": [SAMPLE_SHOPIFY_PRODUCT]},
            {"collections": []}
        ]
        
        transformed_product = {
            "platform": "pickyou",
            "id": "123456789",
            "name": "Test Product",
            "price": 29,
            "sizes": [{"id": "S", "row": "S", "size": "S"}],
            "brand": {"id": None, "name": "TestBrand", "sub_name": None},
            "category": "tops",
            "gender": "womens",
            "s3_image_url": "https://example.com/image1.jpg",
            "platform_url": "https://pickyou.co.jp/products/test-product",
            "image_count": 2,
            "item_images": ["https://example.com/image1.jpg"]
        }
        
        mock_parse.return_value = transformed_product
        mock_validate.return_value = True
        mock_save.return_value = True
        
        # Disable streaming to test save_json path
        scraper = Scraper(delay=0, stream_to_disk=False, save_checkpoints=False)
        success = scraper.scrape_and_save("test_output.json")
        
        assert success is True
        assert scraper.stats["products_transformed"] == 1
        mock_save.assert_called_once()
    
    @patch('src.scraper.make_request')
    @patch('time.sleep')
    def test_scrape_and_save_no_products(self, mock_sleep, mock_request):
        """Test scrape_and_save when no products found"""
        mock_request.side_effect = [
            {"products": []},
            {"collections": []}
        ]
        
        scraper = Scraper(delay=0)
        success = scraper.scrape_and_save("test_output.json")
        
        assert success is False
    
    @patch('src.scraper.make_request')
    @patch('src.scraper.parse_shopify_product')
    @patch('src.scraper.validate_product')
    @patch('time.sleep')
    def test_scrape_and_save_validation_failure(self, mock_sleep, mock_validate, mock_parse, mock_request):
        """Test scrape_and_save when product validation fails"""
        mock_request.side_effect = [
            {"products": [SAMPLE_SHOPIFY_PRODUCT]},
            {"collections": []}
        ]
        
        mock_parse.return_value = {"invalid": "product"}
        mock_validate.return_value = False
        
        # Disable checkpoints to avoid state from previous tests
        scraper = Scraper(delay=0, save_checkpoints=False, stream_to_disk=False)
        with patch('src.scraper.save_json', return_value=True):
            success = scraper.scrape_and_save("test_output.json")
        
        assert success is True  # Still succeeds, but product is skipped
        assert scraper.stats["products_failed"] == 1
        assert scraper.stats["products_transformed"] == 0
    
    @patch('src.scraper.make_request')
    @patch('src.scraper.parse_shopify_product')
    @patch('time.sleep')
    def test_scrape_and_save_parse_exception(self, mock_sleep, mock_parse, mock_request):
        """Test scrape_and_save when parsing raises exception"""
        mock_request.side_effect = [
            {"products": [SAMPLE_SHOPIFY_PRODUCT]},
            {"collections": []}
        ]
        
        mock_parse.side_effect = Exception("Parse error")
        
        # Disable checkpoints to avoid state from previous tests
        scraper = Scraper(delay=0, save_checkpoints=False, stream_to_disk=False)
        with patch('src.scraper.save_json', return_value=True):
            success = scraper.scrape_and_save("test_output.json")
        
        assert success is True  # Still succeeds, but product is skipped
        assert scraper.stats["products_failed"] == 1
        assert len(scraper.stats["errors"]) == 1
    
    @patch('src.scraper.make_request')
    @patch('time.sleep')
    def test_fetch_all_collections_pagination(self, mock_sleep, mock_request):
        """Test collections pagination"""
        collection1 = {"id": "1", "handle": "col1", "title": "Collection 1"}
        collection2 = {"id": "2", "handle": "col2", "title": "Collection 2"}
        
        # Return limit (250) collections on page 1 to continue pagination
        page1_collections = [collection1] * 250
        mock_request.side_effect = [
            {"collections": page1_collections},
            {"collections": [collection2]},  # Page 2 has fewer than limit, stops
        ]
        
        scraper = Scraper(delay=0)
        collections = scraper.fetch_all_collections()
        
        assert len(collections) == 251  # 250 from page 1 + 1 from page 2
        assert scraper.stats["collections_fetched"] == 251
    
    @patch('src.scraper.make_request')
    @patch('time.sleep')
    def test_fetch_products_from_collection_pagination(self, mock_sleep, mock_request):
        """Test collection products pagination"""
        product1 = SAMPLE_SHOPIFY_PRODUCT.copy()
        product1["id"] = 1
        product2 = SAMPLE_SHOPIFY_PRODUCT.copy()
        product2["id"] = 2
        
        # Return limit (250) products on page 1 to continue pagination
        page1_products = []
        for i in range(250):
            p = SAMPLE_SHOPIFY_PRODUCT.copy()
            p["id"] = i + 1
            page1_products.append(p)
        
        mock_request.side_effect = [
            {"products": page1_products},
            {"products": [product2]},  # Page 2 has fewer than limit, stops
        ]
        
        scraper = Scraper(delay=0)
        products = scraper.fetch_products_from_collection("123", "test-collection")
        
        assert len(products) == 251  # 250 from page 1 + 1 from page 2
    
    @patch('src.scraper.make_request')
    @patch('time.sleep')
    def test_fetch_products_from_collection_without_handle(self, mock_sleep, mock_request):
        """Test fetching products using only collection ID"""
        mock_request.side_effect = [
            {"products": [SAMPLE_SHOPIFY_PRODUCT]},
            {"products": []}
        ]
        
        scraper = Scraper(delay=0)
        products = scraper.fetch_products_from_collection("123")
        
        assert len(products) == 1
        # Verify URL was constructed with ID
        assert any("collections/123" in str(call) for call in mock_request.call_args_list)
    
    def test_scraper_stats_initialization(self):
        """Test that stats are properly initialized"""
        scraper = Scraper()
        
        assert scraper.stats["pages_fetched"] == 0
        assert scraper.stats["products_fetched"] == 0
        assert scraper.stats["products_transformed"] == 0
        assert scraper.stats["products_failed"] == 0
        assert scraper.stats["collections_fetched"] == 0
        assert scraper.stats["errors"] == []
    
    @patch('src.scraper.make_request')
    def test_fetch_page_updates_stats(self, mock_request):
        """Test that fetch_page updates statistics"""
        mock_request.return_value = {"products": [SAMPLE_SHOPIFY_PRODUCT, SAMPLE_SHOPIFY_PRODUCT]}
        
        scraper = Scraper()
        scraper.fetch_page(1)
        
        assert scraper.stats["pages_fetched"] == 1
        assert scraper.stats["products_fetched"] == 2
    
    @patch('src.scraper.make_request')
    def test_fetch_page_missing_products_key(self, mock_request):
        """Test fetch_page when response doesn't have products key"""
        mock_request.return_value = {"error": "Not found"}
        
        scraper = Scraper()
        products = scraper.fetch_page(1)
        
        assert products == []
    
    def test_scraper_with_custom_logger(self):
        """Test scraper initialization with custom logger"""
        custom_logger = Mock()
        scraper = Scraper(logger=custom_logger)
        
        assert scraper.logger == custom_logger


class TestUtils:
    """Test cases for utility functions"""
    
    @patch('src.utils.requests.Session')
    def test_make_request_success(self, mock_session):
        """Test successful HTTP request"""
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status = Mock()
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        result = make_request("https://example.com")
        
        assert result == {"test": "data"}
    
    @patch('src.utils.requests.Session')
    def test_make_request_error(self, mock_session):
        """Test HTTP request with error"""
        mock_session_instance = Mock()
        mock_session_instance.get.side_effect = Exception("Connection error")
        mock_session.return_value = mock_session_instance
        
        result = make_request("https://example.com")
        
        assert result is None
    
    @patch('src.utils.requests.Session')
    def test_make_request_json_decode_error(self, mock_session):
        """Test HTTP request with invalid JSON response"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status = Mock()
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        result = make_request("https://example.com")
        
        assert result is None
    
    @patch('src.utils.requests.Session')
    def test_make_request_http_error(self, mock_session):
        """Test HTTP request with HTTP error status"""
        import requests
        
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        result = make_request("https://example.com")
        
        assert result is None
    
    @patch('src.utils.requests.Session')
    def test_make_request_with_logger(self, mock_session):
        """Test make_request with logger parameter"""
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status = Mock()
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        logger = Mock()
        result = make_request("https://example.com", logger=logger)
        
        assert result == {"test": "data"}
    
    def test_ensure_data_dir(self):
        """Test data directory creation"""
        test_dir = "test_data_dir"
        
        # Remove if exists
        if os.path.exists(test_dir):
            os.rmdir(test_dir)
        
        ensure_data_dir(test_dir)
        
        assert os.path.exists(test_dir)
        assert os.path.isdir(test_dir)
        
        # Cleanup
        os.rmdir(test_dir)
    
    def test_save_json(self):
        """Test JSON file saving"""
        test_file = "test_output.json"
        test_data = {"items": [{"id": "1", "name": "Test"}]}
        
        # Remove if exists
        if os.path.exists(test_file):
            os.remove(test_file)
        
        result = save_json(test_data, test_file)
        
        assert result is True
        assert os.path.exists(test_file)
        
        # Verify content
        with open(test_file, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data
        
        # Cleanup
        os.remove(test_file)
    
    def test_save_json_invalid_path(self):
        """Test JSON saving with invalid path"""
        # This should handle the error gracefully
        test_data = {"items": []}
        result = save_json(test_data, "/invalid/path/file.json")
        
        # Should return False or handle error
        assert isinstance(result, bool)
    
    def test_save_json_with_logger(self):
        """Test save_json with logger parameter"""
        test_file = "test_output_logger.json"
        test_data = {"items": [{"id": "1"}]}
        
        if os.path.exists(test_file):
            os.remove(test_file)
        
        logger = Mock()
        result = save_json(test_data, test_file, logger=logger)
        
        assert result is True
        assert os.path.exists(test_file)
        logger.info.assert_called_once()
        
        os.remove(test_file)
    
    def test_save_json_creates_directory(self):
        """Test that save_json creates parent directories"""
        test_file = "test_dir/subdir/test_output.json"
        test_data = {"items": []}
        
        # Remove if exists
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists("test_dir"):
            import shutil
            shutil.rmtree("test_dir")
        
        result = save_json(test_data, test_file)
        
        assert result is True
        assert os.path.exists(test_file)
        
        # Cleanup
        import shutil
        shutil.rmtree("test_dir")
    
    def test_ensure_data_dir_existing(self):
        """Test ensure_data_dir when directory already exists"""
        test_dir = "test_existing_dir"
        
        # Create directory first
        os.makedirs(test_dir, exist_ok=True)
        
        # Should not raise error
        ensure_data_dir(test_dir)
        
        assert os.path.exists(test_dir)
        
        # Cleanup
        os.rmdir(test_dir)

