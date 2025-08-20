"""
Unit tests for Web.py reflection-based step definitions
Testing the reflection-based pattern locator functions
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.automation_library.Web import click_element_pattern_reflection, input_text_pattern_reflection, WebError


class TestWebReflection(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Reset singleton for clean tests
        import qaf.automation.ui.util.pattern_engine
        qaf.automation.ui.util.pattern_engine._pattern_engine_instance = None
    
    @patch('tests.automation_library.Web._get_driver')
    @patch('tests.automation_library.Web._attach_screenshot')
    @patch('tests.automation_library.Web.allure')
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_click_element_pattern_reflection_success(self, mock_exists, mock_get_bundle, 
                                                     mock_allure, mock_attach_screenshot, mock_get_driver):
        """Test successful reflection-based click action"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf',
            'loc.pattern.file': 'resources/locators/locPattern.properties'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = True
        
        # Mock driver and element
        mock_element = MagicMock()
        mock_driver = MagicMock()
        mock_driver.find_element.return_value = mock_element
        mock_get_driver.return_value = mock_driver
        
        # Mock allure
        mock_allure.attach = MagicMock()
        mock_allure.attachment_type.TEXT = "text/plain"
        
        # Test reflection-based click
        click_element_pattern_reflection("button", "Submit", "loginPage")
        
        # Verify element was clicked
        mock_element.click.assert_called_once()
        mock_attach_screenshot.assert_called_once()
        
        # Verify allure logging for method resolution
        mock_allure.attach.assert_any_call(
            "Found function button in PatternEngine!", 
            name="Method Resolution Success", 
            attachment_type="text/plain"
        )
    
    @patch('tests.automation_library.Web._get_driver')
    @patch('tests.automation_library.Web._attach_screenshot')  
    @patch('tests.automation_library.Web.allure')
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_click_element_pattern_reflection_invalid_method(self, mock_exists, mock_get_bundle,
                                                           mock_allure, mock_attach_screenshot, mock_get_driver):
        """Test reflection-based click with invalid method name"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        # Mock allure
        mock_allure.attach = MagicMock()
        mock_allure.attachment_type.TEXT = "text/plain"
        
        # Test with invalid element type
        with self.assertRaises(WebError) as context:
            click_element_pattern_reflection("nonexistent", "Submit", "loginPage")
        
        # Verify error message contains NoSuchMethodException
        self.assertIn("NoSuchMethodException", str(context.exception))
        self.assertIn("nonexistent", str(context.exception))
    
    @patch('tests.automation_library.Web._get_driver')
    @patch('tests.automation_library.Web._attach_screenshot')
    @patch('tests.automation_library.Web.allure')
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_click_element_pattern_reflection_with_page_context(self, mock_exists, mock_get_bundle,
                                                              mock_allure, mock_attach_screenshot, mock_get_driver):
        """Test reflection-based click using page context"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        # Mock driver and element
        mock_element = MagicMock()
        mock_driver = MagicMock()
        mock_driver.find_element.return_value = mock_element
        mock_get_driver.return_value = mock_driver
        
        # Mock allure
        mock_allure.attach = MagicMock()
        mock_allure.attachment_type.TEXT = "text/plain"
        
        # Set page context
        import tests.automation_library.Web as web_module
        web_module._page_context['current_page'] = 'dashboardPage'
        
        # Test without explicit page parameter (should use context)
        click_element_pattern_reflection("link", "Logout")
        
        # Verify element was clicked
        mock_element.click.assert_called_once()
    
    @patch('tests.automation_library.Web.get_pattern_engine')
    @patch('tests.automation_library.Web.allure')
    def test_click_element_pattern_reflection_qaf_unavailable(self, mock_allure, mock_get_pattern_engine):
        """Test behavior when QAF PatternEngine is unavailable"""
        # Mock PatternEngine as unavailable
        mock_get_pattern_engine.return_value = None
        
        # Mock allure
        mock_allure.attach = MagicMock()
        mock_allure.attachment_type.TEXT = "text/plain"
        
        # Test should raise WebError
        with self.assertRaises(WebError) as context:
            click_element_pattern_reflection("button", "Submit", "loginPage")
        
        self.assertIn("PatternEngine system not available", str(context.exception))
    
    @patch('tests.automation_library.Web._get_driver')
    @patch('tests.automation_library.Web._attach_screenshot')
    @patch('tests.automation_library.Web.allure')
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_input_text_pattern_reflection_success(self, mock_exists, mock_get_bundle,
                                                  mock_allure, mock_attach_screenshot, mock_get_driver):
        """Test successful reflection-based input text action"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf',
            'loc.pattern.file': 'resources/locators/locPattern.properties'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = True
        
        # Mock driver and element
        mock_element = MagicMock()
        mock_driver = MagicMock()
        mock_driver.find_element.return_value = mock_element
        mock_get_driver.return_value = mock_driver
        
        # Mock allure
        mock_allure.attach = MagicMock()
        mock_allure.attachment_type.TEXT = "text/plain"
        
        # Test reflection-based input text
        input_text_pattern_reflection("test_username", "Username", "loginPage")
        
        # Verify element actions
        mock_element.clear.assert_called_once()
        mock_element.send_keys.assert_called_once_with("test_username")
        mock_attach_screenshot.assert_called_once()
        
        # Verify allure logging for method resolution
        mock_allure.attach.assert_any_call(
            "Found function input in PatternEngine!", 
            name="Method Resolution Success", 
            attachment_type="text/plain"
        )


if __name__ == '__main__':
    unittest.main()