# PickYou Scraper / PickYou スクレイパー

[English](#english) | [日本語](#japanese)

---

<a name="english"></a>
# English

## Overview

A production-ready Python scraper for fetching all products from pickyou.co.jp using the Shopify API. This scraper is designed for easy integration into extraction pipelines with comprehensive error handling, logging, and data validation.

## Features

- ✅ Fetches all products from pickyou.co.jp via Shopify API
- ✅ Automatic pagination (handles all pages automatically)
- ✅ Transforms Shopify product format to custom JSON format
- ✅ Rate limiting and error handling
- ✅ Retry logic for failed requests
- ✅ Comprehensive unit tests
- ✅ **Pipeline-ready API** for easy integration
- ✅ **CLI interface** with flexible options
- ✅ **Configuration file support** (JSON)
- ✅ **Metadata tracking** in output
- ✅ **Progress callbacks** for monitoring
- ✅ **Professional logging** system
- ✅ **Data validation** before saving

## Quick Start

**Just want to run it?** See [QUICK_START.md](QUICK_START.md) for simple step-by-step instructions!

```bash
cd /Users/m/code/mandilkhadka/pickyou-scraper
source venv/bin/activate
python -m src.cli
```

## Project Structure

```
pickyou-scraper/
├── src/
│   ├── scraper.py      # Main scraper with pagination logic
│   ├── parser.py       # Transform Shopify format to custom format
│   ├── utils.py        # HTTP requests and file I/O helpers
│   ├── pipeline.py     # Pipeline integration module
│   ├── cli.py          # Command-line interface
│   ├── config.py       # Configuration management
│   ├── logger.py       # Logging setup
│   ├── validator.py    # Data validation
│   └── __init__.py
├── tests/
│   ├── test_scraper.py # Unit tests
│   └── __init__.py
├── examples/
│   └── pipeline_integration.py  # Integration examples
├── data/
│   └── pickyou_products.json    # Output file (generated)
├── requirements.txt
├── config.example.json
├── RULES.md
├── QUICK_START.md
├── PIPELINE_INTEGRATION.md
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mandilkhadka/pickyou-scraper.git
cd pickyou-scraper
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface (Recommended)

**Basic usage:**
```bash
python -m src.cli
```

**With options:**
```bash
python -m src.cli --output data/products.json --delay 2.0 --verbose
```

**With config file:**
```bash
python -m src.cli --config config.json
```

**See all options:**
```bash
python -m src.cli --help
```

### Python API (For Pipeline Integration)

**Simple integration:**
```python
from src.pipeline import scrape_products

result = scrape_products(output_file="data/products.json")
```

**Advanced integration:**
```python
from src.pipeline import PipelineScraper
from src.config import Config

config = Config()
pipeline = PipelineScraper(config=config)
result = pipeline.scrape_with_metadata()
```

See [PIPELINE_INTEGRATION.md](PIPELINE_INTEGRATION.md) for complete integration guide.

## Output Format

The scraper outputs JSON in the following format:

```json
{
  "items": [
    {
      "platform": "pickyou",
      "id": "123456789",
      "name": "Product Name",
      "price": 2999,
      "sizes": [
        {
          "id": "S",
          "row": "S",
          "size": "S"
        }
      ],
      "brand": {
        "id": null,
        "name": "Brand Name",
        "sub_name": null
      },
      "category": "tops",
      "gender": "womens",
      "s3_image_url": "https://...",
      "platform_url": "https://pickyou.co.jp/products/product-handle",
      "image_count": 3,
      "item_images": [
        "https://...",
        "https://..."
      ]
    }
  ]
}
```

## Code Documentation

### Module Overview

- **`scraper.py`**: Core scraping logic with pagination and error handling
- **`parser.py`**: Transforms Shopify API format to custom JSON format
- **`utils.py`**: HTTP request utilities with retry logic
- **`pipeline.py`**: Pipeline integration API for programmatic use
- **`cli.py`**: Command-line interface
- **`config.py`**: Configuration management system
- **`logger.py`**: Logging setup and configuration
- **`validator.py`**: Data validation before saving

### Key Functions

#### Scraper Class
- `fetch_page(page)`: Fetches a single page of products
- `fetch_all_products()`: Automatically paginates through all pages
- `scrape_and_save(output_file)`: Complete scraping workflow

#### Parser Functions
- `parse_shopify_product(product, base_url)`: Transforms Shopify product to custom format
- `extract_brand_from_tags(tags)`: Extracts brand from product tags
- `extract_category(product_type, tags)`: Extracts category
- `extract_gender(tags)`: Extracts gender classification

#### Utility Functions
- `make_request(url, ...)`: HTTP GET with retry logic
- `save_json(data, filepath, ...)`: Save data to JSON file
- `ensure_data_dir(dir)`: Create directory if needed

## Testing

Run tests with pytest:

```bash
pytest tests/
```

Run with verbose output:

```bash
pytest tests/ -v
```

## Configuration

Create a `config.json` file:

```json
{
  "base_url": "https://pickyou.co.jp",
  "limit": 250,
  "delay": 1.0,
  "output_file": "data/pickyou_products.json",
  "max_retries": 3,
  "timeout": 30,
  "log_level": "INFO"
}
```

## Error Handling

The scraper includes comprehensive error handling:
- Automatic retries for transient failures
- Graceful handling of individual product errors
- Detailed error logging
- Statistics tracking for failed products

## Contributing

Please follow the guidelines in [RULES.md](RULES.md) when contributing to this project.

## License

[Add your license here]

---

<a name="japanese"></a>
# 日本語

## 概要

Shopify APIを使用してpickyou.co.jpから全商品を取得する本番環境対応のPythonスクレイパーです。このスクレイパーは、包括的なエラーハンドリング、ロギング、データ検証を備えた抽出パイプラインへの簡単な統合を目的として設計されています。

## 機能

- ✅ Shopify API経由でpickyou.co.jpから全商品を取得
- ✅ 自動ページネーション（全ページを自動処理）
- ✅ Shopify商品フォーマットをカスタムJSONフォーマットに変換
- ✅ レート制限とエラーハンドリング
- ✅ 失敗したリクエストのリトライロジック
- ✅ 包括的なユニットテスト
- ✅ **パイプライン対応API** - 簡単な統合
- ✅ **CLIインターフェース** - 柔軟なオプション
- ✅ **設定ファイルサポート** (JSON)
- ✅ **メタデータ追跡** - 出力に含まれる
- ✅ **進捗コールバック** - 監視用
- ✅ **プロフェッショナルなロギングシステム**
- ✅ **データ検証** - 保存前に実行

## クイックスタート

**すぐに実行したい場合** [QUICK_START.md](QUICK_START.md) を参照してください！

```bash
cd /Users/m/code/mandilkhadka/pickyou-scraper
source venv/bin/activate
python -m src.cli
```

## プロジェクト構造

```
pickyou-scraper/
├── src/
│   ├── scraper.py      # ページネーションロジック付きメインスクレイパー
│   ├── parser.py       # Shopifyフォーマットをカスタムフォーマットに変換
│   ├── utils.py        # HTTPリクエストとファイルI/Oヘルパー
│   ├── pipeline.py     # パイプライン統合モジュール
│   ├── cli.py          # コマンドラインインターフェース
│   ├── config.py       # 設定管理
│   ├── logger.py       # ロギング設定
│   ├── validator.py    # データ検証
│   └── __init__.py
├── tests/
│   ├── test_scraper.py # ユニットテスト
│   └── __init__.py
├── examples/
│   └── pipeline_integration.py  # 統合例
├── data/
│   └── pickyou_products.json    # 出力ファイル（生成される）
├── requirements.txt
├── config.example.json
├── RULES.md
├── QUICK_START.md
├── PIPELINE_INTEGRATION.md
└── README.md
```

## インストール

1. リポジトリをクローン:
```bash
git clone https://github.com/mandilkhadka/pickyou-scraper.git
cd pickyou-scraper
```

2. 仮想環境を作成（推奨）:
```bash
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

3. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

## 使用方法

### コマンドラインインターフェース（推奨）

**基本的な使用:**
```bash
python -m src.cli
```

**オプション付き:**
```bash
python -m src.cli --output data/products.json --delay 2.0 --verbose
```

**設定ファイルを使用:**
```bash
python -m src.cli --config config.json
```

**すべてのオプションを表示:**
```bash
python -m src.cli --help
```

### Python API（パイプライン統合用）

**簡単な統合:**
```python
from src.pipeline import scrape_products

result = scrape_products(output_file="data/products.json")
```

**高度な統合:**
```python
from src.pipeline import PipelineScraper
from src.config import Config

config = Config()
pipeline = PipelineScraper(config=config)
result = pipeline.scrape_with_metadata()
```

完全な統合ガイドは [PIPELINE_INTEGRATION.md](PIPELINE_INTEGRATION.md) を参照してください。

## 出力フォーマット

スクレイパーは以下の形式でJSONを出力します:

```json
{
  "items": [
    {
      "platform": "pickyou",
      "id": "123456789",
      "name": "商品名",
      "price": 2999,
      "sizes": [
        {
          "id": "S",
          "row": "S",
          "size": "S"
        }
      ],
      "brand": {
        "id": null,
        "name": "ブランド名",
        "sub_name": null
      },
      "category": "tops",
      "gender": "womens",
      "s3_image_url": "https://...",
      "platform_url": "https://pickyou.co.jp/products/product-handle",
      "image_count": 3,
      "item_images": [
        "https://...",
        "https://..."
      ]
    }
  ]
}
```

## コードドキュメント

### モジュール概要

- **`scraper.py`**: ページネーションとエラーハンドリングを含むコアスクレイピングロジック
- **`parser.py`**: Shopify APIフォーマットをカスタムJSONフォーマットに変換
- **`utils.py`**: リトライロジック付きHTTPリクエストユーティリティ
- **` pipeline.py`**: プログラム使用のためのパイプライン統合API
- **`cli.py`**: コマンドラインインターフェース
- **`config.py`**: 設定管理システム
- **`logger.py`**: ロギング設定と構成
- **`validator.py`**: 保存前のデータ検証

### 主要な関数

#### Scraperクラス
- `fetch_page(page)`: 1ページの商品を取得
- `fetch_all_products()`: 全ページを自動的にページネーション
- `scrape_and_save(output_file)`: 完全なスクレイピングワークフロー

#### パーサー関数
- `parse_shopify_product(product, base_url)`: Shopify商品をカスタムフォーマットに変換
- `extract_brand_from_tags(tags)`: 商品タグからブランドを抽出
- `extract_category(product_type, tags)`: カテゴリを抽出
- `extract_gender(tags)`: 性別分類を抽出

#### ユーティリティ関数
- `make_request(url, ...)`: リトライロジック付きHTTP GET
- `save_json(data, filepath, ...)`: データをJSONファイルに保存
- `ensure_data_dir(dir)`: 必要に応じてディレクトリを作成

## テスト

pytestでテストを実行:

```bash
pytest tests/
```

詳細な出力で実行:

```bash
pytest tests/ -v
```

## 設定

`config.json`ファイルを作成:

```json
{
  "base_url": "https://pickyou.co.jp",
  "limit": 250,
  "delay": 1.0,
  "output_file": "data/pickyou_products.json",
  "max_retries": 3,
  "timeout": 30,
  "log_level": "INFO"
}
```

## エラーハンドリング

スクレイパーには包括的なエラーハンドリングが含まれています:
- 一時的な失敗の自動リトライ
- 個別の商品エラーの適切な処理
- 詳細なエラーロギング
- 失敗した商品の統計追跡

## コントリビューション

このプロジェクトに貢献する際は、[RULES.md](RULES.md)のガイドラインに従ってください。

## ライセンス

[ライセンスをここに追加]
