# 🚀 Quick Start Guide

Get started with the Automated Code Review Agent in 5 minutes!

---

## ⚡ Fast Track (3 Steps)

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Configure API Key
```bash
# Copy template
cp .env.template .env

# Edit .env and add your key
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3️⃣ Run Your First Review
```bash
# Analyze current directory
python main.py --path .

# Or analyze a GitHub repo
python main.py --path https://github.com/pallets/flask
```

**That's it!** 🎉 Your code review report will be in the `./code_reviews/` directory.

---

## 🔍 Verification (Optional but Recommended)

Before running your first review, verify everything is set up correctly:

```bash
python verify_installation.py
```

This checks:
- ✅ Python version (3.11+)
- ✅ All dependencies installed
- ✅ Static tools (Bandit, Radon)
- ✅ Environment configuration
- ✅ Project structure
- ✅ Module imports

---

## 🎬 Try the Demo

Want to see it in action first? Run the interactive demo:

```bash
python demo.py
```

This will:
- Create sample code with intentional issues
- Run the full analysis pipeline
- Show you what a real report looks like
- No need for your own code!

---

## 📖 Detailed Setup

### Prerequisites

**Required:**
- Python 3.11 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

**Optional (for better results):**
- Git (for cloning repositories)

### Installation Steps

#### 1. Clone or Download

```bash
cd "Automated Code Review Agent for Software Quality"
```

#### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **LangGraph** - Workflow orchestration
- **LangChain** - LLM framework
- **Google Gemini** - AI model integration
- **Bandit** - Security scanner
- **Radon** - Complexity analyzer
- **GitPython** - Repository cloning
- Plus utilities (click, colorama, pathspec, etc.)

#### 4. Configure Environment

```bash
# Copy the template
cp .env.template .env
```

Edit `.env` file:
```env
# Required
GOOGLE_API_KEY=your_actual_api_key_here

# Optional customization
GEMINI_MODEL=gemini-1.5-pro-latest  # or gemini-1.5-flash-latest
MAX_FILE_SIZE_MB=5
LOG_LEVEL=INFO
```

#### 5. Verify Installation

```bash
python verify_installation.py
```

Look for green checkmarks (✅). If you see red X's (❌), follow the suggestions.

---

## 🎯 Usage Examples

### Example 1: Analyze Local Project
```bash
python main.py --path /path/to/your/project
```

### Example 2: Analyze GitHub Repository
```bash
python main.py --path https://github.com/django/django
```

### Example 3: Custom Output Directory
```bash
python main.py --path . --output ./my_reviews
```

### Example 4: Use Faster Model
```bash
python main.py --path . --model gemini-1.5-flash-latest
```

### Example 5: Current Directory
```bash
python main.py --path .
```

---

## 📋 Understanding the Output

After running a review, you'll get:

```
./code_reviews/
└── REVIEW_REPORT_2026-01-09_22-00-00.md
```

The report contains:

1. **Executive Summary**
   - Health score (0-100)
   - Statistics and metrics
   - Findings breakdown

2. **Critical Issues** (if any)
   - Immediate attention required
   - Security vulnerabilities
   - Performance bottlenecks

3. **Detailed Findings**
   - 🔒 Security (OWASP Top 10, CWE)
   - ⚡ Performance (Big-O, complexity)
   - ✨ Style (Clean Code, SOLID)

4. **Recommendations**
   - Prioritized by timeline
   - 24 hours / 1 week / 1 month / 1 quarter
   - Actionable steps

---

## 🎨 Customization

### Change Model

Edit `.env`:
```env
# Faster, less detailed
GEMINI_MODEL=gemini-1.5-flash-latest

# Slower, more accurate
GEMINI_MODEL=gemini-1.5-pro-latest
```

### Adjust File Size Limit

```env
MAX_FILE_SIZE_MB=10  # Analyze larger files
```

### Change Log Level

```env
LOG_LEVEL=DEBUG  # More verbose
LOG_LEVEL=WARNING  # Less verbose
```

### Modify Ignore Patterns

```env
IGNORE_PATTERNS=*.pyc,*.pyo,__pycache__,node_modules,custom_dir
```

---

## 🐛 Troubleshooting

### Issue: "GOOGLE_API_KEY not set"
**Solution:** 
```bash
cp .env.template .env
# Edit .env and add your API key
```

### Issue: "Bandit not found"
**Solution:**
```bash
pip install bandit
```

### Issue: "Radon not found"
**Solution:**
```bash
pip install radon
```

### Issue: "No files found to analyze"
**Solution:**
- Check that the path exists
- Verify files aren't all ignored by .gitignore
- Try with a different directory

### Issue: API timeout or rate limit
**Solution:**
- Use `gemini-1.5-flash-latest` (faster model)
- Add delays between requests
- Reduce number of files analyzed

---

## 💡 Tips for Best Results

### 1. Start Small
```bash
# Test with a small project first
python demo.py
```

### 2. Use .gitignore
Create or update `.gitignore` to exclude:
- `node_modules/`
- `venv/`
- Build artifacts
- Test data

### 3. Focus on Important Files
The system automatically prioritizes:
- Python files (for now)
- Files with detected issues
- Non-binary, non-huge files

### 4. Review Reports Carefully
- Start with Critical and High severity issues
- Understand the context before making changes
- Use recommendations as guidelines, not rules

### 5. Iterate
- Fix critical issues
- Re-run the review
- Track improvements over time

---

## 📚 Next Steps

Once you're comfortable:

1. **Explore Documentation**
   - [README.md](README.md) - Full documentation
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
   - [PHASE4_COMPLETE.md](PHASE4_COMPLETE.md) - Implementation details

2. **Customize Prompts**
   - Modify `prompts/security.py` for different security focus
   - Adjust `prompts/performance.py` for your performance goals
   - Customize `prompts/style.py` for your coding standards

3. **Extend the System**
   - Add new agents for specific concerns
   - Integrate additional static analysis tools
   - Create custom report formats

4. **Automate**
   - Add to CI/CD pipeline
   - Create pre-commit hooks
   - Schedule regular reviews

---

## 🆘 Getting Help

### Quick Checks
1. Run `python verify_installation.py`
2. Check `.env` file is configured
3. Ensure you have internet connection (for Gemini API)
4. Review the logs in the terminal

### Common Commands
```bash
# Get help
python main.py --help

# Verify setup
python verify_installation.py

# Run demo
python demo.py

# Check dependencies
pip list | grep langgraph
pip list | grep langchain
```

---

## ✅ You're Ready!

You now have everything you need to run automated code reviews. Start with:

```bash
python demo.py          # Try the demo first
python main.py --path . # Then analyze your code
```

Happy reviewing! 🚀
