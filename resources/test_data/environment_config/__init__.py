"""
Environment Configuration Package
SPF NGEN Framework - Python QAF Implementation

Provides environment-specific configuration loading
Similar to Java QAF environment-config structure
"""

import os
import importlib


def load_environment_config(env_code="DEV"):
    """
    Load environment-specific configuration
    
    Args:
        env_code: Environment code (DEV, UAT, PROD)
        
    Returns:
        dict: Environment configuration
    """
    try:
        # Import environment-specific config module
        config_module = importlib.import_module(f'test_data.environment_config.{env_code}.config')
        
        return {
            'env_config': config_module.ENV_CONFIG,
            'test_users': config_module.TEST_USERS,
            'test_data': config_module.TEST_DATA,
            'expected_errors': config_module.EXPECTED_ERRORS,
            'page_expectations': getattr(config_module, 'PAGE_EXPECTATIONS', {}),
            'performance_expectations': getattr(config_module, 'PERFORMANCE_EXPECTATIONS', {}),
            'scenarios': getattr(config_module, 'UAT_SCENARIOS', {})
        }
        
    except ImportError:
        # Fallback to DEV if environment not found
        if env_code != "DEV":
            return load_environment_config("DEV")
        else:
            raise Exception(f"Environment configuration for {env_code} not found")


def get_test_user(env_code="DEV", user_type="standard_user"):
    """
    Get test user credentials for specific environment
    
    Args:
        env_code: Environment code
        user_type: Type of user (standard_user, admin_user, etc.)
        
    Returns:
        dict: User credentials and details
    """
    config = load_environment_config(env_code)
    return config['test_users'].get(user_type, {})


def get_environment_url(env_code="DEV", url_type="baseurl"):
    """
    Get environment-specific URL
    
    Args:
        env_code: Environment code
        url_type: Type of URL (baseurl, admin.baseurl, api.baseurl)
        
    Returns:
        str: Environment URL
    """
    config = load_environment_config(env_code)
    url_key = f"env.{url_type}" if not url_type.startswith("env.") else url_type
    return config['env_config'].get(url_key, "")


def get_test_data(env_code="DEV", data_category="profile_data"):
    """
    Get test data for specific category
    
    Args:
        env_code: Environment code
        data_category: Category of test data
        
    Returns:
        dict: Test data for category
    """
    config = load_environment_config(env_code)
    return config['test_data'].get(data_category, {})


__all__ = [
    'load_environment_config',
    'get_test_user', 
    'get_environment_url',
    'get_test_data'
]