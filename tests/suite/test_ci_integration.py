#!/usr/bin/env python3
"""
Unit tests for CI/CD integration system
"""

import os
import tempfile
import unittest
import shutil
import json
from unittest.mock import patch, MagicMock

from qaf.automation.suite.ci_integration import (
    CIEnvironment, CIExecutionConfig, CIExecutionResult, CIIntegrator,
    get_ci_exit_code, create_ci_config_from_env
)
from qaf.automation.suite.parser import SuiteConfiguration, ExecutionConfig
from qaf.automation.suite.executor import ExecutionResult


class TestCIEnvironment(unittest.TestCase):
    """Test cases for CI environment detection"""
    
    def test_detect_jenkins_environment(self):
        """Test Jenkins environment detection"""
        with patch.dict(os.environ, {
            'JENKINS_URL': 'http://jenkins.example.com',
            'BUILD_NUMBER': '123',
            'BUILD_URL': 'http://jenkins.example.com/job/test/123/',
            'GIT_BRANCH': 'main',
            'GIT_COMMIT': 'abc123',
            'JOB_NAME': 'test-job',
            'WORKSPACE': '/var/jenkins/workspace/test',
            'NODE_NAME': 'worker-1'
        }, clear=True):
            env = CIEnvironment.detect_environment()
            
            self.assertEqual(env.provider, 'jenkins')
            self.assertEqual(env.build_number, '123')
            self.assertEqual(env.build_url, 'http://jenkins.example.com/job/test/123/')
            self.assertEqual(env.branch, 'main')
            self.assertEqual(env.commit_hash, 'abc123')
            self.assertEqual(env.job_name, 'test-job')
            self.assertEqual(env.workspace, '/var/jenkins/workspace/test')
            self.assertEqual(env.node_name, 'worker-1')
    
    def test_detect_github_actions_environment(self):
        """Test GitHub Actions environment detection"""
        with patch.dict(os.environ, {
            'GITHUB_ACTIONS': 'true',
            'GITHUB_RUN_NUMBER': '42',
            'GITHUB_SERVER_URL': 'https://github.com',
            'GITHUB_REPOSITORY': 'user/repo',
            'GITHUB_RUN_ID': '987654321',
            'GITHUB_REF_NAME': 'feature-branch',
            'GITHUB_SHA': 'def456',
            'GITHUB_PR_NUMBER': '15',
            'GITHUB_JOB': 'test',
            'GITHUB_WORKSPACE': '/github/workspace'
        }, clear=True):
            env = CIEnvironment.detect_environment()
            
            self.assertEqual(env.provider, 'github')
            self.assertEqual(env.build_number, '42')
            self.assertIn('github.com/user/repo/actions/runs/987654321', env.build_url)
            self.assertEqual(env.branch, 'feature-branch')
            self.assertEqual(env.commit_hash, 'def456')
            self.assertEqual(env.pull_request, '15')
    
    def test_detect_gitlab_ci_environment(self):
        """Test GitLab CI environment detection"""
        with patch.dict(os.environ, {
            'GITLAB_CI': 'true',
            'CI_PIPELINE_ID': '789',
            'CI_PIPELINE_URL': 'https://gitlab.com/project/-/pipelines/789',
            'CI_COMMIT_REF_NAME': 'develop',
            'CI_COMMIT_SHA': 'ghi789',
            'CI_MERGE_REQUEST_IID': '25',
            'CI_JOB_NAME': 'test-job',
            'CI_PROJECT_DIR': '/builds/project',
            'CI_RUNNER_DESCRIPTION': 'runner-1'
        }, clear=True):
            env = CIEnvironment.detect_environment()
            
            self.assertEqual(env.provider, 'gitlab')
            self.assertEqual(env.build_number, '789')
            self.assertEqual(env.build_url, 'https://gitlab.com/project/-/pipelines/789')
            self.assertEqual(env.branch, 'develop')
            self.assertEqual(env.pull_request, '25')
    
    def test_detect_unknown_environment(self):
        """Test unknown environment detection"""
        with patch.dict(os.environ, {}, clear=True):
            env = CIEnvironment.detect_environment()
            
            self.assertEqual(env.provider, 'unknown')
            self.assertIsNotNone(env.workspace)


