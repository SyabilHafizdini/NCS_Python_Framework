#!/usr/bin/env python3
"""
End-to-end test scenarios for test suite management feature
"""

import os
import tempfile
import unittest
import shutil
import subprocess
from unittest.mock import patch, MagicMock

from qaf.automation.suite.manager import SuiteManager
from qaf.automation.suite.executor import SuiteExecutor
from qaf.automation.suite.parser import SuiteConfiguration, ExecutionConfig
from qaf.automation.suite.ci_integration import CIIntegrator, CIExecutionConfig


class TestEndToEndScenarios(unittest.TestCase):
    """End-to-end test scenarios that simulate real-world usage"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create realistic project structure
        self.setup_realistic_project()
        
        self.suite_manager = SuiteManager()
        self.suite_executor = SuiteExecutor(self.suite_manager)
        self.ci_integrator = CIIntegrator(self.suite_executor)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def setup_realistic_project(self):
        """Set up a realistic project structure"""
        
        # Create directories
        directories = [
            'test-suites',
            'tests/login',
            'tests/checkout', 
            'tests/api',
            'tests/mobile',
            'reports/allure-results',
            'reports/test_reports'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # Create realistic feature files
        features = {
            'tests/login/user_login.feature': '''Feature: User Login
    As a user
    I want to login to the application
    So that I can access my account

    @smoke @login @regression
    Scenario: Successful login with valid credentials
        Given I am on the login page
        When I enter valid username "standard_user"
        And I enter valid password "secret_sauce"
        And I click the login button
        Then I should be redirected to the dashboard
        And I should see the products page

    @login @regression @negative
    Scenario: Failed login with invalid credentials
        Given I am on the login page
        When I enter invalid username "invalid_user"
        And I enter invalid password "wrong_password"
        And I click the login button
        Then I should see an error message
        And I should remain on the login page

    @login @edge_case
    Scenario: Login with empty credentials
        Given I am on the login page
        When I leave username field empty
        And I leave password field empty
        And I click the login button
        Then I should see validation errors
''',
            
            'tests/checkout/shopping_cart.feature': '''Feature: Shopping Cart
    As a customer
    I want to manage items in my shopping cart
    So that I can purchase products

    @smoke @cart @regression
    Scenario: Add items to cart
        Given I am logged in as a standard user
        And I am on the products page
        When I add "Sauce Labs Backpack" to cart
        And I add "Sauce Labs Bike Light" to cart
        Then the cart should show 2 items
        And the cart icon should display "2"

    @cart @regression
    Scenario: Remove items from cart
        Given I am logged in as a standard user
        And I have items in my cart
        When I remove "Sauce Labs Backpack" from cart
        Then the cart should show 1 item
        And the removed item should not be visible

    @checkout @regression @e2e
    Scenario: Complete checkout process
        Given I am logged in as a standard user
        And I have items in my cart
        When I proceed to checkout
        And I fill in checkout information
        And I complete the purchase
        Then I should see order confirmation
        And the cart should be empty
''',
            
            'tests/api/user_api.feature': '''Feature: User API
    As an API client
    I want to interact with user endpoints
    So that I can manage user data

    @api @smoke @regression
    Scenario: Get user profile
        Given I have valid API credentials
        When I send GET request to "/api/users/profile"
        Then I should receive 200 status code
        And the response should contain user data

    @api @regression
    Scenario: Update user profile
        Given I have valid API credentials
        And I have user profile data
        When I send PUT request to "/api/users/profile"
        Then I should receive 200 status code
        And the user data should be updated

    @api @security
    Scenario: Access protected endpoint without authentication
        Given I have no authentication token
        When I send GET request to "/api/users/profile"
        Then I should receive 401 status code
        And the response should contain authentication error
''',
            
            'tests/mobile/mobile_login.feature': '''Feature: Mobile Login
    As a mobile user
    I want to login through mobile app
    So that I can access mobile features

    @mobile @smoke @regression
    Scenario: Mobile login with touch gestures
        Given I am on the mobile login screen
        When I tap on username field
        And I enter username "mobile_user"
        And I tap on password field
        And I enter password "mobile_password"
        And I tap the login button
        Then I should see the mobile dashboard

    @mobile @regression
    Scenario: Mobile login with biometric authentication
        Given I am on the mobile login screen
        And biometric authentication is enabled
        When I tap on biometric login
        And I provide valid biometric data
        Then I should be logged in automatically
'''
        }
        
        # Write feature files
        for file_path, content in features.items():
            with open(file_path, 'w') as f:
                f.write(content)
        
        # Create behave.ini
        behave_ini = '''[behave]
format = allure_behave.formatter:AllureFormatter
outfiles = reports/allure-results
show_timings = true
logging_level = INFO
show_skipped = false
'''
        with open('behave.ini', 'w') as f:
            f.write(behave_ini)
        
        # Create environment.py
        environment_py = '''import os
from datetime import datetime

def before_all(context):
    """Setup before all tests"""
    context.test_start_time = datetime.now()
    print(f"Test execution started at {context.test_start_time}")

def after_all(context):
    """Cleanup after all tests"""
    test_end_time = datetime.now()
    duration = test_end_time - context.test_start_time
    print(f"Test execution completed at {test_end_time}")
    print(f"Total execution time: {duration}")

def before_scenario(context, scenario):
    """Setup before each scenario"""
    print(f"Starting scenario: {scenario.name}")

def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    print(f"Completed scenario: {scenario.name} - Status: {scenario.status}")
'''
        with open('tests/environment.py', 'w') as f:
            f.write(environment_py)
    
    def test_smoke_test_suite_execution(self):
        """Test execution of smoke test suite"""
        
        # Create smoke test suite
        smoke_suite = SuiteConfiguration(
            name="smoke-tests",
            description="Smoke test suite for critical functionality",
            scenario_paths=[
                "tests.login.user_login",
                "tests.checkout.shopping_cart",
                "tests.api.user_api"
            ],
            include_tags=["smoke"],
            exclude_tags=["manual", "experimental"],
            environment_params={
                "base_url": "https://www.saucedemo.com",
                "browser": "chrome",
                "timeout": "30",
                "screenshot_on_failure": "true"
            }
        )
        
        # Create the suite
        success = self.suite_manager.create_suite(smoke_suite)
        self.assertTrue(success)
        
        # Mock execution
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "5 scenarios passed, 0 failed, 0 skipped"
            mock_run.return_value.stderr = ""
            
            result = self.suite_executor.execute_suite("smoke-tests")
            
            self.assertEqual(result.suite_name, "smoke-tests")
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.passed, 5)
            self.assertEqual(result.failed, 0)
            
            # Verify command structure
            called_command = mock_run.call_args[0][0]
            command_str = ' '.join(called_command)
            
            self.assertIn('--tags', command_str)
            self.assertIn('smoke', command_str)
            self.assertIn('-D', command_str)
            self.assertIn('base_url=https://www.saucedemo.com', command_str)
    
    def test_regression_test_suite_execution(self):
        """Test execution of comprehensive regression suite"""
        
        # Create regression test suite with advanced configuration
        from qaf.automation.suite.parser import TimeoutConfig, RetryConfig, EnvironmentConfig
        
        timeout_config = TimeoutConfig(
            suite_seconds=3600,  # 1 hour
            scenario_seconds=300,  # 5 minutes
            step_seconds=30
        )
        
        retry_config = RetryConfig(
            max_attempts=2,
            delay_seconds=10,
            retry_on_failure=True,
            retry_on_error=True
        )
        
        exec_config = ExecutionConfig(
            stop_on_first_failure=False,
            continue_on_error=False,
            max_parallel_threads=1,
            timeout=timeout_config,
            retry=retry_config
        )
        
        regression_suite = SuiteConfiguration(
            name="regression-tests",
            description="Comprehensive regression test suite",
            scenario_paths=[
                "tests.login.user_login",
                "tests.checkout.shopping_cart",
                "tests.api.user_api",
                "tests.mobile.mobile_login"
            ],
            include_tags=["regression"],
            exclude_tags=["experimental", "manual", "performance"],
            execution_config=exec_config,
            environment_params={
                "base_url": "https://staging.saucedemo.com",
                "browser": "firefox",
                "timeout": "60",
                "screenshot_on_failure": "true",
                "video_recording": "true"
            }
        )
        
        # Create and execute the suite
        success = self.suite_manager.create_suite(regression_suite)
        self.assertTrue(success)
        
        # Mock execution with some failures and retry
        with patch('subprocess.run') as mock_run, \
             patch('time.sleep') as mock_sleep:
            
            # First attempt: some failures
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout="8 scenarios passed, 2 failed, 0 skipped", stderr=""),
                MagicMock(returncode=0, stdout="10 scenarios passed, 0 failed, 0 skipped", stderr="")
            ]
            
            result = self.suite_executor.execute_suite_with_retry(regression_suite)
            
            # Should have retried due to failures
            self.assertEqual(mock_run.call_count, 2)
            mock_sleep.assert_called_once_with(10)  # Retry delay
            
            # Final result should be successful
            self.assertEqual(result.passed, 10)
            self.assertEqual(result.failed, 0)
    
    def test_api_test_suite_execution(self):
        """Test execution of API-only test suite"""
        
        api_suite = SuiteConfiguration(
            name="api-tests",
            description="API testing suite",
            scenario_paths=["tests.api.user_api"],
            include_tags=["api"],
            exclude_tags=["ui", "mobile"],
            environment_params={
                "api_base_url": "https://api.saucedemo.com",
                "api_version": "v1",
                "authentication": "bearer_token",
                "timeout": "15",
                "rate_limit": "100"
            }
        )
        
        success = self.suite_manager.create_suite(api_suite)
        self.assertTrue(success)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "3 scenarios passed, 0 failed, 0 skipped"
            mock_run.return_value.stderr = ""
            
            result = self.suite_executor.execute_suite("api-tests")
            
            self.assertEqual(result.passed, 3)
            self.assertEqual(result.failed, 0)
            
            # Verify API-specific parameters were included
            called_command = mock_run.call_args[0][0]
            command_str = ' '.join(called_command)
            
            self.assertIn('api_base_url=https://api.saucedemo.com', command_str)
            self.assertIn('api_version=v1', command_str)
    
    def test_mobile_test_suite_execution(self):
        """Test execution of mobile-specific test suite"""
        
        mobile_suite = SuiteConfiguration(
            name="mobile-tests",
            description="Mobile application testing suite",
            scenario_paths=["tests.mobile.mobile_login"],
            include_tags=["mobile"],
            exclude_tags=["web", "api"],
            environment_params={
                "platform": "Android",
                "device_name": "Pixel_4",
                "app_package": "com.saucelabs.mydemoapp.rn",
                "automation_name": "UiAutomator2",
                "timeout": "45"
            }
        )
        
        success = self.suite_manager.create_suite(mobile_suite)
        self.assertTrue(success)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "2 scenarios passed, 0 failed, 0 skipped"
            mock_run.return_value.stderr = ""
            
            result = self.suite_executor.execute_suite("mobile-tests")
            
            self.assertEqual(result.passed, 2)
            self.assertEqual(result.failed, 0)
            
            # Verify mobile-specific parameters
            called_command = mock_run.call_args[0][0]
            command_str = ' '.join(called_command)
            
            self.assertIn('platform=Android', command_str)
            self.assertIn('device_name=Pixel_4', command_str)
    
    def test_ci_cd_execution_workflow(self):
        """Test complete CI/CD execution workflow"""
        
        # Create suite for CI/CD
        ci_suite = SuiteConfiguration(
            name="ci-regression",
            description="CI/CD regression test suite",
            scenario_paths=[
                "tests.login.user_login",
                "tests.api.user_api"
            ],
            include_tags=["regression", "smoke"],
            exclude_tags=["manual", "experimental", "performance"]
        )
        
        success = self.suite_manager.create_suite(ci_suite)
        self.assertTrue(success)
        
        # Configure CI execution
        ci_config = CIExecutionConfig(
            fail_fast=True,
            continue_on_error=False,
            retry_count=1,
            output_formats=['allure', 'junit', 'json'],
            environment_variables={
                'CI_BUILD_NUMBER': '123',
                'CI_BRANCH': 'feature/test-suite-management',
                'CI_COMMIT_SHA': 'abc123def456'
            }
        )
        
        # Mock CI environment
        with patch.dict(os.environ, {
            'GITHUB_ACTIONS': 'true',
            'GITHUB_RUN_NUMBER': '123',
            'GITHUB_REF_NAME': 'feature/test-suite-management',
            'GITHUB_SHA': 'abc123def456'
        }):
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "6 scenarios passed, 0 failed, 0 skipped"
                mock_run.return_value.stderr = ""
                
                ci_result = self.ci_integrator.execute_suite_for_ci(ci_suite, ci_config)
                
                self.assertTrue(ci_result.success)
                self.assertEqual(ci_result.exit_code, 0)
                self.assertEqual(ci_result.ci_environment.provider, 'github')
                self.assertGreater(len(ci_result.artifacts_generated), 0)
                
                # Verify environment variables were applied
                self.assertIn('CI_BUILD_NUMBER', ci_suite.environment_params)
                self.assertEqual(ci_suite.environment_params['CI_BUILD_NUMBER'], '123')
    
    def test_suite_management_operations(self):
        """Test comprehensive suite management operations"""
        
        # Create multiple suites for management testing
        suites_data = [
            {
                'name': 'daily-smoke',
                'description': 'Daily smoke test execution',
                'paths': ['tests.login.user_login'],
                'tags': ['smoke']
            },
            {
                'name': 'weekly-regression',
                'description': 'Weekly regression test execution',
                'paths': ['tests.login.user_login', 'tests.checkout.shopping_cart'],
                'tags': ['regression']
            },
            {
                'name': 'api-validation',
                'description': 'API validation and testing',
                'paths': ['tests.api.user_api'],
                'tags': ['api']
            }
        ]
        
        created_suites = []
        
        # Create all suites
        for suite_data in suites_data:
            config = SuiteConfiguration(
                name=suite_data['name'],
                description=suite_data['description'],
                scenario_paths=suite_data['paths'],
                include_tags=suite_data['tags']
            )
            
            success = self.suite_manager.create_suite(config)
            self.assertTrue(success)
            created_suites.append(suite_data['name'])
        
        # Test listing suites
        suite_list = self.suite_manager.list_suites()
        suite_names = [s['name'] for s in suite_list]
        
        for suite_name in created_suites:
            self.assertIn(suite_name, suite_names)
        
        # Test suite details
        for suite_name in created_suites:
            details = self.suite_manager.get_suite_details(suite_name)
            self.assertIsNotNone(details)
            self.assertEqual(details['name'], suite_name)
            self.assertIn('description', details)
            self.assertIn('scenario_paths', details)
            self.assertIn('include_tags', details)
        
        # Test suite validation
        for suite_name in created_suites:
            validation = self.suite_manager.validate_suite(suite_name)
            self.assertTrue(validation['valid'])
            self.assertEqual(len(validation['errors']), 0)
        
        # Test suite update
        updated_config = SuiteConfiguration(
            name='daily-smoke',
            description='Updated daily smoke test execution',
            scenario_paths=['tests.login.user_login', 'tests.api.user_api'],
            include_tags=['smoke', 'critical']
        )
        
        success = self.suite_manager.update_suite('daily-smoke', updated_config)
        self.assertTrue(success)
        
        # Verify update
        updated_details = self.suite_manager.get_suite_details('daily-smoke')
        self.assertEqual(updated_details['description'], 'Updated daily smoke test execution')
        self.assertEqual(len(updated_details['scenario_paths']), 2)
        self.assertIn('critical', updated_details['include_tags'])
        
        # Test suite deletion
        success = self.suite_manager.delete_suite('api-validation')
        self.assertTrue(success)
        
        # Verify deletion
        remaining_suites = self.suite_manager.list_suites()
        remaining_names = [s['name'] for s in remaining_suites]
        self.assertNotIn('api-validation', remaining_names)
        self.assertEqual(len(remaining_suites), 2)
    
    def test_error_recovery_scenarios(self):
        """Test error recovery and handling scenarios"""
        
        # Test execution with system failures
        problematic_suite = SuiteConfiguration(
            name="error-prone-suite",
            scenario_paths=["tests.login.user_login"],
            include_tags=["smoke"]
        )
        
        self.suite_manager.create_suite(problematic_suite)
        
        # Test timeout scenario
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(['behave'], 30)
            
            result = self.suite_executor.execute_suite("error-prone-suite")
            
            self.assertEqual(result.exit_code, 124)  # Timeout exit code
            self.assertIn("timed out", ' '.join(result.error_details).lower())
        
        # Test command execution failure
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, ['behave'])
            
            result = self.suite_executor.execute_suite("error-prone-suite")
            
            self.assertNotEqual(result.exit_code, 0)
            self.assertGreater(len(result.error_details), 0)
        
        # Test invalid suite execution
        with self.assertRaises(Exception):
            self.suite_executor.execute_suite("non-existent-suite")


if __name__ == '__main__':
    unittest.main()