"""
Unit tests for label association functionality in PatternEngine
Testing label finding and forValue variable setting
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from qaf.automation.ui.util.pattern_engine import PatternEngine


class TestLabelAssociation(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Reset singleton for clean tests
        import qaf.automation.ui.util.pattern_engine
        qaf.automation.ui.util.pattern_engine._pattern_engine_instance = None
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    @patch('tests.automation_library.BrowserGlobal._get_driver')
    def test_find_label_association_success(self, mock_get_driver, mock_exists, mock_get_bundle):
        """Test successful label association finding"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        # Mock WebDriver and label element
        mock_label_element = MagicMock()
        mock_label_element.get_attribute.return_value = "username_input"
        
        mock_driver = MagicMock()
        mock_driver.find_elements.return_value = [mock_label_element]
        mock_get_driver.return_value = mock_driver
        
        # Create PatternEngine and test label association
        engine = PatternEngine()
        for_value = engine._find_label_association("Username")
        
        # Verify result
        self.assertEqual(for_value, "username_input")
        
        # Verify WebDriver was called with correct XPath
        mock_driver.find_elements.assert_called()
        call_args = mock_driver.find_elements.call_args_list
        self.assertTrue(any("Username" in str(args) for args in call_args))
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    @patch('tests.automation_library.BrowserGlobal._get_driver')
    def test_find_label_association_no_for_attribute(self, mock_get_driver, mock_exists, mock_get_bundle):
        """Test label found but no 'for' attribute"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        # Mock WebDriver and label element without 'for' attribute
        mock_label_element = MagicMock()
        mock_label_element.get_attribute.return_value = None  # No 'for' attribute
        
        mock_driver = MagicMock()
        mock_driver.find_elements.return_value = [mock_label_element]
        mock_get_driver.return_value = mock_driver
        
        # Create PatternEngine and test label association
        engine = PatternEngine()
        for_value = engine._find_label_association("Username")
        
        # Should return None when no 'for' attribute found
        self.assertIsNone(for_value)
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    @patch('tests.automation_library.BrowserGlobal._get_driver')
    def test_find_label_association_no_labels_found(self, mock_get_driver, mock_exists, mock_get_bundle):
        """Test when no label elements are found"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        # Mock WebDriver with no label elements found
        mock_driver = MagicMock()
        mock_driver.find_elements.return_value = []  # No labels found
        mock_get_driver.return_value = mock_driver
        
        # Create PatternEngine and test label association
        engine = PatternEngine()
        for_value = engine._find_label_association("NonexistentField")
        
        # Should return None when no labels found
        self.assertIsNone(for_value)
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_set_label_association_variable_success(self, mock_exists, mock_get_bundle):
        """Test setting forValue variable when label association found"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        # Create PatternEngine and mock the label finding
        engine = PatternEngine()
        with patch.object(engine, '_find_label_association', return_value="email_input"):
            result = engine._set_label_association_variable("Email")
        
        # Verify result and bundle property setting
        self.assertEqual(result, "email_input")
        mock_bundle.set_property.assert_called_with("loc.auto.forValue", "email_input")
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_set_label_association_variable_no_association(self, mock_exists, mock_get_bundle):
        """Test setting forValue variable when no label association found"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        # Create PatternEngine and mock the label finding to return None
        engine = PatternEngine()
        with patch.object(engine, '_find_label_association', return_value=None):
            result = engine._set_label_association_variable("UnknownField")
        
        # Verify empty result and bundle property clearing
        self.assertEqual(result, "")
        mock_bundle.set_property.assert_called_with("loc.auto.forValue", "")
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_label_association_integrated_in_locator_generation(self, mock_exists, mock_get_bundle):
        """Test that label association is called during locator generation"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_bundle.set_property = MagicMock()
        mock_get_bundle.return_value = mock_bundle
        mock_exists.return_value = False
        
        # Create PatternEngine with patterns
        engine = PatternEngine()
        engine.patterns = {
            'input': ['xpath=//input[@id="${loc.auto.forValue}"]']
        }
        
        # Mock the label association method
        with patch.object(engine, '_set_label_association_variable', return_value="user_email") as mock_set_label:
            result = engine.input("loginPage", "Email")
        
        # Verify label association was called
        mock_set_label.assert_called_once_with("Email")
        
        # Verify result contains the pattern
        self.assertIsNotNone(result)
        self.assertIn('"locator":', result)


if __name__ == '__main__':
    unittest.main()