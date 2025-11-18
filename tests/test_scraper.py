"""Unit tests for scraper functionality"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.scraper import Scraper
from src.parser import parse_shopify_product
from src.utils import make_request, save_json, ensure_data_dir


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

