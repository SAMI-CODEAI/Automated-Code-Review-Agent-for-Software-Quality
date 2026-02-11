"""
Demo Script - Quick Demonstration of the Code Review Agent

This script demonstrates the capabilities of the automated code review system
by analyzing a small sample of code.
"""

import os
import sys
from pathlib import Path
import tempfile

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from utils.logger import setup_logger
from graph.workflow import create_review_graph
from graph.state import create_initial_state

logger = setup_logger(__name__)


# Sample code with intentional issues for demonstration
SAMPLE_CODE_SECURITY = """
# sample_security.py - Intentional security issues for demo

import sqlite3

def get_user(username):
    # SQL Injection vulnerability
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()

def authenticate(password):
    # Hardcoded password
    admin_password = "admin123"
    if password == admin_password:
        return True
    return False

# Using eval (dangerous)
def calculate(expression):
    return eval(expression)
"""

SAMPLE_CODE_PERFORMANCE = """
# sample_performance.py - Intentional performance issues for demo

def find_duplicates(items):
    # O(n²) complexity - inefficient
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates

def process_users(user_ids):
    # N+1 query problem simulation
    users = []
    for user_id in user_ids:
        user = get_user_from_db(user_id)  # Separate query for each
        users.append(user)
    return users

def get_user_from_db(user_id):
    # Placeholder for database query
    pass

# Complex nested logic
def complex_function(a, b, c, d, e):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
                    else:
                        return a + b + c + d
                else:
                    return a + b + c
            else:
                return a + b
        else:
            return a
    else:
        return 0
"""

SAMPLE_CODE_STYLE = """
# sample_style.py - Intentional style issues for demo

# Poor naming
def f(x,y,z):
    return x+y+z

# No docstring
def calculateTotalPrice(items):
    t=0
    for i in items:
        t+=i['price']
    return t

# Magic numbers
def apply_discount(price):
    if price > 100:
        return price * 0.9  # What is 0.9?
    return price

# Long function
def process_order(order):
    # Validate
    if not order:
        return None
    if 'items' not in order:
        return None
    if len(order['items']) == 0:
        return None
    
    # Calculate
    total = 0
    for item in order['items']:
        total += item['price'] * item['quantity']
    
    # Apply discount
    if total > 100:
        total = total * 0.9
    
    # Add tax
    total = total * 1.1
    
    # Format
    result = {
        'order_id': order['id'],
        'total': total,
        'status': 'processed'
    }
    
    return result

# Unused variable
x = 42

# DRY violation
def send_email_to_admin(message):
    email = "admin@example.com"
    print(f"Sending to {email}: {message}")

def send_email_to_user(message):
    email = "user@example.com"
    print(f"Sending to {email}: {message}")
"""


def create_demo_project():
    """Create a temporary demo project with sample code."""
    logger.info("📁 Creating demo project with sample code...")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="code_review_demo_")
    temp_path = Path(temp_dir)
    
    # Create sample files
    (temp_path / "sample_security.py").write_text(SAMPLE_CODE_SECURITY, encoding='utf-8')
    (temp_path / "sample_performance.py").write_text(SAMPLE_CODE_PERFORMANCE, encoding='utf-8')
    (temp_path / "sample_style.py").write_text(SAMPLE_CODE_STYLE, encoding='utf-8')
    
    # Create README
    readme = """# Demo Project

This is a sample project with intentional code issues for demonstrating
the Automated Code Review Agent.

Issues included:
- Security: SQL injection, hardcoded passwords, eval usage
- Performance: O(n²) algorithms, N+1 queries, high complexity
- Style: Poor naming, missing docs, magic numbers
"""
    (temp_path / "README.md").write_text(readme, encoding='utf-8')
    
    logger.info(f"✅ Demo project created at: {temp_path}")
    logger.info(f"   Files: sample_security.py, sample_performance.py, sample_style.py")
    
    return temp_path


def run_demo():
    """Run the demo."""
    print("=" * 80)
    print("🎬 Automated Code Review Agent - Interactive Demo")
    print("=" * 80)
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("\n❌ ERROR: GOOGLE_API_KEY not configured")
        print("Please set your Gemini API key in .env file")
        print("\nSteps:")
        print("1. cp .env.template .env")
        print("2. Edit .env and add your API key")
        print("3. Run this demo again")
        return 1
    
    print("\n📝 This demo will:")
    print("1. Create a temporary project with sample code")
    print("2. Run the full code review workflow")
    print("3. Demonstrate security, performance, and style analysis")
    print("4. Generate a comprehensive review report")
    
    input("\nPress Enter to start the demo...")
    
    try:
        # Create demo project
        demo_path = create_demo_project()
        
        # Create workflow
        logger.info("\n🔧 Initializing review workflow...")
        graph = create_review_graph()
        
        # Create initial state
        initial_state = create_initial_state(
            input_path=str(demo_path),
            output_dir="./demo_output"
        )
        
        # Run review
        print("\n" + "=" * 80)
        print("🚀 Starting Code Review Analysis")
        print("=" * 80)
        
        final_state = graph.invoke(initial_state)
        
        # Display results
        print("\n" + "=" * 80)
        print("📊 Review Results")
        print("=" * 80)
        
        if final_state.get('error'):
            print(f"\n❌ Review failed: {final_state['error']}")
            return 1
        
        # Show statistics
        total_files = final_state.get('total_files', 0)
        security_count = len(final_state.get('security_findings', []))
        performance_count = len(final_state.get('performance_findings', []))
        style_count = len(final_state.get('style_findings', []))
        
        print(f"\n✅ Analysis completed successfully!")
        print(f"\n📈 Statistics:")
        print(f"   Files analyzed: {total_files}")
        print(f"   🔒 Security issues: {security_count}")
        print(f"   ⚡ Performance issues: {performance_count}")
        print(f"   ✨ Style issues: {style_count}")
        
        # Show sample findings
        if security_count > 0:
            print(f"\n🔒 Sample Security Finding:")
            finding = final_state['security_findings'][0]
            print(f"   Type: {finding.get('issue_type')}")
            print(f"   Severity: {finding.get('severity')}")
            print(f"   File: {Path(finding.get('file', '')).name}")
            print(f"   Description: {finding.get('description', '')[:100]}...")
        
        # Report location
        report_path = final_state.get('report_path')
        if report_path:
            print(f"\n📋 Full report generated:")
            print(f"   {report_path}")
            print(f"\n💡 Open the report to see detailed findings and recommendations!")
        
        # Cleanup option
        print("\n" + "=" * 80)
        cleanup = input("\nClean up demo files? (y/n): ").lower().strip()
        if cleanup == 'y':
            import shutil
            shutil.rmtree(demo_path, ignore_errors=True)
            print("✅ Demo files cleaned up")
        else:
            print(f"📁 Demo files preserved at: {demo_path}")
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Next steps:")
        print("   - Review the generated report")
        print("   - Try analyzing your own project:")
        print("     python main.py --path /path/to/your/project")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(run_demo())
