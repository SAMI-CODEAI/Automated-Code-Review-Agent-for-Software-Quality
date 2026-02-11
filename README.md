# Automated Code Review Agent

A production-ready Multi-Agent System (MAS) built with LangGraph for automated code review. The system analyzes codebases from local directories or GitHub repositories and generates comprehensive review reports covering security, performance, and code style.

## 🏗️ System Architecture

### Multi-Agent Design
- **Ingestor Agent**: Clones GitHub repositories or scans local directories
- **Security Agent**: Identifies vulnerabilities (SQL injection, XSS, secret leaks)
- **Performance Agent**: Detects N+1 queries, memory leaks, and complexity issues
- **Style Agent**: Ensures PEP8/Clean Code compliance
- **Aggregator Agent**: Compiles findings into structured reports

### Orchestration
LangGraph manages state transitions and enables parallel agent execution for optimal performance.

## 🚀 Features

- ✅ Support for both local directories and GitHub repositories
- ✅ Parallel agent execution for faster analysis
- ✅ Integration with Bandit (security) and Radon (complexity)
- ✅ Respects .gitignore patterns
- ✅ Handles large repositories with file-by-file processing
- ✅ Generates detailed markdown reports
- ✅ Powered by Google Gemini 1.5 Pro/Flash

## 📋 Prerequisites

- Python 3.11+
- Google Gemini API key
- Git (for repository cloning)

## 🔧 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd "Automated Code Review Agent for Software Quality"
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.template .env
# Edit .env and add your GOOGLE_API_KEY
```

## 💻 Usage

### Quick Start

1. **Configure your API key**:
```bash
# Copy the template
cp .env.template .env

# Edit .env and add your Google Gemini API key
GOOGLE_API_KEY=your_gemini_api_key_here
```

2. **Run a code review**:
```bash
# Review a local directory
python main.py --path /path/to/your/project

# Review a GitHub repository
python main.py --path https://github.com/username/repository

# Specify output directory
python main.py --path . --output ./my_reviews

# Use a specific model
python main.py --path . --model gemini-1.5-flash-latest
```

### Example Output

```bash
$ python main.py --path https://github.com/pallets/flask

================================================================================
🚀 Starting Automated Code Review Agent
================================================================================
📝 Using model: gemini-1.5-pro-latest
📁 Output directory: D:\code_reviews
🔍 Analyzing: https://github.com/pallets/flask

📥 Starting code ingestion
🌐 Source type: Git Repository
📦 Repository: flask
🔄 Cloning repository...
✅ Repository cloned successfully
🔍 Scanning directory...
✅ Scan completed: 127 files found

🔐 Security Node: Starting AI-powered analysis
🔒 Running Bandit security scan...
📊 Bandit found 5 potential issues
🔍 Analyzing (1/15): auth.py
   Found 2 security issues
...
✅ Security analysis complete: 12 findings

⚡ Performance Node: Starting AI-powered analysis
📊 Running Radon complexity analysis...
✅ Performance analysis complete: 8 findings

✨ Style Node: Starting AI-powered analysis
✅ Style analysis complete: 23 findings

📋 Aggregator Node: Starting report compilation
✅ Report saved to: ./code_reviews/REVIEW_REPORT_2026-01-09_21-45-30.md

================================================================================
✅ Review completed successfully!
📋 Report generated: ./code_reviews/REVIEW_REPORT_2026-01-09_21-45-30.md
================================================================================
```

### Additional options
```bash
# Get help
python main.py --help

# Use different Gemini models
python main.py --path . --model gemini-1.5-flash-latest  # Faster
python main.py --path . --model gemini-1.5-pro-latest    # More accurate
```

## 📁 Project Structure

```
├── main.py                 # CLI entry point
├── requirements.txt        # Python dependencies
├── .env.template          # Environment configuration template
├── agents/                # Agent implementations
│   ├── __init__.py
│   ├── ingestor.py       # Code ingestion logic
│   ├── security.py       # Security analysis
│   ├── performance.py    # Performance analysis
│   ├── style.py          # Code style checks
│   └── aggregator.py     # Report compilation
├── graph/                 # LangGraph orchestration
│   ├── __init__.py
│   ├── state.py          # State definitions
│   └── workflow.py       # Graph construction
├── tools/                 # Static analysis tools
│   ├── __init__.py
│   ├── bandit_tool.py    # Security scanning
│   └── radon_tool.py     # Complexity analysis
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── git_ops.py        # Git operations
│   ├── file_scanner.py   # Local file scanning
│   └── logger.py         # Logging configuration
└── prompts/              # Agent prompts
    ├── __init__.py
    ├── security.py
    ├── performance.py
    └── style.py
```

## 🔍 Output

The system generates a `REVIEW_REPORT.md` file containing:

- Executive summary
- Security findings with severity ratings
- Performance bottlenecks and recommendations
- Style violations and suggestions
- File-by-file analysis
- Actionable improvement recommendations

## 🛡️ Quality Guardrails

- File-by-file processing to avoid token limits
- Robust error handling for invalid URLs or inaccessible paths
- .gitignore pattern respect
- Configurable file size limits
- Retry mechanisms for API calls

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.
