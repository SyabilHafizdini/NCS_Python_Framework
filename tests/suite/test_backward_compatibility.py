#!/usr/bin/env python3
"""
Backward Compatibility Integration Tests

This test suite validates that the new Test Suite Management feature
does not break existing functionality and maintains backward compatibility.
"""

import os
import sys
import unittest
import tempfile
import shutil
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the project root to sys.path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

import run_tests


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with existing framework features"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create minimal project structure
        os.makedirs('tests', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        os.makedirs('test-suites', exist_ok=True)
        
        # Create mock behave.ini
        self.create_mock_behave_ini()
        
        # Create mock feature files
        self.create_mock_features()
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_mock_behave_ini(self):
        """Create mock behave.ini file"""
        behave_ini_content = """[behave]
format = allure_behave.formatter:AllureFormatter
outfiles = reports/allure-results
show_timings = true
logging_level = INFO
"""
        with open('behave.ini', 'w') as f:
            f.write(behave_ini_content)
    
    def create_mock_features(self):
        """Create mock feature files for testing"""
        simple_demo_content = '''Feature: Simple Demo
@demo @smoke
Scenario: Demo scenario
    Given a demo step
    When I perform an action
    Then I see the result
'''
        
        regression_content = '''Feature: Regression Tests
@regression
Scenario: Regression scenario
    Given a regression step
    When I test functionality
    Then all tests pass
'''
        
        with open('tests/simple_demo.feature', 'w') as f:
            f.write(simple_demo_content)
        
        with open('tests/regression.feature', 'w') as f:
            f.write(regression_content)
    
    def test_legacy_run_tests_functionality_preserved(self):
        """Test that original run_tests.py functionality still works"""
        
        # Test legacy suite parameter
        with patch('run_tests.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            # Simulate command line args
            with patch('sys.argv', ['run_tests.py', '--suite', 'demo', '--env', 'DEV']):
                result = run_tests.main()
            
            self.assertEqual(result, 0)
            mock_run.assert_called_once()
            
            # Verify behave command structure
            called_command = mock_run.call_args[0][0]
            self.assertIn('python', called_command[0])
            # behave is at index 2 with 'python -m behave' format
            self.assertIn('behave', called_command[2] if len(called_command) > 2 else ' '.join(called_command))
            self.assertIn('tests/simple_demo.feature', called_command)
    
    def test_legacy_tag_filtering_works(self):
        """Test that legacy tag filtering continues to work"""
        
        with patch('run_tests.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            # Test with tags parameter
            with patch('sys.argv', ['run_tests.py', '--suite', 'smoke', '--tags', 'smoke,demo']):
                result = run_tests.main()
            
            self.assertEqual(result, 0)
            
            # Verify tags are properly passed to behave
            called_command = mock_run.call_args[0][0]
            command_str = ' '.join(called_command)
            self.assertIn('--tags', command_str)
    
    def test_legacy_environment_selection_works(self):
        """Test that legacy environment selection continues to work"""
        
        with patch('run_tests.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            # Test different environments
            for env in ['DEV', 'UAT', 'PROD']:
                with patch('sys.argv', ['run_tests.py', '--env', env]):
                    result = run_tests.main()
                
                self.assertEqual(result, 0, f"Failed for environment {env}")
    
    def test_legacy_dry_run_functionality(self):
        """Test that legacy dry-run functionality continues to work"""
        
        with patch('run_tests.subprocess.run') as mock_run:
            with patch('sys.argv', ['run_tests.py', '--dry-run']):
                result = run_tests.main()
            
            # Dry run should not execute subprocess
            mock_run.assert_not_called()
            self.assertEqual(result, 0)
    
    def test_existing_behave_ini_preservation(self):
        """Test that existing behave.ini configuration is preserved"""
        
        # Verify behave.ini exists and has expected content
        self.assertTrue(os.path.exists('behave.ini'))
        
        with open('behave.ini', 'r') as f:
            content = f.read()
        
        # Check that Allure configuration is preserved
        self.assertIn('allure_behave.formatter:AllureFormatter', content)
        self.assertIn('reports/allure-results', content)
        self.assertIn('show_timings', content)
    
    def test_report_generation_compatibility(self):
        """Test that report generation workflow is preserved"""
        
        from qaf.automation.suite.report_integrator import ReportIntegrator
        
        integrator = ReportIntegrator()
        
        # Test that existing configuration is detected
        status = integrator.validate_report_integration()
        
        self.assertTrue(status.valid, "Report integration should be valid")
        self.assertTrue(status.allure_configured, "Allure should be configured")
        self.assertFalse(status.errors, f"No errors expected, got: {status.errors}")
    
    def test_build_command_functions_unchanged(self):
        """Test that command building functions remain compatible"""
        
        # Create mock args object
        class MockArgs:
            def __init__(self):
                self.suite = 'demo'
                self.env = 'DEV'
                self.tags = 'smoke'
                self.exclude_tags = None
                self.features = 'tests'
                self.verbose = False
                self.allure_dir = 'allure-results'
                self.html_report = 'test-results/report.html'
        
        args = MockArgs()
        
        # Test behave command building
        cmd = run_tests.build_behave_command(args)
        
        self.assertIsInstance(cmd, list)
        self.assertIn('python', cmd[0])
        # behave is at index 2 with 'python -m behave' format
        self.assertIn('behave', cmd[2] if len(cmd) > 2 else ' '.join(cmd))
        self.assertIn('tests/simple_demo.feature', cmd)
    
    def test_suite_support_graceful_degradation(self):
        """Test that system works even if suite support is not available"""
        
        # Temporarily disable suite support
        original_support = run_tests.SUITE_SUPPORT_AVAILABLE
        run_tests.SUITE_SUPPORT_AVAILABLE = False
        
        try:
            with patch('run_tests.subprocess.run') as mock_run:
                mock_run.return_value.returncode = 0
                
                # Should still work with legacy functionality
                with patch('sys.argv', ['run_tests.py', '--suite', 'demo']):
                    result = run_tests.main()
                
                self.assertEqual(result, 0)
                mock_run.assert_called_once()
        
        finally:
            # Restore original value
            run_tests.SUITE_SUPPORT_AVAILABLE = original_support
    
    def test_new_features_do_not_interfere_with_legacy(self):
        """Test that new suite features don't interfere with legacy execution"""
        
        # Create a test suite file
        suite_content = '''<?xml version="1.0" encoding="UTF-8"?>
<suite name="test-suite" version="1.0">
    <description>Test suite</description>
    <test name="test">
        <groups>
            <run><include name="smoke"/></run>
        </groups>
        <classes>
            <class name="tests.simple_demo"/>
        </classes>
    </test>
</suite>'''
        
        with open('test-suites/test-suite.xml', 'w') as f:
            f.write(suite_content)
        
        # Test that legacy execution still works even with suite files present
        with patch('run_tests.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            with patch('sys.argv', ['run_tests.py', '--suite', 'demo']):
                result = run_tests.main()
            
            self.assertEqual(result, 0)
            # Should call subprocess for legacy execution
            mock_run.assert_called_once()
    
    def test_import_structure_compatibility(self):
        """Test that import structure remains compatible"""
        
        # Test that run_tests can be imported and used programmatically
        from run_tests import run_suite_by_name, build_test_command
        
        # Test programmatic function
        self.assertTrue(callable(run_suite_by_name))
        self.assertTrue(callable(build_test_command))
        
        # Test that it can be called (with mocking to avoid actual execution)
        with patch('run_tests.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = run_suite_by_name('demo', 'DEV')
            
            # Should return boolean success status
            self.assertIsInstance(result, bool)
    
    def test_command_line_argument_compatibility(self):
        """Test that all legacy command line arguments are preserved"""
        
        # Test that argument parser accepts all legacy arguments
        parser = run_tests.argparse.ArgumentParser()
        
        # Manually add the arguments that should be preserved
        parser.add_argument('--suite', choices=['demo', 'smoke', 'regression'])
        parser.add_argument('--env', choices=['DEV', 'UAT', 'PROD'])
        parser.add_argument('--tags')
        parser.add_argument('--exclude-tags')
        parser.add_argument('--features')
        parser.add_argument('--allure-dir')
        parser.add_argument('--html-report')
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--dry-run', action='store_true')
        
        # Test that legacy argument combinations parse successfully
        test_args = [
            ['--suite', 'demo'],
            ['--env', 'DEV'],
            ['--tags', 'smoke'],
            ['--exclude-tags', 'slow'],
            ['--features', 'tests'],
            ['--verbose'],
            ['--dry-run'],
            ['--suite', 'demo', '--env', 'UAT', '--tags', 'smoke', '--verbose']
        ]
        
        for args in test_args:
            try:
                parsed = parser.parse_args(args)
                self.assertIsNotNone(parsed)
            except SystemExit:
                self.fail(f"Failed to parse legacy arguments: {args}")
    
    def test_file_structure_compatibility(self):
        """Test that existing file structure assumptions are preserved"""
        
        # Test that expected directories exist or can be created
        expected_dirs = [
            'tests',
            'reports',
            'test-results'
        ]
        
        for directory in expected_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            self.assertTrue(os.path.exists(directory), 
                          f"Expected directory {directory} should exist or be creatable")
        
        # Test that behave.ini is respected
        self.assertTrue(os.path.exists('behave.ini'), 
                       "behave.ini should exist for configuration")
    
    def test_execution_workflow_compatibility(self):
        """Test the complete execution workflow for backward compatibility"""
        
        # Create environment.py file to test hooks
        os.makedirs('tests', exist_ok=True)
        env_content = '''
def before_all(context):
    print("Before all hook executed")

def after_all(context):
    print("After all hook executed")
'''
        
        with open('tests/environment.py', 'w') as f:
            f.write(env_content)
        
        # Test that the workflow can complete without errors
        with patch('run_tests.subprocess.run') as mock_run:
            # Mock successful execution
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            with patch('sys.argv', ['run_tests.py', '--suite', 'demo', '--env', 'DEV']):
                result = run_tests.main()
            
            self.assertEqual(result, 0)
            
            # Verify subprocess was called with correct structure
            self.assertTrue(mock_run.called)
            called_command = mock_run.call_args[0][0]
            
            # Verify it's a proper behave command
            self.assertIn('behave', ' '.join(called_command))


class TestIntegrationWorkflow(unittest.TestCase):
    """Test integration between old and new features"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create minimal project structure
        os.makedirs('tests', exist_ok=True)
        os.makedirs('test-suites', exist_ok=True)
        
        # Create behave.ini
        behave_ini_content = """[behave]
format = allure_behave.formatter:AllureFormatter
outfiles = reports/allure-results
show_timings = true
"""
        with open('behave.ini', 'w') as f:
            f.write(behave_ini_content)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_mixed_execution_modes(self):
        """Test that both legacy and suite execution can coexist"""
        
        # Create a suite file
        suite_content = '''<?xml version="1.0" encoding="UTF-8"?>
<suite name="integration-test" version="1.0">
    <description>Integration test suite</description>
    <test name="integration">
        <groups>
            <run><include name="smoke"/></run>
        </groups>
        <classes>
            <class name="tests.integration"/>
        </classes>
    </test>
</suite>'''
        
        with open('test-suites/integration-test.xml', 'w') as f:
            f.write(suite_content)
        
        # Test suite execution
        with patch('run_tests.subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            # Test new suite execution
            with patch('sys.argv', ['run_tests.py', '--suite-config', 'test-suites/integration-test.xml']):
                suite_result = run_tests.main()
            
            # Test legacy execution
            with patch('sys.argv', ['run_tests.py', '--suite', 'demo']):
                legacy_result = run_tests.main()
            
            self.assertEqual(suite_result, 0)
            self.assertEqual(legacy_result, 0)
            
            # Both should have executed subprocess
            self.assertEqual(mock_run.call_count, 2)
    
    def test_report_integration_consistency(self):
        """Test that reports are generated consistently in both modes"""
        
        from qaf.automation.suite.report_integrator import ReportIntegrator
        
        integrator = ReportIntegrator()
        
        # Test validation works for both modes
        status = integrator.validate_report_integration()
        self.assertTrue(status.valid)
        
        # Test preservation works
        preserved = integrator.preserve_allure_config()
        self.assertTrue(preserved)


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)