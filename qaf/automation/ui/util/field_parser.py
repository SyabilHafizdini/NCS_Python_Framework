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
FieldParser - Field name and instance extraction utility

This utility extracts field names and instances from bracketed notation
exactly matching the Java QAF framework implementation:
- fieldNameCheck() equivalent
- fieldInstanceCheck() equivalent
"""

import re
from typing import Tuple


class FieldParser:
    """
    Utility class for parsing field names and extracting instances from bracketed notation
    Matches the Java QAF framework fieldNameCheck() and fieldInstanceCheck() methods
    """
    
    @staticmethod
    def extract_field_name(field_input: str) -> str:
        """
        Extract field name from bracketed instance notation
        Equivalent to Java fieldNameCheck() method
        
        Examples:
            "Submit[2]" -> "Submit"
            "Login" -> "Login"
            "Button[3]" -> "Button"
            "Field[1]" -> "Field"
            
        Args:
            field_input: Field name with optional bracketed instance notation
            
        Returns:
            Field name without instance notation
        """
        if not field_input:
            return ""
        
        # Handle None input
        if field_input is None:
            return ""
        
        # Convert to string if not already
        field_input = str(field_input).strip()
        
        # Check for bracketed notation like "Submit[2]"
        bracket_match = re.search(r'^(.+?)\[(\d+)\]$', field_input)
        
        if bracket_match:
            # Extract the field name part before the bracket
            return bracket_match.group(1).strip()
        else:
            # No bracket notation, return the original field name
            return field_input
    
    @staticmethod
    def extract_instance(field_input: str) -> str:
        """
        Extract instance number from bracketed notation
        Equivalent to Java fieldInstanceCheck() method
        
        Examples:
            "Submit[2]" -> "2"
            "Login" -> "1" (default)
            "Button[3]" -> "3"
            "Field[1]" -> "1"
            
        Args:
            field_input: Field name with optional bracketed instance notation
            
        Returns:
            Instance number as string, defaults to "1" if no instance specified
        """
        if not field_input:
            return "1"
        
        # Handle None input
        if field_input is None:
            return "1"
        
        # Convert to string if not already
        field_input = str(field_input).strip()
        
        # Check for bracketed notation like "Submit[2]"
        bracket_match = re.search(r'^(.+?)\[(\d+)\]$', field_input)
        
        if bracket_match:
            # Extract the instance number
            return bracket_match.group(2)
        else:
            # No bracket notation, return default instance "1"
            return "1"
    
    @staticmethod
    def parse_field(field_input: str) -> Tuple[str, str]:
        """
        Parse field input to extract both field name and instance
        
        Args:
            field_input: Field name with optional bracketed instance notation
            
        Returns:
            Tuple of (field_name, instance) where instance defaults to "1"
            
        Example:
            parse_field("Submit[2]") -> ("Submit", "2")
            parse_field("Login") -> ("Login", "1")
        """
        field_name = FieldParser.extract_field_name(field_input)
        instance = FieldParser.extract_instance(field_input)
        return field_name, instance
    
    @staticmethod
    def has_instance_notation(field_input: str) -> bool:
        """
        Check if field input contains bracketed instance notation
        
        Args:
            field_input: Field name to check
            
        Returns:
            True if field contains bracketed notation like "Submit[2]"
        """
        if not field_input:
            return False
        
        # Check for bracketed notation pattern
        return bool(re.search(r'^.+\[\d+\]$', str(field_input)))
    
    @staticmethod
    def validate_field_name(field_input: str) -> bool:
        """
        Validate that field name is not empty after parsing
        
        Args:
            field_input: Field name to validate
            
        Returns:
            True if field name is valid (not empty after parsing)
        """
        field_name = FieldParser.extract_field_name(field_input)
        return bool(field_name and field_name.strip())


# Convenience functions matching the Java method names
def field_name_check(field_input: str) -> str:
    """Convenience function matching Java fieldNameCheck() method"""
    return FieldParser.extract_field_name(field_input)


def field_instance_check(field_input: str) -> str:
    """Convenience function matching Java fieldInstanceCheck() method"""
    return FieldParser.extract_instance(field_input)