# Quick Start Guide / クイックスタートガイド

[English](#english-quick) | [日本語](#japanese-quick)

---

<a name="english-quick"></a>
# English Quick Start

## 🚀 Simple 3-Step Guide

### Step 1: Open Terminal
Open your terminal and navigate to the project folder:
```bash
cd /Users/m/code/mandilkhadka/pickyou-scraper
```

### Step 2: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 3: Run the Scraper
```bash
python -m src.cli
```

**That's it!** The scraper will start and save all products to `data/pickyou_products.json`

---

## 📋 Complete Commands (Copy & Paste)

### Basic Run
```bash
cd /Users/m/code/mandilkhadka/pickyou-scraper
source venv/bin/activate
python -m src.cli
```

### With Progress Details (Recommended for first time)
```bash
cd /Users/m/code/mandilkhadka/pickyou-scraper
source venv/bin/activate
python -m src.cli --verbose
```

### Save to Custom File
```bash
cd /Users/m/code/mandilkhadka/pickyou-scraper
source venv/bin/activate
python -m src.cli --output data/my_products.json
```

---

## 🎯 Common Commands

| What You Want | Command |
|--------------|---------|
| **Basic scraping** | `python -m src.cli` |
| **See detailed progress** | `python -m src.cli --verbose` |
| **Save to different file** | `python -m src.cli --output data/products.json` |
| **Slower scraping (more polite)** | `python -m src.cli --delay 2.0` |
| **Quiet mode (less output)** | `python -m src.cli --quiet` |
| **See all options** | `python -m src.cli --help` |

---

## ⚡ One-Line Commands

**Quick start:**
```bash
source venv/bin/activate && python -m src.cli
```

**With verbose output:**
```bash
source venv/bin/activate && python -m src.cli --verbose
```

**Custom output file:**
```bash
source venv/bin/activate && python -m src.cli --output data/products.json
```

---

## 📍 Where is the Output?

After running, your scraped data will be saved to:
```
data/pickyou_products.json
```

You can find it in the `data/` folder of your project.

---

## ⏱️ How Long Does It Take?

- **Small store (< 1000 products)**: ~2-5 minutes
- **Medium store (1000-10000 products)**: ~10-30 minutes  
- **Large store (10000+ products)**: ~30-60 minutes

The scraper shows progress as it runs, so you can see how it's doing!

---

## ❓ Troubleshooting

### "Command not found" or "No module named src"
**Solution:** Make sure you're in the project directory and virtual environment is activated:
```bash
cd /Users/m/code/mandilkhadka/pickyou-scraper
source venv/bin/activate
```

### "ModuleNotFoundError: No module named 'requests'"
**Solution:** Install dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Want to stop the scraper?
**Press:** `Ctrl + C` (or `Cmd + C` on Mac)

---

## 🎓 What Happens When You Run It?

1. ✅ Scraper connects to pickyou.co.jp
2. ✅ Fetches all products page by page
3. ✅ Transforms data to your custom format
4. ✅ Saves everything to JSON file
5. ✅ Shows you statistics at the end

---

## 💡 Pro Tips

1. **First time?** Use `--verbose` to see what's happening
2. **Running in background?** Use `--quiet` for less output
3. **Slow internet?** Use `--delay 2.0` to be more polite
4. **Want to save logs?** Use `--log-file logs/scraper.log`

---

## 📞 Need Help?

Run this to see all available options:
```bash
python -m src.cli --help
```

---

**Happy Scraping! 🎉**

---

<a name="japanese-quick"></a>
# 日本語クイックスタート

## 🚀 簡単3ステップガイド

### ステップ1: ターミナルを開く
ターミナルを開き、プロジェクトフォルダに移動:
```bash
cd /Users/m/code/mandilkhadka/pickyou-scraper
```

### ステップ2: 仮想環境をアクティブ化
```bash
source venv/bin/activate
```

### ステップ3: スクレイパーを実行
```bash
python -m src.cli
```

**これだけです！** スクレイパーが開始し、すべての商品を`data/pickyou_products.json`に保存します

---

## 📋 完全なコマンド（コピー&ペースト）

### 基本的な実行
```bash
cd /Users/m/code/mandilkhadka/pickyou-scraper
source venv/bin/activate
python -m src.cli
```

### 進捗の詳細表示（初回推奨）
```bash
cd /Users/m/code/mandilkhadka/pickyou-scraper
source venv/bin/activate
python -m src.cli --verbose
```

### カスタムファイルに保存
```bash
cd /Users/m/code/mandilkhadka/pickyou-scraper
source venv/bin/activate
python -m src.cli --output data/my_products.json
```

---

## 🎯 一般的なコマンド

| やりたいこと | コマンド |
|--------------|---------|
| **基本的なスクレイピング** | `python -m src.cli` |
| **詳細な進捗を表示** | `python -m src.cli --verbose` |
| **別のファイルに保存** | `python -m src.cli --output data/products.json` |
| **遅いスクレイピング（より丁寧）** | `python -m src.cli --delay 2.0` |
| **静かなモード（出力が少ない）** | `python -m src.cli --quiet` |
| **すべてのオプションを表示** | `python -m src.cli --help` |

---

## ⚡ ワンライナーコマンド

**クイックスタート:**
```bash
source venv/bin/activate && python -m src.cli
```

**詳細な出力付き:**
```bash
source venv/bin/activate && python -m src.cli --verbose
```

**カスタム出力ファイル:**
```bash
source venv/bin/activate && python -m src.cli --output data/products.json
```

---

## 📍 出力はどこに？

実行後、スクレイピングされたデータは以下に保存されます:
```
data/pickyou_products.json
```

プロジェクトの`data/`フォルダで見つけることができます。

---

## ⏱️ どのくらい時間がかかりますか？

- **小規模ストア（< 1000商品）**: 約2-5分
- **中規模ストア（1000-10000商品）**: 約10-30分
- **大規模ストア（10000+商品）**: 約30-60分

スクレイパーは実行中に進捗を表示するので、進行状況を確認できます！

---

## ❓ トラブルシューティング

### "Command not found" または "No module named src"
**解決策:** プロジェクトディレクトリにいて、仮想環境がアクティブ化されていることを確認:
```bash
cd /Users/m/code/mandilkhadka/pickyou-scraper
source venv/bin/activate
```

### "ModuleNotFoundError: No module named 'requests'"
**解決策:** 依存関係をインストール:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### スクレイパーを停止したい？
**押す:** `Ctrl + C`（Macの場合は`Cmd + C`）

---

## 🎓 実行すると何が起こりますか？

1. ✅ スクレイパーがpickyou.co.jpに接続
2. ✅ ページごとにすべての商品を取得
3. ✅ データをカスタムフォーマットに変換
4. ✅ すべてをJSONファイルに保存
5. ✅ 最後に統計を表示

---

## 💡 プロのヒント

1. **初めてですか？** `--verbose`を使用して何が起こっているか確認
2. **バックグラウンドで実行？** 出力を減らすために`--quiet`を使用
3. **インターネットが遅い？** より丁寧にするために`--delay 2.0`を使用
4. **ログを保存したい？** `--log-file logs/scraper.log`を使用

---

## 📞 ヘルプが必要ですか？

利用可能なすべてのオプションを表示するには、これを実行:
```bash
python -m src.cli --help
```

---

**スクレイピングを楽しんでください！🎉**
