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

import json
import os
import re
from typing import Dict, List, Optional, Union

from qaf.automation.core import get_bundle
from qaf.automation.util.property_util import PropertyUtil


class PatternLocator:
    """
    Dynamic XPath Pattern Locator Generator
    
    This class implements the pattern-based locator system similar to the Java QAF framework.
    It generates dynamic XPath locators at runtime using configurable patterns with placeholder variables.
    """

    def __init__(self):
        self.pattern_code = get_bundle().get_string('loc.pattern.code', 'loc.qaf')
        self.pattern_enabled = get_bundle().get_boolean('loc.pattern.enabled', True)
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict[str, List[str]]:
        """Load XPath patterns from configuration file"""
        patterns = {}
        if not self.pattern_enabled:
            return patterns

        pattern_file = get_bundle().get_string('loc.pattern.file', 'resources/locators/loc_pattern.properties')
        
        if os.path.exists(pattern_file):
            prop_util = PropertyUtil()
            prop_util.load(pattern_file)
            
            for key, value in prop_util.items():
                if key.startswith(f'{self.pattern_code}.pattern.'):
                    element_type = key.split('.')[-1]
                    # Split multiple XPath patterns separated by |
                    pattern_list = [pattern.strip() for pattern in value.split('|')]
                    patterns[element_type] = pattern_list
        
        return patterns

    def _check_hardcoded_locator(self, page: str, field_type: str, field_name: str) -> Optional[str]:
        """Check if hardcoded locator exists for the element"""
        locator_key = f"{page}.{field_name}.{field_type}"
        hardcoded_locator = get_bundle().get_string(locator_key)
        
        if hardcoded_locator:
            return hardcoded_locator
        
        # Check alternative naming patterns
        alt_keys = [
            f"{page}.{field_name}",
            f"{field_name}.{field_type}",
            f"{field_name}"
        ]
        
        for alt_key in alt_keys:
            alt_locator = get_bundle().get_string(alt_key)
            if alt_locator:
                return alt_locator
        
        return None

    def _generate_dynamic_locator(self, field_type: str, field_name: str, field_value: str = None) -> Optional[str]:
        """Generate dynamic locator using patterns"""
        if field_type not in self.patterns:
            return None

        patterns = self.patterns[field_type]
        processed_patterns = []

        for pattern in patterns:
            # Replace placeholder variables
            processed_pattern = pattern.replace('${loc.auto.fieldName}', field_name)
            
            if field_value:
                processed_pattern = processed_pattern.replace('${loc.auto.fieldValue}', field_value)
                processed_pattern = processed_pattern.replace('${loc.auto.forValue}', field_value)
            
            processed_patterns.append(processed_pattern)

        # Return JSON format locator with multiple fallback patterns
        if len(processed_patterns) == 1:
            return processed_patterns[0]
        else:
            return json.dumps(processed_patterns)

    def _get_locator_key(self, page: str, field_type: str, field_name: str) -> str:
        """Generate locator key pattern"""
        return f"loc.auto.{page}.{field_name}.{field_type}"

    def input(self, page: str, field_name: str, field_value: str = None) -> str:
        """Generate locator for input elements"""
        return self._get_locator(page, 'input', field_name, field_value)

    def button(self, page: str, field_name: str, field_value: str = None) -> str:
        """Generate locator for button elements"""
        return self._get_locator(page, 'button', field_name, field_value)

    def link(self, page: str, field_name: str, field_value: str = None) -> str:
        """Generate locator for link elements"""
        return self._get_locator(page, 'link', field_name, field_value)

    def checkbox(self, page: str, field_name: str, field_value: str = None) -> str:
        """Generate locator for checkbox elements"""
        return self._get_locator(page, 'checkbox', field_name, field_value)

    def radio(self, page: str, field_name: str, field_value: str = None) -> str:
        """Generate locator for radio button elements"""
        return self._get_locator(page, 'radio', field_name, field_value)

    def select(self, page: str, field_name: str, field_value: str = None) -> str:
        """Generate locator for select dropdown elements"""
        return self._get_locator(page, 'select', field_name, field_value)

    def textarea(self, page: str, field_name: str, field_value: str = None) -> str:
        """Generate locator for textarea elements"""
        return self._get_locator(page, 'textarea', field_name, field_value)

    def label(self, page: str, field_name: str, field_value: str = None) -> str:
        """Generate locator for label elements"""
        return self._get_locator(page, 'label', field_name, field_value)

    def text(self, page: str, field_name: str, field_value: str = None) -> str:
        """Generate locator for text elements (div, span, p)"""
        return self._get_locator(page, 'text', field_name, field_value)

    def table(self, page: str, field_name: str, field_value: str = None) -> str:
        """Generate locator for table elements"""
        return self._get_locator(page, 'table', field_name, field_value)

    def image(self, page: str, field_name: str, field_value: str = None) -> str:
        """Generate locator for image elements"""
        return self._get_locator(page, 'image', field_name, field_value)

    def element(self, page: str, field_name: str, field_value: str = None) -> str:
        """Generate locator for generic elements by class"""
        return self._get_locator(page, 'element', field_name, field_value)

    def form(self, page: str, field_name: str, field_value: str = None) -> str:
        """Generate locator for form elements"""
        return self._get_locator(page, 'form', field_name, field_value)

    def _get_locator(self, page: str, field_type: str, field_name: str, field_value: str = None) -> str:
        """
        Core method that implements the locator resolution logic:
        1. Check for hardcoded locator
        2. Generate dynamic locator if no hardcoded version exists
        3. Return appropriate locator string
        """
        # First check for hardcoded locator
        hardcoded_locator = self._check_hardcoded_locator(page, field_type, field_name)
        if hardcoded_locator:
            return hardcoded_locator

        # Generate dynamic locator using patterns
        dynamic_locator = self._generate_dynamic_locator(field_type, field_name, field_value)
        if dynamic_locator:
            return dynamic_locator

        # Fallback - return a basic XPath pattern
        return f"xpath=//*[contains(text(),'{field_name}')]"

    def get_pattern_types(self) -> List[str]:
        """Get list of available pattern types"""
        return list(self.patterns.keys())

    def add_custom_pattern(self, element_type: str, patterns: Union[str, List[str]]) -> None:
        """Add custom pattern at runtime"""
        if isinstance(patterns, str):
            patterns = [patterns]
        self.patterns[element_type] = patterns

    def is_pattern_enabled(self) -> bool:
        """Check if pattern locator system is enabled"""
        return self.pattern_enabled


# Singleton instance for global access
_pattern_locator_instance = None


def get_pattern_locator() -> PatternLocator:
    """Get singleton instance of PatternLocator"""
    global _pattern_locator_instance
    if _pattern_locator_instance is None:
        _pattern_locator_instance = PatternLocator()
    return _pattern_locator_instance


# Convenience functions for direct usage
def input_locator(page: str, field_name: str, field_value: str = None) -> str:
    """Generate input field locator"""
    return get_pattern_locator().input(page, field_name, field_value)


def button_locator(page: str, field_name: str, field_value: str = None) -> str:
    """Generate button locator"""
    return get_pattern_locator().button(page, field_name, field_value)


def link_locator(page: str, field_name: str, field_value: str = None) -> str:
    """Generate link locator"""
    return get_pattern_locator().link(page, field_name, field_value)


def checkbox_locator(page: str, field_name: str, field_value: str = None) -> str:
    """Generate checkbox locator"""
    return get_pattern_locator().checkbox(page, field_name, field_value)


def select_locator(page: str, field_name: str, field_value: str = None) -> str:
    """Generate select dropdown locator"""
    return get_pattern_locator().select(page, field_name, field_value)