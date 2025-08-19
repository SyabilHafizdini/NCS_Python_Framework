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
Comprehensive validation system for test suite management
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .exceptions import (
    SuiteValidationError, SuiteFeatureFileError, SuiteTagValidationError,
    SuiteCompatibilityError, SuiteEnvironmentError, SuiteConfigurationError
)
from .parser import SuiteConfiguration


@dataclass
class ValidationResult:
    """Result of a validation operation"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.details is None:
            self.details = {}
    
    def add_error(self, error: str):
        """Add an error to the result"""
        self.errors.append(error)
        self.valid = False
    
    def add_warning(self, warning: str):
        """Add a warning to the result"""
        self.warnings.append(warning)
    
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result into this one"""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.details.update(other.details)
        if not other.valid:
            self.valid = False


class SuiteNameValidator:
    """Validates suite names according to naming conventions"""
    
    # Valid suite name pattern: alphanumeric, hyphens, underscores
    NAME_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$')
    
    # Reserved names that cannot be used
    RESERVED_NAMES = {
        'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5',
        'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5',
        'lpt6', 'lpt7', 'lpt8', 'lpt9', 'test', 'example', 'sample'
    }
    
    @classmethod
    def validate(cls, name: str) -> ValidationResult:
        """
        Validate suite name
        
        Args:
            name: Suite name to validate
            
        Returns:
            ValidationResult with validation outcome
        """
        result = ValidationResult(valid=True, errors=[], warnings=[], details={})
        
        if not name:
            result.add_error("Suite name cannot be empty")
            return result
        
        if len(name) < 2:
            result.add_error("Suite name must be at least 2 characters long")
        
        if len(name) > 64:
            result.add_error("Suite name cannot be longer than 64 characters")
        
        if not cls.NAME_PATTERN.match(name):
            result.add_error("Suite name must contain only alphanumeric characters, hyphens, and underscores")
            result.add_error("Suite name cannot start or end with hyphens or underscores")
        
        if name.lower() in cls.RESERVED_NAMES:
            result.add_error(f"'{name}' is a reserved name and cannot be used")
        
        if '--' in name or '__' in name:
            result.add_warning("Consecutive hyphens or underscores in suite names are discouraged")
        
        if name.lower() != name:
            result.add_warning("Suite names should use lowercase letters for consistency")
        
        result.details['name'] = name
        result.details['length'] = len(name)
        
        return result


