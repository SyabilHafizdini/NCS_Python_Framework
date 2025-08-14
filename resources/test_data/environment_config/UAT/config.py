"""
UAT Environment Configuration - SPF NGEN Framework
Python equivalent of Java QAF environment-config/UAT/ structure

Contains environment-specific settings for UAT testing
"""

# Base application configuration
ENV_CONFIG = {
    # Application URLs
    'env.baseurl': 'https://spf-ngen-uat.example.com',
    'env.admin.baseurl': 'https://spf-ngen-uat.example.com/admin',
    'env.api.baseurl': 'https://api-spf-ngen-uat.example.com',
    
    # Environment identifier
    'env.code': 'UAT',
    'env.name': 'User Acceptance Testing',
    
    # Browser and WebDriver settings
    'driver.name': 'chromedriver',
    'browser.type': 'chrome',
    'selenium.wait.timeout': '45',  # Longer timeouts for UAT
    'selenium.implicit.timeout': '15',
    
    # Test execution settings
    'test.retry.count': '3',
    'test.screenshot.enabled': 'true',
    'test.video.enabled': 'true',  # Video recording for UAT
    
    # Database settings (if needed)
    'db.host': 'uat-db.spfngen.com',
    'db.port': '5432',
    'db.name': 'spfngen_uat',
    'db.user': 'uattestuser',
    'db.password': 'uat_password',
    
    # API settings
    'api.timeout': '45',
    'api.retry.count': '5',
    'api.auth.enabled': 'true'
}

# Test user accounts for UAT environment
TEST_USERS = {
    'standard_user': {
        'username': 'uat_user',
        'password': 'UATPass123!',
        'email': 'uat.user@spfngen.com',
        'role': 'Standard User',
        'permissions': ['read', 'write']
    },
    
    'admin_user': {
        'username': 'uat_admin',
        'password': 'UATAdminPass123!',
        'email': 'uat.admin@spfngen.com',
        'role': 'Administrator',
        'permissions': ['read', 'write', 'admin', 'user_management']
    },
    
    'readonly_user': {
        'username': 'uat_readonly',
        'password': 'UATReadPass123!',
        'email': 'uat.readonly@spfngen.com',
        'role': 'Read Only User',
        'permissions': ['read']
    },
    
    'business_user': {
        'username': 'business_user',
        'password': 'BusinessPass123!',
        'email': 'business@spfngen.com',
        'role': 'Business User',
        'permissions': ['read', 'write', 'approve']
    },
    
    'invalid_user': {
        'username': 'invalid_uat_user',
        'password': 'wrong_uat_password',
        'email': 'invalid.uat@example.com',
        'role': 'Invalid',
        'permissions': []
    }
}

# Test data for various scenarios - UAT specific
TEST_DATA = {
    'profile_data': {
        'valid_profile': {
            'first_name': 'UAT',
            'last_name': 'Tester',
            'email': 'uat.tester@spfngen.com',
            'phone': '555-0456',
            'department': 'Business Analysis',
            'title': 'Business Analyst'
        },
        
        'business_profile': {
            'first_name': 'Business',
            'last_name': 'User',
            'email': 'business.user@spfngen.com',
            'phone': '555-0789',
            'department': 'Operations',
            'title': 'Operations Manager'
        }
    },
    
    'business_data': {
        'transactions': {
            'valid_transaction': {
                'amount': '1000.00',
                'reference': 'UAT-TXN-001',
                'description': 'UAT Test Transaction'
            },
            'large_transaction': {
                'amount': '50000.00',
                'reference': 'UAT-TXN-LARGE',
                'description': 'Large Amount UAT Test'
            }
        },
        
        'reports': {
            'date_range': {
                'start_date': '2024-01-01',
                'end_date': '2024-12-31'
            },
            'filters': ['Active', 'Pending', 'Completed']
        }
    },
    
    'search_data': {
        'business_searches': ['quarterly report', 'user activity', 'transaction history'],
        'performance_searches': ['large dataset', 'complex query', 'bulk operation'],
        'edge_cases': ['minimal data', 'maximum results', 'boundary conditions']
    }
}

# Error messages expected in UAT environment
EXPECTED_ERRORS = {
    'login': {
        'invalid_credentials': 'Authentication failed. Please check your credentials.',
        'empty_username': 'Username field cannot be empty',
        'empty_password': 'Password field cannot be empty',
        'account_locked': 'Your account has been locked due to multiple failed attempts',
        'session_timeout': 'Your session has timed out. Please log in again.'
    },
    
    'business_validation': {
        'insufficient_funds': 'Insufficient funds to complete transaction',
        'approval_required': 'This transaction requires approval',
        'invalid_amount': 'Please enter a valid amount',
        'duplicate_reference': 'Transaction reference already exists'
    },
    
    'system_errors': {
        'service_unavailable': 'Service is temporarily unavailable',
        'database_error': 'Database connection error. Please try again.',
        'timeout_error': 'Request timed out. Please try again.'
    }
}

# Performance expectations for UAT
PERFORMANCE_EXPECTATIONS = {
    'page_load_times': {
        'login_page': 5,  # seconds
        'dashboard_page': 10,
        'reports_page': 15,
        'data_export': 30
    },
    
    'transaction_processing': {
        'simple_transaction': 3,
        'complex_transaction': 10,
        'bulk_processing': 60
    }
}

# UAT-specific test scenarios
UAT_SCENARIOS = {
    'smoke_tests': [
        'user_login',
        'dashboard_access',
        'basic_navigation',
        'user_logout'
    ],
    
    'regression_tests': [
        'all_user_roles',
        'form_validations',
        'data_operations',
        'report_generation'
    ],
    
    'business_acceptance': [
        'end_to_end_workflows',
        'role_based_permissions',
        'business_rule_validation',
        'integration_testing'
    ]
}