#!/usr/bin/env python3
"""
Unit tests for error handling and validation system
"""

import os
import tempfile
import unittest
import shutil
from unittest.mock import patch, MagicMock

from qaf.automation.suite.exceptions import (
    SuiteManagementError, SuiteValidationError, SuiteConfigurationError,
    SuiteXMLError, SuiteSchemaValidationError, SuiteRepositoryError,
    SuiteNotFoundError, SuiteAlreadyExistsError, SuiteFileSystemError,
    SuiteExecutionError, SuiteFeatureFileError, SuiteTagValidationError,
    SuiteCompatibilityError, SuiteReportIntegrationError, SuiteEnvironmentError,
    create_error, handle_exception
)

from qaf.automation.suite.validators import (
    ValidationResult, SuiteNameValidator, ScenarioPathValidator,
    TagValidator, EnvironmentValidator, SuiteConfigurationValidator,
    validate_suite_configuration, raise_for_validation_result
)

from qaf.automation.suite.parser import SuiteConfiguration, ExecutionConfig


class TestExceptionHierarchy(unittest.TestCase):
    """Test cases for exception hierarchy"""
    
    def test_base_exception_creation(self):
        """Test base exception creation with details"""
        error = SuiteManagementError(
            "Test error",
            details={'key': 'value'},
            error_code='TEST_ERROR'
        )
        
        self.assertEqual(str(error), "[TEST_ERROR] Test error")
        self.assertEqual(error.details['key'], 'value')
        self.assertEqual(error.error_code, 'TEST_ERROR')
    
    def test_validation_error_with_multiple_errors(self):
        """Test validation error with multiple validation errors"""
        error = SuiteValidationError(
            "Validation failed",
            validation_errors=['Error 1', 'Error 2', 'Error 3']
        )
        
        detailed_msg = error.get_detailed_message()
        self.assertIn("Error 1", detailed_msg)
        self.assertIn("Error 2", detailed_msg)
        self.assertIn("Error 3", detailed_msg)
    
    def test_xml_error_with_line_number(self):
        """Test XML error with file and line number details"""
        error = SuiteXMLError(
            "Parse error",
            xml_file="test.xml",
            line_number=42
        )
        
        self.assertEqual(error.xml_file, "test.xml")
        self.assertEqual(error.line_number, 42)
        self.assertIn("test.xml", error.details['xml_file'])
        self.assertEqual(error.details['line_number'], 42)
    
    def test_schema_validation_error(self):
        """Test schema validation error with schema errors"""
        schema_errors = [
            "Element 'suite' missing required attribute 'name'",
            "Invalid element 'invalid_tag' found"
        ]
        
        error = SuiteSchemaValidationError(
            "Schema validation failed",
            schema_errors=schema_errors,
            xml_file="test.xml"
        )
        
        detailed_msg = error.get_detailed_message()
        for schema_error in schema_errors:
            self.assertIn(schema_error, detailed_msg)
    
    def test_feature_file_error(self):
        """Test feature file error with missing and invalid files"""
        error = SuiteFeatureFileError(
            "Feature file validation failed",
            missing_files=['tests/missing.feature'],
            invalid_files=['tests/invalid.feature']
        )
        
        detailed_msg = error.get_detailed_message()
        self.assertIn("tests/missing.feature", detailed_msg)
        self.assertIn("tests/invalid.feature", detailed_msg)
    
    def test_error_factory_function(self):
        """Test error factory function"""
        error = create_error('SUITE_NOT_FOUND', 'Test suite not found', suite_name='test')
        
        self.assertIsInstance(error, SuiteNotFoundError)
        self.assertEqual(error.suite_name, 'test')
        self.assertEqual(error.error_code, 'SUITE_NOT_FOUND')
    
    def test_handle_exception_decorator(self):
        """Test exception handling decorator"""
        
        @handle_exception
        def function_that_raises_file_not_found():
            raise FileNotFoundError("test.xml")
        
        @handle_exception
        def function_that_raises_permission_error():
            raise PermissionError("access denied")
        
        @handle_exception
        def function_that_raises_generic_exception():
            raise ValueError("generic error")
        
        # Test FileNotFoundError conversion
        with self.assertRaises(SuiteFileSystemError) as ctx:
            function_that_raises_file_not_found()
        self.assertIn("File not found", str(ctx.exception))
        
        # Test PermissionError conversion
        with self.assertRaises(SuiteFileSystemError) as ctx:
            function_that_raises_permission_error()
        self.assertIn("Permission denied", str(ctx.exception))
        
        # Test generic exception conversion
        with self.assertRaises(SuiteManagementError) as ctx:
            function_that_raises_generic_exception()
        self.assertIn("Unexpected error", str(ctx.exception))


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult"""
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation and modification"""
        result = ValidationResult(valid=True, errors=[], warnings=[], details={})
        
        self.assertTrue(result.valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 0)
        
        # Add error should set valid to False
        result.add_error("Test error")
        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        
        # Add warning should not affect validity
        result.add_warning("Test warning")
        self.assertFalse(result.valid)
        self.assertEqual(len(result.warnings), 1)
    
    def test_validation_result_merge(self):
        """Test merging validation results"""
        result1 = ValidationResult(valid=True, errors=[], warnings=['Warning 1'], details={'key1': 'value1'})
        result2 = ValidationResult(valid=False, errors=['Error 1'], warnings=['Warning 2'], details={'key2': 'value2'})
        
        result1.merge(result2)
        
        self.assertFalse(result1.valid)
        self.assertEqual(len(result1.errors), 1)
        self.assertEqual(len(result1.warnings), 2)
        self.assertIn('key1', result1.details)
        self.assertIn('key2', result1.details)


