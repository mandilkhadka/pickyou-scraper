"""
Data validation for transformed products.
変換された商品のデータ検証

This module validates that transformed products conform to the expected schema
before they are saved to the output file. This ensures data quality and
prevents downstream pipeline errors.
このモジュールは、変換された商品が期待されるスキーマに準拠していることを
出力ファイルに保存する前に検証します。これによりデータ品質が確保され、
下流のパイプラインエラーを防ぎます。
"""

from typing import Any, Dict


# Constants for validation / 検証用の定数
# Required fields in transformed product / 変換された商品の必須フィールド
REQUIRED_FIELDS = [
    "platform", "id", "name", "price", "sizes", "brand",
    "category", "gender", "s3_image_url", "platform_url",
    "image_count", "item_images"
]

VALID_GENDERS = ["womens", "mens", "unisex"]  # Valid gender values / 有効な性別値
REQUIRED_SIZE_FIELDS = ["id", "row", "size"]  # Required fields in size objects / サイズオブジェクトの必須フィールド
REQUIRED_BRAND_FIELDS = ["id", "name", "sub_name"]  # Required fields in brand object / ブランドオブジェクトの必須フィールド


def validate_product(product: Dict[str, Any]) -> bool:
    """
    Validate that a transformed product has all required fields and correct types.
    
    This function performs comprehensive validation to ensure:
    - All required fields are present
    - Field types are correct
    - Field values are valid (e.g., gender is one of the allowed values)
    - Nested structures (sizes, brand) are properly formatted
    
    Args:
        product: Transformed product dictionary to validate
        
    Returns:
        True if product is valid and ready for saving, False otherwise.
        
    Example:
        >>> product = {
        ...     "platform": "pickyou",
        ...     "id": "123",
        ...     "name": "Test Product",
        ...     "price": 1000,
        ...     "sizes": [{"id": "S", "row": "S", "size": "S"}],
        ...     "brand": {"id": None, "name": "Brand", "sub_name": None},
        ...     "category": "tops",
        ...     "gender": "womens",
        ...     "s3_image_url": "https://example.com/image.jpg",
        ...     "platform_url": "https://pickyou.co.jp/products/test",
        ...     "image_count": 1,
        ...     "item_images": ["https://example.com/image.jpg"]
        ... }
        >>> is_valid = validate_product(product)
        >>> print(is_valid)  # True
    """
    # Step 1: Check all required fields exist
    for field in REQUIRED_FIELDS:
        if field not in product:
            return False
    
    # Step 2: Validate platform field
    # Must be a non-empty string
    if not isinstance(product["platform"], str) or not product["platform"]:
        return False
    
    # Step 3: Validate product ID
    # Must be present and truthy (not empty string, None, etc.)
    if not product["id"]:
        return False
    
    # Step 4: Validate product name
    # Must be a non-empty string
    if not isinstance(product["name"], str) or not product["name"]:
        return False
    
    # Step 5: Validate price
    # Must be an integer (we convert floats to ints during parsing)
    if not isinstance(product["price"], int):
        return False
    
    # Step 6: Validate sizes array
    # Must be a list with at least one item (required by schema)
    if not isinstance(product["sizes"], list) or len(product["sizes"]) == 0:
        return False
    
    # Step 7: Validate each size object structure
    for size in product["sizes"]:
        # Each size must be a dictionary
        if not isinstance(size, dict):
            return False
        # Each size must have required fields
        if not all(field in size for field in REQUIRED_SIZE_FIELDS):
            return False
    
    # Step 8: Validate brand object structure
    if not isinstance(product["brand"], dict):
        return False
    # Brand must have all required fields (values can be None)
    if not all(field in product["brand"] for field in REQUIRED_BRAND_FIELDS):
        return False
    
    # Step 9: Validate category
    # Must be a string (can be empty, but should be a string)
    if not isinstance(product["category"], str):
        return False
    
    # Step 10: Validate gender
    # Must be one of the allowed values
    if product["gender"] not in VALID_GENDERS:
        return False
    
    # Step 11: Validate image_count
    # Must be a non-negative integer
    if not isinstance(product["image_count"], int) or product["image_count"] < 0:
        return False
    
    # Step 12: Validate item_images
    # Must be a list (can be empty if no images)
    if not isinstance(product["item_images"], list):
        return False
    
    # Step 13: Validate platform_url
    # Must be a string (can be empty if handle is missing)
    if not isinstance(product["platform_url"], str):
        return False
    
    # All validations passed
    return True
