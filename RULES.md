# Development Rules and Guidelines / 開発ルールとガイドライン

[日本語](#japanese-rules) | [English](#english-rules)

---

<a name="japanese-rules"></a>
# 日本語ルール

## コードスタイル

- PEP 8 Pythonスタイルガイドに従う
- 関数パラメータと戻り値に型ヒントを使用
- 最大行の長さ: 100文字
- 説明的な変数名と関数名を使用
- すべての関数とクラスにdocstringを追加
- 役立つ場合はdocstringに例を含める

## コミットメッセージ

gitmoji規則に従う:

- ✨ `:sparkles:` - 新機能の追加
- 🐛 `:bug:` - バグ修正
- ♻️ `:recycle:` - リファクタリング
- 📝 `:memo:` - ドキュメント更新
- 🔧 `:wrench:` - 設定ファイルとスクリプトの更新
- ✅ `:white_check_mark:` - テストコードの更新
- 🚚 `:truck:` - ファイルとディレクトリの名前変更
- 🚨 `:rotating_light:` - 見た目のみの修正

**フォーマット:**
```
[絵文字] 簡単な説明

- 詳細な説明ポイント1
- 詳細な説明ポイント2
```

## エラーハンドリング

- 常に例外を適切に処理する
- ネットワークリクエストとファイル操作にtry-exceptブロックを使用
- 説明的なメッセージでエラーをログに記録
- スクレイパーを静かにクラッシュさせない - 常にエラーメッセージをログに記録
- 適切な場合は例外を発生させる代わりに`None`または空のリスト/文字列を返す
- 監視のために統計でエラーを追跡

## レート制限

- リクエスト間のデフォルト遅延: 1.0秒
- Shopify APIレート制限を尊重
- リトライに指数バックオフを実装
- 最大リトライ: 3回の試行
- HTTP 429（リクエストが多すぎる）応答を適切に処理
- API応答時間に基づいて遅延を調整

## データフォーマット検証

- すべての商品には必須フィールドが必要: `platform`, `id`, `name`, `price`
- 価格は整数でなければならない（必要に応じてfloatから変換）
- サイズ配列には少なくとも1つのアイテムが含まれている必要がある
- ブランドオブジェクトには構造が必要: `{id, name, sub_name}`（null可）
- 画像URLは有効な文字列でなければならない（空でも可）
- プラットフォームURLは商品ハンドルから正しく構築する必要がある
- ファイルに保存する前にすべてのデータを検証

## テスト要件

- すべてのコア関数のユニットテストを作成
- モック応答でページネーションロジックをテスト
- サンプルShopifyデータでパーサー変換をテスト
- エラーハンドリングシナリオをテスト
- ファイルI/O操作をテスト
- テストフレームワークにpytestを使用
- >80%のコードカバレッジを目指す
- 成功と失敗の両方のケースをテスト

## ファイル組織

- ソースコードを`src/`ディレクトリに保持
- テストを`tests/`ディレクトリに保持
- 出力データを`data/`ディレクトリに保持
- `__init__.py`ファイルを使用してディレクトリをPythonパッケージにする
- 関連する機能をモジュールにグループ化

## ドキュメント

- 目的を説明するモジュールレベルのdocstringを追加
- Args、Returns、Examplesを含む関数/クラスのdocstringを追加
- 複雑なロジックにインラインコメントを追加
- 定数とその目的を文書化
- README.mdを最新の状態に保つ
- 重要な変更についてCHANGELOG.mdを更新

## 出力フォーマット

- 最終JSONには構造が必要: `{"items": [...]}`
- 各アイテムはカスタムフォーマット仕様に一致する必要がある
- JSONは2スペースのインデントで整形印刷される必要がある
- すべてのファイル操作にUTF-8エンコーディングを使用
- `scrape_with_metadata()`を使用する場合はメタデータを含める

## 依存関係

- 依存関係を最小限に保ち、適切に維持する
- requirements.txtでメジャーバージョン番号を固定
- 各依存関係が必要な理由を文書化
- 不要な外部ライブラリを避ける
- セキュリティのために依存関係を定期的に更新

## コードコメント

- すべてのコードコメントに英語を使用
- 「何を」だけでなく「なぜ」を説明
- 複雑なアルゴリズムとビジネスロジックにコメント
- コード変更に合わせてコメントを最新の状態に保つ
- コミット前にコメントアウトされたコードを削除

## 定数

- モジュールレベルで定数を定義
- 定数名にUPPER_CASEを使用
- 関連する定数をグループ化
- コメントで定数を文書化
- コード内のマジックナンバーを避ける

---

<a name="english-rules"></a>
# English Rules

## Code Style

- Follow PEP 8 Python style guide
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use descriptive variable and function names
- Add docstrings to all functions and classes
- Include examples in docstrings where helpful

## Commit Messages

Follow gitmoji conventions:

- ✨ `:sparkles:` - Added new features
- 🐛 `:bug:` - Bugfix
- ♻️ `:recycle:` - Refactoring
- 📝 `:memo:` - Document update
- 🔧 `:wrench:` - Update configuration files and scripts
- ✅ `:white_check_mark:` - Test code updated
- 🚚 `:truck:` - Renaming files and directories
- 🚨 `:rotating_light:` - Appearance-only correction

**Format:**
```
[emoji] Brief description

- Detailed explanation point 1
- Detailed explanation point 2
```

## Error Handling

- Always handle exceptions gracefully
- Use try-except blocks for network requests and file operations
- Log errors with descriptive messages
- Never let the scraper crash silently - always log error messages
- Return `None` or empty lists/strings instead of raising exceptions where appropriate
- Track errors in statistics for monitoring

## Rate Limiting

- Default delay between requests: 1.0 second
- Respect Shopify API rate limits
- Implement exponential backoff for retries
- Maximum retries: 3 attempts
- Handle HTTP 429 (Too Many Requests) responses appropriately
- Adjust delay based on API response times

## Data Format Validation

- All products must have required fields: `platform`, `id`, `name`, `price`
- Price must be an integer (convert from float if needed)
- Sizes array must contain at least one item
- Brand object must have structure: `{id, name, sub_name}` (can be null)
- Image URLs must be valid strings (can be empty)
- Platform URL must be constructed correctly from product handle
- Validate all data before saving to file

## Testing Requirements

- Write unit tests for all core functions
- Test pagination logic with mock responses
- Test parser transformation with sample Shopify data
- Test error handling scenarios
- Test file I/O operations
- Use pytest for testing framework
- Aim for >80% code coverage
- Test both success and failure cases

## File Organization

- Keep source code in `src/` directory
- Keep tests in `tests/` directory
- Keep output data in `data/` directory
- Use `__init__.py` files to make directories Python packages
- Group related functionality in modules

## Documentation

- Add module-level docstrings explaining purpose
- Add function/class docstrings with Args, Returns, Examples
- Add inline comments for complex logic
- Document constants and their purposes
- Keep README.md up to date
- Update CHANGELOG.md for significant changes

## Output Format

- Final JSON must have structure: `{"items": [...]}`
- Each item must match the custom format specification
- JSON should be pretty-printed with 2-space indentation
- Use UTF-8 encoding for all file operations
- Include metadata when using `scrape_with_metadata()`

## Dependencies

- Keep dependencies minimal and well-maintained
- Pin major version numbers in requirements.txt
- Document why each dependency is needed
- Avoid unnecessary external libraries
- Update dependencies regularly for security

## Code Comments

- Use English for all code comments
- Explain "why" not just "what"
- Comment complex algorithms and business logic
- Keep comments up to date with code changes
- Remove commented-out code before committing

## Constants

- Define constants at module level
- Use UPPER_CASE for constant names
- Group related constants together
- Document constants with comments
- Avoid magic numbers in code
