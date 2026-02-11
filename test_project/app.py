"""
Flask Web Application - Test Project
Contains intentional security vulnerabilities for testing
"""

from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

# SECURITY ISSUE: Hardcoded secret key
app.secret_key = "super_secret_key_12345"

# SECURITY ISSUE: Debug mode enabled in production
app.config['DEBUG'] = True


@app.route('/')
def home():
    return '<h1>Welcome to Test App</h1><a href="/user">Search Users</a>'


@app.route('/user')
def get_user():
    """
    SECURITY ISSUE: SQL Injection vulnerability
    User input is directly concatenated into SQL query
    """
    username = request.args.get('username', '')
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # SQL INJECTION VULNERABILITY
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return f'<h2>User found: {user[1]}</h2>'
    return '<h2>User not found</h2>'


@app.route('/search')
def search():
    """
    SECURITY ISSUE: XSS vulnerability
    User input reflected in response without escaping
    """
    query = request.args.get('q', '')
    
    # XSS VULNERABILITY - no escaping
    html = f'''
    <h1>Search Results</h1>
    <p>You searched for: {query}</p>
    '''
    
    return render_template_string(html)


@app.route('/eval')
def eval_input():
    """
    SECURITY ISSUE: Code injection via eval()
    Extremely dangerous!
    """
    expression = request.args.get('expr', '1+1')
    
    # DANGEROUS: Using eval on user input
    try:
        result = eval(expression)
        return f'Result: {result}'
    except Exception as e:
        return f'Error: {str(e)}'


@app.route('/admin')
def admin():
    """
    SECURITY ISSUE: No authentication check
    Admin page accessible to anyone
    """
    # Missing authentication check
    return '<h1>Admin Dashboard</h1><p>Secret admin data here</p>'


if __name__ == '__main__':
    # SECURITY ISSUE: Running on 0.0.0.0 exposes to network
    app.run(host='0.0.0.0', port=5000, debug=True)
