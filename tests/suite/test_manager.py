#!/usr/bin/env python3
"""
Unit tests for SuiteManager
"""

import os
import tempfile
import unittest
import shutil
from unittest.mock import patch, MagicMock

from qaf.automation.suite.manager import SuiteManager, SuiteManagerError
from qaf.automation.suite.repository import SuiteRepository
from qaf.automation.suite.parser import SuiteConfiguration, ExecutionConfig


class TestSuiteManager(unittest.TestCase):
    """Test cases for SuiteManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.repository = SuiteRepository(self.temp_dir)
        self.manager = SuiteManager(self.repository)
        
        # Create sample suite configurations
        self.sample_suite = SuiteConfiguration(
            name="test-suite",
            description="Test suite for manager testing",
            scenario_paths=["tests.demo.feature"],
            include_tags=["smoke"],
            exclude_tags=["slow"],
            environment_params={"env": "DEV", "browser": "chrome"}
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_suite_success(self):
        """Test successful suite creation"""
        suite = self.manager.create_suite(
            name="new-suite",
            description="New test suite",
            scenario_paths=["tests.feature"],
            include_tags=["regression"]
        )
        
        self.assertEqual(suite.name, "new-suite")
        self.assertEqual(suite.description, "New test suite")
        self.assertEqual(suite.scenario_paths, ["tests.feature"])
        self.assertEqual(suite.include_tags, ["regression"])
        
        # Verify suite was saved
        self.assertTrue(self.repository.suite_exists("new-suite"))
    
    def test_create_suite_already_exists(self):
        """Test creating suite that already exists"""
        # Create first suite
        self.manager.create_suite(name="duplicate-suite", scenario_paths=["tests"])
        
        # Try to create same suite again
        with self.assertRaises(SuiteManagerError) as context:
            self.manager.create_suite(name="duplicate-suite", scenario_paths=["tests"])
        
        self.assertIn("Suite already exists", str(context.exception))
    
    def test_create_suite_invalid_name(self):
        """Test creating suite with invalid name"""
        with self.assertRaises(SuiteManagerError) as context:
            self.manager.create_suite(name="", scenario_paths=["tests"])
        
        self.assertIn("Suite name is required", str(context.exception))
    
    def test_create_suite_no_content(self):
        """Test creating suite with no scenario paths or tags"""
        with self.assertRaises(SuiteManagerError) as context:
            self.manager.create_suite(name="empty-suite")
        
        self.assertIn("scenario paths or include tags", str(context.exception))
    
    def test_create_suite_conflicting_tags(self):
        """Test creating suite with conflicting include/exclude tags"""
        with self.assertRaises(SuiteManagerError) as context:
            self.manager.create_suite(
                name="conflict-suite",
                include_tags=["smoke", "regression"],
                exclude_tags=["smoke"]
            )
        
        self.assertIn("both included and excluded", str(context.exception))
    
    def test_update_suite_success(self):
        """Test successful suite update"""
        # Create initial suite
        self.repository.save_suite(self.sample_suite)
        
        # Update the suite
        updated_suite = self.manager.update_suite(
            "test-suite",
            description="Updated description",
            include_tags=["smoke", "critical"]
        )
        
        self.assertEqual(updated_suite.description, "Updated description")
        self.assertEqual(updated_suite.include_tags, ["smoke", "critical"])
        self.assertEqual(updated_suite.name, "test-suite")  # Name should remain same
    
    def test_update_suite_not_found(self):
        """Test updating non-existent suite"""
        with self.assertRaises(SuiteManagerError) as context:
            self.manager.update_suite("non-existent", description="New desc")
        
        self.assertIn("Suite not found", str(context.exception))
    
    def test_delete_suite_success(self):
        """Test successful suite deletion"""
        # Create suite
        self.repository.save_suite(self.sample_suite)
        self.assertTrue(self.repository.suite_exists("test-suite"))
        
        # Delete suite
        result = self.manager.delete_suite("test-suite", force=True)
        
        self.assertTrue(result)
        self.assertFalse(self.repository.suite_exists("test-suite"))
    
    def test_delete_suite_not_found(self):
        """Test deleting non-existent suite"""
        with self.assertRaises(SuiteManagerError) as context:
            self.manager.delete_suite("non-existent")
        
        self.assertIn("Suite not found", str(context.exception))
    
    def test_delete_suite_not_found_force(self):
        """Test deleting non-existent suite with force=True"""
        result = self.manager.delete_suite("non-existent", force=True)
        self.assertFalse(result)
    
    def test_delete_suite_large_suite_protection(self):
        """Test protection against deleting large suites without force"""
        # Create suite with many scenario paths
        large_suite = SuiteConfiguration(
            name="large-suite",
            scenario_paths=[f"test{i}.feature" for i in range(15)]  # More than 10
        )
        self.repository.save_suite(large_suite)
        
        # Should fail without force
        with self.assertRaises(SuiteManagerError) as context:
            self.manager.delete_suite("large-suite")
        
        self.assertIn("Use force=True", str(context.exception))
        
        # Should succeed with force
        result = self.manager.delete_suite("large-suite", force=True)
        self.assertTrue(result)
    
    def test_get_suite_success(self):
        """Test getting existing suite"""
        self.repository.save_suite(self.sample_suite)
        
        retrieved_suite = self.manager.get_suite("test-suite")
        
        self.assertIsNotNone(retrieved_suite)
        self.assertEqual(retrieved_suite.name, "test-suite")
        self.assertEqual(retrieved_suite.description, self.sample_suite.description)
    
    def test_get_suite_not_found(self):
        """Test getting non-existent suite"""
        result = self.manager.get_suite("non-existent")
        self.assertIsNone(result)
    
    def test_list_suites_names_only(self):
        """Test listing suite names only"""
        # Create multiple suites
        suite1 = SuiteConfiguration(name="suite1", scenario_paths=["tests"])
        suite2 = SuiteConfiguration(name="suite2", include_tags=["smoke"])
        
        self.repository.save_suite(suite1)
        self.repository.save_suite(suite2)
        
        # List names only
        names = self.manager.list_suites(include_details=False)
        
        self.assertEqual(len(names), 2)
        self.assertIn("suite1", names)
        self.assertIn("suite2", names)
        self.assertIsInstance(names, list)
        self.assertIsInstance(names[0], str)
    
    def test_list_suites_with_details(self):
        """Test listing suites with details"""
        # Create suite
        self.repository.save_suite(self.sample_suite)
        
        # List with details
        details = self.manager.list_suites(include_details=True)
        
        self.assertEqual(len(details), 1)
        self.assertIsInstance(details[0], dict)
        self.assertEqual(details[0]['name'], "test-suite")
        self.assertIn('description', details[0])
        self.assertIn('file_path', details[0])
    
    def test_validate_suite_valid(self):
        """Test validating valid suite"""
        self.repository.save_suite(self.sample_suite)
        
        result = self.manager.validate_suite("test-suite")
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_suite_not_found(self):
        """Test validating non-existent suite"""
        result = self.manager.validate_suite("non-existent")
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
    
    def test_validate_suite_conflicting_tags(self):
        """Test validating suite with conflicting tags"""
        # Create suite with conflicting tags using repository directly
        conflicting_suite = SuiteConfiguration(
            name="conflict-suite",
            scenario_paths=["tests"],
            include_tags=["smoke"],
            exclude_tags=["smoke"]  # Same tag in both
        )
        self.repository.save_suite(conflicting_suite)
        
        result = self.manager.validate_suite("conflict-suite")
        
        # Should still be valid XML but have warnings
        self.assertTrue(result['valid'])
        self.assertGreater(len(result['warnings']), 0)
        # Check that warning mentions overlapping tags
        warning_text = ' '.join(result['warnings'])
        self.assertIn("Overlapping", warning_text)
    
    def test_get_suite_metadata(self):
        """Test getting comprehensive suite metadata"""
        self.repository.save_suite(self.sample_suite)
        
        metadata = self.manager.get_suite_metadata("test-suite")
        
        self.assertEqual(metadata['name'], "test-suite")
        self.assertIn('behave_tags_expression', metadata)
        self.assertIn('scenario_count', metadata)
        self.assertIn('validation_status', metadata)
        self.assertIn('validation_warnings', metadata)
        self.assertEqual(metadata['scenario_count'], 1)
        self.assertTrue(metadata['validation_status'])
    
    def test_get_suite_metadata_not_found(self):
        """Test getting metadata for non-existent suite"""
        with self.assertRaises(SuiteManagerError) as context:
            self.manager.get_suite_metadata("non-existent")
        
        self.assertIn("Suite not found", str(context.exception))
    
    def test_duplicate_suite_success(self):
        """Test successful suite duplication"""
        # Create original suite
        self.repository.save_suite(self.sample_suite)
        
        # Duplicate suite
        new_suite = self.manager.duplicate_suite(
            "test-suite", 
            "test-suite-copy",
            "Copied test suite"
        )
        
        self.assertEqual(new_suite.name, "test-suite-copy")
        self.assertEqual(new_suite.description, "Copied test suite")
        self.assertEqual(new_suite.scenario_paths, self.sample_suite.scenario_paths)
        self.assertEqual(new_suite.include_tags, self.sample_suite.include_tags)
        
        # Verify both suites exist
        self.assertTrue(self.repository.suite_exists("test-suite"))
        self.assertTrue(self.repository.suite_exists("test-suite-copy"))
    
    def test_duplicate_suite_source_not_found(self):
        """Test duplicating non-existent suite"""
        with self.assertRaises(SuiteManagerError) as context:
            self.manager.duplicate_suite("non-existent", "new-name")
        
        self.assertIn("Source suite not found", str(context.exception))
    
    def test_duplicate_suite_target_exists(self):
        """Test duplicating to existing target name"""
        # Create two suites
        self.repository.save_suite(self.sample_suite)
        target_suite = SuiteConfiguration(name="target-suite", scenario_paths=["tests"])
        self.repository.save_suite(target_suite)
        
        # Try to duplicate with existing target name
        with self.assertRaises(SuiteManagerError) as context:
            self.manager.duplicate_suite("test-suite", "target-suite")
        
        self.assertIn("Target suite already exists", str(context.exception))
    
    def test_import_suite_from_file(self):
        """Test importing suite from external file"""
        # Create a test file
        test_file = os.path.join(self.temp_dir, "import_test.xml")
        self.repository.save_suite(self.sample_suite)
        
        # Export to test file
        source_path = os.path.join(self.temp_dir, "test-suite.xml")
        shutil.copy2(source_path, test_file)
        
        # Delete original
        self.repository.delete_suite("test-suite")
        
        # Import from file
        imported_name = self.manager.import_suite_from_file(test_file, "imported-suite")
        
        self.assertEqual(imported_name, "imported-suite")
        self.assertTrue(self.repository.suite_exists("imported-suite"))
    
    def test_export_suite_to_file(self):
        """Test exporting suite to external file"""
        # Create suite
        self.repository.save_suite(self.sample_suite)
        
        # Export to file
        export_path = os.path.join(self.temp_dir, "exported.xml")
        result_path = self.manager.export_suite_to_file("test-suite", export_path)
        
        self.assertEqual(result_path, export_path)
        self.assertTrue(os.path.exists(export_path))
        
        # Verify exported file is valid
        from qaf.automation.suite.parser import SuiteConfigurationParser
        parser = SuiteConfigurationParser()
        imported_suite = parser.parse_suite_config(export_path)
        self.assertEqual(imported_suite.name, "test-suite")
    
    def test_export_suite_not_found(self):
        """Test exporting non-existent suite"""
        export_path = os.path.join(self.temp_dir, "nonexistent.xml")
        
        with self.assertRaises(SuiteManagerError) as context:
            self.manager.export_suite_to_file("non-existent", export_path)
        
        self.assertIn("Suite not found", str(context.exception))
    
    def test_get_manager_statistics(self):
        """Test getting manager statistics"""
        # Create multiple suites
        suite1 = SuiteConfiguration(name="suite1", scenario_paths=["tests"])
        suite2 = SuiteConfiguration(name="suite2", include_tags=["smoke"])
        
        self.repository.save_suite(suite1)
        self.repository.save_suite(suite2)
        
        # Get statistics
        stats = self.manager.get_manager_statistics()
        
        self.assertEqual(stats['total_suites'], 2)
        self.assertEqual(stats['valid_suites'], 2)
        self.assertEqual(stats['invalid_suites'], 0)
        self.assertIn(self.temp_dir, stats['repository_path'])
        self.assertGreater(stats['total_size_bytes'], 0)
    
    def test_search_suites_by_name(self):
        """Test searching suites by name pattern"""
        # Create test suites
        suite1 = SuiteConfiguration(name="smoke-tests", include_tags=["smoke"])
        suite2 = SuiteConfiguration(name="regression-tests", include_tags=["regression"])
        suite3 = SuiteConfiguration(name="api-smoke-tests", include_tags=["api", "smoke"])
        
        self.repository.save_suite(suite1)
        self.repository.save_suite(suite2)
        self.repository.save_suite(suite3)
        
        # Search by name pattern
        results = self.manager.search_suites(name_pattern="smoke")
        
        self.assertEqual(len(results), 2)
        names = [suite['name'] for suite in results]
        self.assertIn("smoke-tests", names)
        self.assertIn("api-smoke-tests", names)
        self.assertNotIn("regression-tests", names)
    
    def test_search_suites_by_tag(self):
        """Test searching suites by include tag"""
        # Create test suites
        suite1 = SuiteConfiguration(name="suite1", include_tags=["smoke", "critical"])
        suite2 = SuiteConfiguration(name="suite2", include_tags=["regression"])
        suite3 = SuiteConfiguration(name="suite3", include_tags=["smoke"])
        
        self.repository.save_suite(suite1)
        self.repository.save_suite(suite2)
        self.repository.save_suite(suite3)
        
        # Search by include tag
        results = self.manager.search_suites(include_tag="smoke")
        
        self.assertEqual(len(results), 2)
        names = [suite['name'] for suite in results]
        self.assertIn("suite1", names)
        self.assertIn("suite3", names)
        self.assertNotIn("suite2", names)
    
    def test_search_suites_by_environment(self):
        """Test searching suites by environment parameter"""
        # Create test suites
        suite1 = SuiteConfiguration(name="dev-suite", environment_params={"env": "DEV"})
        suite2 = SuiteConfiguration(name="uat-suite", environment_params={"env": "UAT"})
        suite3 = SuiteConfiguration(name="prod-suite", environment_params={"env": "PROD"})
        
        # Add scenario paths to make them valid
        for suite in [suite1, suite2, suite3]:
            suite.scenario_paths = ["tests"]
        
        self.repository.save_suite(suite1)
        self.repository.save_suite(suite2)
        self.repository.save_suite(suite3)
        
        # Search by environment
        results = self.manager.search_suites(environment="UAT")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "uat-suite")
    
    def test_search_suites_multiple_criteria(self):
        """Test searching suites with multiple criteria"""
        # Create test suites
        suite1 = SuiteConfiguration(
            name="smoke-dev-tests", 
            include_tags=["smoke"],
            environment_params={"env": "DEV"}
        )
        suite2 = SuiteConfiguration(
            name="smoke-uat-tests",
            include_tags=["smoke"], 
            environment_params={"env": "UAT"}
        )
        suite3 = SuiteConfiguration(
            name="regression-dev-tests",
            include_tags=["regression"],
            environment_params={"env": "DEV"}
        )
        
        # Add scenario paths to make them valid
        for suite in [suite1, suite2, suite3]:
            suite.scenario_paths = ["tests"]
        
        self.repository.save_suite(suite1)
        self.repository.save_suite(suite2)
        self.repository.save_suite(suite3)
        
        # Search with multiple criteria
        results = self.manager.search_suites(
            name_pattern="smoke",
            include_tag="smoke",
            environment="DEV"
        )
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "smoke-dev-tests")


if __name__ == '__main__':
    unittest.main()