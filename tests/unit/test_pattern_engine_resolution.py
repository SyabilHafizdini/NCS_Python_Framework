"""
Unit tests for PatternEngine core locator resolution methods - FIXED VERSION
Testing _check_hardcoded_locator, _generate_dynamic_locator, _get_locator methods
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from qaf.automation.ui.util.pattern_engine import PatternEngine


class TestPatternEngineResolution(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Reset singleton for clean tests
        import qaf.automation.ui.util.pattern_engine
        qaf.automation.ui.util.pattern_engine._pattern_engine_instance = None
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_generate_property_key(self, mock_exists, mock_get_bundle):
        """Test _generate_property_key method"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.return_value = 'loc.qaf'
        mock_bundle.get_boolean.return_value = True
        mock_get_bundle.return_value = mock_bundle
        
        # Mock file doesn't exist
        mock_exists.return_value = False
        
        # Create PatternEngine instance
        engine = PatternEngine()
        
        # Test property key generation
        result = engine._generate_property_key("login-page", "d365_button", "submit@button")
        
        # Should clean special characters and convert to camelCase
        expected = "loc.qaf.loginPage.button.submitButton"
        self.assertEqual(result, expected)
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_get_locator_ultimate_fallback(self, mock_exists, mock_get_bundle):
        """Test _get_locator ultimate fallback when no patterns available"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        def mock_get_string(key, default=None):
            values = {
                'loc.pattern.code': 'loc.qaf',
                'loc.pattern.file': 'test.properties'
            }
            return values.get(key, key if default is None else default)
        mock_bundle.get_string.side_effect = mock_get_string
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        
        # Mock file doesn't exist
        mock_exists.return_value = False
        
        # Create PatternEngine instance (no patterns)
        engine = PatternEngine()
        
        # Test locator resolution with no hardcoded or patterns
        result = engine._get_locator("loginPage", "button", "Submit")
        
        # Should return basic XPath fallback
        self.assertEqual(result, "xpath=//*[contains(text(),'Submit')]")
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_get_locator_pattern_fallback(self, mock_exists, mock_get_bundle):
        """Test _get_locator falls back to pattern generation"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        def mock_get_string(key, default=None):
            values = {
                'loc.pattern.code': 'loc.qaf',
                'loc.pattern.file': 'test.properties'
            }
            return values.get(key, key if default is None else default)
        mock_bundle.get_string.side_effect = mock_get_string
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        
        # Mock file doesn't exist
        mock_exists.return_value = False
        
        # Create PatternEngine instance with patterns
        engine = PatternEngine()
        engine.patterns = {
            'button': ['xpath=//button[text()="${loc.auto.fieldName}"]']
        }
        
        # Test locator resolution (no hardcoded locator)
        result = engine._get_locator("loginPage", "button", "Submit")
        
        # Should return pattern-generated locator
        self.assertIn('"locator":', result)
        self.assertIn('Submit', result)
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_generate_dynamic_locator_success(self, mock_exists, mock_get_bundle):
        """Test _generate_dynamic_locator with available patterns"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        def mock_get_string(key, default=None):
            values = {
                'loc.pattern.code': 'loc.qaf',
                'loc.pattern.file': 'test.properties'
            }
            return values.get(key, key if default is None else default)
        mock_bundle.get_string.side_effect = mock_get_string
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        
        # Mock file doesn't exist
        mock_exists.return_value = False
        
        # Create PatternEngine instance and set up patterns manually
        engine = PatternEngine()
        engine.patterns = {
            'button': [
                'xpath=//button[text()="${loc.auto.fieldName}"]',
                'xpath=//input[@value="${loc.auto.fieldName}"]'
            ]
        }
        
        # Test dynamic locator generation
        result = engine._generate_dynamic_locator("button", "Submit", "submit-btn")
        
        # Should return QAF JSON format
        self.assertIsNotNone(result)
        self.assertIn('"locator":', result)
        self.assertIn('"desc":', result)
        self.assertIn('Submit', result)
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_generate_dynamic_locator_no_patterns(self, mock_exists, mock_get_bundle):
        """Test _generate_dynamic_locator when no patterns available"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        def mock_get_string(key, default=None):
            values = {
                'loc.pattern.code': 'loc.qaf',
                'loc.pattern.file': 'test.properties'
            }
            return values.get(key, key if default is None else default)
        mock_bundle.get_string.side_effect = mock_get_string
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        
        # Mock file doesn't exist
        mock_exists.return_value = False
        
        # Create PatternEngine instance (no patterns loaded)
        engine = PatternEngine()
        
        # Test when no patterns available for element type
        result = engine._generate_dynamic_locator("nonexistent", "Submit")
        
        # Should return None
        self.assertIsNone(result)
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_check_alternative_locator_names(self, mock_exists, mock_get_bundle):
        """Test _check_alternative_locator_names method"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        def mock_get_string(key, default=None):
            values = {
                'loc.pattern.code': 'loc.qaf',
                'loc.pattern.file': 'test.properties',
                'Submit.button': 'xpath=//button[@name="submit"]',  # Alternative pattern
                'Submit': 'xpath=//input[@value="Submit"]'  # Another alternative
            }
            return values.get(key, key if default is None else default)
        mock_bundle.get_string.side_effect = mock_get_string
        mock_bundle.get_boolean.return_value = True
        mock_get_bundle.return_value = mock_bundle
        
        # Mock file doesn't exist
        mock_exists.return_value = False
        
        # Create PatternEngine instance
        engine = PatternEngine()
        
        # Test alternative locator resolution
        result = engine._check_alternative_locator_names("loginPage", "button", "Submit")
        
        # Should find the Submit.button alternative
        self.assertEqual(result, 'xpath=//button[@name="submit"]')


if __name__ == '__main__':
    unittest.main()