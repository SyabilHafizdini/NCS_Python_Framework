#!/usr/bin/env python3
"""
Integration tests for the complete test suite management workflow
"""

import os
import tempfile
import unittest
import shutil
import json
from unittest.mock import patch, MagicMock

from qaf.automation.suite.manager import SuiteManager
from qaf.automation.suite.executor import SuiteExecutor, ExecutionResult
from qaf.automation.suite.parser import SuiteConfiguration, ExecutionConfig
from qaf.automation.suite.repository import SuiteRepository
from qaf.automation.suite.ci_integration import CIIntegrator, CIExecutionConfig


class TestSuiteManagementWorkflow(unittest.TestCase):
    """Integration tests for complete suite management workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create necessary directories
        os.makedirs('test-suites', exist_ok=True)
        os.makedirs('tests', exist_ok=True)
        os.makedirs('reports/allure-results', exist_ok=True)
        
        # Create mock feature files
        self.create_mock_feature_files()
        
        # Initialize components
        self.suite_manager = SuiteManager()
        self.suite_executor = SuiteExecutor(self.suite_manager)
        self.ci_integrator = CIIntegrator(self.suite_executor)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_mock_feature_files(self):
        """Create mock feature files for testing"""
        # Create login feature
        login_feature = '''Feature: Login functionality
    @smoke @regression
    Scenario: Successful login
        Given I am on the login page
        When I enter valid credentials
        Then I should be logged in successfully
        
    @regression
    Scenario: Invalid login
        Given I am on the login page
        When I enter invalid credentials
        Then I should see an error message
'''
        
        # Create checkout feature
        checkout_feature = '''Feature: Checkout functionality
    @regression @e2e
    Scenario: Complete checkout process
        Given I am logged in
        When I add items to cart
        And I proceed to checkout
        Then I should complete the purchase
        
    @regression
    Scenario: Checkout with empty cart
        Given I am logged in
        When I try to checkout with empty cart
        Then I should see an empty cart message
'''
        
        # Create API tests feature
        api_feature = '''Feature: API tests
    @api @regression
    Scenario: Get user data
        Given I have valid API credentials
        When I request user data
        Then I should receive valid response
        
    @api @smoke
    Scenario: Create new user
        Given I have admin credentials
        When I create a new user
        Then the user should be created successfully
'''
        
        # Write feature files
        with open('tests/login.feature', 'w') as f:
            f.write(login_feature)
        
        with open('tests/checkout.feature', 'w') as f:
            f.write(checkout_feature)
        
        with open('tests/api_tests.feature', 'w') as f:
            f.write(api_feature)
    
    def test_complete_suite_lifecycle(self):
        """Test complete suite lifecycle: create, validate, execute"""
        
        # Step 1: Create a new test suite
        suite_config = SuiteConfiguration(
            name="integration-test-suite",
            description="Integration test suite for workflow validation",
            scenario_paths=["tests.login", "tests.checkout"],
            include_tags=["regression"],
            exclude_tags=["manual"],
            environment_params={
                "base_url": "https://test.example.com",
                "browser": "chrome"
            }
        )
        
        # Save the suite
        success = self.suite_manager.create_suite(suite_config)
        self.assertTrue(success)
        
        # Step 2: Validate the suite exists and is valid
        saved_config = self.suite_manager.get_suite("integration-test-suite")
        self.assertIsNotNone(saved_config)
        self.assertEqual(saved_config.name, "integration-test-suite")
        
        validation = self.suite_manager.validate_suite("integration-test-suite")
        self.assertTrue(validation['valid'])
        
        # Step 3: List suites and verify our suite is there
        suite_names = self.suite_manager.list_suites()
        self.assertIn("integration-test-suite", suite_names)
        
        # Step 4: Mock execution and verify command building
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "3 scenarios passed, 0 failed, 0 skipped"
            mock_run.return_value.stderr = ""
            
            result = self.suite_executor.execute_suite("integration-test-suite")
            
            self.assertEqual(result.suite_name, "integration-test-suite")
            self.assertEqual(result.exit_code, 0)
            
            # Verify the command was built correctly
            mock_run.assert_called_once()
            called_command = mock_run.call_args[0][0]
            
            # Check basic command structure
            self.assertIn('python', called_command[0])
            self.assertIn('behave', called_command[2])
            
            # Check tags are included
            command_str = ' '.join(called_command)
            self.assertIn('--tags', command_str)
            self.assertIn('regression', command_str)
            
            # Check environment parameters
            self.assertIn('-D', command_str)
            self.assertIn('base_url=https://test.example.com', command_str)
    
    def test_advanced_suite_with_execution_config(self):
        """Test suite with advanced execution configuration"""
        
        # Create suite with advanced execution config
        exec_config = ExecutionConfig(
            stop_on_first_failure=True,
            max_parallel_threads=2
        )
        
        suite_config = SuiteConfiguration(
            name="advanced-test-suite",
            description="Advanced test suite with execution config",
            scenario_paths=["tests.api_tests"],
            include_tags=["api", "smoke"],
            execution_config=exec_config,
            environment_params={
                "api_base_url": "https://api.test.example.com",
                "timeout": "30"
            }
        )
        
        # Save and validate
        success = self.suite_manager.create_suite(suite_config)
        self.assertTrue(success)
        
        # Mock execution with stop on first failure
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "2 scenarios passed, 0 failed"
            mock_run.return_value.stderr = ""
            
            result = self.suite_executor.execute_suite("advanced-test-suite")
            
            # Verify stop flag was added to command
            called_command = mock_run.call_args[0][0]
            self.assertIn('--stop', called_command)
    
    def test_suite_with_retry_execution(self):
        """Test suite execution with retry logic"""
        
        from qaf.automation.suite.parser import RetryConfig
        
        # Create suite with retry configuration
        retry_config = RetryConfig(
            max_attempts=3,
            delay_seconds=1,  # Short delay for testing
            retry_on_failure=True
        )
        
        exec_config = ExecutionConfig(retry=retry_config)
        
        suite_config = SuiteConfiguration(
            name="retry-test-suite",
            description="Test suite with retry logic",
            scenario_paths=["tests.login"],
            include_tags=["smoke"],
            execution_config=exec_config
        )
        
        self.suite_manager.create_suite(suite_config)
        
        # Mock execution that fails twice then succeeds
        with patch('subprocess.run') as mock_run, \
             patch('time.sleep') as mock_sleep:
            
            mock_run.side_effect = [
                # First attempt: failure
                MagicMock(returncode=0, stdout="1 scenario passed, 1 failed", stderr=""),
                # Second attempt: failure
                MagicMock(returncode=0, stdout="1 scenario passed, 1 failed", stderr=""),
                # Third attempt: success
                MagicMock(returncode=0, stdout="2 scenarios passed, 0 failed", stderr="")
            ]
            
            result = self.suite_executor.execute_suite_with_retry(suite_config)
            
            # Should have executed 3 times
            self.assertEqual(mock_run.call_count, 3)
            # Should have slept twice (between attempts)
            self.assertEqual(mock_sleep.call_count, 2)
            # Final result should be successful
            self.assertEqual(result.failed, 0)
    
    def test_ci_integration_workflow(self):
        """Test CI/CD integration workflow"""
        
        # Create suite for CI execution
        suite_config = SuiteConfiguration(
            name="ci-test-suite",
            description="Test suite for CI/CD integration",
            scenario_paths=["tests.api_tests"],
            include_tags=["api", "regression"]
        )
        
        self.suite_manager.create_suite(suite_config)
        
        # Create CI configuration
        ci_config = CIExecutionConfig(
            fail_fast=False,
            output_formats=['junit', 'json'],
            environment_variables={'CI_BUILD': 'true'}
        )
        
        # Mock successful execution
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "5 scenarios passed, 0 failed"
            mock_run.return_value.stderr = ""
            
            ci_result = self.ci_integrator.execute_suite_for_ci(suite_config, ci_config)
            
            self.assertTrue(ci_result.success)
            self.assertEqual(ci_result.exit_code, 0)
            self.assertGreater(len(ci_result.artifacts_generated), 0)
            
            # Verify environment variables were applied
            self.assertIn('CI_BUILD', suite_config.environment_params)
    
    def test_error_handling_workflow(self):
        """Test error handling throughout the workflow"""
        
        # Test invalid suite name
        with self.assertRaises(Exception):
            self.suite_manager.get_suite("non-existent-suite")
        
        # Test invalid scenario paths
        invalid_config = SuiteConfiguration(
            name="invalid-suite",
            scenario_paths=["non_existent.feature"]
        )
        
        success = self.suite_manager.create_suite(invalid_config)
        self.assertTrue(success)  # Should create but validation will fail
        
        validation = self.suite_manager.validate_suite("invalid-suite")
        self.assertFalse(validation['valid'])
        self.assertGreater(len(validation['errors']), 0)
    
    def test_suite_update_workflow(self):
        """Test suite update and modification workflow"""
        
        # Create initial suite
        original_config = SuiteConfiguration(
            name="updatable-suite",
            description="Original description",
            scenario_paths=["tests.login"],
            include_tags=["smoke"]
        )
        
        self.suite_manager.create_suite(original_config)
        
        # Update the suite
        updated_config = SuiteConfiguration(
            name="updatable-suite",
            description="Updated description",
            scenario_paths=["tests.login", "tests.checkout"],
            include_tags=["smoke", "regression"],
            environment_params={"updated": "true"}
        )
        
        success = self.suite_manager.update_suite("updatable-suite", updated_config)
        self.assertTrue(success)
        
        # Verify the update
        retrieved_config = self.suite_manager.get_suite("updatable-suite")
        self.assertEqual(retrieved_config.description, "Updated description")
        self.assertEqual(len(retrieved_config.scenario_paths), 2)
        self.assertIn("regression", retrieved_config.include_tags)
        self.assertEqual(retrieved_config.environment_params["updated"], "true")
    
    def test_multiple_suites_management(self):
        """Test managing multiple test suites"""
        
        # Create multiple suites
        suites = [
            SuiteConfiguration(
                name="smoke-suite",
                description="Smoke test suite",
                scenario_paths=["tests.login"],
                include_tags=["smoke"]
            ),
            SuiteConfiguration(
                name="regression-suite",
                description="Regression test suite",
                scenario_paths=["tests.login", "tests.checkout"],
                include_tags=["regression"]
            ),
            SuiteConfiguration(
                name="api-suite",
                description="API test suite",
                scenario_paths=["tests.api_tests"],
                include_tags=["api"]
            )
        ]
        
        # Create all suites
        for suite in suites:
            success = self.suite_manager.create_suite(suite)
            self.assertTrue(success)
        
        # Verify all suites exist
        suite_names = self.suite_manager.list_suites()
        
        self.assertIn("smoke-suite", suite_names)
        self.assertIn("regression-suite", suite_names)
        self.assertIn("api-suite", suite_names)
        self.assertEqual(len(suite_names), 3)
        
        # Test suite deletion
        success = self.suite_manager.delete_suite("api-suite")
        self.assertTrue(success)
        
        updated_names = self.suite_manager.list_suites()
        self.assertNotIn("api-suite", updated_names)
        self.assertEqual(len(updated_names), 2)


class TestPerformanceAndScalability(unittest.TestCase):
    """Test performance and scalability aspects"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('test-suites', exist_ok=True)
        os.makedirs('tests', exist_ok=True)
        
        self.suite_manager = SuiteManager()
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_large_suite_configuration(self):
        """Test handling of large suite configurations"""
        
        # Create a large suite with many scenario paths and tags
        large_scenario_paths = [f"tests.module_{i}" for i in range(100)]
        large_include_tags = [f"tag_{i}" for i in range(50)]
        large_exclude_tags = [f"exclude_{i}" for i in range(25)]
        large_env_params = {f"param_{i}": f"value_{i}" for i in range(200)}
        
        large_config = SuiteConfiguration(
            name="large-test-suite",
            description="Large test suite for performance testing",
            scenario_paths=large_scenario_paths,
            include_tags=large_include_tags,
            exclude_tags=large_exclude_tags,
            environment_params=large_env_params
        )
        
        # Test creation and retrieval performance
        import time
        
        start_time = time.time()
        success = self.suite_manager.create_suite(large_config)
        creation_time = time.time() - start_time
        
        self.assertTrue(success)
        self.assertLess(creation_time, 5.0)  # Should complete within 5 seconds
        
        start_time = time.time()
        retrieved_config = self.suite_manager.get_suite("large-test-suite")
        retrieval_time = time.time() - start_time
        
        self.assertIsNotNone(retrieved_config)
        self.assertLess(retrieval_time, 2.0)  # Should complete within 2 seconds
        
        # Verify data integrity
        self.assertEqual(len(retrieved_config.scenario_paths), 100)
        self.assertEqual(len(retrieved_config.include_tags), 50)
        self.assertEqual(len(retrieved_config.environment_params), 200)
    
    def test_concurrent_suite_operations(self):
        """Test concurrent suite operations"""
        
        import threading
        import time
        
        results = []
        errors = []
        
        def create_suite(suite_id):
            try:
                config = SuiteConfiguration(
                    name=f"concurrent-suite-{suite_id}",
                    description=f"Concurrent test suite {suite_id}",
                    scenario_paths=[f"tests.concurrent_{suite_id}"],
                    include_tags=[f"concurrent_{suite_id}"]
                )
                success = self.suite_manager.create_suite(config)
                results.append((suite_id, success))
            except Exception as e:
                errors.append((suite_id, str(e)))
        
        # Create multiple threads to create suites concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_suite, args=(i,))
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Verify results
        self.assertEqual(len(results), 10)
        self.assertEqual(len(errors), 0)
        self.assertLess(total_time, 10.0)  # Should complete within 10 seconds
        
        # Verify all suites were created successfully
        for suite_id, success in results:
            self.assertTrue(success)
            
            # Verify suite exists
            config = self.suite_manager.get_suite(f"concurrent-suite-{suite_id}")
            self.assertIsNotNone(config)


