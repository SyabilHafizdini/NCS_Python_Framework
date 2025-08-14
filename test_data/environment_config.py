"""
Environment Configuration Module
Provides environment-specific configuration loading for different test environments.
"""

def load_environment_config(environment="DEV"):
    """Load configuration for the specified environment"""
    return {
        "base_url": "https://www.saucedemo.com/v1/",
        "timeout": 30,
        "environment": environment
    }

def get_test_user(user_type="standard"):
    """Get test user credentials based on user type"""
    users = {
        "standard": {"username": "standard_user", "password": "secret_sauce"},
        "locked_out": {"username": "locked_out_user", "password": "secret_sauce"},
        "problem": {"username": "problem_user", "password": "secret_sauce"},
        "performance": {"username": "performance_glitch_user", "password": "secret_sauce"}
    }
    return users.get(user_type, users["standard"])

def get_environment_url(environment="DEV"):
    """Get base URL for the specified environment"""
    urls = {
        "DEV": "https://www.saucedemo.com/v1/",
        "UAT": "https://www.saucedemo.com/v1/",
        "PROD": "https://www.saucedemo.com/v1/"
    }
    return urls.get(environment, urls["DEV"])