"""
DEV Environment Configuration - SPF NGEN Framework
Python equivalent of Java QAF environment-config/DEV/ structure

Contains environment-specific settings for development testing
"""

# Base application configuration
ENV_CONFIG = {
    # Application URLs
    'env.baseurl': 'https://spf-ngen-dev.example.com',
    'env.admin.baseurl': 'https://spf-ngen-dev.example.com/admin',
    'env.api.baseurl': 'https://api-spf-ngen-dev.example.com',
    
    # Environment identifier
    'env.code': 'DEV',
    'env.name': 'Development',
    
    # Browser and WebDriver settings
    'driver.name': 'chromedriver',
    'browser.type': 'chrome',
    'selenium.wait.timeout': '30',
    'selenium.implicit.timeout': '10',
    
    # Test execution settings
    'test.retry.count': '2',
    'test.screenshot.enabled': 'true',
    'test.video.enabled': 'false',
    
    # Database settings (if needed)
    'db.host': 'dev-db.spfngen.com',
    'db.port': '5432',
    'db.name': 'spfngen_dev',
    'db.user': 'testuser',
    'db.password': 'dev_password',
    
    # API settings
    'api.timeout': '30',
    'api.retry.count': '3',
    'api.auth.enabled': 'true'
}

# Test user accounts for DEV environment
TEST_USERS = {
    'standard_user': {
        'username': 'testuser',
        'password': 'TestPass123!',
        'email': 'testuser@spfngen.com',
        'role': 'Standard User',
        'permissions': ['read', 'write']
    },
    
    'admin_user': {
        'username': 'admin_test',
        'password': 'AdminPass123!',
        'email': 'admin@spfngen.com',
        'role': 'Administrator',
        'permissions': ['read', 'write', 'admin', 'user_management']
    },
    
    'readonly_user': {
        'username': 'readonly_test',
        'password': 'ReadPass123!',
        'email': 'readonly@spfngen.com',
        'role': 'Read Only User',
        'permissions': ['read']
    },
    
    'invalid_user': {
        'username': 'invalid_user',
        'password': 'wrong_password',
        'email': 'invalid@example.com',
        'role': 'Invalid',
        'permissions': []
    }
}

# Test data for various scenarios
TEST_DATA = {
    'profile_data': {
        'valid_profile': {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test.user@spfngen.com',
            'phone': '555-0123',
            'department': 'QA Testing',
            'title': 'Test Engineer'
        },
        
        'updated_profile': {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated.user@spfngen.com',
            'phone': '555-0199',
            'department': 'Quality Assurance',
            'title': 'Senior Test Engineer'
        }
    },
    
    'search_data': {
        'valid_searches': ['test data', 'user management', 'system'],
        'invalid_searches': ['!!!invalid!!!', '@@@@', ''],
        'special_characters': ['test@data', 'user#123', 'system$']
    },
    
    'form_validation': {
        'empty_fields': '',
        'max_length_exceeded': 'a' * 256,
        'special_characters': '!@#$%^&*()_+',
        'sql_injection': "'; DROP TABLE users; --",
        'xss_attempt': '<script>alert("xss")</script>'
    }
}

# Error messages expected in DEV environment
EXPECTED_ERRORS = {
    'login': {
        'invalid_credentials': 'Invalid username or password',
        'empty_username': 'Username is required',
        'empty_password': 'Password is required',
        'account_locked': 'Account is temporarily locked'
    },
    
    'form_validation': {
        'required_field': 'This field is required',
        'invalid_email': 'Please enter a valid email address',
        'password_too_short': 'Password must be at least 8 characters',
        'invalid_phone': 'Please enter a valid phone number'
    },
    
    'authorization': {
        'access_denied': 'You do not have permission to access this resource',
        'session_expired': 'Your session has expired. Please login again',
        'insufficient_privileges': 'Insufficient privileges to perform this action'
    }
}

# Page load timeouts and expectations
PAGE_EXPECTATIONS = {
    'login_page': {
        'load_timeout': 30,
        'expected_elements': ['username_field', 'password_field', 'login_button'],
        'expected_title': 'SPF NGEN - Login'
    },
    
    'dashboard_page': {
        'load_timeout': 45,
        'expected_elements': ['welcome_message', 'navigation_menu', 'user_profile'],
        'expected_url_fragment': 'dashboard'
    },
    
    'profile_page': {
        'load_timeout': 30,
        'expected_elements': ['profile_form', 'save_button', 'cancel_button'],
        'expected_url_fragment': 'profile'
    }
}