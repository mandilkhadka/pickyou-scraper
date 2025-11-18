# Code Guide / コードガイド

[English](#english-guide) | [日本語](#japanese-guide)

---

<a name="english-guide"></a>
# English Guide

## Understanding the Codebase

This guide helps developers understand the codebase structure, design patterns, and how to work with the code.

## Architecture Overview

The scraper follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐
│   CLI Layer     │  ← User interface (cli.py)
└────────┬────────┘
         │
┌────────▼────────┐
│ Pipeline Layer  │  ← Integration API (pipeline.py)
└────────┬────────┘
         │
┌────────▼────────┐
│  Scraper Layer  │  ← Core logic (scraper.py)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Parser │ │Utils  │  ← Data transformation & utilities
└───────┘ └───────┘
```

## Module Responsibilities

### 1. `scraper.py` - Core Scraping Logic
**Purpose**: Main orchestration of the scraping process

**Key Components**:
- `Scraper` class: Manages the entire scraping workflow
- `fetch_page()`: Retrieves a single page from API
- `fetch_all_products()`: Handles pagination automatically
- `scrape_and_save()`: Complete workflow from fetch to save

**Design Patterns**:
- Single Responsibility: Each method has one clear purpose
- Error Recovery: Continues processing even if individual products fail
- Statistics Tracking: Monitors success/failure rates

**Key Constants**:
- `SHOPIFY_MAX_LIMIT = 250`: Maximum products per page
- `PROGRESS_LOG_INTERVAL = 1000`: Log progress every N products

### 2. `parser.py` - Data Transformation
**Purpose**: Converts Shopify API format to custom JSON format

**Key Functions**:
- `parse_shopify_product()`: Main transformation function
- `extract_brand_from_tags()`: Extracts brand from tags
- `extract_category()`: Determines product category
- `extract_gender()`: Classifies gender (womens/mens/unisex)

**Design Patterns**:
- Data Normalization: Handles inconsistent API responses (tags as string/list)
- Fallback Values: Provides defaults when data is missing
- Multi-language Support: Handles both English and Japanese keywords

**Key Constants**:
- `BRAND_KEYWORDS`: Keywords to identify brand tags
- `CATEGORY_KEYWORDS`: Keywords to identify categories
- `GENDER_WOMENS_KEYWORDS`: Keywords for women's products
- `GENDER_MENS_KEYWORDS`: Keywords for men's products

### 3. `utils.py` - Utility Functions
**Purpose**: Reusable HTTP and file operations

**Key Functions**:
- `make_request()`: HTTP GET with retry logic
- `save_json()`: Save data to JSON file
- `ensure_data_dir()`: Create directories if needed

**Design Patterns**:
- Retry Pattern: Automatic retries for transient failures
- Error Handling: Graceful degradation on failures
- Logging Integration: Optional logger parameter

**Key Constants**:
- `DEFAULT_TIMEOUT = 30`: HTTP request timeout
- `DEFAULT_MAX_RETRIES = 3`: Number of retry attempts
- `RETRY_STATUS_CODES`: HTTP codes that trigger retry

### 4. `validator.py` - Data Validation
**Purpose**: Ensures data quality before saving

**Key Function**:
- `validate_product()`: Comprehensive product validation

**Validation Steps**:
1. Check all required fields exist
2. Validate field types
3. Validate field values (e.g., gender must be valid)
4. Validate nested structures (sizes, brand)

**Key Constants**:
- `REQUIRED_FIELDS`: List of required product fields
- `VALID_GENDERS`: Allowed gender values
- `REQUIRED_SIZE_FIELDS`: Required fields in size objects

### 5. `pipeline.py` - Integration API
**Purpose**: Clean API for pipeline integration

**Key Components**:
- `PipelineScraper` class: Wrapper for easy integration
- `scrape_products()`: Convenience function for simple use cases

**Design Patterns**:
- Facade Pattern: Simplifies complex scraper interface
- Callback Pattern: Supports progress tracking
- Metadata Pattern: Embeds scraping metadata in output

### 6. `config.py` - Configuration Management
**Purpose**: Centralized configuration handling

**Key Features**:
- Default values
- File-based configuration
- Runtime overrides
- Dictionary-like interface

**Design Patterns**:
- Configuration Pattern: Centralized settings management
- Priority System: File > Defaults, kwargs > File

### 7. `logger.py` - Logging Setup
**Purpose**: Centralized logging configuration

**Key Features**:
- Console and file logging
- Configurable log levels
- UTF-8 encoding support
- Formatted output with timestamps

### 8. `cli.py` - Command Line Interface
**Purpose**: User-friendly terminal interface

**Key Features**:
- Argument parsing
- Config file support
- Verbose/quiet modes
- Help documentation

## Code Flow

### Typical Scraping Flow

```
1. User runs: python -m src.cli
   ↓
2. CLI parses arguments and creates Scraper instance
   ↓
3. Scraper.scrape_and_save() is called
   ↓
4. fetch_all_products() paginates through API
   ↓
5. For each product: parse_shopify_product() transforms data
   ↓
6. validate_product() ensures data quality
   ↓
7. save_json() writes to file
   ↓
8. Statistics are logged
```

### Error Handling Flow

```
API Request Fails
  ↓
make_request() catches exception
  ↓
Logs error and returns None
  ↓
fetch_page() receives None
  ↓
Returns empty list
  ↓
fetch_all_products() detects empty list
  ↓
Stops pagination gracefully
```

## Best Practices

### 1. Adding New Features

1. **Add constants at module level**
   ```python
   # At top of file
   NEW_FEATURE_DEFAULT = "value"
   ```

2. **Document with docstrings**
   ```python
   def new_function(param: str) -> bool:
       """
       Brief description.
       
       Args:
           param: Description
           
       Returns:
           Description
       """
   ```

3. **Add inline comments for complex logic**
   ```python
   # Complex calculation explained here
   result = complex_calculation()
   ```

### 2. Error Handling

Always use try-except blocks:
```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Error message: {e}")
    return None  # or appropriate default
```

### 3. Type Hints

Always include type hints:
```python
def function(param: str, count: int) -> Dict[str, Any]:
    ...
```

### 4. Logging

Use appropriate log levels:
- `logger.debug()`: Detailed debugging info
- `logger.info()`: General information
- `logger.warning()`: Warnings (non-critical)
- `logger.error()`: Errors that need attention

## Testing

### Running Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_scraper.py

# With coverage
pytest tests/ --cov=src
```

### Writing Tests

Follow this pattern:
```python
def test_function_name():
    """Test description."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

## Common Tasks

### Adding a New Field to Output

1. Update `parser.py`:
   ```python
   return {
       ...
       "new_field": extract_new_field(product),
   }
   ```

2. Update `validator.py`:
   ```python
   REQUIRED_FIELDS.append("new_field")
   # Add validation logic
   ```

3. Update tests in `tests/test_scraper.py`

### Changing API Endpoint

Update in `scraper.py`:
```python
self.api_endpoint = f"{base_url}/new-endpoint.json"
```

### Adding New Configuration Option

1. Add to `config.py` DEFAULT_CONFIG
2. Add CLI argument in `cli.py`
3. Use in `scraper.py` via config object

---

<a name="japanese-guide"></a>
# 日本語ガイド

## コードベースの理解

このガイドは、開発者がコードベースの構造、デザインパターン、コードの操作方法を理解するのに役立ちます。

## アーキテクチャ概要

スクレイパーは、明確な関心の分離を持つモジュールアーキテクチャに従います:

```
┌─────────────────┐
│   CLI層          │  ← ユーザーインターフェース (cli.py)
└────────┬────────┘
         │
┌────────▼────────┐
│ パイプライン層   │  ← 統合API (pipeline.py)
└────────┬────────┘
         │
┌────────▼────────┐
│ スクレイパー層   │  ← コアロジック (scraper.py)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│パーサー│ │ユーティリティ│  ← データ変換とユーティリティ
└───────┘ └───────┘
```

## モジュールの責任

### 1. `scraper.py` - コアスクレイピングロジック
**目的**: スクレイピングプロセスの主要なオーケストレーション

**主要コンポーネント**:
- `Scraper`クラス: スクレイピングワークフロー全体を管理
- `fetch_page()`: APIから1ページを取得
- `fetch_all_products()`: ページネーションを自動処理
- `scrape_and_save()`: 取得から保存までの完全なワークフロー

**デザインパターン**:
- 単一責任: 各メソッドに明確な目的がある
- エラー回復: 個別の商品が失敗しても処理を継続
- 統計追跡: 成功率/失敗率を監視

**主要な定数**:
- `SHOPIFY_MAX_LIMIT = 250`: ページあたりの最大商品数
- `PROGRESS_LOG_INTERVAL = 1000`: N商品ごとに進捗をログ

### 2. `parser.py` - データ変換
**目的**: Shopify APIフォーマットをカスタムJSONフォーマットに変換

**主要な関数**:
- `parse_shopify_product()`: メイン変換関数
- `extract_brand_from_tags()`: タグからブランドを抽出
- `extract_category()`: 商品カテゴリを決定
- `extract_gender()`: 性別を分類（womens/mens/unisex）

**デザインパターン**:
- データ正規化: 一貫性のないAPI応答を処理（タグを文字列/リストとして）
- フォールバック値: データが欠落している場合のデフォルトを提供
- 多言語サポート: 英語と日本語のキーワードを処理

**主要な定数**:
- `BRAND_KEYWORDS`: ブランドタグを識別するキーワード
- `CATEGORY_KEYWORDS`: カテゴリを識別するキーワード
- `GENDER_WOMENS_KEYWORDS`: 女性向け商品のキーワード
- `GENDER_MENS_KEYWORDS`: 男性向け商品のキーワード

### 3. `utils.py` - ユーティリティ関数
**目的**: 再利用可能なHTTPとファイル操作

**主要な関数**:
- `make_request()`: リトライロジック付きHTTP GET
- `save_json()`: データをJSONファイルに保存
- `ensure_data_dir()`: 必要に応じてディレクトリを作成

**デザインパターン**:
- リトライパターン: 一時的な失敗の自動リトライ
- エラーハンドリング: 失敗時の適切な処理
- ロギング統合: オプションのロガーパラメータ

**主要な定数**:
- `DEFAULT_TIMEOUT = 30`: HTTPリクエストタイムアウト
- `DEFAULT_MAX_RETRIES = 3`: リトライ試行回数
- `RETRY_STATUS_CODES`: リトライをトリガーするHTTPコード

### 4. `validator.py` - データ検証
**目的**: 保存前のデータ品質を確保

**主要な関数**:
- `validate_product()`: 包括的な商品検証

**検証ステップ**:
1. すべての必須フィールドが存在することを確認
2. フィールドタイプを検証
3. フィールド値を検証（例: 性別が有効である必要がある）
4. ネストされた構造を検証（サイズ、ブランド）

**主要な定数**:
- `REQUIRED_FIELDS`: 必須商品フィールドのリスト
- `VALID_GENDERS`: 許可された性別値
- `REQUIRED_SIZE_FIELDS`: サイズオブジェクトの必須フィールド

### 5. `pipeline.py` - 統合API
**目的**: パイプライン統合のためのクリーンなAPI

**主要コンポーネント**:
- `PipelineScraper`クラス: 簡単な統合のためのラッパー
- `scrape_products()`: 簡単な使用例のための便利関数

**デザインパターン**:
- ファサードパターン: 複雑なスクレイパーインターフェースを簡素化
- コールバックパターン: 進捗追跡をサポート
- メタデータパターン: 出力にスクレイピングメタデータを埋め込み

### 6. `config.py` - 設定管理
**目的**: 集中化された設定処理

**主要機能**:
- デフォルト値
- ファイルベースの設定
- ランタイムオーバーライド
- 辞書のようなインターフェース

**デザインパターン**:
- 設定パターン: 集中化された設定管理
- 優先順位システム: ファイル > デフォルト、kwargs > ファイル

### 7. `logger.py` - ロギング設定
**目的**: 集中化されたロギング設定

**主要機能**:
- コンソールとファイルロギング
- 設定可能なログレベル
- UTF-8エンコーディングサポート
- タイムスタンプ付きフォーマット出力

### 8. `cli.py` - コマンドラインインターフェース
**目的**: ユーザーフレンドリーなターミナルインターフェース

**主要機能**:
- 引数解析
- 設定ファイルサポート
- 詳細/静かなモード
- ヘルプドキュメント

## コードフロー

### 典型的なスクレイピングフロー

```
1. ユーザーが実行: python -m src.cli
   ↓
2. CLIが引数を解析し、Scraperインスタンスを作成
   ↓
3. Scraper.scrape_and_save()が呼び出される
   ↓
4. fetch_all_products()がAPIをページネーション
   ↓
5. 各商品について: parse_shopify_product()がデータを変換
   ↓
6. validate_product()がデータ品質を確保
   ↓
7. save_json()がファイルに書き込み
   ↓
8. 統計がログに記録される
```

### エラーハンドリングフロー

```
APIリクエストが失敗
  ↓
make_request()が例外をキャッチ
  ↓
エラーをログに記録し、Noneを返す
  ↓
fetch_page()がNoneを受信
  ↓
空のリストを返す
  ↓
fetch_all_products()が空のリストを検出
  ↓
ページネーションを適切に停止
```

## ベストプラクティス

### 1. 新機能の追加

1. **モジュールレベルで定数を追加**
   ```python
   # ファイルの先頭
   NEW_FEATURE_DEFAULT = "value"
   ```

2. **docstringでドキュメント化**
   ```python
   def new_function(param: str) -> bool:
       """
       簡単な説明。
       
       Args:
           param: 説明
           
       Returns:
           説明
       """
   ```

3. **複雑なロジックにインラインコメントを追加**
   ```python
   # ここで複雑な計算を説明
   result = complex_calculation()
   ```

### 2. エラーハンドリング

常にtry-exceptブロックを使用:
```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"エラーメッセージ: {e}")
    return None  # または適切なデフォルト
