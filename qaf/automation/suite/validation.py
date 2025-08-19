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

import os
import xml.etree.ElementTree as ET
from typing import List, Optional
from xml.dom import minidom

from .exceptions import SuiteXMLError, SuiteSchemaValidationError, handle_exception

# Backward compatibility alias
XMLValidationError = SuiteXMLError

class SchemaValidator:
    """
    XML Schema validation utilities for test suite configuration files
    """
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize schema validator
        
        Args:
            schema_path: Path to XSD schema file. If None, uses default suite.xsd
        """
        if schema_path is None:
            # Default to suite.xsd in the schemas directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            schema_path = os.path.join(project_root, 'test-suites', 'schemas', 'suite.xsd')
        
        self.schema_path = schema_path
        self._validate_schema_exists()
    
    def _validate_schema_exists(self) -> None:
        """Validate that the schema file exists"""
        if not os.path.exists(self.schema_path):
            raise SuiteXMLError(f"Schema file not found: {self.schema_path}", xml_file=self.schema_path)
    
    @handle_exception
    def validate_xml_syntax(self, xml_path: str) -> bool:
        """
        Validate XML file syntax (well-formed XML)
        
        Args:
            xml_path: Path to XML file to validate
            
        Returns:
            True if XML is well-formed
            
        Raises:
            SuiteXMLError: If XML syntax is invalid
        """
        try:
            ET.parse(xml_path)
            return True
        except ET.ParseError as e:
            # Extract line number if available
            line_number = getattr(e, 'lineno', None)
            raise SuiteXMLError(f"Invalid XML syntax in {xml_path}: {str(e)}", 
                              xml_file=xml_path, line_number=line_number)
        except FileNotFoundError:
            raise SuiteXMLError(f"XML file not found: {xml_path}", xml_file=xml_path)
    
    @handle_exception
    def validate_xml_content(self, xml_path: str) -> List[str]:
        """
        Validate XML content against basic suite requirements
        
        Args:
            xml_path: Path to XML file to validate
            
        Returns:
            List of validation warnings (empty if valid)
            
        Raises:
            SuiteXMLError: If critical validation errors found
        """
        warnings = []
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Check root element is 'suite' (handle namespaces)
            tag_name = root.tag.split('}')[-1] if '}' in root.tag else root.tag
            if tag_name != 'suite':
                raise SuiteXMLError(f"Root element must be 'suite', found: {tag_name}", xml_file=xml_path)
            
            # Check required 'name' attribute
            if 'name' not in root.attrib:
                raise SuiteXMLError("Suite element missing required 'name' attribute", xml_file=xml_path)
            
            # Validate suite name format
            suite_name = root.attrib['name']
            if not suite_name.strip():
                raise SuiteXMLError("Suite name cannot be empty", xml_file=xml_path)
            
            # Check for at least one test element
            test_elements = root.findall('test')
            if not test_elements:
                warnings.append("No test elements found - suite will have no executable tests")
            
            # Validate test elements
            for test in test_elements:
                if 'name' not in test.attrib:
                    raise SuiteXMLError("Test element missing required 'name' attribute", xml_file=xml_path)
                
                # Check for classes or groups
                classes = test.find('classes')
                groups = test.find('groups')
                
                if classes is None and groups is None:
                    warnings.append(f"Test '{test.attrib['name']}' has no classes or groups defined")
                
                # Validate classes structure
                if classes is not None:
                    class_elements = classes.findall('class')
                    if not class_elements:
                        warnings.append(f"Test '{test.attrib['name']}' has empty classes section")
                    else:
                        for class_elem in class_elements:
                            if 'name' not in class_elem.attrib:
                                raise SuiteXMLError("Class element missing required 'name' attribute", xml_file=xml_path)
                
                # Validate groups structure
                if groups is not None:
                    run_elem = groups.find('run')
                    if run_elem is None:
                        warnings.append(f"Test '{test.attrib['name']}' has groups but no run element")
                    else:
                        includes = run_elem.findall('include')
                        excludes = run_elem.findall('exclude')
                        if not includes and not excludes:
                            warnings.append(f"Test '{test.attrib['name']}' has empty run section")
                        
                        # Validate tag names
                        for include in includes:
                            if 'name' not in include.attrib:
                                raise SuiteXMLError("Include element missing required 'name' attribute", xml_file=xml_path)
                        
                        for exclude in excludes:
                            if 'name' not in exclude.attrib:
                                raise SuiteXMLError("Exclude element missing required 'name' attribute", xml_file=xml_path)
            
            # Validate parameters section
            parameters = root.find('parameters')
            if parameters is not None:
                param_elements = parameters.findall('parameter')
                for param in param_elements:
                    if 'name' not in param.attrib or 'value' not in param.attrib:
                        raise SuiteXMLError("Parameter element missing required 'name' or 'value' attribute", xml_file=xml_path)
            
            return warnings
            
        except ET.ParseError as e:
            line_number = getattr(e, 'lineno', None)
            raise SuiteXMLError(f"XML parsing error: {str(e)}", xml_file=xml_path, line_number=line_number)
    
    @handle_exception
    def get_validation_summary(self, xml_path: str) -> dict:
        """
        Get comprehensive validation summary for XML file
        
        Args:
            xml_path: Path to XML file to validate
            
        Returns:
            Dictionary with validation results
        """
        summary = {
            'file_path': xml_path,
            'valid': False,
            'syntax_valid': False,
            'content_valid': False,
            'warnings': [],
            'errors': []
        }
        
        try:
            # Check syntax
            self.validate_xml_syntax(xml_path)
            summary['syntax_valid'] = True
            
            # Check content
            warnings = self.validate_xml_content(xml_path)
            summary['content_valid'] = True
            summary['warnings'] = warnings
            summary['valid'] = True
            
        except SuiteXMLError as e:
            summary['errors'].append(str(e))
        
        return summary
    
    def format_xml_file(self, xml_path: str, output_path: Optional[str] = None) -> str:
        """
        Format XML file with proper indentation
        
        Args:
            xml_path: Path to input XML file
            output_path: Path for formatted output (overwrites input if None)
            
        Returns:
            Path to formatted file
        """
        if output_path is None:
            output_path = xml_path
        
        try:
            tree = ET.parse(xml_path)
            rough_string = ET.tostring(tree.getroot(), 'unicode')
            reparsed = minidom.parseString(rough_string)
            formatted_xml = reparsed.toprettyxml(indent="    ")
            
            # Remove empty lines
            lines = [line for line in formatted_xml.split('\n') if line.strip()]
            formatted_xml = '\n'.join(lines)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_xml)
            
            return output_path
            
        except Exception as e:
            raise SuiteXMLError(f"Error formatting XML file: {str(e)}", xml_file=xml_path)