class TestSuiteNameValidator(unittest.TestCase):
    """Test cases for SuiteNameValidator"""
    
    def test_valid_suite_names(self):
        """Test validation of valid suite names"""
        valid_names = ['test-suite', 'smoke_tests', 'regression', 'api-tests-v1', 'demo123']
        
        for name in valid_names:
            with self.subTest(name=name):
                result = SuiteNameValidator.validate(name)
                self.assertTrue(result.valid, f"Name '{name}' should be valid")
    
    def test_invalid_suite_names(self):
        """Test validation of invalid suite names"""
        invalid_names = [
            '',  # empty
            'a',  # too short
            '-test',  # starts with hyphen
            'test-',  # ends with hyphen
            '_test',  # starts with underscore
            'test_',  # ends with underscore
            'test suite',  # contains space
            'test@suite',  # contains special character
            'a' * 65,  # too long
            'con',  # reserved name
            'test--suite',  # consecutive hyphens
            'TEST_SUITE'  # uppercase (warning)
        ]
        
        for name in invalid_names:
            with self.subTest(name=name):
                result = SuiteNameValidator.validate(name)
                if name == 'TEST_SUITE':
                    # Uppercase should be valid but with warning
                    self.assertTrue(result.valid)
                    self.assertGreater(len(result.warnings), 0)
                elif name == 'test--suite':
                    # Consecutive hyphens should be valid but with warning
                    self.assertTrue(result.valid)
                    self.assertGreater(len(result.warnings), 0)
                else:
                    self.assertFalse(result.valid, f"Name '{name}' should be invalid")


