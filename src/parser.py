"""
Parser to transform Shopify product format to custom JSON format.

This module handles the transformation of raw Shopify API product data
into the custom format required by the extraction pipeline.
"""

from typing import Any, Dict, List, Optional


# Constants for tag matching
BRAND_KEYWORDS = ["brand", "ブランド", "メーカー"]  # English and Japanese brand keywords
CATEGORY_KEYWORDS = ["tops", "bottoms", "shoes", "accessories", "トップス", "ボトムス", "シューズ"]
GENDER_WOMENS_KEYWORDS = ["women", "レディース", "女性"]
GENDER_MENS_KEYWORDS = ["men", "メンズ", "男性"]
DEFAULT_CATEGORY = "uncategorized"
DEFAULT_GENDER = "unisex"
DEFAULT_SIZE = "One Size"


def extract_brand_from_tags(tags: List[str]) -> Optional[Dict[str, Any]]:
    """
    Extract brand information from product tags.
    
    Searches through product tags for brand-related keywords and extracts
    the brand name. Supports both English and Japanese keywords.
    
    Args:
        tags: List of product tags (strings)
        
    Returns:
        Brand dictionary with structure: {"id": None, "name": str, "sub_name": None}
        Returns None if no brand found in tags.
        
    Example:
        >>> tags = ["brand:Nike", "sports", "shoes"]
        >>> brand = extract_brand_from_tags(tags)
        >>> print(brand["name"])  # "Nike"
    """
    if not tags:
        return None
    
    # Search for brand-related tags
    for tag in tags:
        tag_lower = tag.lower()
        
        # Check if tag contains brand keywords
        if any(keyword in tag_lower for keyword in BRAND_KEYWORDS):
            # Extract brand name from tag
            # Format can be "brand:Name" or just "Name"
            parts = tag.split(":")
            if len(parts) > 1:
                # Extract name after colon
                brand_name = parts[-1].strip()
            else:
                # Use entire tag as brand name
                brand_name = tag.strip()
            
            return {
                "id": None,  # Brand ID not available from tags
                "name": brand_name,
                "sub_name": None  # Sub-brand not available from tags
            }
    
    return None


def extract_category(product_type: Optional[str], tags: List[str]) -> str:
    """
    Extract product category from product_type field or tags.
    
    First tries to use the product_type field from Shopify.
    If not available, searches tags for category keywords.
    Falls back to "uncategorized" if nothing found.
    
    Args:
        product_type: Shopify product_type field (can be None)
        tags: List of product tags
        
    Returns:
        Category string (lowercase) or "uncategorized" as default.
        
    Example:
        >>> category = extract_category("Tops", ["womens", "fashion"])
        >>> print(category)  # "tops"
    """
    # Prefer product_type if available (more reliable)
    if product_type:
        return product_type.lower()
    
    # Search tags for category keywords
    for tag in tags:
        tag_lower = tag.lower()
        if any(cat in tag_lower for cat in CATEGORY_KEYWORDS):
            return tag_lower
    
    # Default fallback
    return DEFAULT_CATEGORY


def extract_gender(tags: List[str]) -> str:
    """
    Extract gender classification from product tags.
    
    Searches tags for gender indicators in both English and Japanese.
    Returns "womens", "mens", or "unisex" (default).
    
    Args:
        tags: List of product tags
        
    Returns:
        Gender string: "womens", "mens", or "unisex" (default).
        
    Example:
        >>> gender = extract_gender(["womens", "fashion", "tops"])
        >>> print(gender)  # "womens"
    """
    if not tags:
        return DEFAULT_GENDER
    
    # Convert all tags to lowercase for case-insensitive matching
    tags_lower = [tag.lower() for tag in tags]
    
    # Check for women's/girl's indicators
    if any(keyword in tag for tag in tags_lower for keyword in GENDER_WOMENS_KEYWORDS):
        return "womens"
    
    # Check for men's/boy's indicators
    if any(keyword in tag for tag in tags_lower for keyword in GENDER_MENS_KEYWORDS):
        return "mens"
    
    # Default to unisex if no gender indicators found
    return DEFAULT_GENDER