class TestCIExecutionConfig(unittest.TestCase):
    """Test cases for CI execution configuration"""
    
    def test_default_configuration(self):
        """Test default CI execution configuration"""
        config = CIExecutionConfig()
        
        self.assertFalse(config.fail_fast)
        self.assertFalse(config.continue_on_error)
        self.assertEqual(config.timeout_minutes, 60)
        self.assertEqual(config.retry_count, 0)
        self.assertEqual(config.retry_delay_seconds, 10)
        self.assertIn('allure', config.output_formats)
        self.assertIn('junit', config.output_formats)
    
    def test_custom_configuration(self):
        """Test custom CI execution configuration"""
        config = CIExecutionConfig(
            fail_fast=True,
            retry_count=3,
            output_formats=['json'],
            environment_variables={'TEST_VAR': 'value'}
        )
        
        self.assertTrue(config.fail_fast)
        self.assertEqual(config.retry_count, 3)
        self.assertEqual(config.output_formats, ['json'])
        self.assertEqual(config.environment_variables['TEST_VAR'], 'value')


class TestCIExecutionResult(unittest.TestCase):
    """Test cases for CI execution result"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.execution_result = ExecutionResult(
            exit_code=0,
            duration=30.5,
            scenarios_passed=5,
            scenarios_failed=1,
            scenarios_skipped=0,
            command_output="Test output"
        )
        
        self.ci_environment = CIEnvironment(
            provider='github',
            build_number='123',
            branch='main'
        )
        
        self.ci_result = CIExecutionResult(
            success=True,
            exit_code=0,
            duration_seconds=30.5,
            execution_result=self.execution_result,
            ci_environment=self.ci_environment,
            artifacts_generated=['reports/test.xml']
        )
    
    def test_to_json(self):
        """Test JSON serialization"""
        json_str = self.ci_result.to_json()
        data = json.loads(json_str)
        
        self.assertEqual(data['success'], True)
        self.assertEqual(data['exit_code'], 0)
        self.assertEqual(data['duration_seconds'], 30.5)
        self.assertEqual(data['ci_environment']['provider'], 'github')
        self.assertEqual(data['artifacts_generated'], ['reports/test.xml'])
    
    def test_to_junit_xml(self):
        """Test JUnit XML generation"""
        xml_str = self.ci_result.to_junit_xml()
        
        self.assertIn('<testsuites', xml_str)
        self.assertIn('tests="6"', xml_str)  # 5 passed + 1 failed
        self.assertIn('failures="1"', xml_str)
        self.assertIn('time="30.5"', xml_str)
    
    def test_failed_execution_junit_xml(self):
        """Test JUnit XML for failed execution"""
        failed_result = CIExecutionResult(
            success=False,
            exit_code=1,
            duration_seconds=15.0,
            execution_result=self.execution_result,
            ci_environment=self.ci_environment,
            artifacts_generated=[],
            error_message="Suite execution failed"
        )
        
        xml_str = failed_result.to_junit_xml()
        
        self.assertIn('<failure', xml_str)
        self.assertIn('Suite execution failed', xml_str)
        self.assertIn('Exit code: 1', xml_str)


class TestCIIntegrator(unittest.TestCase):
    """Test cases for CI integrator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create mock suite configuration
        self.suite_config = SuiteConfiguration(
            name='test-suite',
            description='Test suite',
            scenario_paths=['tests.demo'],
            include_tags=['smoke'],
            exclude_tags=[],
            environment_params={},
            execution_config=ExecutionConfig()
        )
        
        # Create test directories
        os.makedirs('reports', exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('qaf.automation.suite.ci_integration.CIIntegrator._get_current_time')
    @patch('qaf.automation.suite.executor.SuiteExecutor.execute_suite')
    def test_execute_suite_for_ci_success(self, mock_execute, mock_time):
        """Test successful CI suite execution"""
        # Mock time
        mock_time.side_effect = [0.0, 30.5]  # start, end
        
        # Mock successful execution
        mock_execute.return_value = ExecutionResult(
            exit_code=0,
            duration=30.5,
            scenarios_passed=5,
            scenarios_failed=0,
            scenarios_skipped=0,
            command_output="All tests passed"
        )
        
        integrator = CIIntegrator()
        ci_config = CIExecutionConfig()
        
        result = integrator.execute_suite_for_ci(self.suite_config, ci_config)
        
        self.assertTrue(result.success)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.duration_seconds, 30.5)
        self.assertEqual(result.execution_result.scenarios_passed, 5)
        self.assertEqual(result.ci_environment.provider, 'unknown')
    
    @patch('qaf.automation.suite.ci_integration.CIIntegrator._get_current_time')
    @patch('qaf.automation.suite.executor.SuiteExecutor.execute_suite')
    def test_execute_suite_for_ci_with_retries(self, mock_execute, mock_time):
        """Test CI suite execution with retries"""
        # Mock time
        mock_time.side_effect = [0.0, 60.0]  # start, end after retries
        
        # Mock execution that fails first time, succeeds second time
        mock_execute.side_effect = [
            ExecutionResult(exit_code=1, duration=15.0, scenarios_passed=0, scenarios_failed=1, scenarios_skipped=0, command_output="Failed"),
            ExecutionResult(exit_code=0, duration=20.0, scenarios_passed=1, scenarios_failed=0, scenarios_skipped=0, command_output="Passed")
        ]
        
        integrator = CIIntegrator()
        ci_config = CIExecutionConfig(retry_count=1, retry_delay_seconds=0)
        
        with patch('time.sleep'):  # Speed up test
            result = integrator.execute_suite_for_ci(self.suite_config, ci_config)
        
        self.assertTrue(result.success)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(mock_execute.call_count, 2)
    
    def test_apply_ci_environment_variables(self):
        """Test application of CI environment variables"""
        integrator = CIIntegrator()
        ci_config = CIExecutionConfig(environment_variables={'CUSTOM_VAR': 'value'})
        
        integrator._apply_ci_environment_variables(self.suite_config, ci_config)
        
        self.assertIn('CI_PROVIDER', self.suite_config.environment_params)
        self.assertIn('CUSTOM_VAR', self.suite_config.environment_params)
        self.assertEqual(self.suite_config.environment_params['CI_PROVIDER'], 'unknown')
        self.assertEqual(self.suite_config.environment_params['CUSTOM_VAR'], 'value')
    
    def test_determine_success_fail_fast(self):
        """Test success determination with fail fast"""
        integrator = CIIntegrator()
        ci_config = CIExecutionConfig(fail_fast=True)
        
        # Success case
        result_success = ExecutionResult(exit_code=0, duration=10, scenarios_passed=5, scenarios_failed=0, scenarios_skipped=0, command_output="")
        self.assertTrue(integrator._determine_success(result_success, ci_config))
        
        # Failure case with fail fast
        result_failure = ExecutionResult(exit_code=0, duration=10, scenarios_passed=4, scenarios_failed=1, scenarios_skipped=0, command_output="")
        self.assertFalse(integrator._determine_success(result_failure, ci_config))
    
    def test_determine_success_continue_on_error(self):
        """Test success determination with continue on error"""
        integrator = CIIntegrator()
        ci_config = CIExecutionConfig(continue_on_error=True)
        
        # Even with failures, should return True
        result_failure = ExecutionResult(exit_code=1, duration=10, scenarios_passed=0, scenarios_failed=5, scenarios_skipped=0, command_output="")
        self.assertTrue(integrator._determine_success(result_failure, ci_config))
    
    def test_generate_ci_artifacts(self):
        """Test CI artifact generation"""
        integrator = CIIntegrator()
        ci_config = CIExecutionConfig(output_formats=['junit', 'json'])
        
        execution_result = ExecutionResult(
            exit_code=0, duration=10, scenarios_passed=3, scenarios_failed=0, scenarios_skipped=0, command_output=""
        )
        
        artifacts = integrator._generate_ci_artifacts(execution_result, ci_config)
        
        # Should generate junit and json files
        junit_generated = any('junit' in artifact for artifact in artifacts)
        json_generated = any('json' in artifact for artifact in artifacts)
        
        self.assertTrue(junit_generated)
        self.assertTrue(json_generated)
    
    def test_get_ci_environment_info(self):
        """Test CI environment information gathering"""
        integrator = CIIntegrator()
        
        info = integrator.get_ci_environment_info()
        
        self.assertIn('detected_provider', info)
        self.assertIn('environment_details', info)
        self.assertIn('available_variables', info)
        self.assertIn('recommendations', info)
        self.assertEqual(info['detected_provider'], 'unknown')
        self.assertIsInstance(info['recommendations'], list)


