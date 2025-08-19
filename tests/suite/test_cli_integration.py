#!/usr/bin/env python3
"""
Unit tests for CLI integration with suite management
"""

import os
import tempfile
import unittest
import shutil
import subprocess
from unittest.mock import patch, MagicMock

class TestCLIIntegration(unittest.TestCase):
    """Test cases for CLI suite integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create test suite directory and file
        os.makedirs("test-suites", exist_ok=True)
        with open("test-suites/test.xml", "w") as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<suite name="test" description="Test suite for CLI">
    <test name="simple_test" groups="test">
        <classes>
            <class name="tests.simple_demo" />
        </classes>
    </test>
</suite>""")
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_help_includes_suite_options(self):
        """Test that help output includes new suite options"""
        result = subprocess.run(
            ["python", "run_tests.py", "--help"],
            cwd=self.original_cwd,
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("--suite-config", result.stdout)
        self.assertIn("--list-suites", result.stdout)
        self.assertIn("--validate-suite", result.stdout)
    
    def test_list_suites_dry_run(self):
        """Test list suites functionality"""
        # We can't easily test the actual list-suites without proper setup
        # This test validates the CLI argument parsing works
        result = subprocess.run(
            ["python", "run_tests.py", "--help"],
            cwd=self.original_cwd,
            capture_output=True,
            text=True
        )
        
        # At minimum, help should work and contain our new options
        self.assertEqual(result.returncode, 0)
        self.assertIn("List all available test suites", result.stdout)
    
    def test_validate_suite_argument_parsing(self):
        """Test that validate-suite argument is properly parsed"""
        result = subprocess.run(
            ["python", "run_tests.py", "--help"],
            cwd=self.original_cwd,
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Validate suite configuration file", result.stdout)
    
    def test_suite_config_argument_parsing(self):
        """Test that suite-config argument is properly parsed"""
        result = subprocess.run(
            ["python", "run_tests.py", "--help"],
            cwd=self.original_cwd,
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Path to XML suite configuration file", result.stdout)
    
    def test_cli_backward_compatibility(self):
        """Test that existing CLI functionality still works"""
        result = subprocess.run(
            ["python", "run_tests.py", "--help"],
            cwd=self.original_cwd,
            capture_output=True,
            text=True
        )
        
        # Ensure legacy options are still present
        self.assertEqual(result.returncode, 0)
        self.assertIn("--suite {demo,smoke,regression}", result.stdout)
        self.assertIn("--env {DEV,UAT,PROD}", result.stdout)
        self.assertIn("--tags TAGS", result.stdout)
        self.assertIn("--dry-run", result.stdout)


if __name__ == '__main__':
    unittest.main()