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
PatternEngine - Core pattern resolution engine

This class implements the exact locator resolution logic from the Java QAF framework,
transforming semantic field names into dynamic XPath locators through pattern templates
with variable substitution.
"""

import os
import json
from typing import Dict, List, Optional

from qaf.automation.core import get_bundle
from qaf.automation.util.property_util import PropertyUtil
from .case_converter import CaseConverter
from .field_parser import FieldParser
from .variable_substitution import VariableSubstitution


class PatternEngine:
    """
    Core pattern resolution engine implementing Java QAF equivalent functionality
    
    This class provides the main pattern locator functionality exactly matching
    the Java PatternLocator implementation:
    - Dynamic locator generation using configurable patterns
    - Variable substitution with placeholder replacement
    - Explicit locator checking with fallback to pattern generation
    - Support for multiple element types with consistent API
    """

    def __init__(self):
        """
        Initialize PatternEngine with configuration from bundle
        Matches Java PatternLocator constructor behavior
        """
        # Load configuration from bundle exactly matching Java implementation
        self.pattern_code = get_bundle().get_string('loc.pattern.code', 'loc.qaf')
        self.pattern_enabled = get_bundle().get_boolean('loc.pattern.enabled', True)
        
        # Initialize patterns dictionary
        self.patterns = {}
        
        # Load patterns from configuration file
        self._load_patterns()
    
    def _load_patterns(self) -> None:
        """
        Load XPath patterns from configuration file
        Matches Java PatternLocator pattern loading behavior
        """
        if not self.pattern_enabled:
            print("Pattern system disabled - loc.pattern.enabled=false")
            return
        
        # Get pattern file path from configuration
        pattern_file = get_bundle().get_string(
            'loc.pattern.file', 
            'resources/locators/locPattern.properties'
        )
        
        if not os.path.exists(pattern_file):
            print(f"Pattern file not found: {pattern_file}")
            return
        
        try:
            # Load patterns using PropertyUtil
            prop_util = PropertyUtil()
            prop_util.load(pattern_file)
            
            # Process patterns matching Java implementation
            for key in prop_util.keys():
                if key.startswith(f'{self.pattern_code}.pattern.'):
                    # Extract element type from key
                    # e.g., "loc.qaf.pattern.button" -> "button"
                    element_type = key.split('.')[-1]
                    
                    # Get pattern value and split on | for multiple patterns
                    pattern_value = prop_util.get_string(key)
                    if pattern_value:
                        # Split multiple XPath patterns separated by |
                        pattern_list = [pattern.strip() for pattern in pattern_value.split('|')]
                        self.patterns[element_type] = pattern_list
            
            print(f"Loaded {len(self.patterns)} pattern types from {pattern_file}")
            
        except Exception as e:
            print(f"Error loading patterns from {pattern_file}: {e}")
    
    def _check_hardcoded_locator(self, page: str, field_type: str, field_name: str) -> Optional[str]:
        """
        Check if hardcoded locator exists for the element
        Equivalent to Java checkLoc() method
        
        Args:
            page: Page name (e.g., "loginPage")
            field_type: Element type (e.g., "button", "input")
            field_name: Field name (e.g., "Submit", "Username")
            
        Returns:
            Hardcoded locator string if found, None otherwise
        """
        # Clear auto-generation variables (matching Java implementation)
        get_bundle().set_property("loc.auto.fieldName", "")
        get_bundle().set_property("loc.auto.fieldInstance", "")
        get_bundle().set_property("loc.auto.forValue", "")
        get_bundle().set_property("loc.auto.fieldValue", "")
        
        # Generate camelCase locator name matching Java implementation
        # Exact replication of Java: CaseUtils.toCamelCase(argPageName.replaceAll("[^a-zA-Z0-9]", " "), false, ' ')
        import re
        page_clean = re.sub(r'[^a-zA-Z0-9]', ' ', page)
        field_type_clean = re.sub(r'[^a-zA-Z0-9]', ' ', field_type.replace("d365_", ""))
        field_name_clean = re.sub(r'[^a-zA-Z0-9]', ' ', field_name)
        
        page_camel = CaseConverter.to_camel_case_java_exact(page_clean, False)
        field_type_camel = CaseConverter.to_camel_case_java_exact(field_type_clean, False)
        field_name_camel = CaseConverter.to_camel_case_java_exact(field_name_clean, False)
        
        locator_name = f"{self.pattern_code}.{page_camel}.{field_type_camel}.{field_name_camel}"
        
        # Check for explicit locator in bundle
        locator_value = get_bundle().get_string(locator_name)
        
        # If no explicit locator found or value is too short, return None for auto-generation
        if not locator_value or locator_value == locator_name or len(locator_value) < 5:
            return None
        
        return locator_value
    
    def _check_alternative_locator_names(self, page: str, field_type: str, field_name: str) -> Optional[str]:
        """
        Check alternative naming patterns for locators
        Matches Java implementation's fallback locator checking
        
        Args:
            page: Page name
            field_type: Element type 
            field_name: Field name
            
        Returns:
            Alternative locator if found, None otherwise
        """
        # Alternative naming patterns to try
        alt_keys = [
            f"{page}.{field_name}",
            f"{field_name}.{field_type}",
            f"{field_name}"
        ]
        
        for alt_key in alt_keys:
            alt_locator = get_bundle().get_string(alt_key)
            if alt_locator and alt_locator != alt_key and len(alt_locator) >= 5:
                return alt_locator
        
        return None
    
    def _generate_dynamic_locator(self, field_type: str, field_name: str, field_value: str = None) -> Optional[str]:
        """
        Generate dynamic locator using patterns
        Equivalent to Java generateLoc() method
        
        Args:
            field_type: Element type for pattern lookup
            field_name: Field name for variable substitution
            field_value: Optional field value for substitution
            
        Returns:
            QAF JSON format locator string or None if no patterns available
        """
        # Extract field name and instance from bracketed notation
        clean_field_name = FieldParser.extract_field_name(field_name)
        field_instance = FieldParser.extract_instance(field_name)
        
        # Set field variables for pattern substitution (matching Java implementation)
        get_bundle().set_property("loc.auto.fieldName", clean_field_name)
        get_bundle().set_property("loc.auto.fieldInstance", field_instance)
        
        # Get pattern template for element type
        pattern_key = f"{self.pattern_code}.pattern.{field_type}"
        
        if field_type not in self.patterns:
            print(f"=====>[ERROR] => [Locator Pattern '{pattern_key}' not available]")
            return None
        
        pattern_templates = self.patterns[field_type]
        
        if not pattern_templates:
            print(f"=====>[ERROR] => [Locator Pattern '{pattern_key}' not available]")
            return None
        
        # Process pattern template with variable substitution
        pattern_string = " | ".join(pattern_templates)
        
        # Generate final locator with QAF JSON format
        qaf_locator = VariableSubstitution.process_pattern_template(
            pattern_string, 
            clean_field_name, 
            field_instance, 
            field_value, 
            None,  # for_value will be set later if needed
            field_type
        )
        
        return qaf_locator
    
    def _get_locator(self, page: str, field_type: str, field_name: str, field_value: str = None) -> str:
        """
        Core method that implements the locator resolution logic:
        1. Check for hardcoded locator
        2. Check alternative locator naming patterns  
        3. Generate dynamic locator if no hardcoded version exists
        4. Return appropriate locator string
        
        Args:
            page: Page name for locator context
            field_type: Element type (button, input, etc.)
            field_name: Field name to locate
            field_value: Optional field value for patterns
            
        Returns:
            Locator string (either hardcoded or generated)
        """
        # Step 1: Check for primary hardcoded locator
        hardcoded_locator = self._check_hardcoded_locator(page, field_type, field_name)
        if hardcoded_locator:
            return hardcoded_locator
        
        # Step 2: Check alternative locator naming patterns
        alternative_locator = self._check_alternative_locator_names(page, field_type, field_name)
        if alternative_locator:
            return alternative_locator
        
        # Step 3: Generate dynamic locator using patterns
        dynamic_locator = self._generate_dynamic_locator(field_type, field_name, field_value)
        if dynamic_locator:
            return dynamic_locator
        
        # Step 4: Ultimate fallback - return a basic XPath pattern
        clean_field_name = FieldParser.extract_field_name(field_name)
        return f"xpath=//*[contains(text(),'{clean_field_name}')]"
    
    def _generate_property_key(self, page: str, field_type: str, field_name: str) -> str:
        """
        Generate property key using camelCase conversion
        Matches exact Java implementation logic
        
        Args:
            page: Page name
            field_type: Element type
            field_name: Field name
            
        Returns:
            Generated property key in format: {pattern_code}.{page}.{type}.{field}
        """
        import re
        
        # Clean inputs by removing non-alphanumeric characters (matching Java regex)
        page_clean = re.sub(r'[^a-zA-Z0-9]', ' ', page)
        field_type_clean = re.sub(r'[^a-zA-Z0-9]', ' ', field_type.replace("d365_", ""))
        field_name_clean = re.sub(r'[^a-zA-Z0-9]', ' ', field_name)
        
        # Convert to camelCase using exact Java behavior
        page_camel = CaseConverter.to_camel_case_java_exact(page_clean, False)
        field_type_camel = CaseConverter.to_camel_case_java_exact(field_type_clean, False)
        field_name_camel = CaseConverter.to_camel_case_java_exact(field_name_clean, False)
        
        return f"{self.pattern_code}.{page_camel}.{field_type_camel}.{field_name_camel}"
    
    def resolve_locator(self, page: str, field_type: str, field_name: str, field_value: str = None) -> str:
        """
        Public method to resolve locator with comprehensive logging
        
        Args:
            page: Page name for locator context
            field_type: Element type
            field_name: Field name to locate  
            field_value: Optional field value for patterns
            
        Returns:
            Resolved locator string
        """
        try:
            result = self._get_locator(page, field_type, field_name, field_value)
            
            # Log successful resolution
            print(f"Pattern locator resolved: {page}.{field_type}.{field_name} -> {result[:100]}...")
            
            return result
            
        except Exception as e:
            print(f"Error resolving pattern locator for {page}.{field_type}.{field_name}: {e}")
            
            # Return fallback locator
            clean_field_name = FieldParser.extract_field_name(field_name)
            fallback = f"xpath=//*[contains(text(),'{clean_field_name}')]"
            print(f"Using fallback locator: {fallback}")
            
            return fallback
    
    def get_pattern_types(self) -> List[str]:
        """Get list of available pattern types"""
        return list(self.patterns.keys())
    
    def is_pattern_enabled(self) -> bool:
        """Check if pattern locator system is enabled"""
        return self.pattern_enabled
    
    def get_pattern_code(self) -> str:
        """Get the pattern code prefix"""
        return self.pattern_code


# Singleton instance for global access
_pattern_engine_instance = None


def get_pattern_engine() -> PatternEngine:
    """Get singleton instance of PatternEngine"""
    global _pattern_engine_instance
    if _pattern_engine_instance is None:
        _pattern_engine_instance = PatternEngine()
    return _pattern_engine_instance