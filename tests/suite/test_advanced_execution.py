#!/usr/bin/env python3
"""
Unit tests for advanced execution configuration features
"""

import os
import tempfile
import unittest
import shutil
from unittest.mock import patch, MagicMock

from qaf.automation.suite.parser import (
    SuiteConfiguration, ExecutionConfig, TimeoutConfig, 
    RetryConfig, EnvironmentConfig, EnvironmentProfile,
    SuiteConfigurationParser
)
from qaf.automation.suite.executor import SuiteExecutor, ExecutionResult


class TestAdvancedExecutionConfig(unittest.TestCase):
    """Test cases for advanced execution configuration"""
    
    def test_timeout_config_defaults(self):
        """Test default timeout configuration values"""
        timeout_config = TimeoutConfig()
        
        self.assertEqual(timeout_config.suite_seconds, 3600)
        self.assertEqual(timeout_config.scenario_seconds, 300)
        self.assertEqual(timeout_config.step_seconds, 30)
    
    def test_timeout_config_custom_values(self):
        """Test custom timeout configuration values"""
        timeout_config = TimeoutConfig(
            suite_seconds=7200,
            scenario_seconds=600,
            step_seconds=60
        )
        
        self.assertEqual(timeout_config.suite_seconds, 7200)
        self.assertEqual(timeout_config.scenario_seconds, 600)
        self.assertEqual(timeout_config.step_seconds, 60)
    
    def test_retry_config_defaults(self):
        """Test default retry configuration values"""
        retry_config = RetryConfig()
        
        self.assertEqual(retry_config.max_attempts, 1)
        self.assertEqual(retry_config.delay_seconds, 5)
        self.assertFalse(retry_config.retry_on_failure)
        self.assertTrue(retry_config.retry_on_error)
    
    def test_retry_config_custom_values(self):
        """Test custom retry configuration values"""
        retry_config = RetryConfig(
            max_attempts=3,
            delay_seconds=10,
            retry_on_failure=True,
            retry_on_error=False
        )
        
        self.assertEqual(retry_config.max_attempts, 3)
        self.assertEqual(retry_config.delay_seconds, 10)
        self.assertTrue(retry_config.retry_on_failure)
        self.assertFalse(retry_config.retry_on_error)
    
    def test_environment_profile(self):
        """Test environment profile configuration"""
        profile = EnvironmentProfile(
            name="production",
            extends="staging"
        )
        profile.properties["DB_HOST"] = "prod.example.com"
        profile.properties["LOG_LEVEL"] = "ERROR"
        
        self.assertEqual(profile.name, "production")
        self.assertEqual(profile.extends, "staging")
        self.assertEqual(profile.properties["DB_HOST"], "prod.example.com")
        self.assertEqual(profile.properties["LOG_LEVEL"], "ERROR")
    
    def test_environment_config(self):
        """Test environment configuration"""
        env_config = EnvironmentConfig(default_environment="staging")
        
        # Add environment variables
        env_config.variables["GLOBAL_VAR"] = "global_value"
        env_config.variables["test.TEST_VAR"] = "test_value"
        env_config.variables["prod.PROD_VAR"] = "prod_value"
        
        # Add profiles
        test_profile = EnvironmentProfile("test")
        test_profile.properties["DB_HOST"] = "test.example.com"
        env_config.profiles["test"] = test_profile
        
        self.assertEqual(env_config.default_environment, "staging")
        self.assertEqual(env_config.variables["GLOBAL_VAR"], "global_value")
        self.assertEqual(env_config.variables["test.TEST_VAR"], "test_value")
        self.assertIn("test", env_config.profiles)
    
    def test_execution_config_advanced(self):
        """Test advanced execution configuration"""
        timeout_config = TimeoutConfig(suite_seconds=1800)
        retry_config = RetryConfig(max_attempts=2, retry_on_failure=True)
        env_config = EnvironmentConfig(default_environment="test")
        
        exec_config = ExecutionConfig(
            stop_on_first_failure=True,
            continue_on_error=False,
            max_parallel_threads=2,
            timeout=timeout_config,
            retry=retry_config,
            environment=env_config
        )
        
        self.assertTrue(exec_config.stop_on_first_failure)
        self.assertFalse(exec_config.continue_on_error)
        self.assertEqual(exec_config.max_parallel_threads, 2)
        self.assertEqual(exec_config.timeout.suite_seconds, 1800)
        self.assertEqual(exec_config.retry.max_attempts, 2)
        self.assertEqual(exec_config.environment.default_environment, "test")
    
    def test_execution_config_backward_compatibility(self):
        """Test backward compatibility with legacy execution config"""
        exec_config = ExecutionConfig(
            stop_on_failure=True,
            max_retries=2,
            timeout_seconds=1800
        )
        
        # Check backward compatibility mapping
        self.assertTrue(exec_config.stop_on_first_failure)
        self.assertEqual(exec_config.retry.max_attempts, 3)  # max_retries + 1
        self.assertEqual(exec_config.timeout.suite_seconds, 1800)


