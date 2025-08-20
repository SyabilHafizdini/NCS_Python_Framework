"""
Unit tests for PatternEngine class
Testing PatternEngine initialization and configuration loading
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from qaf.automation.ui.util.pattern_engine import PatternEngine, get_pattern_engine


class TestPatternEngine(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Reset singleton for clean tests
        import qaf.automation.ui.util.pattern_engine
        qaf.automation.ui.util.pattern_engine._pattern_engine_instance = None
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_pattern_engine_initialization(self, mock_exists, mock_get_bundle):
        """Test PatternEngine initialization with mocked bundle"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf',
            'loc.pattern.file': 'resources/locators/locPattern.properties'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_get_bundle.return_value = mock_bundle
        
        # Mock file doesn't exist to skip pattern loading
        mock_exists.return_value = False
        
        # Create PatternEngine instance
        engine = PatternEngine()
        
        # Verify initialization
        self.assertEqual(engine.pattern_code, 'loc.qaf')
        self.assertTrue(engine.pattern_enabled)
        self.assertEqual(engine.patterns, {})
        
        # Verify bundle calls
        mock_bundle.get_string.assert_any_call('loc.pattern.code', 'loc.qaf')
        mock_bundle.get_boolean.assert_called_with('loc.pattern.enabled', True)
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    @patch('qaf.automation.ui.util.pattern_engine.PropertyUtil')
    def test_pattern_loading_success(self, mock_property_util_class, mock_exists, mock_get_bundle):
        """Test successful pattern loading from file"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf',
            'loc.pattern.file': 'test_patterns.properties'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_get_bundle.return_value = mock_bundle
        
        # Mock file exists
        mock_exists.return_value = True
        
        # Mock PropertyUtil
        mock_prop_util = MagicMock()
        mock_prop_util.keys.return_value = [
            'loc.qaf.pattern.button',
            'loc.qaf.pattern.input',
            'other.property'  # Should be ignored
        ]
        mock_prop_util.get_string.side_effect = lambda key: {
            'loc.qaf.pattern.button': 'xpath=//button[text()="${loc.auto.fieldName}"] | xpath=//input[@value="${loc.auto.fieldName}"]',
            'loc.qaf.pattern.input': 'xpath=//input[@placeholder="${loc.auto.fieldName}"]'
        }.get(key, '')
        
        mock_property_util_class.return_value = mock_prop_util
        
        # Create PatternEngine instance
        engine = PatternEngine()
        
        # Verify patterns were loaded
        self.assertIn('button', engine.patterns)
        self.assertIn('input', engine.patterns)
        self.assertEqual(len(engine.patterns), 2)
        
        # Verify button patterns (should be split on |)
        button_patterns = engine.patterns['button']
        self.assertEqual(len(button_patterns), 2)
        self.assertIn('xpath=//button[text()="${loc.auto.fieldName}"]', button_patterns)
        self.assertIn('xpath=//input[@value="${loc.auto.fieldName}"]', button_patterns)
        
        # Verify input patterns
        input_patterns = engine.patterns['input']
        self.assertEqual(len(input_patterns), 1)
        self.assertIn('xpath=//input[@placeholder="${loc.auto.fieldName}"]', input_patterns)
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    def test_pattern_engine_disabled(self, mock_get_bundle):
        """Test PatternEngine behavior when disabled"""
        # Mock bundle configuration with patterns disabled
        mock_bundle = MagicMock()
        mock_bundle.get_string.return_value = 'loc.qaf'
        mock_bundle.get_boolean.return_value = False  # Pattern system disabled
        mock_get_bundle.return_value = mock_bundle
        
        # Create PatternEngine instance
        engine = PatternEngine()
        
        # Verify disabled state
        self.assertFalse(engine.pattern_enabled)
        self.assertEqual(engine.patterns, {})
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    def test_pattern_file_not_found(self, mock_exists, mock_get_bundle):
        """Test handling when pattern file doesn't exist"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf',
            'loc.pattern.file': 'nonexistent.properties'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_get_bundle.return_value = mock_bundle
        
        # Mock file doesn't exist
        mock_exists.return_value = False
        
        # Create PatternEngine instance
        engine = PatternEngine()
        
        # Verify graceful handling
        self.assertEqual(engine.patterns, {})
        self.assertTrue(engine.pattern_enabled)
    
    def test_get_pattern_types(self):
        """Test get_pattern_types method"""
        with patch('qaf.automation.ui.util.pattern_engine.get_bundle'), \
             patch('qaf.automation.ui.util.pattern_engine.os.path.exists', return_value=False):
            
            engine = PatternEngine()
            engine.patterns = {'button': ['pattern1'], 'input': ['pattern2']}
            
            pattern_types = engine.get_pattern_types()
            self.assertEqual(set(pattern_types), {'button', 'input'})
    
    def test_is_pattern_enabled(self):
        """Test is_pattern_enabled method"""
        with patch('qaf.automation.ui.util.pattern_engine.get_bundle') as mock_get_bundle, \
             patch('qaf.automation.ui.util.pattern_engine.os.path.exists', return_value=False):
            
            # Test enabled
            mock_bundle = MagicMock()
            mock_bundle.get_boolean.return_value = True
            mock_get_bundle.return_value = mock_bundle
            
            engine = PatternEngine()
            self.assertTrue(engine.is_pattern_enabled())
            
            # Test disabled
            engine.pattern_enabled = False
            self.assertFalse(engine.is_pattern_enabled())
    
    def test_get_pattern_code(self):
        """Test get_pattern_code method"""
        with patch('qaf.automation.ui.util.pattern_engine.get_bundle') as mock_get_bundle, \
             patch('qaf.automation.ui.util.pattern_engine.os.path.exists', return_value=False):
            
            mock_bundle = MagicMock()
            mock_bundle.get_string.return_value = 'test.pattern'
            mock_get_bundle.return_value = mock_bundle
            
            engine = PatternEngine()
            self.assertEqual(engine.get_pattern_code(), 'test.pattern')
    
    def test_singleton_pattern(self):
        """Test that get_pattern_engine returns singleton instance"""
        with patch('qaf.automation.ui.util.pattern_engine.get_bundle'), \
             patch('qaf.automation.ui.util.pattern_engine.os.path.exists', return_value=False):
            
            # Get first instance
            engine1 = get_pattern_engine()
            
            # Get second instance
            engine2 = get_pattern_engine()
            
            # Should be the same instance
            self.assertIs(engine1, engine2)
    
    @patch('qaf.automation.ui.util.pattern_engine.get_bundle')
    @patch('qaf.automation.ui.util.pattern_engine.os.path.exists')
    @patch('qaf.automation.ui.util.pattern_engine.PropertyUtil')
    def test_pattern_loading_error_handling(self, mock_property_util_class, mock_exists, mock_get_bundle):
        """Test error handling during pattern loading"""
        # Mock bundle configuration
        mock_bundle = MagicMock()
        mock_bundle.get_string.side_effect = lambda key, default=None: {
            'loc.pattern.code': 'loc.qaf',
            'loc.pattern.file': 'error_file.properties'
        }.get(key, default)
        mock_bundle.get_boolean.return_value = True
        mock_get_bundle.return_value = mock_bundle
        
        # Mock file exists
        mock_exists.return_value = True
        
        # Mock PropertyUtil to raise exception
        mock_property_util_class.side_effect = Exception("File read error")
        
        # Create PatternEngine instance - should handle error gracefully
        engine = PatternEngine()
        
        # Verify graceful error handling
        self.assertEqual(engine.patterns, {})
        self.assertTrue(engine.pattern_enabled)


if __name__ == '__main__':
    unittest.main()