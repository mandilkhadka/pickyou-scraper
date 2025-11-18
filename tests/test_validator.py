"""Unit tests for validator functionality"""

import pytest
from src.validator import validate_product


# Valid product for testing
VALID_PRODUCT = {
    "platform": "pickyou",
    "id": "123456789",
    "name": "Test Product",
    "price": 1000,
    "sizes": [
        {
            "id": "S",
            "row": "S",
            "size": "S"
        },
        {
            "id": "M",
            "row": "M",
            "size": "M"
        }
    ],
    "brand": {
        "id": None,
        "name": "TestBrand",
        "sub_name": None
    },
    "category": "tops",
    "gender": "womens",
    "s3_image_url": "https://example.com/image.jpg",
    "platform_url": "https://pickyou.co.jp/products/test-product",
    "image_count": 1,
    "item_images": ["https://example.com/image.jpg"]
}


class TestValidator:
    """Test cases for product validation"""
    
    def test_validate_product_valid(self):
        """Test validation of a valid product"""
        assert validate_product(VALID_PRODUCT) is True
    
    def test_validate_product_missing_platform(self):
        """Test validation fails when platform is missing"""
        product = VALID_PRODUCT.copy()
        del product["platform"]
        assert validate_product(product) is False
    
    def test_validate_product_empty_platform(self):
        """Test validation fails when platform is empty"""
        product = VALID_PRODUCT.copy()
        product["platform"] = ""
        assert validate_product(product) is False
    
    def test_validate_product_missing_id(self):
        """Test validation fails when id is missing"""
        product = VALID_PRODUCT.copy()
        del product["id"]
        assert validate_product(product) is False
    
    def test_validate_product_empty_id(self):
        """Test validation fails when id is empty"""
        product = VALID_PRODUCT.copy()
        product["id"] = ""
        assert validate_product(product) is False
    
    def test_validate_product_none_id(self):
        """Test validation fails when id is None"""
        product = VALID_PRODUCT.copy()
        product["id"] = None
        assert validate_product(product) is False
    
    def test_validate_product_missing_name(self):
        """Test validation fails when name is missing"""
        product = VALID_PRODUCT.copy()
        del product["name"]
        assert validate_product(product) is False
    
    def test_validate_product_empty_name(self):
        """Test validation fails when name is empty"""
        product = VALID_PRODUCT.copy()
        product["name"] = ""
        assert validate_product(product) is False
    
    def test_validate_product_missing_price(self):
        """Test validation fails when price is missing"""
        product = VALID_PRODUCT.copy()
        del product["price"]
        assert validate_product(product) is False
    
    def test_validate_product_price_not_int(self):
        """Test validation fails when price is not an integer"""
        product = VALID_PRODUCT.copy()
        product["price"] = "1000"  # String instead of int
        assert validate_product(product) is False
        
        product["price"] = 1000.5  # Float instead of int
        assert validate_product(product) is False
    
    def test_validate_product_missing_sizes(self):
        """Test validation fails when sizes is missing"""
        product = VALID_PRODUCT.copy()
        del product["sizes"]
        assert validate_product(product) is False
    
    def test_validate_product_empty_sizes(self):
        """Test validation fails when sizes is empty"""
        product = VALID_PRODUCT.copy()
        product["sizes"] = []
        assert validate_product(product) is False
    
    def test_validate_product_sizes_not_list(self):
        """Test validation fails when sizes is not a list"""
        product = VALID_PRODUCT.copy()
        product["sizes"] = "not a list"
        assert validate_product(product) is False
    
    def test_validate_product_size_missing_fields(self):
        """Test validation fails when size object is missing required fields"""
        product = VALID_PRODUCT.copy()
        product["sizes"] = [{"id": "S"}]  # Missing "row" and "size"
        assert validate_product(product) is False
        
        product["sizes"] = [{"id": "S", "row": "S"}]  # Missing "size"
        assert validate_product(product) is False
    
    def test_validate_product_size_not_dict(self):
        """Test validation fails when size is not a dictionary"""
        product = VALID_PRODUCT.copy()
        product["sizes"] = ["S", "M"]  # List of strings instead of dicts
        assert validate_product(product) is False
    
    def test_validate_product_missing_brand(self):
        """Test validation fails when brand is missing"""
        product = VALID_PRODUCT.copy()
        del product["brand"]
        assert validate_product(product) is False
    
    def test_validate_product_brand_not_dict(self):
        """Test validation fails when brand is not a dictionary"""
        product = VALID_PRODUCT.copy()
        product["brand"] = "not a dict"
        assert validate_product(product) is False
    
    def test_validate_product_brand_missing_fields(self):
        """Test validation fails when brand is missing required fields"""
        product = VALID_PRODUCT.copy()
        product["brand"] = {"id": None, "name": "Test"}  # Missing "sub_name"
        assert validate_product(product) is False
        
        product["brand"] = {"name": "Test", "sub_name": None}  # Missing "id"
        assert validate_product(product) is False
    
    def test_validate_product_brand_none_values(self):
        """Test validation passes when brand fields are None"""
        product = VALID_PRODUCT.copy()
        product["brand"] = {"id": None, "name": None, "sub_name": None}
        assert validate_product(product) is True
    
    def test_validate_product_missing_category(self):
        """Test validation fails when category is missing"""
        product = VALID_PRODUCT.copy()
        del product["category"]
        assert validate_product(product) is False
    
    def test_validate_product_category_not_string(self):
        """Test validation fails when category is not a string"""
        product = VALID_PRODUCT.copy()
        product["category"] = 123
        assert validate_product(product) is False
    
    def test_validate_product_empty_category(self):
        """Test validation passes when category is empty string"""
        product = VALID_PRODUCT.copy()
        product["category"] = ""
        assert validate_product(product) is True
    
    def test_validate_product_missing_gender(self):
        """Test validation fails when gender is missing"""
        product = VALID_PRODUCT.copy()
        del product["gender"]
        assert validate_product(product) is False
    
    def test_validate_product_invalid_gender(self):
        """Test validation fails when gender is not a valid value"""
        product = VALID_PRODUCT.copy()
        product["gender"] = "invalid"
        assert validate_product(product) is False
        
        product["gender"] = "women"  # Should be "womens"
        assert validate_product(product) is False
    
    def test_validate_product_valid_genders(self):
        """Test validation passes for all valid gender values"""
        product = VALID_PRODUCT.copy()
        
        product["gender"] = "womens"
        assert validate_product(product) is True
        
        product["gender"] = "mens"
        assert validate_product(product) is True
        
        product["gender"] = "unisex"
        assert validate_product(product) is True
    
    def test_validate_product_missing_image_count(self):
        """Test validation fails when image_count is missing"""
        product = VALID_PRODUCT.copy()
        del product["image_count"]
        assert validate_product(product) is False
    
    def test_validate_product_image_count_not_int(self):
        """Test validation fails when image_count is not an integer"""
        product = VALID_PRODUCT.copy()
        product["image_count"] = "1"
        assert validate_product(product) is False
    
    def test_validate_product_negative_image_count(self):
        """Test validation fails when image_count is negative"""
        product = VALID_PRODUCT.copy()
        product["image_count"] = -1
        assert validate_product(product) is False
    
    def test_validate_product_zero_image_count(self):
        """Test validation passes when image_count is zero"""
        product = VALID_PRODUCT.copy()
        product["image_count"] = 0
        assert validate_product(product) is True
    
    def test_validate_product_missing_item_images(self):
        """Test validation fails when item_images is missing"""
        product = VALID_PRODUCT.copy()
        del product["item_images"]
        assert validate_product(product) is False
    
    def test_validate_product_item_images_not_list(self):
        """Test validation fails when item_images is not a list"""
        product = VALID_PRODUCT.copy()
        product["item_images"] = "not a list"
        assert validate_product(product) is False
    
    def test_validate_product_empty_item_images(self):
        """Test validation passes when item_images is empty"""
        product = VALID_PRODUCT.copy()
        product["item_images"] = []
        assert validate_product(product) is True
    
    def test_validate_product_missing_platform_url(self):
        """Test validation fails when platform_url is missing"""
        product = VALID_PRODUCT.copy()
        del product["platform_url"]
        assert validate_product(product) is False
    
    def test_validate_product_platform_url_not_string(self):
        """Test validation fails when platform_url is not a string"""
        product = VALID_PRODUCT.copy()
        product["platform_url"] = 123
        assert validate_product(product) is False
    
    def test_validate_product_empty_platform_url(self):
        """Test validation passes when platform_url is empty string"""
        product = VALID_PRODUCT.copy()
        product["platform_url"] = ""
        assert validate_product(product) is True
    
    def test_validate_product_missing_s3_image_url(self):
        """Test validation fails when s3_image_url is missing"""
        product = VALID_PRODUCT.copy()
        del product["s3_image_url"]
        assert validate_product(product) is False
    
    def test_validate_product_all_required_fields(self):
        """Test that all required fields are checked"""
        # Test with minimal valid product
        minimal_product = {
            "platform": "pickyou",
            "id": "1",
            "name": "Product",
            "price": 0,
            "sizes": [{"id": "One Size", "row": "One Size", "size": "One Size"}],
            "brand": {"id": None, "name": None, "sub_name": None},
            "category": "",
            "gender": "unisex",
            "s3_image_url": "",
            "platform_url": "",
            "image_count": 0,
            "item_images": []
        }
        assert validate_product(minimal_product) is True
    
    def test_validate_product_multiple_sizes(self):
        """Test validation with multiple sizes"""
        product = VALID_PRODUCT.copy()
        product["sizes"] = [
            {"id": "XS", "row": "XS", "size": "XS"},
            {"id": "S", "row": "S", "size": "S"},
            {"id": "M", "row": "M", "size": "M"},
            {"id": "L", "row": "L", "size": "L"},
            {"id": "XL", "row": "XL", "size": "XL"}
        ]
        assert validate_product(product) is True

