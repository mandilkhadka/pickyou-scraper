"""Parser to transform Shopify product format to custom JSON format"""

from typing import Any, Dict, List, Optional


def extract_brand_from_tags(tags: List[str]) -> Optional[Dict[str, Any]]:
    """
    Extract brand information from product tags.
    
    Args:
        tags: List of product tags
        
    Returns:
        Brand dictionary with id, name, sub_name, or None
    """
    if not tags:
        return None
    
    # Look for brand-related tags (common patterns)
    brand_keywords = ["brand", "ブランド", "メーカー"]
    for tag in tags:
        tag_lower = tag.lower()
        if any(keyword in tag_lower for keyword in brand_keywords):
            # Try to extract brand name
            parts = tag.split(":")
            if len(parts) > 1:
                brand_name = parts[-1].strip()
            else:
                brand_name = tag.strip()
            
            return {
                "id": None,
                "name": brand_name,
                "sub_name": None
            }
    
    return None


def extract_category(product_type: Optional[str], tags: List[str]) -> str:
    """
    Extract category from product_type or tags.
    
    Args:
        product_type: Shopify product_type field
        tags: List of product tags
        
    Returns:
        Category string or "uncategorized"
    """
    if product_type:
        return product_type.lower()
    
    # Common category tags
    category_tags = ["tops", "bottoms", "shoes", "accessories", "トップス", "ボトムス", "シューズ"]
    for tag in tags:
        tag_lower = tag.lower()
        if any(cat in tag_lower for cat in category_tags):
            return tag_lower
    
    return "uncategorized"


def extract_gender(tags: List[str]) -> str:
    """
    Extract gender from tags.
    
    Args:
        tags: List of product tags
        
    Returns:
        Gender string (womens, mens, unisex) or "unisex" as default
    """
    if not tags:
        return "unisex"
    
    tags_lower = [tag.lower() for tag in tags]
    
    # Check for gender indicators
    if any("women" in tag or "レディース" in tag or "女性" in tag for tag in tags_lower):
        return "womens"
    if any("men" in tag or "メンズ" in tag or "男性" in tag for tag in tags_lower):
        return "mens"
    
    return "unisex"


def parse_shopify_product(shopify_product: Dict[str, Any], base_url: str = "https://pickyou.co.jp") -> Dict[str, Any]:
    """
    Transform Shopify product object to custom JSON format.
    
    Args:
        shopify_product: Shopify product object from API
        base_url: Base URL for constructing platform URLs
        
    Returns:
        Transformed product in custom format
    """
    # Extract basic fields
    product_id = str(shopify_product.get("id", ""))
    handle = shopify_product.get("handle", "")
    title = shopify_product.get("title", "")
    tags = shopify_product.get("tags", "").split(",") if shopify_product.get("tags") else []
    tags = [tag.strip() for tag in tags if tag.strip()]
    product_type = shopify_product.get("product_type")
    variants = shopify_product.get("variants", [])
    images = shopify_product.get("images", [])
    
    # Extract price (use first variant's price)
    price = 0
    if variants and len(variants) > 0:
        try:
            price = int(float(variants[0].get("price", 0)))
        except (ValueError, TypeError):
            price = 0
    
    # Extract sizes from variants
    sizes = []
    for variant in variants:
        variant_title = variant.get("title", "")
        if variant_title and variant_title != "Default Title":
            sizes.append({
                "id": variant_title,
                "row": variant_title,
                "size": variant_title
            })
    
    # If no sizes found, create a default
    if not sizes:
        sizes.append({
            "id": "One Size",
            "row": "One Size",
            "size": "One Size"
        })
    
    # Extract brand
    brand = extract_brand_from_tags(tags)
    if not brand:
        brand = {
            "id": None,
            "name": None,
            "sub_name": None
        }
    
    # Extract category
    category = extract_category(product_type, tags)
    
    # Extract gender
    gender = extract_gender(tags)
    
    # Extract images
    image_urls = [img.get("src", "") for img in images if img.get("src")]
    s3_image_url = image_urls[0] if image_urls else ""
    image_count = len(image_urls)
    
    # Construct platform URL
    platform_url = f"{base_url}/products/{handle}" if handle else ""
    
    # Build custom format
    return {
        "platform": "pickyou",
        "id": product_id,
        "name": title,
        "price": price,
        "sizes": sizes,
        "brand": brand,
        "category": category,
        "gender": gender,
        "s3_image_url": s3_image_url,
        "platform_url": platform_url,
        "image_count": image_count,
        "item_images": image_urls
    }

