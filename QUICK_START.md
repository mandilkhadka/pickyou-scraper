# Quick Start Guide - PickYou Scraper

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

