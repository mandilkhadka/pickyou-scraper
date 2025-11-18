"""
Parser to transform Shopify product format to custom JSON format.
Shopify商品形式をカスタムJSON形式に変換するパーサー

This module handles the transformation of raw Shopify API product data
into the custom format required by the extraction pipeline.
このモジュールは、生のShopify API商品データを抽出パイプラインで必要な
カスタム形式に変換する処理を行います。
"""

from typing import Any, Dict, List, Optional


# Constants for tag matching / タグマッチング用の定数
# English and Japanese brand keywords / 英語と日本語のブランドキーワード
BRAND_KEYWORDS = ["brand", "ブランド", "メーカー"]
# Category keywords in English and Japanese / 英語と日本語のカテゴリキーワード
CATEGORY_KEYWORDS = ["tops", "bottoms", "shoes", "accessories", "トップス", "ボトムス", "シューズ"]
# Women's gender keywords / 女性の性別キーワード
GENDER_WOMENS_KEYWORDS = ["women", "レディース", "女性"]
# Men's gender keywords / 男性の性別キーワード
GENDER_MENS_KEYWORDS = ["men", "メンズ", "男性"]
# Default values / デフォルト値
DEFAULT_CATEGORY = "uncategorized"  # Default category / デフォルトカテゴリ
DEFAULT_GENDER = "unisex"  # Default gender / デフォルト性別
DEFAULT_SIZE = "One Size"  # Default size / デフォルトサイズ


def extract_brand_from_tags(tags: List[str]) -> Optional[Dict[str, Any]]:
    """
    Extract brand information from product tags.
    商品タグからブランド情報を抽出
    
    Searches through product tags for brand-related keywords and extracts
    the brand name. Supports both English and Japanese keywords.
    商品タグ内でブランド関連のキーワードを検索し、ブランド名を抽出します。
    英語と日本語のキーワードの両方をサポートします。
    
    Args:
        tags: List of product tags (strings) / 商品タグのリスト（文字列）
        
    Returns:
        Brand dictionary with structure: {"id": None, "name": str, "sub_name": None}
        Returns None if no brand found in tags.
        構造: {"id": None, "name": str, "sub_name": None} のブランド辞書
        タグにブランドが見つからない場合はNoneを返す。
        
    Example:
        >>> tags = ["brand:Nike", "sports", "shoes"]
        >>> brand = extract_brand_from_tags(tags)
        >>> print(brand["name"])  # "Nike"
    """
    if not tags:
        return None
    
    # Search for brand-related tags / ブランド関連のタグを検索
    for tag in tags:
        tag_lower = tag.lower()
        
        # Check if tag contains brand keywords / タグにブランドキーワードが含まれているかチェック
        if any(keyword in tag_lower for keyword in BRAND_KEYWORDS):
            # Extract brand name from tag / タグからブランド名を抽出
            # Format can be "brand:Name" or just "Name" / 形式は "brand:Name" または単に "Name"
            parts = tag.split(":")
            if len(parts) > 1:
                # Extract name after colon / コロンの後の名前を抽出
                brand_name = parts[-1].strip()
            else:
                # Use entire tag as brand name / タグ全体をブランド名として使用
                brand_name = tag.strip()
            
            return {
                "id": None,  # Brand ID not available from tags / タグからブランドIDは利用不可
                "name": brand_name,
                "sub_name": None  # Sub-brand not available from tags / タグからサブブランドは利用不可
            }
    
    return None


