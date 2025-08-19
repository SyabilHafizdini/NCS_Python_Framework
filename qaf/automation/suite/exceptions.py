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
Comprehensive exception hierarchy for test suite management operations
"""

from typing import List, Dict, Any, Optional


class SuiteManagementError(Exception):
    """Base exception for all suite management operations"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, error_code: str = None):
        self.message = message
        self.details = details or {}
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)
    
    def __str__(self):
        return f"[{self.error_code}] {self.message}"
    
    def get_detailed_message(self) -> str:
        """Get detailed error message with context"""
        msg = str(self)
        if self.details:
            msg += f"\nDetails: {self.details}"
        return msg


class SuiteValidationError(SuiteManagementError):
    """Exception raised when suite validation fails"""
    
    def __init__(self, message: str, validation_errors: List[str] = None, **kwargs):
        self.validation_errors = validation_errors or []
        super().__init__(message, **kwargs)
    
    def get_detailed_message(self) -> str:
        msg = super().get_detailed_message()
        if self.validation_errors:
            msg += f"\nValidation Errors:\n" + "\n".join(f"  - {error}" for error in self.validation_errors)
        return msg


class SuiteConfigurationError(SuiteManagementError):
    """Exception raised when suite configuration is invalid"""
    pass


class SuiteXMLError(SuiteConfigurationError):
    """Exception raised when XML parsing or validation fails"""
    
    def __init__(self, message: str, xml_file: str = None, line_number: int = None, **kwargs):
        self.xml_file = xml_file
        self.line_number = line_number
        details = kwargs.get('details', {})
        if xml_file:
            details['xml_file'] = xml_file
        if line_number:
            details['line_number'] = line_number
        kwargs['details'] = details
        super().__init__(message, **kwargs)


class SuiteSchemaValidationError(SuiteXMLError):
    """Exception raised when XML schema validation fails"""
    
    def __init__(self, message: str, schema_errors: List[str] = None, **kwargs):
        self.schema_errors = schema_errors or []
        super().__init__(message, **kwargs)
    
    def get_detailed_message(self) -> str:
        msg = super().get_detailed_message()
        if self.schema_errors:
            msg += f"\nSchema Validation Errors:\n" + "\n".join(f"  - {error}" for error in self.schema_errors)
        return msg


class SuiteRepositoryError(SuiteManagementError):
    """Exception raised when repository operations fail"""
    pass


class SuiteNotFoundError(SuiteRepositoryError):
    """Exception raised when requested suite is not found"""
    
    def __init__(self, suite_name: str, **kwargs):
        self.suite_name = suite_name
        message = f"Suite '{suite_name}' not found"
        super().__init__(message, **kwargs)


class SuiteAlreadyExistsError(SuiteRepositoryError):
    """Exception raised when trying to create a suite that already exists"""
    
    def __init__(self, suite_name: str, **kwargs):
        self.suite_name = suite_name
        message = f"Suite '{suite_name}' already exists"
        super().__init__(message, **kwargs)


class SuiteFileSystemError(SuiteRepositoryError):
    """Exception raised when file system operations fail"""
    
    def __init__(self, message: str, file_path: str = None, operation: str = None, **kwargs):
        self.file_path = file_path
        self.operation = operation
        details = kwargs.get('details', {})
        if file_path:
            details['file_path'] = file_path
        if operation:
            details['operation'] = operation
        kwargs['details'] = details
        super().__init__(message, **kwargs)


class SuiteExecutionError(SuiteManagementError):
    """Exception raised when suite execution fails"""
    
    def __init__(self, message: str, suite_name: str = None, exit_code: int = None, **kwargs):
        self.suite_name = suite_name
        self.exit_code = exit_code
        details = kwargs.get('details', {})
        if suite_name:
            details['suite_name'] = suite_name
        if exit_code is not None:
            details['exit_code'] = exit_code
        kwargs['details'] = details
        super().__init__(message, **kwargs)


class SuiteFeatureFileError(SuiteValidationError):
    """Exception raised when feature files referenced in suite are missing or invalid"""
    
    def __init__(self, message: str, missing_files: List[str] = None, invalid_files: List[str] = None, **kwargs):
        self.missing_files = missing_files or []
        self.invalid_files = invalid_files or []
        super().__init__(message, **kwargs)
    
    def get_detailed_message(self) -> str:
        msg = super().get_detailed_message()
        if self.missing_files:
            msg += f"\nMissing Files:\n" + "\n".join(f"  - {file}" for file in self.missing_files)
        if self.invalid_files:
            msg += f"\nInvalid Files:\n" + "\n".join(f"  - {file}" for file in self.invalid_files)
        return msg