class ScenarioPathValidator:
    """Validates scenario paths and feature file existence"""
    
    @classmethod
    def validate(cls, scenario_paths: List[str], base_directory: str = ".") -> ValidationResult:
        """
        Validate scenario paths and check feature file existence
        
        Args:
            scenario_paths: List of scenario paths to validate
            base_directory: Base directory for resolving relative paths
            
        Returns:
            ValidationResult with validation outcome
        """
        result = ValidationResult(valid=True, errors=[], warnings=[], details={})
        
        if not scenario_paths:
            result.add_error("At least one scenario path must be specified")
            return result
        
        missing_files = []
        invalid_paths = []
        valid_paths = []
        
        for path in scenario_paths:
            if not path or not isinstance(path, str):
                invalid_paths.append(str(path))
                continue
            
            # Convert dotted path to file path
            feature_path = cls._convert_to_feature_path(path, base_directory)
            
            if os.path.exists(feature_path):
                valid_paths.append(path)
                # Validate feature file content
                cls._validate_feature_file_content(feature_path, result)
            else:
                missing_files.append(feature_path)
        
        if invalid_paths:
            result.add_error(f"Invalid scenario paths: {', '.join(invalid_paths)}")
        
        if missing_files:
            result.add_error(f"Missing feature files: {', '.join(missing_files)}")
        
        if len(valid_paths) == 0 and len(scenario_paths) > 0:
            result.add_error("No valid scenario paths found")
        
        result.details['total_paths'] = len(scenario_paths)
        result.details['valid_paths'] = len(valid_paths)
        result.details['missing_files'] = missing_files
        result.details['invalid_paths'] = invalid_paths
        
        return result
    
    @staticmethod
    def _convert_to_feature_path(dotted_path: str, base_directory: str) -> str:
        """Convert dotted path to feature file path"""
        path_parts = dotted_path.split('.')
        return os.path.join(base_directory, *path_parts) + '.feature'
    
    @staticmethod
    def _validate_feature_file_content(feature_path: str, result: ValidationResult):
        """Validate basic feature file content"""
        try:
            with open(feature_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                result.add_warning(f"Feature file is empty: {feature_path}")
                return
            
            # Check for basic Gherkin structure
            if 'Feature:' not in content:
                result.add_warning(f"Feature file may be missing Feature declaration: {feature_path}")
            
            if 'Scenario:' not in content and 'Scenario Outline:' not in content:
                result.add_warning(f"Feature file may be missing Scenario declarations: {feature_path}")
        
        except Exception as e:
            result.add_warning(f"Could not validate feature file content {feature_path}: {str(e)}")


class TagValidator:
    """Validates behave tags"""
    
    # Valid tag pattern: alphanumeric, hyphens, underscores
    TAG_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$')
    
    # Reserved tags that have special meaning
    RESERVED_TAGS = {'skip', 'wip', 'fixture'}
    
    @classmethod
    def validate(cls, include_tags: List[str], exclude_tags: List[str]) -> ValidationResult:
        """
        Validate include and exclude tags
        
        Args:
            include_tags: Tags to include
            exclude_tags: Tags to exclude
            
        Returns:
            ValidationResult with validation outcome
        """
        result = ValidationResult(valid=True, errors=[], warnings=[], details={})
        
        # Validate include tags
        invalid_include = cls._validate_tag_list(include_tags, "include")
        if invalid_include:
            result.add_error(f"Invalid include tags: {', '.join(invalid_include)}")
        
        # Validate exclude tags
        invalid_exclude = cls._validate_tag_list(exclude_tags, "exclude")
        if invalid_exclude:
            result.add_error(f"Invalid exclude tags: {', '.join(invalid_exclude)}")
        
        # Check for conflicts
        conflicts = set(include_tags) & set(exclude_tags)
        if conflicts:
            result.add_error(f"Tags cannot be both included and excluded: {', '.join(conflicts)}")
        
        # Check for reserved tags
        reserved_included = set(include_tags) & cls.RESERVED_TAGS
        if reserved_included:
            result.add_warning(f"Using reserved tags in include list: {', '.join(reserved_included)}")
        
        result.details['include_count'] = len(include_tags)
        result.details['exclude_count'] = len(exclude_tags)
        result.details['conflicts'] = list(conflicts)
        
        return result
    
    @classmethod
    def _validate_tag_list(cls, tags: List[str], tag_type: str) -> List[str]:
        """Validate a list of tags and return invalid ones"""
        invalid_tags = []
        
        for tag in tags:
            if not tag or not isinstance(tag, str):
                invalid_tags.append(str(tag))
                continue
            
            if not cls.TAG_PATTERN.match(tag):
                invalid_tags.append(tag)
        
        return invalid_tags


class EnvironmentValidator:
    """Validates environment parameters and configuration"""
    
    # Valid parameter name pattern
    PARAM_NAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
    
    @classmethod
    def validate(cls, environment_params: Dict[str, str], environment: str = None) -> ValidationResult:
        """
        Validate environment parameters
        
        Args:
            environment_params: Environment parameters to validate
            environment: Target environment name
            
        Returns:
            ValidationResult with validation outcome
        """
        result = ValidationResult(valid=True, errors=[], warnings=[], details={})
        
        if environment_params:
            invalid_params = []
            sensitive_params = []
            
            for key, value in environment_params.items():
                # Validate parameter name
                if not cls.PARAM_NAME_PATTERN.match(key):
                    invalid_params.append(key)
                
                # Check for potentially sensitive parameters
                if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                    sensitive_params.append(key)
                
                # Validate value
                if not isinstance(value, str):
                    result.add_warning(f"Parameter value should be string: {key}={value}")
            
            if invalid_params:
                result.add_error(f"Invalid parameter names: {', '.join(invalid_params)}")
            
            if sensitive_params:
                result.add_warning(f"Potentially sensitive parameters detected: {', '.join(sensitive_params)}")
        
        # Validate environment name
        if environment:
            valid_environments = ['DEV', 'UAT', 'PROD', 'TEST', 'STAGING']
            if environment not in valid_environments:
                result.add_warning(f"Non-standard environment name: {environment}")
        
        result.details['param_count'] = len(environment_params) if environment_params else 0
        result.details['environment'] = environment
        
        return result


class SuiteConfigurationValidator:
    """Comprehensive validator for entire suite configuration"""
    
    def __init__(self, base_directory: str = "."):
        self.base_directory = base_directory
        self.name_validator = SuiteNameValidator()
        self.path_validator = ScenarioPathValidator()
        self.tag_validator = TagValidator()
        self.env_validator = EnvironmentValidator()
    
    def validate(self, config: SuiteConfiguration) -> ValidationResult:
        """
        Perform comprehensive validation of suite configuration
        
        Args:
            config: Suite configuration to validate
            
        Returns:
            ValidationResult with validation outcome
        """
        result = ValidationResult(valid=True, errors=[], warnings=[], details={})
        
        # Validate suite name
        name_result = self.name_validator.validate(config.name)
        result.merge(name_result)
        
        # Validate scenario paths
        path_result = self.path_validator.validate(config.scenario_paths, self.base_directory)
        result.merge(path_result)
        
        # Validate tags
        tag_result = self.tag_validator.validate(config.include_tags, config.exclude_tags)
        result.merge(tag_result)
        
        # Validate environment
        env_result = self.env_validator.validate(
            config.environment_params,
            config.execution_config.environment if config.execution_config else None
        )
        result.merge(env_result)
        
        # Validate description
        if not config.description:
            result.add_warning("Suite description is empty - consider adding one for documentation")
        elif len(config.description) > 500:
            result.add_warning("Suite description is very long - consider shortening for readability")
        
        # Cross-validation checks
        self._perform_cross_validation(config, result)
        
        result.details['configuration'] = {
            'name': config.name,
            'scenario_count': len(config.scenario_paths),
            'include_tag_count': len(config.include_tags),
            'exclude_tag_count': len(config.exclude_tags),
            'env_param_count': len(config.environment_params) if config.environment_params else 0
        }
        
        return result
    
    def _perform_cross_validation(self, config: SuiteConfiguration, result: ValidationResult):
        """Perform cross-validation between different configuration elements"""
        
        # Check if tags make sense with scenario paths
        if config.include_tags and not config.exclude_tags:
            result.add_warning("Only include tags specified - consider if exclude tags are needed")
        
        # Check execution configuration
        if config.execution_config:
            if config.execution_config.timeout_seconds > 3600:
                result.add_warning("Execution timeout is very long (>1 hour)")
            
            if config.execution_config.max_retries > 5:
                result.add_warning("High retry count may indicate underlying test issues")
    
    def validate_compatibility(self, config: SuiteConfiguration) -> ValidationResult:
        """
        Validate suite compatibility with current environment
        
        Args:
            config: Suite configuration to validate
            
        Returns:
            ValidationResult with compatibility validation outcome
        """
        result = ValidationResult(valid=True, errors=[], warnings=[], details={})
        
        # Check Python version compatibility
        import sys
        if sys.version_info < (3, 6):
            result.add_error("Python 3.6 or higher is required")
        
        # Check required dependencies
        required_modules = ['behave', 'selenium']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            result.add_error(f"Missing required modules: {', '.join(missing_modules)}")
        
        # Check behave.ini existence
        if not os.path.exists('behave.ini'):
            result.add_warning("behave.ini not found - using default behave configuration")
        
        # Check reports directory
        if not os.path.exists('reports'):
            result.add_warning("reports directory not found - will be created during execution")
        
        result.details['python_version'] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        result.details['missing_modules'] = missing_modules
        
        return result


def validate_suite_configuration(config: SuiteConfiguration, base_directory: str = ".") -> ValidationResult:
    """
    Convenience function for comprehensive suite validation
    
    Args:
        config: Suite configuration to validate
        base_directory: Base directory for resolving paths
        
    Returns:
        ValidationResult with validation outcome
    """
    validator = SuiteConfigurationValidator(base_directory)
    return validator.validate(config)


def raise_for_validation_result(result: ValidationResult, operation_name: str = "operation"):
    """
    Raise appropriate exception if validation result contains errors
    
    Args:
        result: ValidationResult to check
        operation_name: Name of operation for error context
    """
    if not result.valid:
        if len(result.errors) == 1:
            raise SuiteValidationError(
                f"Validation failed for {operation_name}: {result.errors[0]}",
                validation_errors=result.errors
            )
        else:
            raise SuiteValidationError(
                f"Validation failed for {operation_name} with {len(result.errors)} error(s)",
                validation_errors=result.errors
            )