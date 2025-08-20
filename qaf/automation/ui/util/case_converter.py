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
CaseConverter - Exact Java CaseUtils.toCamelCase equivalent

This utility provides camelCase conversion matching the exact behavior 
of Apache Commons Lang CaseUtils.toCamelCase method used in the Java QAF framework.
"""

import re
from typing import Optional


class CaseConverter:
    """
    Utility class for case conversion operations matching Java CaseUtils behavior
    """
    
    @staticmethod
    def to_camel_case(text: str, capitalize_first: bool = False, delimiter: str = ' ') -> str:
        """
        Convert text to camelCase exactly matching Java CaseUtils.toCamelCase behavior
        
        Args:
            text: The input text to convert
            capitalize_first: Whether to capitalize the first character
            delimiter: The delimiter character to split on (default: ' ')
            
        Returns:
            String in camelCase format
            
        Example:
            to_camel_case("hello world", False, ' ') -> "helloWorld"
            to_camel_case("hello world", True, ' ') -> "HelloWorld"
            to_camel_case("test_field_name", False, '_') -> "testFieldName"
        """
        if not text:
            return ""
            
        # Handle None or empty strings
        if text is None:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # Remove special characters and replace with spaces for consistent processing
        # This matches the Java implementation's handling of non-alphanumeric characters
        cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Split on the delimiter and any whitespace
        if delimiter == ' ':
            # Split on any whitespace when delimiter is space
            words = re.split(r'\s+', cleaned_text.strip())
        else:
            # Replace delimiter with space and then split
            normalized = cleaned_text.replace(delimiter, ' ')
            words = re.split(r'\s+', normalized.strip())
        
        # Filter out empty strings
        words = [word for word in words if word]
        
        if not words:
            return ""
        
        # Build camelCase string
        camel_case_parts = []
        
        for i, word in enumerate(words):
            if not word:
                continue
                
            # Convert word to lowercase first
            word = word.lower()
            
            # Capitalize first letter if:
            # - capitalize_first is True and this is the first word, OR
            # - this is not the first word (subsequent words always capitalized)
            if (i == 0 and capitalize_first) or i > 0:
                word = word[0].upper() + word[1:] if len(word) > 1 else word.upper()
            
            camel_case_parts.append(word)
        
        return ''.join(camel_case_parts)
    
    @staticmethod
    def to_camel_case_java_exact(text: str, capitalize_first: bool = False) -> str:
        """
        Exact implementation matching Java CaseUtils.toCamelCase behavior
        for the pattern locator use case
        
        This method handles the specific case conversion used in:
        CaseUtils.toCamelCase(argPageName.replaceAll("[^a-zA-Z0-9]", " "), false, ' ')
        
        Args:
            text: Input text to convert
            capitalize_first: Whether to capitalize first character
            
        Returns:
            camelCase string exactly matching Java behavior
        """
        if not text:
            return ""
        
        # Step 1: Replace all non-alphanumeric characters with spaces
        # This exactly matches: argPageName.replaceAll("[^a-zA-Z0-9]", " ")
        cleaned = re.sub(r'[^a-zA-Z0-9]', ' ', text)
        
        # Step 2: Split on whitespace and filter empty strings
        words = [word for word in cleaned.split() if word]
        
        if not words:
            return ""
        
        # Step 3: Convert to camelCase
        result_parts = []
        for i, word in enumerate(words):
            word_lower = word.lower()
            
            # First word: capitalize only if capitalize_first is True
            # Subsequent words: always capitalize first letter
            if i == 0:
                if capitalize_first:
                    result_parts.append(word_lower.capitalize())
                else:
                    result_parts.append(word_lower)
            else:
                result_parts.append(word_lower.capitalize())
        
        return ''.join(result_parts)


# Convenience functions matching the Java usage patterns
def to_camel_case(text: str, capitalize_first: bool = False, delimiter: str = ' ') -> str:
    """Convenience function for camelCase conversion"""
    return CaseConverter.to_camel_case(text, capitalize_first, delimiter)


def to_camel_case_java_exact(text: str, capitalize_first: bool = False) -> str:
    """Convenience function for exact Java behavior matching"""
    return CaseConverter.to_camel_case_java_exact(text, capitalize_first)