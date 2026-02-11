# 🧪 Test Project Created + API Setup Guide

## ✅ What I've Created for You

### 1. **Test Project** (`test_project/` folder)

A complete Python web application with **intentional code issues** for testing:

**Files Created:**
- **[app.py](file:///d:/SAMI/AgenticAI/Automated%20Code%20Review%20Agent%20for%20Software%20Quality/test_project/app.py)** - Flask app with security vulnerabilities:
  - SQL Injection
  - XSS (Cross-Site Scripting)
  - Hardcoded secrets
  - eval() usage (code injection)
  - Missing authentication
  - Debug mode enabled

- **[database.py](file:///d:/SAMI/AgenticAI/Automated%20Code%20Review%20Agent%20for%20Software%20Quality/test_project/database.py)** - Database with performance issues:
  - N+1 query problem
  - O(n²) algorithms
  - High cyclomatic complexity
  - Inefficient data processing

- **[utils.py](file:///d:/SAMI/AgenticAI/Automated%20Code%20Review%20Agent%20for%20Software%20Quality/test_project/utils.py)** - Utilities with style issues:
  - Poor function naming
  - Missing docstrings
  - Magic numbers
  - DRY violations
  - No type hints
  - Inconsistent naming conventions

- **[config.py](file:///d:/SAMI/AgenticAI/Automated%20Code%20Review%20Agent%20for%20Software%20Quality/test_project/config.py)** - Configuration with hardcoded secrets:
  - Database passwords
  - API keys (Stripe, AWS, SendGrid)
  - Admin credentials
  - Encryption keys

### 2. **API Key Setup Guide**

Created comprehensive guide: **[API_KEY_SETUP.md](file:///d:/SAMI/AgenticAI/Automated%20Code%20Review%20Agent%20for%20Software%20Quality/API_KEY_SETUP.md)**

---

## 🔑 **ONLY ONE API KEY NEEDED: Google Gemini**

### Quick Setup:

1. **Get Your Free API Key**:
   - 🔗 Visit: **https://makersuite.google.com/app/apikey**
   - Sign in with Google Account
   - Click "Create API key"
   - Copy the key (starts with `AIza...`)

2. **Configure .env File**:
   ```bash
   # Copy template
   copy .env.template .env
   
   # Edit .env and add:
   GOOGLE_API_KEY=AIzaSyD-YOUR-ACTUAL-KEY-HERE
   ```

That's it! No other API keys needed.

---

## 🧪 How to Test the System

### Step 1: Set Up Environment (One-Time)

```bash
# 1. Make sure you have Python 3.11+ installed
python --version

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
copy .env.template .env
# Edit .env and add your GOOGLE_API_KEY

# 4. Verify setup
python verify_installation.py
```

### Step 2: Test on the Sample Project

```bash
# Analyze the test project
python main.py --path test_project
```

**What will happen:**
1. ✅ Scans all 4 Python files
2. ✅ Runs Bandit security scanner
3. ✅ Runs Radon complexity analyzer
4. ✅ AI analyzes each file with Gemini
5. ✅ Generates comprehensive report

**Expected findings:**
- **Security**: ~8-12 issues (SQL injection, XSS, secrets, etc.)
- **Performance**: ~5-8 issues (N+1, O(n²), complexity)
- **Style**: ~10-15 issues (naming, docs, DRY violations)

### Step 3: Review the Report

```bash
# Report will be in:
./code_reviews/REVIEW_REPORT_<timestamp>.md
```

Open the markdown file to see:
- Executive summary with health score
- Critical issues requiring immediate attention
- Detailed findings by category
- Prioritized recommendations

---

## 📊 Expected Test Results

When you run the test, you should find:

### 🔒 Security Issues (HIGH Priority)

**From app.py:**
1. SQL Injection in `get_user()` function
2. XSS vulnerability in `search()` function
3. eval() usage in `eval_input()` function
4. Hardcoded secret key
5. Debug mode enabled in production
6. No authentication on admin endpoint

**From config.py:**
7. Hardcoded database password
8. Exposed API keys (Stripe, AWS, SendGrid)
9. Hardcoded encryption key
10. Admin credentials in code

### ⚡ Performance Issues (MEDIUM Priority)

**From database.py:**
1. N+1 query problem in `get_all_users()`
2. O(n²) algorithm in `find_duplicates()`
3. Multiple passes in `process_large_dataset()`
4. Loading entire dataset in `search_users_slow()`
5. Very high cyclomatic complexity in `calculate_complex()`

### ✨ Style Issues (LOW Priority)

**From utils.py:**
1. Poor function name: `f(x, y)`
2. Missing docstring in `calculateTotal()`
3. Magic numbers in `apply_discount()`
4. Long function: `process_user_data()`
5. DRY violations (repeated email sending code)
6. Unused variables
7. Bare except clause
8. No type hints
9. Inconsistent naming (camelCase vs snake_case)

---

## 🎯 What This Demonstrates

This test project showcases the system's ability to detect:

**✅ Security vulnerabilities** - Real exploitable issues
**✅ Performance bottlenecks** - Scalability problems
**✅ Code quality issues** - Maintainability concerns
**✅ Best practice violations** - Industry standards

---

## 💡 Next Steps After Testing

Once you've tested with this project:

1. **Review the Generated Report**
   - Check if findings are accurate
   - Verify recommendations make sense

2. **Test on Your Own Code**
   ```bash
   python main.py --path /path/to/your/project
   ```

3. **Experiment with Settings**
   - Try `gemini-1.5-flash-latest` for speed
   - Try `gemini-1.5-pro-latest` for accuracy
   - Adjust in `.env` file

4. **Customize for Your Needs**
   - Modify prompts in `prompts/` folder
   - Adjust ignore patterns in `.env`
   - Add custom analysis rules

---

## 📋 Quick Reference

### Test Command:
```bash
python main.py --path test_project
```

### View Results:
```bash
# Navigate to output folder
cd code_reviews

# Open the latest report (Windows)
start REVIEW_REPORT_*.md

# Or find the latest file
dir /O-D REVIEW_REPORT_*.md
```

### Re-run with Different Models:
```bash
# Faster (Flash)
python main.py --path test_project --model gemini-1.5-flash-latest

# More accurate (Pro)
python main.py --path test_project --model gemini-1.5-pro-latest
```

---

## ✅ Summary

**You have everything you need:**

- ✅ **Test project** with realistic code issues
- ✅ **API key guide** with setup instructions
- ✅ **Clear documentation** on what to expect

**To get started:**

1. Get API key: https://makersuite.google.com/app/apikey
2. Add to `.env` file: `GOOGLE_API_KEY=your_key`
3. Run: `python main.py --path test_project`
4. Review the generated report!

🚀 **Ready to test your AI code review system!**
