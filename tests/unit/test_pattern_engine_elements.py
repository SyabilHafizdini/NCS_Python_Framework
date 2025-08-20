"""
Unit tests for PatternEngine element type methods
Testing the 15 most common element type methods
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from qaf.automation.ui.util.pattern_engine import PatternEngine


class TestPatternEngineElements(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Reset singleton for clean tests
        import qaf.automation.ui.util.pattern_engine
        qaf.automation.ui.util.pattern_engine._pattern_engine_instance = None
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_button_element_method(self, mock_exists, mock_get_bundle):
        """Test button() element method"""
        # Mock setup
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf',
            'loc.pattern.file': 'test.properties'
        }.get(key, key if default is None else default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        # Create engine
        engine = PatternEngine()
        
        # Test button method
        result = engine.button("loginPage", "Submit")
        
        # Should return fallback locator
        self.assertEqual(result, "xpath=//*[contains(text(),'Submit')]")
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_input_element_method(self, mock_exists, mock_get_bundle):
        """Test input() element method"""
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf',
            'loc.pattern.file': 'test.properties'
        }.get(key, key if default is None else default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        engine = PatternEngine()
        result = engine.input("loginPage", "Username")
        
        self.assertEqual(result, "xpath=//*[contains(text(),'Username')]")
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_link_element_method(self, mock_exists, mock_get_bundle):
        """Test link() element method"""
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, key if default is None else default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        engine = PatternEngine()
        result = engine.link("homePage", "Contact Us")
        
        self.assertEqual(result, "xpath=//*[contains(text(),'Contact Us')]")
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_checkbox_element_method(self, mock_exists, mock_get_bundle):
        """Test checkbox() element method"""
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, key if default is None else default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        engine = PatternEngine()
        result = engine.checkbox("registrationPage", "Terms")
        
        self.assertEqual(result, "xpath=//*[contains(text(),'Terms')]")
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_select_element_method(self, mock_exists, mock_get_bundle):
        """Test select() element method"""
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, key if default is None else default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        engine = PatternEngine()
        result = engine.select("profilePage", "Country")
        
        self.assertEqual(result, "xpath=//*[contains(text(),'Country')]")
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_all_15_element_methods_exist(self, mock_exists, mock_get_bundle):
        """Test that all 15 element methods exist and are callable"""
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, key if default is None else default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        engine = PatternEngine()
        
        # List of expected element methods
        expected_methods = [
            'button', 'input', 'link', 'checkbox', 'radio', 'select', 
            'textarea', 'label', 'text', 'table', 'image', 'div', 
            'span', 'form', 'element'
        ]
        
        # Test each method exists and is callable
        for method_name in expected_methods:
            with self.subTest(method=method_name):
                self.assertTrue(hasattr(engine, method_name))
                method = getattr(engine, method_name)
                self.assertTrue(callable(method))
                
                # Test method can be called
                result = method("testPage", "TestField")
                self.assertIsNotNone(result)
                self.assertIsInstance(result, str)
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_element_method_with_field_value(self, mock_exists, mock_get_bundle):
        """Test element methods with optional field_value parameter"""
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, key if default is None else default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        engine = PatternEngine()
        
        # Test with field_value parameter
        result = engine.button("loginPage", "Submit", "login-btn")
        self.assertEqual(result, "xpath=//*[contains(text(),'Submit')]")
        
        # Test without field_value parameter
        result = engine.button("loginPage", "Submit")
        self.assertEqual(result, "xpath=//*[contains(text(),'Submit')]")
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_element_method_with_patterns(self, mock_exists, mock_get_bundle):
        """Test element methods when patterns are available"""
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, key if default is None else default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        engine = PatternEngine()
        
        # Add patterns manually
        engine.patterns = {
            'button': ['xpath=//button[text()="${loc.auto.fieldName}"]'],
            'input': ['xpath=//input[@placeholder="${loc.auto.fieldName}"]']
        }
        
        # Test button with pattern
        result = engine.button("loginPage", "Submit")
        self.assertIn('"locator":', result)  # Should return QAF JSON format
        self.assertIn('Submit', result)
        
        # Test input with pattern
        result = engine.input("loginPage", "Username")
        self.assertIn('"locator":', result)
        self.assertIn('Username', result)


if __name__ == '__main__':
    unittest.main()