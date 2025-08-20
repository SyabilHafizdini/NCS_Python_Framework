#  Copyright (c) 2022 Infostretch Corporation
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  #
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

"""
VariableSubstitution - Pattern placeholder replacement utility

This utility handles pattern variable substitution exactly matching 
the Java QAF framework implementation for generating dynamic locators.
"""

import json
import re
from typing import Dict, List, Any


class VariableSubstitution:
    """
    Utility class for pattern variable substitution matching Java QAF behavior
    """
    
    # Standard pattern variables matching Java implementation
    FIELD_NAME_VAR = "${loc.auto.fieldName}"
    FIELD_INSTANCE_VAR = "${loc.auto.fieldInstance}"
    FOR_VALUE_VAR = "${loc.auto.forValue}"
    FIELD_VALUE_VAR = "${loc.auto.fieldValue}"
    
    @staticmethod
    def substitute_variables(pattern_template: str, variables: Dict[str, str]) -> str:
        """
        Replace pattern variables with actual values
        
        Args:
            pattern_template: Template string containing variable placeholders
            variables: Dictionary mapping variable names to their values
            
        Returns:
            String with variables replaced by actual values
            
        Example:
            template = "xpath=//button[text()='${loc.auto.fieldName}']"
            variables = {"${loc.auto.fieldName}": "Submit"}
            result = "xpath=//button[text()='Submit']"
        """
        if not pattern_template:
            return ""
        
        if not variables:
            return pattern_template
        
        result = pattern_template
        
        # Replace each variable with its value
        for var_name, var_value in variables.items():
            if var_value is not None:
                result = result.replace(var_name, str(var_value))
        
        return result
    
    @staticmethod
    def substitute_pattern_variables(pattern_template: str, field_name: str, 
                                   field_instance: str = "1", field_value: str = None, 
                                   for_value: str = None) -> str:
        """
        Substitute standard pattern variables with provided values
        Matches the Java implementation's variable substitution logic
        
        Args:
            pattern_template: Template containing pattern variables
            field_name: Value to replace ${loc.auto.fieldName}
            field_instance: Value to replace ${loc.auto.fieldInstance} (default "1")
            field_value: Value to replace ${loc.auto.fieldValue}
            for_value: Value to replace ${loc.auto.forValue}
            
        Returns:
            Template with variables substituted
        """
        variables = {
            VariableSubstitution.FIELD_NAME_VAR: field_name or "",
            VariableSubstitution.FIELD_INSTANCE_VAR: field_instance or "1",
            VariableSubstitution.FIELD_VALUE_VAR: field_value or "",
            VariableSubstitution.FOR_VALUE_VAR: for_value or ""
        }
        
        return VariableSubstitution.substitute_variables(pattern_template, variables)
    
    @staticmethod
    def create_qaf_json_locator(locator_patterns: List[str], field_name: str, 
                               element_type: str) -> str:
        """
        Create QAF JSON format locator exactly matching Java implementation
        
        Format: {"locator":[...], "desc":"field_name : [element_type] Field "}
        
        Args:
            locator_patterns: List of XPath patterns (after variable substitution)
            field_name: Field name for description
            element_type: Element type for description
            
        Returns:
            JSON string in QAF format
        """
        qaf_locator = {
            "locator": locator_patterns,
            "desc": f"{field_name} : [{element_type}] Field "
        }
        
        return json.dumps(qaf_locator, separators=(',', ':'))
    
    @staticmethod
    def parse_pattern_array(pattern_string: str) -> List[str]:
        """
        Parse comma-separated pattern string into array
        Handles patterns like: "xpath=//button[...], xpath=//input[...]"
        
        Args:
            pattern_string: Comma-separated pattern string
            
        Returns:
            List of individual patterns
        """
        if not pattern_string:
            return []
        
        # Split on comma and clean up each pattern
        patterns = []
        for pattern in pattern_string.split(','):
            pattern = pattern.strip()
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    @staticmethod
    def process_pattern_template(pattern_template: str, field_name: str, 
                               field_instance: str = "1", field_value: str = None,
                               for_value: str = None, element_type: str = "element") -> str:
        """
        Complete pattern processing: parse, substitute variables, create QAF JSON
        This matches the complete flow in the Java generateLoc() method
        
        Args:
            pattern_template: Raw pattern template from properties
            field_name: Field name for substitution
            field_instance: Instance number for substitution
            field_value: Field value for substitution
            for_value: For attribute value for substitution
            element_type: Element type for JSON description
            
        Returns:
            QAF JSON format locator string
        """
        # Step 1: Parse pattern array
        pattern_array = VariableSubstitution.parse_pattern_array(pattern_template)
        
        if not pattern_array:
            return ""
        
        # Step 2: Substitute variables in each pattern
        substituted_patterns = []
        for pattern in pattern_array:
            substituted = VariableSubstitution.substitute_pattern_variables(
                pattern, field_name, field_instance, field_value, for_value
            )
            substituted_patterns.append(substituted)
        
        # Step 3: Create QAF JSON format
        return VariableSubstitution.create_qaf_json_locator(
            substituted_patterns, field_name, element_type
        )
    
    @staticmethod
    def extract_variables_from_template(pattern_template: str) -> List[str]:
        """
        Extract all variable placeholders from a pattern template
        
        Args:
            pattern_template: Template to analyze
            
        Returns:
            List of variable placeholders found in template
        """
        if not pattern_template:
            return []
        
        # Find all ${...} patterns
        variable_pattern = r'\$\{[^}]+\}'
        variables = re.findall(variable_pattern, pattern_template)
        
        return list(set(variables))  # Remove duplicates
    
    @staticmethod
    def validate_template_variables(pattern_template: str) -> bool:
        """
        Validate that template contains only known variable types
        
        Args:
            pattern_template: Template to validate
            
        Returns:
            True if all variables in template are known/supported
        """
        known_variables = {
            VariableSubstitution.FIELD_NAME_VAR,
            VariableSubstitution.FIELD_INSTANCE_VAR,
            VariableSubstitution.FOR_VALUE_VAR,
            VariableSubstitution.FIELD_VALUE_VAR
        }
        
        found_variables = VariableSubstitution.extract_variables_from_template(pattern_template)
        
        # Check if all found variables are in the known set
        for var in found_variables:
            if var not in known_variables:
                return False
        
        return True


# Convenience functions for common operations
def substitute_pattern_variables(pattern_template: str, field_name: str, 
                               field_instance: str = "1", field_value: str = None, 
                               for_value: str = None) -> str:
    """Convenience function for pattern variable substitution"""
    return VariableSubstitution.substitute_pattern_variables(
        pattern_template, field_name, field_instance, field_value, for_value
    )


def create_qaf_json_locator(locator_patterns: List[str], field_name: str, 
                           element_type: str) -> str:
    """Convenience function for QAF JSON locator creation"""
    return VariableSubstitution.create_qaf_json_locator(
        locator_patterns, field_name, element_type
    )