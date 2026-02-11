"""
Configuration - Test Project
SECURITY ISSUE: Contains hardcoded secrets
"""

# SECURITY ISSUE: Hardcoded database password
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'admin',
    'password': 'admin123',  # HARDCODED PASSWORD!
    'database': 'myapp'
}

# SECURITY ISSUE: Hardcoded API keys
API_KEYS = {
    'stripe': 'sk_live_1234567890abcdef',  # EXPOSED SECRET KEY!
    'sendgrid': 'SG.1234567890abcdef',
    'aws_access': 'AKIAIOSFODNN7EXAMPLE',
    'aws_secret': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
}

# SECURITY ISSUE: Hardcoded encryption key
ENCRYPTION_KEY = "my_super_secret_key_do_not_share"

# SECURITY ISSUE: Admin credentials
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'Password123!'
}

# CONFIGURATION
APP_CONFIG = {
    'debug': True,  # Should be False in production
    'secret_key': 'flask_secret_key_12345',
    'session_timeout': 3600,
}
