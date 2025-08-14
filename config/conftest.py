"""
Pytest configuration for QAF framework
"""
import pytest

def pytest_configure(config):
    """Configure pytest with QAF step definitions"""
    try:
        # Manually register steps after pytest is initialized
        from qaf.automation.bdd2.step_registry import register_steps
        register_steps()
    except Exception as e:
        print(f"Warning: Could not register QAF steps: {e}")

# Register custom markers
def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "pattern_locator: mark test as pattern locator test")  
    config.addinivalue_line("markers", "accessibility: mark test as accessibility test")
    config.addinivalue_line("markers", "pattern_demo: mark test as pattern demo")
    config.addinivalue_line("markers", "web: mark test as web test")
    config.addinivalue_line("markers", "saucedemo: mark test as saucedemo test")