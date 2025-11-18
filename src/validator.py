"""Data validation for transformed products"""

from typing import Any, Dict


def validate_product(product: Dict[str, Any]) -> bool:
    """
    Validate that a transformed product has all required fields.
    
    Args:
        product: Transformed product dictionary
        
    Returns:
        True if product is valid, False otherwise
    """
    # Required fields
    required_fields = ["platform", "id", "name", "price", "sizes", "brand", 
                      "category", "gender", "s3_image_url", "platform_url", 
                      "image_count", "item_images"]
    
    # Check all required fields exist
    for field in required_fields:
        if field not in product:
            return False
    
    # Validate platform
    if not isinstance(product["platform"], str) or not product["platform"]:
        return False
    
    # Validate id
    if not product["id"]:
        return False
    
    # Validate name
    if not isinstance(product["name"], str) or not product["name"]:
        return False
    
    # Validate price (must be integer)
    if not isinstance(product["price"], int):
        return False
    
    # Validate sizes (must be list with at least one item)
    if not isinstance(product["sizes"], list) or len(product["sizes"]) == 0:
        return False
    
    # Validate each size object
    for size in product["sizes"]:
        if not isinstance(size, dict):
            return False
        if "id" not in size or "row" not in size or "size" not in size:
            return False
    
    # Validate brand (must be dict with id, name, sub_name)
    if not isinstance(product["brand"], dict):
        return False
    if "id" not in product["brand"] or "name" not in product["brand"] or "sub_name" not in product["brand"]:
        return False
    
    # Validate category
    if not isinstance(product["category"], str):
        return False
    
    # Validate gender
    if product["gender"] not in ["womens", "mens", "unisex"]:
        return False
    
    # Validate image_count (must be integer)
    if not isinstance(product["image_count"], int) or product["image_count"] < 0:
        return False
    
    # Validate item_images (must be list)
    if not isinstance(product["item_images"], list):
        return False
    
    # Validate platform_url
    if not isinstance(product["platform_url"], str):
        return False
    
    return True

