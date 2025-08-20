"""
Unit tests for CaseConverter utility class
Testing exact Java CaseUtils.toCamelCase equivalent behavior
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from qaf.automation.ui.util.case_converter import CaseConverter, to_camel_case, to_camel_case_java_exact


class TestCaseConverter(unittest.TestCase):
    
    def test_basic_camel_case_conversion(self):
        """Test basic camelCase conversion"""
        # Test with capitalize_first=False (default)
        self.assertEqual(CaseConverter.to_camel_case("hello world"), "helloWorld")
        self.assertEqual(CaseConverter.to_camel_case("test field name"), "testFieldName")
        self.assertEqual(CaseConverter.to_camel_case("login page"), "loginPage")
        
        # Test with capitalize_first=True
        self.assertEqual(CaseConverter.to_camel_case("hello world", True), "HelloWorld")
        self.assertEqual(CaseConverter.to_camel_case("test field name", True), "TestFieldName")
        self.assertEqual(CaseConverter.to_camel_case("login page", True), "LoginPage")
    
    def test_single_word(self):
        """Test single word conversion"""
        self.assertEqual(CaseConverter.to_camel_case("hello"), "hello")
        self.assertEqual(CaseConverter.to_camel_case("hello", True), "Hello")
        self.assertEqual(CaseConverter.to_camel_case("LOGIN"), "login")
        self.assertEqual(CaseConverter.to_camel_case("LOGIN", True), "Login")
    
    def test_empty_and_none_inputs(self):
        """Test edge cases with empty/None inputs"""
        self.assertEqual(CaseConverter.to_camel_case(""), "")
        self.assertEqual(CaseConverter.to_camel_case(None), "")
        self.assertEqual(CaseConverter.to_camel_case("   "), "")
    
    def test_java_exact_behavior(self):
        """Test exact Java CaseUtils.toCamelCase behavior"""
        # Test cases matching Java implementation
        self.assertEqual(CaseConverter.to_camel_case_java_exact("login_page"), "loginPage")
        self.assertEqual(CaseConverter.to_camel_case_java_exact("login-page"), "loginPage")
        self.assertEqual(CaseConverter.to_camel_case_java_exact("login.page"), "loginPage")
        self.assertEqual(CaseConverter.to_camel_case_java_exact("login@page"), "loginPage")
        
        # With capitalize_first=True
        self.assertEqual(CaseConverter.to_camel_case_java_exact("login_page", True), "LoginPage")
        self.assertEqual(CaseConverter.to_camel_case_java_exact("login-page", True), "LoginPage")
    
    def test_special_characters_removal(self):
        """Test removal of special characters"""
        test_cases = [
            ("field@name#test", "fieldNameTest"),
            ("button$value%data", "buttonValueData"),
            ("test!field*name", "testFieldName"),
            ("login&page(form)", "loginPageForm"),
            ("data[0].field", "data0Field")
        ]
        
        for input_text, expected in test_cases:
            result = CaseConverter.to_camel_case_java_exact(input_text)
            self.assertEqual(result, expected, f"Failed for input: {input_text}")
    
    def test_multiple_spaces_and_delimiters(self):
        """Test handling of multiple consecutive spaces/delimiters"""
        self.assertEqual(CaseConverter.to_camel_case_java_exact("login   page"), "loginPage")
        self.assertEqual(CaseConverter.to_camel_case_java_exact("test___field"), "testField")
        self.assertEqual(CaseConverter.to_camel_case_java_exact("button---name"), "buttonName")
    
    def test_numbers_in_text(self):
        """Test handling of numbers in field names"""
        self.assertEqual(CaseConverter.to_camel_case_java_exact("field1 name2"), "field1Name2")
        self.assertEqual(CaseConverter.to_camel_case_java_exact("test123 button"), "test123Button")
        self.assertEqual(CaseConverter.to_camel_case_java_exact("button 2 submit"), "button2Submit")
    
    def test_convenience_functions(self):
        """Test convenience functions"""
        self.assertEqual(to_camel_case("hello world"), "helloWorld")
        self.assertEqual(to_camel_case_java_exact("login_page"), "loginPage")
    
    def test_different_delimiters(self):
        """Test different delimiter characters"""
        self.assertEqual(CaseConverter.to_camel_case("hello_world", False, '_'), "helloWorld")
        self.assertEqual(CaseConverter.to_camel_case("hello-world", False, '-'), "helloWorld")
        self.assertEqual(CaseConverter.to_camel_case("hello.world", False, '.'), "helloWorld")


if __name__ == '__main__':
    unittest.main()