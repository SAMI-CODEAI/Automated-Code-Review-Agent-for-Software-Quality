"""
Utility Functions - Test Project
Contains style and quality issues
"""

import hashlib
import random


# STYLE ISSUE: Poor function name
def f(x, y):
    """No meaningful name"""
    return x + y


# STYLE ISSUE: No docstring
def calculateTotal(items):
    t = 0
    for i in items:
        t += i['price']
    return t


# STYLE ISSUE: Magic numbers
def apply_discount(price):
    if price > 100:
        return price * 0.9  # What is 0.9?
    if price > 50:
        return price * 0.95  # What is 0.95?
    return price


# STYLE ISSUE: Long function doing too much
def process_user_data(user):
    # Validate
    if not user:
        return None
    if 'name' not in user:
        return None
    if 'email' not in user:
        return None
    if len(user['name']) < 2:
        return None
    
    # Clean name
    name = user['name'].strip()
    name = name.lower()
    name = name.capitalize()
    
    # Hash email
    email = user['email'].lower().strip()
    email_hash = hashlib.md5(email.encode()).hexdigest()
    
    # Generate ID
    user_id = random.randint(1000, 9999)
    
    # Format result
    result = {
        'id': user_id,
        'name': name,
        'email_hash': email_hash,
        'status': 'active',
        'created': '2024-01-01'
    }
    
    return result


# STYLE ISSUE: DRY violation
def send_email_to_admin(message):
    recipient = "admin@example.com"
    subject = "Admin Notification"
    print(f"Sending to: {recipient}")
    print(f"Subject: {subject}")
    print(f"Message: {message}")
    return True


def send_email_to_user(message):
    recipient = "user@example.com"
    subject = "User Notification"
    print(f"Sending to: {recipient}")
    print(f"Subject: {subject}")
    print(f"Message: {message}")
    return True


def send_email_to_support(message):
    recipient = "support@example.com"
    subject = "Support Request"
    print(f"Sending to: {recipient}")
    print(f"Subject: {subject}")
    print(f"Message: {message}")
    return True


# STYLE ISSUE: Unused variables
unused_var = 42
another_unused = "not used anywhere"


# STYLE ISSUE: Poor error handling
def risky_operation():
    try:
        result = 10 / 0
        return result
    except:  # Bare except
        pass  # Silent failure


# STYLE ISSUE: No type hints
def merge_data(data1, data2, option):
    if option:
        return data1 + data2
    else:
        return data1


# STYLE ISSUE: Inconsistent naming (camelCase vs snake_case)
def getUserName(userId):
    return f"user_{userId}"


def get_user_email(user_id):
    return f"user{user_id}@example.com"
