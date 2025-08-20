"""
Unit tests for VariableSubstitution utility class
Testing pattern variable replacement and QAF JSON locator generation
"""

import unittest
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from qaf.automation.ui.util.variable_substitution import VariableSubstitution, substitute_pattern_variables, create_qaf_json_locator


class TestVariableSubstitution(unittest.TestCase):
    
    def test_basic_variable_substitution(self):
        """Test basic variable replacement"""
        template = "xpath=//button[text()='${loc.auto.fieldName}']"
        variables = {"${loc.auto.fieldName}": "Submit"}
        
        result = VariableSubstitution.substitute_variables(template, variables)
        expected = "xpath=//button[text()='Submit']"
        self.assertEqual(result, expected)
    
    def test_multiple_variable_substitution(self):
        """Test multiple variable replacement in single template"""
        template = "xpath=//input[@name='${loc.auto.fieldValue}' and @placeholder='${loc.auto.fieldName}']"
        variables = {
            "${loc.auto.fieldName}": "Username",
            "${loc.auto.fieldValue}": "username-field"
        }
        
        result = VariableSubstitution.substitute_variables(template, variables)
        expected = "xpath=//input[@name='username-field' and @placeholder='Username']"
        self.assertEqual(result, expected)
    
    def test_substitute_pattern_variables(self):
        """Test standard pattern variable substitution"""
        template = "xpath=//button[text()='${loc.auto.fieldName}' and @id='${loc.auto.fieldValue}']"
        
        result = VariableSubstitution.substitute_pattern_variables(
            template, "Submit", "1", "submit-btn", "submit-field"
        )
        expected = "xpath=//button[text()='Submit' and @id='submit-btn']"
        self.assertEqual(result, expected)
    
    def test_all_pattern_variables(self):
        """Test all pattern variables in one template"""
        template = ("xpath=//input[@name='${loc.auto.fieldName}' and @id='${loc.auto.fieldValue}' "
                   "and @for='${loc.auto.forValue}' and contains(@class,'instance-${loc.auto.fieldInstance}')]")
        
        result = VariableSubstitution.substitute_pattern_variables(
            template, "Username", "2", "username-input", "username-label"
        )
        expected = ("xpath=//input[@name='Username' and @id='username-input' "
                   "and @for='username-label' and contains(@class,'instance-2')]")
        self.assertEqual(result, expected)
    
    def test_create_qaf_json_locator(self):
        """Test QAF JSON locator generation"""
        patterns = [
            "xpath=//button[text()='Submit']",
            "xpath=//input[@type='submit' and @value='Submit']"
        ]
        
        result = VariableSubstitution.create_qaf_json_locator(patterns, "Submit", "button")
        
        # Parse result to verify structure
        parsed = json.loads(result)
        self.assertEqual(parsed["locator"], patterns)
        self.assertEqual(parsed["desc"], "Submit : [button] Field ")
    
    def test_parse_pattern_array(self):
        """Test parsing comma-separated pattern strings"""
        pattern_string = ("xpath=//button[text()='Submit'], "
                         "xpath=//input[@type='submit'], "
                         "id=submit-button")
        
        result = VariableSubstitution.parse_pattern_array(pattern_string)
        expected = [
            "xpath=//button[text()='Submit']",
            "xpath=//input[@type='submit']",
            "id=submit-button"
        ]
        self.assertEqual(result, expected)
    
    def test_parse_pattern_array_edge_cases(self):
        """Test edge cases for pattern array parsing"""
        # Empty string
        self.assertEqual(VariableSubstitution.parse_pattern_array(""), [])
        
        # Single pattern
        single = "xpath=//button[text()='Submit']"
        self.assertEqual(VariableSubstitution.parse_pattern_array(single), [single])
        
        # Patterns with extra whitespace
        messy = "  xpath=//button[text()='Submit']  ,   xpath=//input[@type='submit']  "
        expected = ["xpath=//button[text()='Submit']", "xpath=//input[@type='submit']"]
        self.assertEqual(VariableSubstitution.parse_pattern_array(messy), expected)
    
    def test_process_pattern_template_complete(self):
        """Test complete pattern processing flow"""
        pattern_template = ("xpath=//button[text()='${loc.auto.fieldName}'], "
                           "xpath=//input[@type='submit' and @value='${loc.auto.fieldName}']")
        
        result = VariableSubstitution.process_pattern_template(
            pattern_template, "Submit", "1", "submit-btn", None, "button"
        )
        
        # Parse result to verify
        parsed = json.loads(result)
        expected_patterns = [
            "xpath=//button[text()='Submit']",
            "xpath=//input[@type='submit' and @value='Submit']"
        ]
        
        self.assertEqual(parsed["locator"], expected_patterns)
        self.assertEqual(parsed["desc"], "Submit : [button] Field ")
    
    def test_extract_variables_from_template(self):
        """Test extraction of variable placeholders"""
        template = "xpath=//input[@name='${loc.auto.fieldName}' and @id='${loc.auto.fieldValue}']"
        
        result = VariableSubstitution.extract_variables_from_template(template)
        expected = ["${loc.auto.fieldName}", "${loc.auto.fieldValue}"]
        
        # Sort both lists for comparison since order might vary
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_validate_template_variables(self):
        """Test template variable validation"""
        # Valid template with known variables
        valid_template = "xpath=//button[text()='${loc.auto.fieldName}' and @id='${loc.auto.fieldValue}']"
        self.assertTrue(VariableSubstitution.validate_template_variables(valid_template))
        
        # Invalid template with unknown variable
        invalid_template = "xpath=//button[text()='${unknown.variable}']"
        self.assertFalse(VariableSubstitution.validate_template_variables(invalid_template))
        
        # Empty template
        self.assertTrue(VariableSubstitution.validate_template_variables(""))
        
        # Template with no variables
        no_vars = "xpath=//button[text()='Submit']"
        self.assertTrue(VariableSubstitution.validate_template_variables(no_vars))
    
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        # Empty template
        self.assertEqual(VariableSubstitution.substitute_variables("", {}), "")
        
        # None template
        self.assertEqual(VariableSubstitution.substitute_variables(None, {}), "")
        
        # Empty variables
        template = "xpath=//button[text()='${loc.auto.fieldName}']"
        result = VariableSubstitution.substitute_variables(template, {})
        self.assertEqual(result, template)  # Should remain unchanged
        
        # None variables
        result = VariableSubstitution.substitute_variables(template, None)
        self.assertEqual(result, template)  # Should remain unchanged
    
    def test_convenience_functions(self):
        """Test convenience functions"""
        # Test substitute_pattern_variables function
        template = "xpath=//button[text()='${loc.auto.fieldName}']"
        result = substitute_pattern_variables(template, "Submit")
        expected = "xpath=//button[text()='Submit']"
        self.assertEqual(result, expected)
        
        # Test create_qaf_json_locator function
        patterns = ["xpath=//button[text()='Submit']"]
        result = create_qaf_json_locator(patterns, "Submit", "button")
        parsed = json.loads(result)
        self.assertEqual(parsed["locator"], patterns)
        self.assertEqual(parsed["desc"], "Submit : [button] Field ")
    
    def test_variable_with_special_characters(self):
        """Test variable substitution with special characters"""
        template = "xpath=//button[text()='${loc.auto.fieldName}']"
        variables = {"${loc.auto.fieldName}": "Submit & Continue"}
        
        result = VariableSubstitution.substitute_variables(template, variables)
        expected = "xpath=//button[text()='Submit & Continue']"
        self.assertEqual(result, expected)
    
    def test_repeated_variable_substitution(self):
        """Test same variable appearing multiple times"""
        template = "xpath=//button[text()='${loc.auto.fieldName}' or @title='${loc.auto.fieldName}']"
        variables = {"${loc.auto.fieldName}": "Submit"}
        
        result = VariableSubstitution.substitute_variables(template, variables)
        expected = "xpath=//button[text()='Submit' or @title='Submit']"
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()