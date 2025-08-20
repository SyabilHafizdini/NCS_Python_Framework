"""
Unit tests for FieldParser utility class
Testing field name and instance extraction from bracketed notation
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from qaf.automation.ui.util.field_parser import FieldParser, field_name_check, field_instance_check


class TestFieldParser(unittest.TestCase):
    
    def test_extract_field_name_with_instance(self):
        """Test field name extraction with instance notation"""
        test_cases = [
            ("Submit[2]", "Submit"),
            ("Login[1]", "Login"),
            ("Button[5]", "Button"),
            ("CancelButton[3]", "CancelButton"),
            ("SaveAndContinue[10]", "SaveAndContinue")
        ]
        
        for input_field, expected_name in test_cases:
            result = FieldParser.extract_field_name(input_field)
            self.assertEqual(result, expected_name, f"Failed for input: {input_field}")
    
    def test_extract_field_name_without_instance(self):
        """Test field name extraction without instance notation"""
        test_cases = [
            ("Submit", "Submit"),
            ("Login", "Login"),
            ("Button", "Button"),
            ("CancelButton", "CancelButton"),
            ("SaveAndContinue", "SaveAndContinue")
        ]
        
        for input_field, expected_name in test_cases:
            result = FieldParser.extract_field_name(input_field)
            self.assertEqual(result, expected_name, f"Failed for input: {input_field}")
    
    def test_extract_instance_with_notation(self):
        """Test instance extraction with bracketed notation"""
        test_cases = [
            ("Submit[2]", "2"),
            ("Login[1]", "1"),
            ("Button[5]", "5"),
            ("CancelButton[3]", "3"),
            ("SaveAndContinue[10]", "10")
        ]
        
        for input_field, expected_instance in test_cases:
            result = FieldParser.extract_instance(input_field)
            self.assertEqual(result, expected_instance, f"Failed for input: {input_field}")
    
    def test_extract_instance_without_notation(self):
        """Test instance extraction defaults to '1' without notation"""
        test_cases = [
            ("Submit", "1"),
            ("Login", "1"),
            ("Button", "1"),
            ("CancelButton", "1"),
            ("SaveAndContinue", "1")
        ]
        
        for input_field, expected_instance in test_cases:
            result = FieldParser.extract_instance(input_field)
            self.assertEqual(result, expected_instance, f"Failed for input: {input_field}")
    
    def test_parse_field_complete(self):
        """Test complete field parsing returning both name and instance"""
        test_cases = [
            ("Submit[2]", ("Submit", "2")),
            ("Login", ("Login", "1")),
            ("Button[5]", ("Button", "5")),
            ("CancelButton", ("CancelButton", "1"))
        ]
        
        for input_field, expected_tuple in test_cases:
            result = FieldParser.parse_field(input_field)
            self.assertEqual(result, expected_tuple, f"Failed for input: {input_field}")
    
    def test_edge_cases(self):
        """Test edge cases and invalid inputs"""
        # Empty string
        self.assertEqual(FieldParser.extract_field_name(""), "")
        self.assertEqual(FieldParser.extract_instance(""), "1")
        
        # None input
        self.assertEqual(FieldParser.extract_field_name(None), "")
        self.assertEqual(FieldParser.extract_instance(None), "1")
        
        # Whitespace
        self.assertEqual(FieldParser.extract_field_name("  Submit[2]  "), "Submit")
        self.assertEqual(FieldParser.extract_instance("  Submit[2]  "), "2")
    
    def test_invalid_bracket_notation(self):
        """Test handling of invalid bracket notation"""
        # Missing closing bracket
        self.assertEqual(FieldParser.extract_field_name("Submit[2"), "Submit[2")
        self.assertEqual(FieldParser.extract_instance("Submit[2"), "1")
        
        # Missing opening bracket
        self.assertEqual(FieldParser.extract_field_name("Submit2]"), "Submit2]")
        self.assertEqual(FieldParser.extract_instance("Submit2]"), "1")
        
        # Non-numeric instance
        self.assertEqual(FieldParser.extract_field_name("Submit[abc]"), "Submit[abc]")
        self.assertEqual(FieldParser.extract_instance("Submit[abc]"), "1")
        
        # Empty brackets
        self.assertEqual(FieldParser.extract_field_name("Submit[]"), "Submit[]")
        self.assertEqual(FieldParser.extract_instance("Submit[]"), "1")
    
    def test_has_instance_notation(self):
        """Test detection of instance notation"""
        # Valid instance notation
        self.assertTrue(FieldParser.has_instance_notation("Submit[2]"))
        self.assertTrue(FieldParser.has_instance_notation("Login[1]"))
        self.assertTrue(FieldParser.has_instance_notation("Button[10]"))
        
        # No instance notation
        self.assertFalse(FieldParser.has_instance_notation("Submit"))
        self.assertFalse(FieldParser.has_instance_notation("Login"))
        
        # Invalid notation
        self.assertFalse(FieldParser.has_instance_notation("Submit[2"))
        self.assertFalse(FieldParser.has_instance_notation("Submit2]"))
        self.assertFalse(FieldParser.has_instance_notation("Submit[abc]"))
        self.assertFalse(FieldParser.has_instance_notation("Submit[]"))
        
        # Empty/None
        self.assertFalse(FieldParser.has_instance_notation(""))
        self.assertFalse(FieldParser.has_instance_notation(None))
    
    def test_validate_field_name(self):
        """Test field name validation"""
        # Valid field names
        self.assertTrue(FieldParser.validate_field_name("Submit"))
        self.assertTrue(FieldParser.validate_field_name("Submit[2]"))
        self.assertTrue(FieldParser.validate_field_name("LoginButton"))
        
        # Invalid field names
        self.assertFalse(FieldParser.validate_field_name(""))
        self.assertFalse(FieldParser.validate_field_name(None))
        self.assertFalse(FieldParser.validate_field_name("   "))
    
    def test_convenience_functions(self):
        """Test convenience functions match class methods"""
        self.assertEqual(field_name_check("Submit[2]"), "Submit")
        self.assertEqual(field_instance_check("Submit[2]"), "2")
        self.assertEqual(field_name_check("Login"), "Login")
        self.assertEqual(field_instance_check("Login"), "1")
    
    def test_numeric_field_names(self):
        """Test field names that contain numbers"""
        test_cases = [
            ("Button1[2]", "Button1", "2"),
            ("Field123", "Field123", "1"),
            ("Test2Button[5]", "Test2Button", "5")
        ]
        
        for input_field, expected_name, expected_instance in test_cases:
            name_result = FieldParser.extract_field_name(input_field)
            instance_result = FieldParser.extract_instance(input_field)
            self.assertEqual(name_result, expected_name, f"Name failed for: {input_field}")
            self.assertEqual(instance_result, expected_instance, f"Instance failed for: {input_field}")


if __name__ == '__main__':
    unittest.main()