class TestCIUtilities(unittest.TestCase):
    """Test cases for CI utility functions"""
    
    def test_get_ci_exit_code_success(self):
        """Test CI exit code for successful execution"""
        result = ExecutionResult(
            exit_code=0, duration=10, scenarios_passed=5, scenarios_failed=0, scenarios_skipped=0, command_output=""
        )
        
        exit_code = get_ci_exit_code(result)
        self.assertEqual(exit_code, 0)
    
    def test_get_ci_exit_code_system_failure(self):
        """Test CI exit code for system failure"""
        result = ExecutionResult(
            exit_code=2, duration=10, scenarios_passed=0, scenarios_failed=0, scenarios_skipped=0, command_output=""
        )
        
        exit_code = get_ci_exit_code(result)
        self.assertEqual(exit_code, 2)
    
    def test_get_ci_exit_code_fail_fast(self):
        """Test CI exit code with fail fast enabled"""
        result = ExecutionResult(
            exit_code=0, duration=10, scenarios_passed=4, scenarios_failed=1, scenarios_skipped=0, command_output=""
        )
        
        # Without fail fast
        exit_code = get_ci_exit_code(result, fail_fast=False)
        self.assertEqual(exit_code, 0)
        
        # With fail fast
        exit_code = get_ci_exit_code(result, fail_fast=True)
        self.assertEqual(exit_code, 1)
    
    @patch.dict(os.environ, {
        'QAF_FAIL_FAST': 'true',
        'QAF_RETRY_COUNT': '3',
        'QAF_OUTPUT_FORMATS': 'junit,json',
        'QAF_CUSTOM_VAR': 'test_value'
    })
    def test_create_ci_config_from_env(self):
        """Test CI config creation from environment variables"""
        config = create_ci_config_from_env()
        
        self.assertTrue(config.fail_fast)
        self.assertEqual(config.retry_count, 3)
        self.assertIn('junit', config.output_formats)
        self.assertIn('json', config.output_formats)
        self.assertEqual(config.environment_variables['CUSTOM_VAR'], 'test_value')
    
    @patch.dict(os.environ, {})
    def test_create_ci_config_from_env_defaults(self):
        """Test CI config creation with default values"""
        config = create_ci_config_from_env()
        
        self.assertFalse(config.fail_fast)
        self.assertFalse(config.continue_on_error)
        self.assertEqual(config.retry_count, 0)
        self.assertEqual(config.timeout_minutes, 60)
        self.assertIn('allure', config.output_formats)