class TestAdvancedXMLParsing(unittest.TestCase):
    """Test cases for parsing advanced execution configuration from XML"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.parser = SuiteConfigurationParser()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_parse_execution_config_xml(self):
        """Test parsing execution configuration from XML"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<suite name="advanced-test-suite">
    <description>Test suite with advanced execution configuration</description>
    <execution stopOnFirstFailure="true" continueOnError="false" maxParallelThreads="2">
        <timeout suite="1800" scenario="600" step="60"/>
        <retry maxAttempts="3" delaySeconds="10" retryOnFailure="true" retryOnError="false"/>
        <environment default="staging">
            <variable name="GLOBAL_VAR" value="global_value"/>
            <variable name="BASE_URL" value="test.example.com" environment="test"/>
            <variable name="BASE_URL" value="prod.example.com" environment="prod"/>
            <profile name="test" extends="base">
                <property name="DB_HOST" value="test-db.example.com"/>
                <property name="LOG_LEVEL" value="DEBUG"/>
            </profile>
            <profile name="prod">
                <property name="DB_HOST" value="prod-db.example.com"/>
                <property name="LOG_LEVEL" value="ERROR"/>
            </profile>
        </environment>
    </execution>
    <test name="advanced-tests">
        <classes>
            <class name="tests.advanced"/>
        </classes>
    </test>
</suite>'''
        
        xml_path = os.path.join(self.temp_dir, 'advanced_suite.xml')
        with open(xml_path, 'w') as f:
            f.write(xml_content)
        
        config = self.parser.parse_suite_config(xml_path)
        
        self.assertEqual(config.name, "advanced-test-suite")
        self.assertTrue(config.execution_config.stop_on_first_failure)
        self.assertFalse(config.execution_config.continue_on_error)
        self.assertEqual(config.execution_config.max_parallel_threads, 2)
        
        # Check timeout configuration
        self.assertEqual(config.execution_config.timeout.suite_seconds, 1800)
        self.assertEqual(config.execution_config.timeout.scenario_seconds, 600)
        self.assertEqual(config.execution_config.timeout.step_seconds, 60)
        
        # Check retry configuration
        self.assertEqual(config.execution_config.retry.max_attempts, 3)
        self.assertEqual(config.execution_config.retry.delay_seconds, 10)
        self.assertTrue(config.execution_config.retry.retry_on_failure)
        self.assertFalse(config.execution_config.retry.retry_on_error)
        
        # Check environment configuration
        self.assertEqual(config.execution_config.environment.default_environment, "staging")
        self.assertEqual(config.execution_config.environment.variables["GLOBAL_VAR"], "global_value")
        self.assertEqual(config.execution_config.environment.variables["test.BASE_URL"], "test.example.com")
        self.assertEqual(config.execution_config.environment.variables["prod.BASE_URL"], "prod.example.com")
        
        # Check profiles
        self.assertIn("test", config.execution_config.environment.profiles)
        self.assertIn("prod", config.execution_config.environment.profiles)
        
        test_profile = config.execution_config.environment.profiles["test"]
        self.assertEqual(test_profile.name, "test")
        self.assertEqual(test_profile.extends, "base")
        self.assertEqual(test_profile.properties["DB_HOST"], "test-db.example.com")
        self.assertEqual(test_profile.properties["LOG_LEVEL"], "DEBUG")
    
    def test_parse_legacy_execution_config(self):
        """Test parsing legacy execution configuration from parameters"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<suite name="legacy-test-suite">
    <description>Test suite with legacy execution configuration</description>
    <parameters>
        <parameter name="stop_on_failure" value="true"/>
        <parameter name="retry_count" value="2"/>
        <parameter name="timeout" value="1800"/>
    </parameters>
    <test name="legacy-tests">
        <classes>
            <class name="tests.legacy"/>
        </classes>
    </test>
</suite>'''
        
        xml_path = os.path.join(self.temp_dir, 'legacy_suite.xml')
        with open(xml_path, 'w') as f:
            f.write(xml_content)
        
        config = self.parser.parse_suite_config(xml_path)
        
        self.assertEqual(config.name, "legacy-test-suite")
        self.assertTrue(config.execution_config.stop_on_failure)
        self.assertEqual(config.execution_config.max_retries, 2)
        self.assertEqual(config.execution_config.timeout_seconds, 1800)
        
        # Check that backward compatibility is maintained
        self.assertTrue(config.execution_config.stop_on_first_failure)
        self.assertEqual(config.execution_config.retry.max_attempts, 3)  # 2 + 1
        self.assertEqual(config.execution_config.timeout.suite_seconds, 1800)
    
    def test_export_advanced_execution_config(self):
        """Test exporting advanced execution configuration to XML"""
        # Create configuration with advanced settings
        timeout_config = TimeoutConfig(suite_seconds=1800, scenario_seconds=600, step_seconds=60)
        retry_config = RetryConfig(max_attempts=3, delay_seconds=10, retry_on_failure=True)
        env_config = EnvironmentConfig(default_environment="test")
        
        env_config.variables["GLOBAL_VAR"] = "global_value"
        env_config.variables["test.TEST_VAR"] = "test_value"
        
        test_profile = EnvironmentProfile("test")
        test_profile.properties["DB_HOST"] = "test.example.com"
        env_config.profiles["test"] = test_profile
        
        exec_config = ExecutionConfig(
            stop_on_first_failure=True,
            max_parallel_threads=2,
            timeout=timeout_config,
            retry=retry_config,
            environment=env_config
        )
        
        config = SuiteConfiguration(
            name="export-test-suite",
            description="Test suite for export",
            scenario_paths=["tests.export"],
            execution_config=exec_config
        )
        
        # Export to XML
        output_path = os.path.join(self.temp_dir, 'exported_suite.xml')
        self.parser.export_suite_config(config, output_path)
        
        # Parse back and verify
        parsed_config = self.parser.parse_suite_config(output_path)
        
        self.assertEqual(parsed_config.name, "export-test-suite")
        self.assertTrue(parsed_config.execution_config.stop_on_first_failure)
        self.assertEqual(parsed_config.execution_config.max_parallel_threads, 2)
        self.assertEqual(parsed_config.execution_config.timeout.suite_seconds, 1800)
        self.assertEqual(parsed_config.execution_config.retry.max_attempts, 3)
        self.assertEqual(parsed_config.execution_config.environment.default_environment, "test")