def extract_category(product_type: Optional[str], tags: List[str]) -> str:
    """
    Extract product category from product_type field or tags.
    product_typeフィールドまたはタグから商品カテゴリを抽出
    
    First tries to use the product_type field from Shopify.
    If not available, searches tags for category keywords.
    Falls back to "uncategorized" if nothing found.
    まずShopifyのproduct_typeフィールドを使用しようとします。
    利用できない場合は、タグ内でカテゴリキーワードを検索します。
    何も見つからない場合は "uncategorized" にフォールバックします。
    
    Args:
        product_type: Shopify product_type field (can be None) / Shopify product_typeフィールド（Noneの可能性あり）
        tags: List of product tags / 商品タグのリスト
        
    Returns:
        Category string (lowercase) or "uncategorized" as default.
        カテゴリ文字列（小文字）またはデフォルトとして "uncategorized"
        
    Example:
        >>> category = extract_category("Tops", ["womens", "fashion"])
        >>> print(category)  # "tops"
    """
    # Prefer product_type if available (more reliable) / 利用可能な場合はproduct_typeを優先（より信頼性が高い）
    if product_type:
        return product_type.lower()
    
    # Search tags for category keywords / タグ内でカテゴリキーワードを検索
    for tag in tags:
        tag_lower = tag.lower()
        if any(cat in tag_lower for cat in CATEGORY_KEYWORDS):
            return tag_lower
    
    # Default fallback / デフォルトのフォールバック
    return DEFAULT_CATEGORY


def extract_gender(tags: List[str]) -> str:
    """
    Extract gender classification from product tags.
    商品タグから性別分類を抽出
    
    Searches tags for gender indicators in both English and Japanese.
    Returns "womens", "mens", or "unisex" (default).
    タグ内で英語と日本語の両方の性別指標を検索します。
    "womens"、"mens"、または "unisex"（デフォルト）を返します。
    
    Args:
        tags: List of product tags / 商品タグのリスト
        
    Returns:
        Gender string: "womens", "mens", or "unisex" (default).
        性別文字列: "womens"、"mens"、または "unisex"（デフォルト）
        
    Example:
        >>> gender = extract_gender(["womens", "fashion", "tops"])
        >>> print(gender)  # "womens"
    """
    if not tags:
        return DEFAULT_GENDER
    
    # Convert all tags to lowercase for case-insensitive matching / 大文字小文字を区別しないマッチングのためにすべてのタグを小文字に変換
    tags_lower = [tag.lower() for tag in tags]
    
    # Check for women's/girl's indicators / 女性/女の子の指標をチェック
    if any(keyword in tag for tag in tags_lower for keyword in GENDER_WOMENS_KEYWORDS):
        return "womens"
    
    # Check for men's/boy's indicators / 男性/男の子の指標をチェック
    if any(keyword in tag for tag in tags_lower for keyword in GENDER_MENS_KEYWORDS):
        return "mens"
    
    # Default to unisex if no gender indicators found / 性別指標が見つからない場合はデフォルトでユニセックス
    return DEFAULT_GENDER