class TestCIIntegrationEndToEnd(unittest.TestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create report directories
        os.makedirs('reports/allure-results', exist_ok=True)
        os.makedirs('reports/test_reports', exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('qaf.automation.suite.executor.SuiteExecutor.execute_suite')
    def test_full_ci_workflow(self, mock_execute):
        """Test complete CI workflow"""
        # Mock successful execution
        mock_execute.return_value = ExecutionResult(
            exit_code=0,
            duration=25.0,
            scenarios_passed=10,
            scenarios_failed=0,
            scenarios_skipped=1,
            command_output="Tests completed successfully"
        )
        
        # Create suite configuration
        suite_config = SuiteConfiguration(
            name='full-test-suite',
            description='Full CI test suite',
            scenario_paths=['tests.integration'],
            include_tags=['integration'],
            exclude_tags=['manual'],
            environment_params={'BASE_URL': 'https://test.example.com'},
            execution_config=ExecutionConfig(environment='CI')
        )
        
        # Create CI configuration
        ci_config = CIExecutionConfig(
            fail_fast=False,
            continue_on_error=False,
            retry_count=1,
            output_formats=['allure', 'junit', 'json'],
            environment_variables={'CI_BUILD': 'true'}
        )
        
        # Execute
        integrator = CIIntegrator()
        result = integrator.execute_suite_for_ci(suite_config, ci_config)
        
        # Verify results
        self.assertTrue(result.success)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.execution_result.scenarios_passed, 10)
        self.assertEqual(result.ci_environment.provider, 'unknown')
        self.assertGreater(len(result.artifacts_generated), 0)
        
        # Verify environment variables were applied
        self.assertIn('CI_PROVIDER', suite_config.environment_params)
        self.assertIn('CI_BUILD', suite_config.environment_params)


if __name__ == '__main__':
    unittest.main()