# 🔧 Installation & Setup Instructions

## ⚠️ Current Status from Verification

The verification script found the following issues that need to be addressed:

### Issues Detected:
1. ❌ **Python Version**: 3.9.9 (Need 3.11+)
2. ❌ **Missing Dependencies**: LangGraph, pathspec, langchain-google-genai
3. ❌ **Missing Tools**: Bandit, Radon
4. ❌ **Environment**: .env file not configured

---

## 🛠️ Complete Setup Guide

### Step 1: Upgrade Python (REQUIRED)

**Current:** Python 3.9.9  
**Required:** Python 3.11 or higher

#### Windows:
```bash
# Download from python.org
# https://www.python.org/downloads/

# Or use winget
winget install Python.Python.3.11

# Or use Chocolatey
choco install python311
```

#### Linux:
```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv

# Or build from source
wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz
tar -xf Python-3.11.7.tgz
cd Python-3.11.7
./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall
```

#### macOS:
```bash
# Using Homebrew
brew install python@3.11

# Or download from python.org
```

**After installing, verify:**
```bash
python --version  # Should show 3.11 or higher
# or
python3.11 --version
```

---

### Step 2: Create Virtual Environment (RECOMMENDED)

```bash
# Navigate to project directory
cd "d:/SAMI/AgenticAI/Automated Code Review Agent for Software Quality"

# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Verify Python version in venv
python --version  # Should show 3.11+
```

---

### Step 3: Install All Dependencies

```bash
# Activate virtual environment first (if not already active)

# Install all requirements
pip install --upgrade pip
pip install -r requirements.txt

# This will install:
# - langgraph>=0.2.0
# - langchain>=0.3.0
# - langchain-google-genai>=2.0.0
# - GitPython>=3.1.40
# - bandit>=1.7.5
# - radon>=6.0.1
# - pathspec>=0.12.0
# - And all other dependencies
```

**Verify installation:**
```bash
pip list | grep langgraph
pip list | grep pathspec
bandit --version
radon --version
```

---

### Step 4: Configure Environment

```bash
# Copy the template
cp .env.template .env

# OR on Windows PowerShell:
copy .env.template .env
```

**Edit `.env` file** and add your Google Gemini API key:

```env
# Get your key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_actual_key_here

# Optional: Choose model (default is gemini-1.5-pro-latest)
GEMINI_MODEL=gemini-1.5-pro-latest
# or
GEMINI_MODEL=gemini-1.5-flash-latest  # Faster, cheaper

# Optional: Customize settings
MAX_FILE_SIZE_MB=5
LOG_LEVEL=INFO
MAX_TOKENS_PER_REQUEST=100000
TEMPERATURE=0.1
```

---

### Step 5: Verify Installation Again

```bash
python verify_installation.py
```

**Expected output:**
```
✅ Python Version: PASS
✅ Dependencies: PASS
✅ Static Analysis Tools: PASS
✅ Environment Config: PASS
✅ Project Structure: PASS
✅ Module Imports: PASS

🎉 All checks passed! The system is ready to use.
```

---

## 🚀 Quick Start After Setup

Once all checks pass:

### 1. Run the Demo
```bash
python demo.py
```

### 2. Analyze Your Code
```bash
# Local directory
python main.py --path .

# GitHub repository
python main.py --path https://github.com/pallets/flask

# Custom output
python main.py --path . --output ./my_reviews
```

---

## 🔍 Troubleshooting

### Issue: Python 3.11 not found after installation

**Solution:**
```bash
# Try different commands
python3.11 --version
py -3.11 --version  # Windows

# Update PATH or create alias
alias python=python3.11  # Linux/Mac
```

### Issue: pip install fails with permission error

**Solution:**
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python3.11 -m venv venv
```

### Issue: "No module named 'langgraph'"

**Solution:**
```bash
# Ensure you're in the virtual environment
# Check where pip installs packages
pip show langgraph

# Reinstall if needed
pip uninstall langgraph
pip install langgraph
```

### Issue: Bandit or Radon not found

**Solution:**
```bash
# They should be installed with requirements.txt
# But you can install separately:
pip install bandit radon

# Verify
which bandit  # Linux/Mac
where bandit  # Windows
```

### Issue: API key error

**Solution:**
1. Verify `.env` file exists in project root
2. Check that `GOOGLE_API_KEY` is set (not the template value)
3. Get a valid key from: https://makersuite.google.com/app/apikey
4. Restart terminal after editing `.env`

### Issue: Module import errors with type hints

**Cause:** Using Python < 3.10 (type union syntax `str | Path` not supported)

**Solution:** Must upgrade to Python 3.11+

---

## 📋 Installation Checklist

Use this checklist to track your setup:

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Bandit installed and working (`bandit --version`)
- [ ] Radon installed and working (`radon --version`)
- [ ] `.env` file created from template
- [ ] `GOOGLE_API_KEY` configured in `.env`
- [ ] Verification script passes (`python verify_installation.py`)
- [ ] Demo runs successfully (`python demo.py`)

---

## 🎯 Next Steps After Successful Setup

1. **Test with Demo**
   ```bash
   python demo.py
   ```

2. **Review the Output**
   - Check `./demo_output/` for generated report
   - Review the findings and recommendations

3. **Analyze Real Code**
   ```bash
   python main.py --path /path/to/your/project
   ```

4. **Customize for Your Needs**
   - Modify prompts in `prompts/` directory
   - Adjust settings in `.env`
   - Add custom ignore patterns

---

## 📞 Support

If you continue to have issues:

1. **Check Python version**: `python --version` (must be 3.11+)
2. **Check virtual environment**: Ensure it's activated
3. **Check package installation**: `pip list`
4. **Review logs**: Check terminal output for specific errors
5. **Reinstall from scratch**: Delete `venv/` and start over

---

## ✅ Success Criteria

You're ready when:
- ✅ `python verify_installation.py` shows all green checkmarks
- ✅ `python demo.py` runs without errors
- ✅ Reports are generated in `./code_reviews/` or `./demo_output/`

---

**Good luck with your setup!** 🚀

Once everything is installed, you'll have a powerful AI-powered code review system at your fingertips.