class SuiteTagValidationError(SuiteValidationError):
    """Exception raised when tag validation fails"""
    
    def __init__(self, message: str, invalid_tags: List[str] = None, **kwargs):
        self.invalid_tags = invalid_tags or []
        super().__init__(message, **kwargs)
    
    def get_detailed_message(self) -> str:
        msg = super().get_detailed_message()
        if self.invalid_tags:
            msg += f"\nInvalid Tags:\n" + "\n".join(f"  - {tag}" for tag in self.invalid_tags)
        return msg


class SuiteCompatibilityError(SuiteValidationError):
    """Exception raised when suite is incompatible with current configuration"""
    
    def __init__(self, message: str, compatibility_issues: List[str] = None, **kwargs):
        self.compatibility_issues = compatibility_issues or []
        super().__init__(message, **kwargs)
    
    def get_detailed_message(self) -> str:
        msg = super().get_detailed_message()
        if self.compatibility_issues:
            msg += f"\nCompatibility Issues:\n" + "\n".join(f"  - {issue}" for issue in self.compatibility_issues)
        return msg


class SuiteReportIntegrationError(SuiteManagementError):
    """Exception raised when report integration validation fails"""
    
    def __init__(self, message: str, integration_errors: List[str] = None, **kwargs):
        self.integration_errors = integration_errors or []
        super().__init__(message, **kwargs)
    
    def get_detailed_message(self) -> str:
        msg = super().get_detailed_message()
        if self.integration_errors:
            msg += f"\nIntegration Errors:\n" + "\n".join(f"  - {error}" for error in self.integration_errors)
        return msg


class SuiteEnvironmentError(SuiteManagementError):
    """Exception raised when environment configuration is invalid"""
    
    def __init__(self, message: str, environment: str = None, missing_params: List[str] = None, **kwargs):
        self.environment = environment
        self.missing_params = missing_params or []
        details = kwargs.get('details', {})
        if environment:
            details['environment'] = environment
        kwargs['details'] = details
        super().__init__(message, **kwargs)
    
    def get_detailed_message(self) -> str:
        msg = super().get_detailed_message()
        if self.missing_params:
            msg += f"\nMissing Parameters:\n" + "\n".join(f"  - {param}" for param in self.missing_params)
        return msg


# Error code mappings for easy reference
ERROR_CODES = {
    'SUITE_NOT_FOUND': SuiteNotFoundError,
    'SUITE_EXISTS': SuiteAlreadyExistsError,
    'INVALID_XML': SuiteXMLError,
    'SCHEMA_VALIDATION': SuiteSchemaValidationError,
    'MISSING_FILES': SuiteFeatureFileError,
    'INVALID_TAGS': SuiteTagValidationError,
    'EXECUTION_FAILED': SuiteExecutionError,
    'FILESYSTEM_ERROR': SuiteFileSystemError,
    'COMPATIBILITY_ERROR': SuiteCompatibilityError,
    'REPORT_INTEGRATION': SuiteReportIntegrationError,
    'ENVIRONMENT_ERROR': SuiteEnvironmentError,
    'CONFIGURATION_ERROR': SuiteConfigurationError,
    'VALIDATION_ERROR': SuiteValidationError,
    'MANAGEMENT_ERROR': SuiteManagementError
}


def create_error(error_code: str, message: str, **kwargs) -> SuiteManagementError:
    """
    Factory function to create specific error types based on error codes
    
    Args:
        error_code: Error code from ERROR_CODES
        message: Error message
        **kwargs: Additional parameters for specific error types
        
    Returns:
        Appropriate exception instance
    """
    error_class = ERROR_CODES.get(error_code, SuiteManagementError)
    
    # Handle special cases where specific constructors need different parameters
    if error_class == SuiteNotFoundError and 'suite_name' in kwargs:
        suite_name = kwargs.pop('suite_name')
        return error_class(suite_name, error_code=error_code, **kwargs)
    elif error_class == SuiteAlreadyExistsError and 'suite_name' in kwargs:
        suite_name = kwargs.pop('suite_name')
        return error_class(suite_name, error_code=error_code, **kwargs)
    else:
        return error_class(message, error_code=error_code, **kwargs)


def handle_exception(func):
    """
    Decorator to provide consistent exception handling for suite operations
    
    Usage:
        @handle_exception
        def some_suite_operation():
            # operation code
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SuiteManagementError:
            # Re-raise suite management exceptions as-is
            raise
        except FileNotFoundError as e:
            raise SuiteFileSystemError(f"File not found: {str(e)}", file_path=str(e.filename)) from e
        except PermissionError as e:
            raise SuiteFileSystemError(f"Permission denied: {str(e)}", file_path=str(e.filename)) from e
        except OSError as e:
            raise SuiteFileSystemError(f"File system error: {str(e)}") from e
        except Exception as e:
            raise SuiteManagementError(f"Unexpected error: {str(e)}") from e
    
    return wrapper