def parse_shopify_product(
    shopify_product: Dict[str, Any], 
    base_url: str = "https://pickyou.co.jp"
) -> Dict[str, Any]:
    """
    Transform Shopify product object to custom JSON format.
    
    This is the main transformation function that converts a raw Shopify
    product object into the custom format required by the pipeline.
    
    Args:
        shopify_product: Raw Shopify product object from API
        base_url: Base URL for constructing product URLs (default: "https://pickyou.co.jp")
        
    Returns:
        Transformed product dictionary in custom format with fields:
        - platform: "pickyou"
        - id: Product ID (string)
        - name: Product title
        - price: Price as integer
        - sizes: List of size objects
        - brand: Brand object with id, name, sub_name
        - category: Category string
        - gender: Gender string (womens/mens/unisex)
        - s3_image_url: Primary image URL
        - platform_url: Full product URL
        - image_count: Number of images
        - item_images: List of all image URLs
        
    Example:
        >>> shopify_product = {
        ...     "id": 123,
        ...     "title": "Test Product",
        ...     "handle": "test-product",
        ...     "variants": [{"title": "S", "price": "29.99"}],
        ...     "images": [{"src": "https://example.com/image.jpg"}]
        ... }
        >>> result = parse_shopify_product(shopify_product)
        >>> print(result["name"])  # "Test Product"
        >>> print(result["price"])  # 29
    """
    # Extract basic product information
    product_id = str(shopify_product.get("id", ""))
    handle = shopify_product.get("handle", "")  # URL-friendly product identifier
    title = shopify_product.get("title", "")
    
    # Handle tags - Shopify API can return tags as string or list
    # We normalize to a list for consistent processing
    tags_raw = shopify_product.get("tags", "")
    if isinstance(tags_raw, list):
        # Already a list, just clean it up
        tags = [str(tag).strip() for tag in tags_raw if tag]
    elif isinstance(tags_raw, str):
        # Comma-separated string, split it
        tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]
    else:
        # Unknown format, use empty list
        tags = []
    
    # Extract other product fields
    product_type = shopify_product.get("product_type")
    variants = shopify_product.get("variants", [])  # Product variants (sizes, colors, etc.)
    images = shopify_product.get("images", [])  # Product images
    
    # Extract price from first variant (Shopify stores price per variant)
    price = 0
    if variants and len(variants) > 0:
        try:
            # Convert price string to integer (Shopify returns prices as strings)
            price = int(float(variants[0].get("price", 0)))
        except (ValueError, TypeError):
            # If price conversion fails, default to 0
            price = 0
    
    # Extract sizes from variants
    # Each variant typically represents a different size
    sizes = []
    for variant in variants:
        variant_title = variant.get("title", "")
        # Skip "Default Title" which Shopify uses when there's only one variant
        if variant_title and variant_title != "Default Title":
            sizes.append({
                "id": variant_title,
                "row": variant_title,  # Same as id for now
                "size": variant_title
            })
    
    # If no sizes found, create a default "One Size" entry
    # This ensures the sizes array is never empty (required by schema)
    if not sizes:
        sizes.append({
            "id": DEFAULT_SIZE,
            "row": DEFAULT_SIZE,
            "size": DEFAULT_SIZE
        })
    
    # Extract brand information from tags
    brand = extract_brand_from_tags(tags)
    if not brand:
        # Create empty brand structure if no brand found
        brand = {
            "id": None,
            "name": None,
            "sub_name": None
        }
    
    # Extract category and gender using helper functions
    category = extract_category(product_type, tags)
    gender = extract_gender(tags)
    
    # Extract image URLs
    image_urls = [img.get("src", "") for img in images if img.get("src")]
    s3_image_url = image_urls[0] if image_urls else ""  # Primary image (first one)
    image_count = len(image_urls)
    
    # Construct full product URL on the platform
    platform_url = f"{base_url}/products/{handle}" if handle else ""
    
    # Build and return the custom format product object
    return {
        "platform": "pickyou",
        "id": product_id,
        "name": title,
        "price": price,
        "sizes": sizes,
        "brand": brand,
        "category": category,
        "gender": gender,
        "s3_image_url": s3_image_url,  # Note: This is actually the original URL, not S3
        "platform_url": platform_url,
        "image_count": image_count,
        "item_images": image_urls
    }