class TestAdvancedExecutor(unittest.TestCase):
    """Test cases for advanced executor functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.executor = SuiteExecutor()
        
        # Create mock suite configuration
        self.timeout_config = TimeoutConfig(suite_seconds=1800)
        self.retry_config = RetryConfig(max_attempts=2, retry_on_failure=True)
        self.env_config = EnvironmentConfig()
        self.env_config.variables["TEST_VAR"] = "test_value"
        self.env_config.variables["staging.STAGING_VAR"] = "staging_value"
        
        test_profile = EnvironmentProfile("test")
        test_profile.properties["DB_HOST"] = "test.example.com"
        self.env_config.profiles["test"] = test_profile
        
        self.exec_config = ExecutionConfig(
            stop_on_first_failure=True,
            timeout=self.timeout_config,
            retry=self.retry_config,
            environment=self.env_config
        )
        
        self.suite_config = SuiteConfiguration(
            name="test-suite",
            scenario_paths=["tests.advanced"],
            execution_config=self.exec_config
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_execution_timeout(self):
        """Test timeout calculation for execution"""
        timeout = self.executor._get_execution_timeout(self.exec_config)
        self.assertEqual(timeout, 1800)
        
        # Test legacy timeout
        legacy_config = ExecutionConfig(timeout_seconds=3600)
        timeout = self.executor._get_execution_timeout(legacy_config)
        self.assertEqual(timeout, 3600)
        
        # Test no timeout
        no_timeout_config = ExecutionConfig()
        timeout = self.executor._get_execution_timeout(no_timeout_config)
        self.assertIsNone(timeout)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_apply_environment_config(self):
        """Test application of environment configuration"""
        self.executor._apply_environment_config(self.exec_config)
        
        # Check global variables
        self.assertEqual(os.environ.get("TEST_VAR"), "test_value")
        
        # Check environment-specific variables (should not be applied since ENVIRONMENT is not set)
        self.assertNotIn("STAGING_VAR", os.environ)
        
        # Check profile properties (should be applied since default is 'test')
        self.assertEqual(os.environ.get("DB_HOST"), "test.example.com")
    
    @patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=True)
    def test_apply_environment_config_staging(self):
        """Test application of environment configuration for staging environment"""
        self.executor._apply_environment_config(self.exec_config)
        
        # Check global variables
        self.assertEqual(os.environ.get("TEST_VAR"), "test_value")
        
        # Check environment-specific variables
        self.assertEqual(os.environ.get("STAGING_VAR"), "staging_value")
    
    def test_get_environment_variables_for_execution(self):
        """Test getting environment variables for execution"""
        env_vars = self.executor.get_environment_variables_for_execution(self.suite_config)
        
        # Should include global variables and test profile properties
        self.assertEqual(env_vars["TEST_VAR"], "test_value")
        self.assertEqual(env_vars["DB_HOST"], "test.example.com")
        
        # Should not include staging-specific variables
        self.assertNotIn("STAGING_VAR", env_vars)
    
    @patch('time.sleep')
    @patch('qaf.automation.suite.executor.SuiteExecutor.execute_suite_config')
    def test_execute_suite_with_retry_success_first_attempt(self, mock_execute, mock_sleep):
        """Test retry execution with success on first attempt"""
        # Mock successful execution
        mock_execute.return_value = ExecutionResult(
            suite_name="test-suite",
            exit_code=0,
            passed=5,
            failed=0
        )
        
        result = self.executor.execute_suite_with_retry(self.suite_config)
        
        # Should only execute once
        self.assertEqual(mock_execute.call_count, 1)
        mock_sleep.assert_not_called()
        self.assertEqual(result.exit_code, 0)
    
    @patch('time.sleep')
    @patch('qaf.automation.suite.executor.SuiteExecutor.execute_suite_config')
    def test_execute_suite_with_retry_failure_then_success(self, mock_execute, mock_sleep):
        """Test retry execution with failure then success"""
        # Mock execution that fails first time, succeeds second time
        mock_execute.side_effect = [
            ExecutionResult(suite_name="test-suite", exit_code=0, passed=3, failed=2),
            ExecutionResult(suite_name="test-suite", exit_code=0, passed=5, failed=0)
        ]
        
        result = self.executor.execute_suite_with_retry(self.suite_config)
        
        # Should execute twice
        self.assertEqual(mock_execute.call_count, 2)
        mock_sleep.assert_called_once()
        self.assertEqual(result.failed, 0)  # Final result should be successful
    
    @patch('time.sleep')
    @patch('qaf.automation.suite.executor.SuiteExecutor.execute_suite_config')
    def test_execute_suite_with_retry_max_attempts(self, mock_execute, mock_sleep):
        """Test retry execution reaching max attempts"""
        # Mock execution that always fails
        mock_execute.return_value = ExecutionResult(
            suite_name="test-suite",
            exit_code=0,
            passed=3,
            failed=2
        )
        
        result = self.executor.execute_suite_with_retry(self.suite_config)
        
        # Should execute max_attempts times
        self.assertEqual(mock_execute.call_count, 2)
        self.assertEqual(mock_sleep.call_count, 1)
        self.assertEqual(result.failed, 2)  # Should return final failed result
    
    def test_check_stop_on_first_failure(self):
        """Test stop on first failure checking"""
        # Test with failure
        failed_result = ExecutionResult(suite_name="test", failed=1)
        should_stop = self.executor.check_stop_on_first_failure(self.suite_config, failed_result)
        self.assertTrue(should_stop)
        
        # Test with success
        success_result = ExecutionResult(suite_name="test", failed=0, exit_code=0)
        should_stop = self.executor.check_stop_on_first_failure(self.suite_config, success_result)
        self.assertFalse(should_stop)
        
        # Test with system error
        error_result = ExecutionResult(suite_name="test", exit_code=1)
        should_stop = self.executor.check_stop_on_first_failure(self.suite_config, error_result)
        self.assertTrue(should_stop)
    
    def test_check_stop_on_first_failure_disabled(self):
        """Test stop on first failure when disabled"""
        # Create config without stop on first failure
        config_no_stop = SuiteConfiguration(
            name="test-suite",
            execution_config=ExecutionConfig(stop_on_first_failure=False)
        )
        
        failed_result = ExecutionResult(suite_name="test", failed=1)
        should_stop = self.executor.check_stop_on_first_failure(config_no_stop, failed_result)
        self.assertFalse(should_stop)


if __name__ == '__main__':
    unittest.main()