class TestCompatibilityAndRegression(unittest.TestCase):
    """Test compatibility and regression scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        os.makedirs('test-suites', exist_ok=True)
        os.makedirs('tests', exist_ok=True)
        
        # Create behave.ini to test compatibility
        behave_ini_content = '''[behave]
format = allure_behave.formatter:AllureFormatter
outfiles = reports/allure-results
show_timings = true
logging_level = INFO
'''
        with open('behave.ini', 'w') as f:
            f.write(behave_ini_content)
        
        # Create environment.py to test compatibility
        env_py_content = '''import os
from datetime import datetime

def before_all(context):
    """Setup before all tests"""
    print("Setting up test environment")

def after_all(context):
    """Cleanup after all tests"""
    print("Cleaning up test environment")
'''
        os.makedirs('tests', exist_ok=True)
        with open('tests/environment.py', 'w') as f:
            f.write(env_py_content)
        
        self.suite_executor = SuiteExecutor()
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_behave_ini_compatibility(self):
        """Test that existing behave.ini configuration is preserved"""
        
        # Validate execution environment
        validation = self.suite_executor.validate_execution_environment()
        
        self.assertTrue(validation['environment_info']['behave_ini_exists'])
        self.assertTrue(validation['environment_info']['allure_formatter_configured'])
        self.assertTrue(validation['environment_info']['allure_output_configured'])
    
    def test_environment_py_compatibility(self):
        """Test that existing tests/environment.py is preserved"""
        
        validation = self.suite_executor.validate_execution_environment()
        self.assertTrue(validation['environment_info']['environment_py_exists'])
    
    def test_legacy_execution_methods(self):
        """Test that legacy execution methods still work"""
        
        # Create a simple suite with legacy execution config
        from qaf.automation.suite.parser import SuiteConfiguration, ExecutionConfig
        
        legacy_config = SuiteConfiguration(
            name="legacy-suite",
            scenario_paths=["tests.legacy"],
            execution_config=ExecutionConfig(
                stop_on_failure=True,  # Legacy field
                max_retries=2,         # Legacy field
                timeout_seconds=1800   # Legacy field
            )
        )
        
        # Verify that legacy fields are mapped to new fields
        self.assertTrue(legacy_config.execution_config.stop_on_first_failure)
        self.assertEqual(legacy_config.execution_config.retry.max_attempts, 3)  # 2 + 1
        self.assertEqual(legacy_config.execution_config.timeout.suite_seconds, 1800)
    
    def test_backwards_compatible_xml_parsing(self):
        """Test parsing of legacy XML format"""
        
        legacy_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<suite name="legacy-xml-suite">
    <description>Legacy XML format test</description>
    <parameters>
        <parameter name="stop_on_failure" value="true"/>
        <parameter name="retry_count" value="1"/>
        <parameter name="timeout" value="3600"/>
        <parameter name="env" value="test"/>
    </parameters>
    <test name="legacy-tests">
        <classes>
            <class name="tests.legacy_test"/>
        </classes>
        <groups>
            <run>
                <include name="smoke"/>
                <exclude name="manual"/>
            </run>
        </groups>
    </test>
</suite>'''
        
        xml_path = os.path.join(self.temp_dir, 'legacy_suite.xml')
        with open(xml_path, 'w') as f:
            f.write(legacy_xml)
        
        from qaf.automation.suite.parser import SuiteConfigurationParser
        parser = SuiteConfigurationParser()
        
        config = parser.parse_suite_config(xml_path)
        
        # Verify legacy parameters are parsed correctly
        self.assertEqual(config.name, "legacy-xml-suite")
        self.assertTrue(config.execution_config.stop_on_failure)
        self.assertEqual(config.execution_config.max_retries, 1)
        self.assertEqual(config.execution_config.timeout_seconds, 3600)
        
        # Verify backward compatibility mapping
        self.assertTrue(config.execution_config.stop_on_first_failure)


if __name__ == '__main__':
    unittest.main()