def parse_shopify_product(
    shopify_product: Dict[str, Any], 
    base_url: str = "https://pickyou.co.jp"
) -> Dict[str, Any]:
    """
    Transform Shopify product object to custom JSON format.
    Shopify商品オブジェクトをカスタムJSON形式に変換
    
    This is the main transformation function that converts a raw Shopify
    product object into the custom format required by the pipeline.
    これは、生のShopify商品オブジェクトをパイプラインで必要な
    カスタム形式に変換するメインの変換関数です。
    
    Args:
        shopify_product: Raw Shopify product object from API / APIからの生のShopify商品オブジェクト
        base_url: Base URL for constructing product URLs (default: "https://pickyou.co.jp") / 商品URLを構築するためのベースURL（デフォルト: "https://pickyou.co.jp"）
        
    Returns:
        Transformed product dictionary in custom format with fields:
        カスタム形式の変換された商品辞書（以下のフィールドを含む）：
        - platform: "pickyou"
        - id: Product ID (string) / 商品ID（文字列）
        - name: Product title / 商品タイトル
        - price: Price as integer / 価格（整数）
        - sizes: List of size objects / サイズオブジェクトのリスト
        - brand: Brand object with id, name, sub_name / id、name、sub_nameを含むブランドオブジェクト
        - category: Category string / カテゴリ文字列
        - gender: Gender string (womens/mens/unisex) / 性別文字列（womens/mens/unisex）
        - s3_image_url: Primary image URL / プライマリ画像URL
        - platform_url: Full product URL / 完全な商品URL
        - image_count: Number of images / 画像数
        - item_images: List of all image URLs / すべての画像URLのリスト
        
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
    # Extract basic product information / 基本的な商品情報を抽出
    product_id = str(shopify_product.get("id", ""))
    handle = shopify_product.get("handle", "")  # URL-friendly product identifier / URLに適した商品識別子
    title = shopify_product.get("title", "")
    
    # Handle tags - Shopify API can return tags as string or list
    # We normalize to a list for consistent processing
    # タグを処理 - Shopify APIはタグを文字列またはリストとして返す可能性がある
    # 一貫した処理のためにリストに正規化
    tags_raw = shopify_product.get("tags", "")
    if isinstance(tags_raw, list):
        # Already a list, just clean it up / 既にリストなので、クリーンアップするだけ
        tags = [str(tag).strip() for tag in tags_raw if tag]
    elif isinstance(tags_raw, str):
        # Comma-separated string, split it / カンマ区切りの文字列なので分割
        tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]
    else:
        # Unknown format, use empty list / 不明な形式なので空のリストを使用
        tags = []
    
    # Extract other product fields / その他の商品フィールドを抽出
    product_type = shopify_product.get("product_type")
    # Product variants (sizes, colors, etc.) / 商品バリアント（サイズ、色など）
    variants = shopify_product.get("variants", [])
    images = shopify_product.get("images", [])  # Product images / 商品画像
    
    # Extract price from first variant (Shopify stores price per variant)
    # 最初のバリアントから価格を抽出（Shopifyはバリアントごとに価格を保存）
    price = 0
    if variants and len(variants) > 0:
        try:
            # Convert price string to integer (Shopify returns prices as strings)
            # 価格文字列を整数に変換（Shopifyは価格を文字列として返す）
            price = int(float(variants[0].get("price", 0)))
        except (ValueError, TypeError):
            # If price conversion fails, default to 0 / 価格変換が失敗した場合、デフォルトで0
            price = 0
    
    # Extract sizes from variants / バリアントからサイズを抽出
    # Each variant typically represents a different size / 各バリアントは通常異なるサイズを表す
    sizes = []
    for variant in variants:
        variant_title = variant.get("title", "")
        # Skip "Default Title" which Shopify uses when there's only one variant
        # バリアントが1つしかない場合にShopifyが使用する "Default Title" をスキップ
        if variant_title and variant_title != "Default Title":
            sizes.append({
                "id": variant_title,
                "row": variant_title,  # Same as id for now / 今のところidと同じ
                "size": variant_title
            })
    
    # If no sizes found, create a default "One Size" entry
    # This ensures the sizes array is never empty (required by schema)
    # サイズが見つからない場合、デフォルトの "One Size" エントリを作成
    # これにより、sizes配列が空になることがない（スキーマで必須）
    if not sizes:
        sizes.append({
            "id": DEFAULT_SIZE,
            "row": DEFAULT_SIZE,
            "size": DEFAULT_SIZE
        })
    
    # Extract brand information from tags / タグからブランド情報を抽出
    brand = extract_brand_from_tags(tags)
    if not brand:
        # Create empty brand structure if no brand found / ブランドが見つからない場合は空のブランド構造を作成
        brand = {
            "id": None,
            "name": None,
            "sub_name": None
        }
    
    # Extract category and gender using helper functions / ヘルパー関数を使用してカテゴリと性別を抽出
    category = extract_category(product_type, tags)
    gender = extract_gender(tags)
    
    # Extract image URLs / 画像URLを抽出
    image_urls = [img.get("src", "") for img in images if img.get("src")]
    s3_image_url = image_urls[0] if image_urls else ""  # Primary image (first one) / プライマリ画像（最初の1つ）
    image_count = len(image_urls)
    
    # Construct full product URL on the platform / プラットフォーム上の完全な商品URLを構築
    platform_url = f"{base_url}/products/{handle}" if handle else ""
    
    # Build and return the custom format product object / カスタム形式の商品オブジェクトを構築して返す
    return {
        "platform": "pickyou",
        "id": product_id,
        "name": title,
        "price": price,
        "sizes": sizes,
        "brand": brand,
        "category": category,
        "gender": gender,
        # Note: This is actually the original URL, not S3 / 注意: これは実際には元のURLであり、S3ではない
        "s3_image_url": s3_image_url,
        "platform_url": platform_url,
        "image_count": image_count,
        "item_images": image_urls
    }
