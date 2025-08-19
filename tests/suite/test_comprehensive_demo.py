#!/usr/bin/env python3
"""
Comprehensive demonstration test for the Test Suite Management feature
This test demonstrates all major functionality working together
"""

import os
import tempfile
import unittest
import shutil
from unittest.mock import patch

from qaf.automation.suite.manager import SuiteManager
from qaf.automation.suite.executor import SuiteExecutor
from qaf.automation.suite.parser import (
    SuiteConfiguration, ExecutionConfig, TimeoutConfig, 
    RetryConfig, EnvironmentConfig, EnvironmentProfile
)
from qaf.automation.suite.ci_integration import CIIntegrator, CIExecutionConfig


class TestSuiteManagementDemo(unittest.TestCase):
    """Comprehensive demonstration of test suite management functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create necessary directories
        os.makedirs('test-suites', exist_ok=True)
        os.makedirs('tests', exist_ok=True)
        os.makedirs('reports/allure-results', exist_ok=True)
        
        # Create mock feature files
        self.create_mock_features()
        
        self.suite_manager = SuiteManager()
        self.suite_executor = SuiteExecutor(self.suite_manager)
        self.ci_integrator = CIIntegrator(self.suite_executor)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_mock_features(self):
        """Create mock feature files"""
        login_feature = '''Feature: Login
@smoke @regression
Scenario: Valid login
    Given I am on login page
    When I enter valid credentials
    Then I should be logged in
'''
        
        api_feature = '''Feature: API Tests
@api @regression
Scenario: Get user data
    Given I have API access
    When I request user data
    Then I get valid response
'''
        
        with open('tests/login.feature', 'w') as f:
            f.write(login_feature)
        
        with open('tests/api.feature', 'w') as f:
            f.write(api_feature)
    
    def test_complete_suite_management_workflow(self):
        """Test complete suite management workflow from creation to execution"""
        
        print("\n=== Test Suite Management Feature Demonstration ===")
        
        # 1. Create basic smoke test suite
        print("\n1. Creating basic smoke test suite...")
        smoke_suite = SuiteConfiguration(
            name="demo-smoke-tests",
            description="Demonstration smoke test suite",
            scenario_paths=["tests.login"],
            include_tags=["smoke"],
            exclude_tags=["manual"],
            environment_params={
                "base_url": "https://demo.saucedemo.com",
                "browser": "chrome"
            }
        )
        
        success = self.suite_manager.create_suite(smoke_suite)
        self.assertTrue(success)
        print("[OK] Basic smoke test suite created successfully")
        
        # 2. Create advanced regression suite with execution config
        print("\n2. Creating advanced regression suite with timeout and retry...")
        timeout_config = TimeoutConfig(suite_seconds=1800, scenario_seconds=300)
        retry_config = RetryConfig(max_attempts=2, retry_on_failure=True)
        env_config = EnvironmentConfig(default_environment="staging")
        env_config.variables["API_TIMEOUT"] = "30"
        env_config.variables["staging.DB_HOST"] = "staging-db.example.com"
        
        staging_profile = EnvironmentProfile("staging")
        staging_profile.properties["LOG_LEVEL"] = "INFO"
        staging_profile.properties["SCREENSHOT_ON_FAILURE"] = "true"
        env_config.profiles["staging"] = staging_profile
        
        exec_config = ExecutionConfig(
            stop_on_first_failure=False,
            timeout=timeout_config,
            retry=retry_config,
            environment=env_config
        )
        
        regression_suite = SuiteConfiguration(
            name="demo-regression-tests",
            description="Advanced regression suite with execution configuration",
            scenario_paths=["tests.login", "tests.api"],
            include_tags=["regression"],
            exclude_tags=["experimental"],
            execution_config=exec_config,
            environment_params={
                "base_url": "https://staging.saucedemo.com",
                "browser": "firefox"
            }
        )
        
        success = self.suite_manager.create_suite(regression_suite)
        self.assertTrue(success)
        print("[OK] Advanced regression suite created with execution configuration")
        
        # 3. List and verify suites
        print("\n3. Listing created suites...")
        suite_names = self.suite_manager.list_suites()
        self.assertIn("demo-smoke-tests", suite_names)
        self.assertIn("demo-regression-tests", suite_names)
        print(f"[OK] Found {len(suite_names)} suites: {', '.join(suite_names)}")
        
        # 4. Validate suites
        print("\n4. Validating suite configurations...")
        for suite_name in suite_names:
            validation = self.suite_manager.validate_suite(suite_name)
            self.assertTrue(validation['valid'])
            print(f"[OK] Suite '{suite_name}' validation passed")
        
        # 5. Execute smoke tests
        print("\n5. Executing smoke test suite...")
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "2 scenarios passed, 0 failed, 0 skipped"
            mock_run.return_value.stderr = ""
            
            result = self.suite_executor.execute_suite("demo-smoke-tests")
            
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.passed, 2)
            self.assertEqual(result.failed, 0)
            print("[OK] Smoke tests executed successfully (2 scenarios passed)")
            
            # Verify command structure
            called_command = mock_run.call_args[0][0]
            command_str = ' '.join(called_command)
            self.assertIn('--tags', command_str)
            self.assertIn('smoke', command_str)
            self.assertIn('base_url=https://demo.saucedemo.com', command_str)
            print("[OK] Command structure validated (tags and parameters included)")
        
        # 6. Execute regression tests with retry
        print("\n6. Testing advanced execution with retry logic...")
        with patch('subprocess.run') as mock_run, \
             patch('time.sleep') as mock_sleep:
            
            # Simulate failure then success
            mock_run.side_effect = [
                # First attempt: partial failure
                type('Result', (), {'returncode': 0, 'stdout': '3 scenarios passed, 1 failed', 'stderr': ''})(),
                # Second attempt: success
                type('Result', (), {'returncode': 0, 'stdout': '4 scenarios passed, 0 failed', 'stderr': ''})()
            ]
            
            result = self.suite_executor.execute_suite_with_retry(regression_suite)
            
            self.assertEqual(mock_run.call_count, 2)
            self.assertEqual(result.passed, 4)
            self.assertEqual(result.failed, 0)
            print("[OK] Retry logic executed successfully (failed first, passed on retry)")
        
        # 7. Test CI/CD integration
        print("\n7. Testing CI/CD integration...")
        ci_config = CIExecutionConfig(
            fail_fast=True,
            output_formats=['junit', 'json'],
            environment_variables={'CI_BUILD': 'demo-123'}
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "4 scenarios passed, 0 failed"
            mock_run.return_value.stderr = ""
            
            ci_result = self.ci_integrator.execute_suite_for_ci(regression_suite, ci_config)
            
            self.assertTrue(ci_result.success)
            self.assertEqual(ci_result.exit_code, 0)
            self.assertGreater(len(ci_result.artifacts_generated), 0)
            print("[OK] CI/CD integration successful with artifact generation")
        
        # 8. Update suite configuration
        print("\n8. Testing suite update functionality...")
        updated_config = self.suite_manager.update_suite(
            "demo-smoke-tests",
            description="Updated smoke test suite with API tests",
            scenario_paths=["tests.login", "tests.api"],
            include_tags=["smoke", "api"],
            environment_params={
                "base_url": "https://demo.saucedemo.com",
                "browser": "chrome",
                "api_timeout": "30"
            }
        )
        self.assertIsNotNone(updated_config)
        
        # Verify update
        retrieved_config = self.suite_manager.get_suite("demo-smoke-tests")
        self.assertEqual(len(retrieved_config.scenario_paths), 2)
        self.assertIn("api", retrieved_config.include_tags)
        self.assertIn("api_timeout", retrieved_config.environment_params)
        print("[OK] Suite update successful (added API tests and parameters)")
        
        # 9. Test suite deletion
        print("\n9. Testing suite deletion...")
        success = self.suite_manager.delete_suite("demo-regression-tests")
        self.assertTrue(success)
        
        remaining_suites = self.suite_manager.list_suites()
        self.assertNotIn("demo-regression-tests", remaining_suites)
        self.assertEqual(len(remaining_suites), 1)
        print("[OK] Suite deletion successful")
        
        # 10. Test export/import functionality
        print("\n10. Testing XML export functionality...")
        from qaf.automation.suite.parser import SuiteConfigurationParser
        
        parser = SuiteConfigurationParser()
        export_path = "exported-suite.xml"
        
        final_config = self.suite_manager.get_suite("demo-smoke-tests")
        parser.export_suite_config(final_config, export_path)
        
        # Verify export by re-importing
        imported_config = parser.parse_suite_config(export_path)
        self.assertEqual(imported_config.name, final_config.name)
        self.assertEqual(imported_config.description, final_config.description)
        self.assertEqual(len(imported_config.scenario_paths), len(final_config.scenario_paths))
        print("[OK] XML export/import functionality verified")
        
        print("\n=== Test Suite Management Feature Demo Complete ===")
        print("[SUCCESS] All core functionality demonstrated successfully!")
        print(f"   - Suite creation (basic and advanced)")
        print(f"   - XML configuration with timeout/retry/environment settings")
        print(f"   - Suite validation and listing")
        print(f"   - Test execution with mocked behave commands")
        print(f"   - Advanced retry logic")
        print(f"   - CI/CD integration with artifact generation")
        print(f"   - Suite update and modification")
        print(f"   - Suite deletion")
        print(f"   - XML export/import functionality")
        print(f"   - Environment variable and profile management")
        print(f"   - Tag-based filtering")
        print(f"   - Command parameter injection")


if __name__ == '__main__':
    unittest.main(verbosity=2)