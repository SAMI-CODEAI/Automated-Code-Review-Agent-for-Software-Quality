"""
Installation Verification Script

Run this script to verify that all dependencies are installed correctly
and the system is ready to use.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_python_version():
    """Check Python version."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.11+")
        return False


def check_dependencies():
    """Check if all required packages are installed."""
    print("\n🔍 Checking dependencies...")
    
    required_packages = {
        'langgraph': 'LangGraph',
        'langchain': 'LangChain',
        'langchain_google_genai': 'LangChain Google Generative AI',
        'git': 'GitPython',
        'pathspec': 'pathspec',
        'colorama': 'colorama',
        'click': 'click',
        'pydantic': 'pydantic',
        'dotenv': 'python-dotenv',
    }
    
    missing = []
    for package, name in required_packages.items():
        try:
            if package == 'git':
                import git
            elif package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"✅ {name} - OK")
        except ImportError:
            print(f"❌ {name} - MISSING")
            missing.append(name)
    
    return len(missing) == 0, missing


def check_static_tools():
    """Check if static analysis tools are installed."""
    print("\n🔍 Checking static analysis tools...")
    
    import subprocess
    
    tools = {
        'bandit': 'Bandit (Security Scanner)',
        'radon': 'Radon (Complexity Analyzer)'
    }
    
    missing = []
    for cmd_name, name in tools.items():
        try:
            result = subprocess.run(
                [sys.executable, '-m', cmd_name, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print(f"✅ {name} - {version}")
            else:
                print(f"⚠️ {name} - Installed but version check failed")
        except FileNotFoundError:
            print(f"❌ {name} - NOT INSTALLED")
            missing.append(name)
        except subprocess.TimeoutExpired:
            print(f"⚠️ {name} - Timeout during check")
    
    return len(missing) == 0, missing


def check_environment():
    """Check environment configuration."""
    print("\n🔍 Checking environment configuration...")
    
    import os
    from dotenv import load_dotenv
    
    # Try to load .env
    env_file = project_root / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print("✅ .env file found")
    else:
        print("⚠️ .env file not found (using .env.template as reference)")
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key and api_key != 'your_gemini_api_key_here':
        print(f"✅ GOOGLE_API_KEY configured ({len(api_key)} characters)")
        return True
    else:
        print("❌ GOOGLE_API_KEY not configured or using template value")
        print("   Please set your Gemini API key in .env file")
        return False


def check_project_structure():
    """Check if all required directories and files exist."""
    print("\n🔍 Checking project structure...")
    
    required_dirs = [
        'agents',
        'graph',
        'tools',
        'utils',
        'prompts'
    ]
    
    required_files = [
        'main.py',
        'requirements.txt',
        'agents/__init__.py',
        'graph/workflow.py',
        'graph/state.py',
    ]
    
    all_ok = True
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
            all_ok = False
    
    for file_name in required_files:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"✅ {file_name} exists")
        else:
            print(f"❌ {file_name} missing")
            all_ok = False
    
    return all_ok


def test_imports():
    """Test if all modules can be imported."""
    print("\n🔍 Testing module imports...")
    
    modules = [
        ('agents.ingestor', 'IngestorAgent'),
        ('agents.security', 'SecurityAgent'),
        ('agents.performance', 'PerformanceAgent'),
        ('agents.style', 'StyleAgent'),
        ('agents.aggregator', 'AggregatorAgent'),
        ('graph.workflow', 'create_review_graph'),
        ('graph.state', 'ReviewState'),
        ('tools.bandit_tool', 'run_bandit_scan'),
        ('tools.radon_tool', 'run_radon_analysis'),
        ('utils.git_ops', 'is_git_url'),
        ('utils.file_scanner', 'scan_local_directory'),
        ('utils.logger', 'setup_logger'),
    ]
    
    all_ok = True
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"❌ {module_name}.{class_name} - {str(e)}")
            all_ok = False
    
    return all_ok


def main():
    """Run all verification checks."""
    print("=" * 80)
    print("🔬 Automated Code Review Agent - Installation Verification")
    print("=" * 80)
    
    checks = []
    
    # Python version
    checks.append(("Python Version", check_python_version()))
    
    # Dependencies
    deps_ok, missing_deps = check_dependencies()
    checks.append(("Dependencies", deps_ok))
    
    # Static tools
    tools_ok, missing_tools = check_static_tools()
    checks.append(("Static Analysis Tools", tools_ok))
    
    # Environment
    checks.append(("Environment Config", check_environment()))
    
    # Project structure
    checks.append(("Project Structure", check_project_structure()))
    
    # Module imports
    checks.append(("Module Imports", test_imports()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Verification Summary")
    print("=" * 80)
    
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name}: {status}")
    
    all_passed = all(passed for _, passed in checks)
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("🎉 All checks passed! The system is ready to use.")
        print("\n💡 Quick start:")
        print("   python main.py --path https://github.com/pallets/flask")
        print("   python main.py --path .")
        return 0
    else:
        print("⚠️ Some checks failed. Please address the issues above.")
        
        if not deps_ok:
            print("\n📦 Install missing dependencies:")
            print("   pip install -r requirements.txt")
        
        if not tools_ok:
            print("\n🔧 Install missing tools:")
            if 'Bandit' in str(missing_tools):
                print("   pip install bandit")
            if 'Radon' in str(missing_tools):
                print("   pip install radon")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
