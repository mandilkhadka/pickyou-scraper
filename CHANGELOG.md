# Changelog / 変更履歴

[日本語](#japanese-changelog) | [English](#english-changelog)

---

<a name="japanese-changelog"></a>
# 日本語変更履歴

## [1.1.0] - パイプライン統合アップデート

### 追加

#### 🚀 パイプライン統合モジュール (`src/pipeline.py`)
- **`PipelineScraper`クラス**: プログラム使用のためのクリーンなAPI
- **`scrape_products()`関数**: クイック統合関数
- **メタデータサポート**: 出力への自動メタデータ含める
- **進捗コールバック**: スクレイピング進捗を追跡
- **バッチコールバック**: 商品をバッチで処理

#### 🎯 CLIインターフェース (`src/cli.py`)
- argparseによる完全なコマンドラインインターフェース
- CLI経由ですべての設定オプションをサポート
- 詳細/静かなモード
- 設定ファイルサポート
- ヘルプドキュメント

#### ⚙️ 設定管理 (`src/config.py`)
- JSONベースの設定ファイル
- 適切なデフォルト値を持つデフォルト設定
- 簡単なオーバーライドメカニズム
- 設定ファイルの読み込みと保存

#### 📚 ドキュメント
- **PIPELINE_INTEGRATION.md**: 完全な統合ガイド
- **examples/pipeline_integration.py**: 動作例
- **config.example.json**: 設定ファイルの例
- 新機能でREADMEを更新

#### 📊 機能強化
- 出力ファイルでのメタデータ追跡
- API経由でアクセス可能な最終統計
- より良いエラー報告構造
- 監視用のステータスエンドポイント

### 改善

- 関心の分離の改善
- よりモジュール化されたアーキテクチャ
- エラーハンドリングの強化
- 全体を通じたプロフェッショナルなロギング
- より良いドキュメント

### 使用例

**簡単な統合:**
```python
from src.pipeline import scrape_products
result = scrape_products()
```

**高度な統合:**
```python
from src.pipeline import PipelineScraper
pipeline = PipelineScraper()
result = pipeline.scrape_with_metadata()
```

**CLI使用:**
```bash
python -m src.cli --output data/products.json --verbose
```

## [1.0.0] - 初回リリース

### 機能
- Shopify APIスクレイピング
- 自動ページネーション
- データ変換
- エラーハンドリングとリトライロジック
- ロギングシステム
- データ検証
- ユニットテスト

---

<a name="english-changelog"></a>
# English Changelog

## [1.1.0] - Pipeline Integration Update

### Added

#### 🚀 Pipeline Integration Module (`src/pipeline.py`)
- **`PipelineScraper` class**: Clean API for programmatic use
- **`scrape_products()` function**: Quick integration function
- **Metadata support**: Automatic metadata inclusion in output
- **Progress callbacks**: Track scraping progress
- **Batch callbacks**: Process products in batches

#### 🎯 CLI Interface (`src/cli.py`)
- Full command-line interface with argparse
- Support for all configuration options via CLI
- Verbose/quiet modes
- Config file support
- Help documentation

#### ⚙️ Configuration Management (`src/config.py`)
- JSON-based configuration files
- Default configuration with sensible defaults
- Easy override mechanism
- Config file loading and saving

#### 📚 Documentation
- **PIPELINE_INTEGRATION.md**: Complete integration guide
- **examples/pipeline_integration.py**: Working examples
- **config.example.json**: Example configuration file
- Updated README with new features

#### 📊 Enhanced Features
- Metadata tracking in output files
- Final statistics accessible via API
- Better error reporting structure
- Status endpoint for monitoring

### Improved

- Better separation of concerns
- More modular architecture
- Enhanced error handling
- Professional logging throughout
- Better documentation

### Usage Examples

**Simple Integration:**
```python
from src.pipeline import scrape_products
result = scrape_products()
```

**Advanced Integration:**
```python
from src.pipeline import PipelineScraper
pipeline = PipelineScraper()
result = pipeline.scrape_with_metadata()
```

**CLI Usage:**
```bash
python -m src.cli --output data/products.json --verbose
```

## [1.0.0] - Initial Release

### Features
- Shopify API scraping
- Automatic pagination
- Data transformation
- Error handling and retry logic
- Logging system
- Data validation
- Unit tests