class TestScenarioPathValidator(unittest.TestCase):
    """Test cases for ScenarioPathValidator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create test feature files
        os.makedirs('tests', exist_ok=True)
        with open('tests/valid.feature', 'w') as f:
            f.write('Feature: Valid test\n  Scenario: Test scenario\n    Given something\n')
        
        with open('tests/empty.feature', 'w') as f:
            f.write('')
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_valid_scenario_paths(self):
        """Test validation of valid scenario paths"""
        result = ScenarioPathValidator.validate(['tests.valid'], self.temp_dir)
        
        self.assertTrue(result.valid)
        self.assertEqual(result.details['valid_paths'], 1)
        self.assertEqual(len(result.details['missing_files']), 0)
    
    def test_missing_scenario_files(self):
        """Test validation with missing feature files"""
        result = ScenarioPathValidator.validate(['tests.missing'], self.temp_dir)
        
        self.assertFalse(result.valid)
        self.assertIn('Missing feature files', result.errors[0])
        self.assertGreater(len(result.details['missing_files']), 0)
    
    def test_empty_scenario_paths(self):
        """Test validation with empty scenario paths list"""
        result = ScenarioPathValidator.validate([], self.temp_dir)
        
        self.assertFalse(result.valid)
        self.assertIn('At least one scenario path', result.errors[0])
    
    def test_empty_feature_file_warning(self):
        """Test warning for empty feature file"""
        result = ScenarioPathValidator.validate(['tests.empty'], self.temp_dir)
        
        self.assertTrue(result.valid)  # File exists but empty
        self.assertGreater(len(result.warnings), 0)
        self.assertIn('empty', result.warnings[0])


class TestTagValidator(unittest.TestCase):
    """Test cases for TagValidator"""
    
    def test_valid_tags(self):
        """Test validation of valid tags"""
        result = TagValidator.validate(
            include_tags=['smoke', 'regression', 'api-v1'],
            exclude_tags=['slow', 'unstable']
        )
        
        self.assertTrue(result.valid)
        self.assertEqual(result.details['include_count'], 3)
        self.assertEqual(result.details['exclude_count'], 2)
    
    def test_invalid_tag_format(self):
        """Test validation of invalid tag formats"""
        result = TagValidator.validate(
            include_tags=['valid-tag', 'invalid tag', '@invalid'],
            exclude_tags=['valid_tag']
        )
        
        self.assertFalse(result.valid)
        self.assertIn('Invalid include tags', result.errors[0])
    
    def test_conflicting_tags(self):
        """Test validation of conflicting include/exclude tags"""
        result = TagValidator.validate(
            include_tags=['smoke', 'regression'],
            exclude_tags=['smoke', 'slow']
        )
        
        self.assertFalse(result.valid)
        self.assertIn('cannot be both included and excluded', result.errors[0])
        self.assertIn('smoke', result.details['conflicts'])
    
    def test_reserved_tags_warning(self):
        """Test warning for reserved tags"""
        result = TagValidator.validate(
            include_tags=['smoke', 'skip'],
            exclude_tags=[]
        )
        
        self.assertTrue(result.valid)
        self.assertGreater(len(result.warnings), 0)
        self.assertIn('reserved tags', result.warnings[0])


class TestEnvironmentValidator(unittest.TestCase):
    """Test cases for EnvironmentValidator"""
    
    def test_valid_environment_params(self):
        """Test validation of valid environment parameters"""
        params = {
            'base_url': 'https://example.com',
            'timeout': '30',
            'browser': 'chrome'
        }
        
        result = EnvironmentValidator.validate(params, 'DEV')
        
        self.assertTrue(result.valid)
        self.assertEqual(result.details['param_count'], 3)
        self.assertEqual(result.details['environment'], 'DEV')
    
    def test_invalid_parameter_names(self):
        """Test validation of invalid parameter names"""
        params = {
            'valid_param': 'value',
            '123invalid': 'value',  # starts with number
            'invalid-param': 'value'  # contains hyphen
        }
        
        result = EnvironmentValidator.validate(params)
        
        self.assertFalse(result.valid)
        self.assertIn('Invalid parameter names', result.errors[0])
    
    def test_sensitive_parameter_warning(self):
        """Test warning for potentially sensitive parameters"""
        params = {
            'api_password': 'secret',
            'auth_token': 'token123',
            'secret_key': 'key456'
        }
        
        result = EnvironmentValidator.validate(params)
        
        self.assertTrue(result.valid)
        self.assertGreater(len(result.warnings), 0)
        self.assertIn('sensitive parameters', result.warnings[0])
    
    def test_non_standard_environment_warning(self):
        """Test warning for non-standard environment names"""
        result = EnvironmentValidator.validate({}, 'CUSTOM_ENV')
        
        self.assertTrue(result.valid)
        self.assertGreater(len(result.warnings), 0)
        self.assertIn('Non-standard environment', result.warnings[0])


class TestSuiteConfigurationValidator(unittest.TestCase):
    """Test cases for comprehensive suite configuration validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create test feature file
        os.makedirs('tests', exist_ok=True)
        with open('tests/demo.feature', 'w') as f:
            f.write('Feature: Demo\n  Scenario: Test\n    Given something\n')
        
        self.validator = SuiteConfigurationValidator(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_valid_configuration(self):
        """Test validation of valid configuration"""
        config = SuiteConfiguration(
            name='valid-suite',
            description='A valid test suite',
            scenario_paths=['tests.demo'],
            include_tags=['smoke'],
            exclude_tags=['slow'],
            environment_params={'env': 'test'},
            execution_config=ExecutionConfig(environment='DEV')
        )
        
        result = self.validator.validate(config)
        
        self.assertTrue(result.valid)
        self.assertEqual(result.details['configuration']['name'], 'valid-suite')
    
    def test_configuration_with_warnings(self):
        """Test configuration that's valid but has warnings"""
        config = SuiteConfiguration(
            name='UPPERCASE-SUITE',  # Should warn about uppercase
            description='',  # Should warn about empty description
            scenario_paths=['tests.demo'],
            include_tags=['smoke'],
            exclude_tags=[],
            environment_params={},
            execution_config=ExecutionConfig(
                timeout_seconds=7200,  # Should warn about long timeout
                max_retries=10  # Should warn about high retry count
            )
        )
        
        result = self.validator.validate(config)
        
        self.assertTrue(result.valid)
        self.assertGreater(len(result.warnings), 0)
    
    def test_invalid_configuration(self):
        """Test validation of invalid configuration"""
        config = SuiteConfiguration(
            name='',  # Invalid empty name
            description='Test',
            scenario_paths=['tests.nonexistent'],  # Missing file
            include_tags=['invalid tag'],  # Invalid tag format
            exclude_tags=[],
            environment_params={'123invalid': 'value'},  # Invalid param name
            execution_config=ExecutionConfig()
        )
        
        result = self.validator.validate(config)
        
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_compatibility_validation(self):
        """Test compatibility validation"""
        config = SuiteConfiguration(
            name='test-suite',
            description='Test',
            scenario_paths=['tests.demo'],
            include_tags=[],
            exclude_tags=[],
            environment_params={},
            execution_config=ExecutionConfig()
        )
        
        result = self.validator.validate_compatibility(config)
        
        # Should be valid but may have warnings about missing files
        self.assertTrue(result.valid)
        self.assertIn('python_version', result.details)


class TestValidationUtilities(unittest.TestCase):
    """Test cases for validation utility functions"""
    
    def test_raise_for_validation_result_valid(self):
        """Test raise_for_validation_result with valid result"""
        result = ValidationResult(valid=True, errors=[], warnings=[], details={})
        
        # Should not raise any exception
        try:
            raise_for_validation_result(result, "test operation")
        except Exception:
            self.fail("Should not raise exception for valid result")
    
    def test_raise_for_validation_result_invalid(self):
        """Test raise_for_validation_result with invalid result"""
        result = ValidationResult(valid=False, errors=['Error 1', 'Error 2'], warnings=[], details={})
        
        with self.assertRaises(SuiteValidationError) as ctx:
            raise_for_validation_result(result, "test operation")
        
        self.assertIn("test operation", str(ctx.exception))
        self.assertEqual(len(ctx.exception.validation_errors), 2)
    
    def test_validate_suite_configuration_convenience_function(self):
        """Test the convenience validation function"""
        config = SuiteConfiguration(
            name='test-suite',
            description='Test suite',
            scenario_paths=[],  # Invalid empty paths
            include_tags=[],
            exclude_tags=[],
            environment_params={},
            execution_config=ExecutionConfig()
        )
        
        result = validate_suite_configuration(config)
        
        self.assertFalse(result.valid)
        self.assertIn('At least one scenario path', result.errors[0])


if __name__ == '__main__':
    unittest.main()