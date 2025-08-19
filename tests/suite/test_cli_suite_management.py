#!/usr/bin/env python3
"""
Unit tests for CLI suite management commands
"""

import os
import tempfile
import unittest
import shutil
from unittest.mock import patch, MagicMock
from io import StringIO

# Import the CLI handler functions
try:
    from run_tests import (
        handle_create_suite, handle_delete_suite, 
        handle_suite_details, handle_update_suite
    )
    CLI_FUNCTIONS_AVAILABLE = True
except ImportError:
    CLI_FUNCTIONS_AVAILABLE = False

@unittest.skipUnless(CLI_FUNCTIONS_AVAILABLE, "CLI functions not available")
class TestCLISuiteManagement(unittest.TestCase):
    """Test cases for CLI suite management commands"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create test suite directory
        os.makedirs("test-suites", exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('builtins.input')
    @patch('qaf.automation.suite.manager.SuiteManager')
    def test_handle_create_suite_interactive(self, mock_manager_class, mock_input):
        """Test interactive suite creation"""
        # Mock user inputs
        mock_input.side_effect = [
            "Test suite description",  # description
            "tests.demo",              # scenario path
            "",                        # end scenario paths
            "smoke,demo",              # include tags
            "slow",                    # exclude tags
            "env=test",                # environment parameter
            "",                        # end parameters
            "y"                        # confirmation
        ]
        
        # Mock manager
        mock_manager = MagicMock()
        mock_manager.repository.suite_exists.return_value = False
        mock_manager.create_suite.return_value = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        # Test the function
        result = handle_create_suite("test-suite")
        
        # Verify success
        self.assertEqual(result, 0)
        mock_manager.create_suite.assert_called_once()
        
        # Verify correct parameters were passed
        call_args = mock_manager.create_suite.call_args
        self.assertIn("test-suite", call_args[1]['name'])
        self.assertIn("Test suite description", call_args[1]['description'])
        self.assertIn("tests.demo", call_args[1]['scenario_paths'])
        self.assertIn("smoke", call_args[1]['include_tags'])
        self.assertIn("slow", call_args[1]['exclude_tags'])
    
    @patch('builtins.input')
    @patch('qaf.automation.suite.manager.SuiteManager')
    def test_handle_create_suite_cancelled(self, mock_manager_class, mock_input):
        """Test suite creation cancellation"""
        # Mock user inputs (cancel at confirmation)
        mock_input.side_effect = [
            "Test description",
            "tests.demo",
            "",
            "",
            "",
            "",
            "n"  # cancel
        ]
        
        mock_manager = MagicMock()
        mock_manager.repository.suite_exists.return_value = False
        mock_manager_class.return_value = mock_manager
        
        result = handle_create_suite("test-suite")
        
        # Verify cancellation
        self.assertEqual(result, 0)
        mock_manager.create_suite.assert_not_called()
    
    @patch('qaf.automation.suite.manager.SuiteManager')
    def test_handle_create_suite_already_exists(self, mock_manager_class):
        """Test creation of existing suite"""
        mock_manager = MagicMock()
        mock_manager.repository.suite_exists.return_value = True
        mock_manager_class.return_value = mock_manager
        
        result = handle_create_suite("existing-suite")
        
        # Verify error handling
        self.assertEqual(result, 1)
        mock_manager.create_suite.assert_not_called()
    
    @patch('builtins.input')
    @patch('qaf.automation.suite.manager.SuiteManager')
    def test_handle_delete_suite_confirmed(self, mock_manager_class, mock_input):
        """Test successful suite deletion"""
        # Mock confirmations
        mock_input.side_effect = ["y", "DELETE"]
        
        mock_manager = MagicMock()
        mock_manager.repository.suite_exists.return_value = True
        mock_manager.get_suite.return_value = MagicMock(
            name="test-suite",
            description="Test description",
            scenario_paths=["tests.demo"],
            include_tags=["smoke"],
            exclude_tags=[]
        )
        mock_manager.delete_suite.return_value = True
        mock_manager_class.return_value = mock_manager
        
        result = handle_delete_suite("test-suite")
        
        # Verify success
        self.assertEqual(result, 0)
        mock_manager.delete_suite.assert_called_once_with("test-suite")
    
    @patch('builtins.input')
    @patch('qaf.automation.suite.manager.SuiteManager')
    def test_handle_delete_suite_cancelled(self, mock_manager_class, mock_input):
        """Test suite deletion cancellation"""
        # Mock user declining first confirmation
        mock_input.side_effect = ["n"]
        
        mock_manager = MagicMock()
        mock_manager.repository.suite_exists.return_value = True
        mock_manager.get_suite.return_value = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        result = handle_delete_suite("test-suite")
        
        # Verify cancellation
        self.assertEqual(result, 0)
        mock_manager.delete_suite.assert_not_called()
    
    @patch('qaf.automation.suite.manager.SuiteManager')
    def test_handle_delete_suite_not_found(self, mock_manager_class):
        """Test deletion of non-existent suite"""
        mock_manager = MagicMock()
        mock_manager.repository.suite_exists.return_value = False
        mock_manager_class.return_value = mock_manager
        
        result = handle_delete_suite("nonexistent-suite")
        
        # Verify error handling
        self.assertEqual(result, 1)
        mock_manager.delete_suite.assert_not_called()
    
    @patch('qaf.automation.suite.manager.SuiteManager')
    @patch('qaf.automation.suite.report_integrator.ReportIntegrator')
    def test_handle_suite_details_success(self, mock_integrator_class, mock_manager_class):
        """Test successful suite details display"""
        # Mock suite data
        mock_manager = MagicMock()
        mock_manager.repository.suite_exists.return_value = True
        mock_manager.repository.get_suite_details.return_value = {
            'file_path': 'test-suites/test.xml',
            'file_size': 500,
            'last_modified': 1234567890
        }
        mock_manager.get_suite.return_value = MagicMock(
            name="test-suite",
            description="Test description",
            version="1.0",
            scenario_paths=["tests.demo"],
            include_tags=["smoke"],
            exclude_tags=["slow"],
            environment_params={"env": "test"},
            execution_config=MagicMock(
                stop_on_failure=False,
                timeout_seconds=300,
                max_retries=2,
                environment="DEV"
            )
        )
        mock_manager_class.return_value = mock_manager
        
        # Mock integrator
        mock_integrator = MagicMock()
        mock_integrator.validate_report_integration.return_value = MagicMock(
            allure_configured=True
        )
        mock_integrator_class.return_value = mock_integrator
        
        # Mock os.path.exists to return True for feature files
        with patch('os.path.exists', return_value=True):
            result = handle_suite_details("test-suite")
        
        # Verify success
        self.assertEqual(result, 0)
    
    @patch('qaf.automation.suite.manager.SuiteManager')
    def test_handle_suite_details_not_found(self, mock_manager_class):
        """Test suite details for non-existent suite"""
        mock_manager = MagicMock()
        mock_manager.repository.suite_exists.return_value = False
        mock_manager_class.return_value = mock_manager
        
        result = handle_suite_details("nonexistent-suite")
        
        # Verify error handling
        self.assertEqual(result, 1)
    
    @patch('builtins.input')
    @patch('qaf.automation.suite.manager.SuiteManager')
    def test_handle_update_suite_success(self, mock_manager_class, mock_input):
        """Test successful suite update"""
        # Mock user inputs
        mock_input.side_effect = [
            "Updated description",  # new description
            "n",                   # don't update paths
            "smoke,regression",    # new include tags
            "unstable",           # new exclude tags
            "y"                   # confirmation
        ]
        
        mock_manager = MagicMock()
        mock_manager.repository.suite_exists.return_value = True
        mock_config = MagicMock(
            name="test-suite",
            description="Old description",
            scenario_paths=["tests.demo"],
            include_tags=["smoke"],
            exclude_tags=[],
            environment_params={}
        )
        mock_manager.get_suite.return_value = mock_config
        mock_manager.update_suite.return_value = True
        mock_manager_class.return_value = mock_manager
        
        result = handle_update_suite("test-suite")
        
        # Verify success
        self.assertEqual(result, 0)
        mock_manager.update_suite.assert_called_once()
        
        # Verify description was updated
        self.assertEqual(mock_config.description, "Updated description")
    
    @patch('builtins.input')
    @patch('qaf.automation.suite.manager.SuiteManager')
    def test_handle_update_suite_cancelled(self, mock_manager_class, mock_input):
        """Test suite update cancellation"""
        # Mock user inputs (cancel at confirmation)
        mock_input.side_effect = [
            "",    # keep description
            "n",   # don't update paths
            "",    # keep include tags
            "",    # keep exclude tags
            "n"    # cancel
        ]
        
        mock_manager = MagicMock()
        mock_manager.repository.suite_exists.return_value = True
        mock_manager.get_suite.return_value = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        result = handle_update_suite("test-suite")
        
        # Verify cancellation
        self.assertEqual(result, 0)
        mock_manager.update_suite.assert_not_called()
    
    @patch('qaf.automation.suite.manager.SuiteManager')
    def test_handle_update_suite_not_found(self, mock_manager_class):
        """Test update of non-existent suite"""
        mock_manager = MagicMock()
        mock_manager.repository.suite_exists.return_value = False
        mock_manager_class.return_value = mock_manager
        
        result = handle_update_suite("nonexistent-suite")
        
        # Verify error handling
        self.assertEqual(result, 1)
        mock_manager.update_suite.assert_not_called()


if __name__ == '__main__':
    unittest.main()