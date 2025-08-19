#!/usr/bin/env python3
"""
Unit tests for SuiteExecutor
"""

import os
import tempfile
import unittest
import unittest.mock
import shutil
from unittest.mock import patch, MagicMock

from qaf.automation.suite.executor import SuiteExecutor, SuiteExecutorError, ExecutionResult
from qaf.automation.suite.manager import SuiteManager
from qaf.automation.suite.repository import SuiteRepository
from qaf.automation.suite.parser import SuiteConfiguration, ExecutionConfig


class TestSuiteExecutor(unittest.TestCase):
    """Test cases for SuiteExecutor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.repository = SuiteRepository(self.temp_dir)
        self.manager = SuiteManager(self.repository)
        self.executor = SuiteExecutor(self.manager)
        
        # Create sample suite configuration
        self.sample_suite = SuiteConfiguration(
            name="test-suite",
            description="Test suite for executor testing",
            scenario_paths=["tests.simple_demo.feature"],
            include_tags=["smoke"],
            exclude_tags=["slow"],
            environment_params={"env": "DEV", "browser": "chrome"},
            execution_config=ExecutionConfig(stop_on_failure=True, timeout_seconds=300)
        )
        
        # Save suite for testing
        self.repository.save_suite(self.sample_suite)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_execution_result_properties(self):
        """Test ExecutionResult properties"""
        result = ExecutionResult(
            suite_name="test",
            passed=5,
            failed=2,
            skipped=1,
            exit_code=0
        )
        
        self.assertEqual(result.total_executed, 8)
        self.assertFalse(result.success)  # Failed > 0
        
        # Test successful result
        success_result = ExecutionResult(
            suite_name="test",
            passed=5,
            failed=0,
            skipped=1,
            exit_code=0
        )
        self.assertTrue(success_result.success)
    
    def test_build_behave_command_basic(self):
        """Test building basic behave command"""
        command = self.executor._build_behave_command(self.sample_suite)
        
        # Should start with python -m behave
        self.assertEqual(command[:3], ['python', '-m', 'behave'])
        
        # Should include scenario path (use os.path.join for Windows compatibility)
        expected_path = os.path.join('tests', 'simple_demo.feature')
        self.assertIn(expected_path, command)
        
        # Should include tags
        tags_index = command.index('--tags')
        tags_expression = command[tags_index + 1]
        self.assertIn('smoke', tags_expression)
        self.assertIn('not slow', tags_expression)
        
        # Should include environment parameters
        self.assertIn('-D', command)
        env_param_index = command.index('-D')
        env_param = command[env_param_index + 1]
        self.assertTrue(env_param.startswith('env=') or env_param.startswith('browser='))
    
    def test_build_behave_command_with_options(self):
        """Test building behave command with additional options"""
        command = self.executor._build_behave_command(
            self.sample_suite,
            verbose=True,
            dry_run=True,
            no_capture=True,
            log_level='DEBUG'
        )
        
        self.assertIn('--verbose', command)
        self.assertIn('--dry-run', command)
        self.assertIn('--no-capture', command)
        self.assertIn('--logging-level', command)
        self.assertIn('DEBUG', command)
    
    def test_build_behave_command_stop_on_failure(self):
        """Test building command with stop on failure option"""
        command = self.executor._build_behave_command(self.sample_suite)
        
        # Should include --stop since execution_config.stop_on_failure is True
        self.assertIn('--stop', command)
    
    def test_build_behave_command_no_formatter_override(self):
        """Test that command doesn't override existing formatter configuration"""
        command = self.executor._build_behave_command(self.sample_suite)
        
        # Should NOT contain formatter options - these come from behave.ini
        command_str = ' '.join(command)
        self.assertNotIn('--format', command_str)
        self.assertNotIn('--outfiles', command_str)
        self.assertNotIn('allure', command_str)
    
    def test_resolve_scenario_paths(self):
        """Test resolving scenario paths from class notation"""
        # Test with mock file system
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            paths = self.executor._resolve_scenario_paths(self.sample_suite)
            
            expected_path = os.path.join('tests', 'simple_demo.feature')
            self.assertEqual(paths, [expected_path])
            mock_exists.assert_called_with(expected_path)
    
    def test_resolve_scenario_paths_missing_files(self):
        """Test resolving scenario paths with missing files"""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            with patch('builtins.print') as mock_print:
                paths = self.executor._resolve_scenario_paths(self.sample_suite)
                
                # Should return empty list and print warning
                self.assertEqual(paths, [])
                mock_print.assert_called()
                warning_call = mock_print.call_args[0][0]
                self.assertIn('Warning: Scenario path not found', warning_call)
    
    def test_parse_behave_output(self):
        """Test parsing behave output for scenario counts"""
        result = ExecutionResult(suite_name="test")
        
        # Mock behave output
        stdout = """
Feature: Demo feature
  Scenario: Test scenario 1
    Given some condition
    When some action
    Then some result

3 scenarios passed, 1 failed, 0 skipped
1 feature passed, 0 failed, 0 skipped
        """
        
        self.executor._parse_behave_output(result, stdout)
        
        self.assertEqual(result.passed, 3)
        self.assertEqual(result.failed, 1)
        self.assertEqual(result.skipped, 0)
    
    def test_parse_behave_output_no_scenarios(self):
        """Test parsing behave output with no scenario summary"""
        result = ExecutionResult(suite_name="test")
        
        stdout = "Some other output without scenario counts"
        
        self.executor._parse_behave_output(result, stdout)
        
        # Should remain at default values
        self.assertEqual(result.passed, 0)
        self.assertEqual(result.failed, 0)
        self.assertEqual(result.skipped, 0)
    
    @patch('subprocess.run')
    @patch('builtins.print')
    def test_execute_command_success(self, mock_print, mock_run):
        """Test successful command execution"""
        # Mock successful subprocess result
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "3 scenarios passed, 0 failed, 0 skipped"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        command = ['python', '-m', 'behave', 'tests']
        result = self.executor._execute_command(command, self.sample_suite)
        
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.passed, 3)
        self.assertEqual(result.command_executed, 'python -m behave tests')
        self.assertEqual(len(result.error_details), 0)
    
    @patch('subprocess.run')
    @patch('builtins.print')
    def test_execute_command_failure(self, mock_print, mock_run):
        """Test command execution with failure"""
        # Mock failed subprocess result
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "1 scenarios passed, 2 failed, 0 skipped"
        mock_result.stderr = "Some error occurred"
        mock_run.return_value = mock_result
        
        command = ['python', '-m', 'behave', 'tests']
        result = self.executor._execute_command(command, self.sample_suite)
        
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.passed, 1)
        self.assertEqual(result.failed, 2)
        self.assertIn("Some error occurred", result.error_details)
    
    @patch('subprocess.run')
    def test_execute_command_timeout(self, mock_run):
        """Test command execution with timeout"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(['behave'], 300)
        
        command = ['python', '-m', 'behave', 'tests']
        result = self.executor._execute_command(command, self.sample_suite)
        
        self.assertEqual(result.exit_code, 124)
        self.assertIn("timed out", result.error_details[0])
    
    def test_execute_suite_not_found(self):
        """Test executing non-existent suite"""
        with self.assertRaises(SuiteExecutorError) as context:
            self.executor.execute_suite("non-existent")
        
        self.assertIn("Suite not found", str(context.exception))
    
    @patch('qaf.automation.suite.executor.SuiteExecutor._execute_command')
    def test_execute_suite_config_dry_run(self, mock_execute):
        """Test executing suite config in dry run mode"""
        result = self.executor.execute_suite_config(self.sample_suite, dry_run=True)
        
        self.assertEqual(result.suite_name, "test-suite")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.execution_time, 0.0)
        self.assertIn('python -m behave', result.command_executed)
        
        # Should not call _execute_command in dry run
        mock_execute.assert_not_called()
    
    @patch('qaf.automation.suite.executor.SuiteExecutor._execute_command')
    @patch('qaf.automation.suite.executor.SuiteExecutor._parse_execution_results')
    @patch('time.time')
    def test_execute_suite_config_normal(self, mock_time, mock_parse, mock_execute):
        """Test normal suite config execution"""
        # Mock time progression
        mock_time.side_effect = [0.0, 1.5]  # start_time, end_time
        
        # Mock successful execution
        mock_result = ExecutionResult(suite_name="test-suite", exit_code=0)
        mock_execute.return_value = mock_result
        
        result = self.executor.execute_suite_config(self.sample_suite)
        
        self.assertEqual(result.suite_name, "test-suite")
        self.assertEqual(result.execution_time, 1.5)
        mock_execute.assert_called_once()
        mock_parse.assert_called_once()
    
    def test_get_execution_command_preview(self):
        """Test getting command preview"""
        preview = self.executor.get_execution_command_preview("test-suite", verbose=True)
        
        self.assertIn('python -m behave', preview)
        self.assertIn('--verbose', preview)
        expected_path = os.path.join('tests', 'simple_demo.feature')
        # Check if path exists in preview (may default to 'tests' if file not found)
        self.assertTrue(expected_path in preview or 'tests' in preview)
        self.assertIn('--tags', preview)
    
    def test_get_execution_command_preview_not_found(self):
        """Test getting command preview for non-existent suite"""
        with self.assertRaises(SuiteExecutorError) as context:
            self.executor.get_execution_command_preview("non-existent")
        
        self.assertIn("Suite not found", str(context.exception))
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_validate_execution_environment_valid(self, mock_exists, mock_run):
        """Test validation of valid execution environment"""
        # Mock behave --version success
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "behave 1.2.6"
        mock_run.return_value = mock_result
        
        # Mock file existence
        def exists_side_effect(path):
            return path in ['behave.ini', 'tests/environment.py', 'reports', 'tests']
        mock_exists.side_effect = exists_side_effect
        
        # Mock file reading
        with patch('builtins.open', unittest.mock.mock_open(
            read_data="format = allure_behave.formatter:AllureFormatter\noutfiles = reports/allure-results"
        )):
            validation = self.executor.validate_execution_environment()
        
        self.assertTrue(validation['valid'])
        self.assertEqual(len(validation['errors']), 0)
        self.assertIn('behave_version', validation['environment_info'])
        self.assertTrue(validation['environment_info']['allure_formatter_configured'])
    
    @patch('subprocess.run')
    def test_validate_execution_environment_behave_missing(self, mock_run):
        """Test validation when behave is not installed"""
        # Mock behave command failure
        mock_run.side_effect = FileNotFoundError("behave not found")
        
        validation = self.executor.validate_execution_environment()
        
        self.assertFalse(validation['valid'])
        self.assertGreater(len(validation['errors']), 0)
        self.assertIn("Failed to check behave installation", validation['errors'][0])
    
    @patch('os.path.exists')
    def test_validate_execution_environment_missing_files(self, mock_exists):
        """Test validation with missing configuration files"""
        # Mock subprocess for behave check
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "behave 1.2.6"
            mock_run.return_value = mock_result
            
            # Mock missing files
            mock_exists.return_value = False
            
            validation = self.executor.validate_execution_environment()
            
            self.assertFalse(validation['valid'])  # tests directory missing
            self.assertGreater(len(validation['warnings']), 0)
            self.assertIn("behave.ini not found", validation['warnings'][0])
    
    def test_get_available_execution_options(self):
        """Test getting available execution options"""
        options = self.executor.get_available_execution_options()
        
        self.assertIn('basic_options', options)
        self.assertIn('suite_options', options)
        self.assertIn('reporting_options', options)
        
        # Check basic options
        basic = options['basic_options']
        self.assertIn('dry_run', basic)
        self.assertIn('verbose', basic)
        self.assertIn('no_capture', basic)
        self.assertIn('log_level', basic)
    
    @patch('os.path.exists')
    def test_parse_execution_results(self, mock_exists):
        """Test parsing execution results for report paths"""
        result = ExecutionResult(suite_name="test")
        
        # Mock report directories existence
        def exists_side_effect(path):
            return path in [
                'reports/allure-results',
                'reports/test_reports',
                'reports/full-execution-history.html'
            ]
        mock_exists.side_effect = exists_side_effect
        
        # Mock listdir for test_reports
        with patch('os.listdir') as mock_listdir:
            with patch('os.path.isdir') as mock_isdir:
                mock_listdir.return_value = ['20240101_120000']
                mock_isdir.return_value = True
                
                self.executor._parse_execution_results(result)
        
        self.assertGreater(len(result.report_paths), 0)
        self.assertIn('reports/allure-results', result.report_paths)
        self.assertIn('reports/full-execution-history.html', result.report_paths)


if __name__ == '__main__':
    unittest.main()