```

### 3. 型ヒント

常に型ヒントを含める:
```python
def function(param: str, count: int) -> Dict[str, Any]:
    ...
```

### 4. ロギング

適切なログレベルを使用:
- `logger.debug()`: 詳細なデバッグ情報
- `logger.info()`: 一般的な情報
- `logger.warning()`: 警告（非致命的）
- `logger.error()`: 注意が必要なエラー

## テスト

### テストの実行

```bash
# すべてのテスト
pytest tests/

# 特定のテストファイル
pytest tests/test_scraper.py

# カバレッジ付き
pytest tests/ --cov=src
```

### テストの作成

このパターンに従う:
```python
def test_function_name():
    """テストの説明。"""
    # Arrange（準備）
    input_data = create_test_data()
    
    # Act（実行）
    result = function_under_test(input_data)
    
    # Assert（検証）
    assert result == expected_output
```

## 一般的なタスク

### 出力に新しいフィールドを追加

1. `parser.py`を更新:
   ```python
   return {
       ...
       "new_field": extract_new_field(product),
   }
   ```

2. `validator.py`を更新:
   ```python
   REQUIRED_FIELDS.append("new_field")
   # 検証ロジックを追加
   ```

3. `tests/test_scraper.py`のテストを更新

### APIエンドポイントの変更

`scraper.py`で更新:
```python
self.api_endpoint = f"{base_url}/new-endpoint.json"
```

### 新しい設定オプションの追加

1. `config.py`のDEFAULT_CONFIGに追加
2. `cli.py`にCLI引数を追加
3. `scraper.py`でconfigオブジェクト経由で使用

