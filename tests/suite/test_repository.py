#!/usr/bin/env python3
"""
Unit tests for SuiteRepository
"""

import os
import tempfile
import unittest
import shutil
from unittest.mock import patch, MagicMock

from qaf.automation.suite.repository import SuiteRepository, SuiteRepositoryError
from qaf.automation.suite.parser import SuiteConfiguration, ExecutionConfig


class TestSuiteRepository(unittest.TestCase):
    """Test cases for SuiteRepository"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.repository = SuiteRepository(self.temp_dir)
        
        # Create a sample suite configuration
        self.sample_suite = SuiteConfiguration(
            name="test-suite",
            description="Test suite for repository testing",
            scenario_paths=["tests.demo.feature"],
            include_tags=["smoke"],
            exclude_tags=["slow"],
            environment_params={"env": "DEV", "browser": "chrome"}
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_repository_initialization(self):
        """Test repository initialization creates directory"""
        new_temp_dir = os.path.join(self.temp_dir, "new_repo")
        repo = SuiteRepository(new_temp_dir)
        
        # Directory should be created
        self.assertTrue(os.path.exists(new_temp_dir))
        self.assertEqual(repo.suites_directory, new_temp_dir)
    
    def test_save_suite_success(self):
        """Test successful suite saving"""
        result = self.repository.save_suite(self.sample_suite)
        
        self.assertTrue(result)
        
        # Verify file was created
        expected_path = os.path.join(self.temp_dir, "test-suite.xml")
        self.assertTrue(os.path.exists(expected_path))
    
    def test_save_suite_invalid_name(self):
        """Test saving suite with invalid name"""
        invalid_suite = SuiteConfiguration(name="", description="Invalid")
        
        with self.assertRaises(SuiteRepositoryError) as context:
            self.repository.save_suite(invalid_suite)
        
        self.assertIn("Suite name cannot be empty", str(context.exception))
    
    def test_save_suite_invalid_characters(self):
        """Test saving suite with invalid characters in name"""
        invalid_suite = SuiteConfiguration(name="test<>suite", description="Invalid")
        
        with self.assertRaises(SuiteRepositoryError) as context:
            self.repository.save_suite(invalid_suite)
        
        self.assertIn("invalid character", str(context.exception))
    
    def test_save_suite_no_content(self):
        """Test saving suite with no scenario paths or tags"""
        empty_suite = SuiteConfiguration(
            name="empty-suite",
            description="Empty suite"
        )
        
        with self.assertRaises(SuiteRepositoryError) as context:
            self.repository.save_suite(empty_suite)
        
        self.assertIn("scenario paths or include tags", str(context.exception))
    
    def test_load_suite_success(self):
        """Test successful suite loading"""
        # First save a suite
        self.repository.save_suite(self.sample_suite)
        
        # Then load it
        loaded_suite = self.repository.load_suite("test-suite")
        
        self.assertIsNotNone(loaded_suite)
        self.assertEqual(loaded_suite.name, self.sample_suite.name)
        self.assertEqual(loaded_suite.description, self.sample_suite.description)
        self.assertEqual(loaded_suite.scenario_paths, self.sample_suite.scenario_paths)
        self.assertEqual(loaded_suite.include_tags, self.sample_suite.include_tags)
        self.assertEqual(loaded_suite.exclude_tags, self.sample_suite.exclude_tags)
    
    def test_load_suite_not_found(self):
        """Test loading non-existent suite"""
        result = self.repository.load_suite("non-existent")
        self.assertIsNone(result)
    
    def test_delete_suite_success(self):
        """Test successful suite deletion"""
        # First save a suite
        self.repository.save_suite(self.sample_suite)
        
        # Verify it exists
        self.assertTrue(self.repository.suite_exists("test-suite"))
        
        # Delete it
        result = self.repository.delete_suite("test-suite")
        
        self.assertTrue(result)
        self.assertFalse(self.repository.suite_exists("test-suite"))
    
    def test_delete_suite_not_found(self):
        """Test deleting non-existent suite"""
        result = self.repository.delete_suite("non-existent")
        self.assertFalse(result)
    
    def test_list_available_suites(self):
        """Test listing available suites"""
        # Save multiple suites
        suite1 = SuiteConfiguration(name="suite1", scenario_paths=["tests"])
        suite2 = SuiteConfiguration(name="suite2", include_tags=["smoke"])
        
        self.repository.save_suite(suite1)
        self.repository.save_suite(suite2)
        
        # List suites
        suites = self.repository.list_available_suites()
        
        self.assertEqual(len(suites), 2)
        self.assertIn("suite1", suites)
        self.assertIn("suite2", suites)
        self.assertEqual(suites, sorted(suites))  # Should be sorted
    
    def test_list_available_suites_empty(self):
        """Test listing suites in empty repository"""
        suites = self.repository.list_available_suites()
        self.assertEqual(len(suites), 0)
    
    def test_suite_exists(self):
        """Test suite existence checking"""
        # Should not exist initially
        self.assertFalse(self.repository.suite_exists("test-suite"))
        
        # Save suite
        self.repository.save_suite(self.sample_suite)
        
        # Should exist now
        self.assertTrue(self.repository.suite_exists("test-suite"))
    
    def test_get_suite_details(self):
        """Test getting detailed suite information"""
        # Save suite
        self.repository.save_suite(self.sample_suite)
        
        # Get details
        details = self.repository.get_suite_details("test-suite")
        
        self.assertIsNotNone(details)
        self.assertEqual(details['name'], "test-suite")
        self.assertEqual(details['description'], self.sample_suite.description)
        self.assertEqual(details['scenario_paths'], self.sample_suite.scenario_paths)
        self.assertEqual(details['include_tags'], self.sample_suite.include_tags)
        self.assertEqual(details['exclude_tags'], self.sample_suite.exclude_tags)
        self.assertIn('file_path', details)
        self.assertIn('file_size', details)
        self.assertIn('last_modified', details)
    
    def test_get_suite_details_not_found(self):
        """Test getting details for non-existent suite"""
        details = self.repository.get_suite_details("non-existent")
        self.assertIsNone(details)
    
    def test_validate_suite_integrity_valid(self):
        """Test integrity validation for valid suite"""
        # Save a valid suite
        self.repository.save_suite(self.sample_suite)
        
        # Validate integrity
        result = self.repository.validate_suite_integrity("test-suite")
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_suite_integrity_not_found(self):
        """Test integrity validation for non-existent suite"""
        result = self.repository.validate_suite_integrity("non-existent")
        
        self.assertFalse(result['valid'])
        self.assertIn('Suite file not found', result['errors'])
    
    def test_backup_suite(self):
        """Test creating suite backup"""
        # Save a suite
        self.repository.save_suite(self.sample_suite)
        
        # Create backup
        backup_path = self.repository.backup_suite("test-suite")
        
        # Verify backup was created
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue(backup_path.endswith('.xml'))
        self.assertIn('test-suite', backup_path)
    
    def test_backup_suite_not_found(self):
        """Test backing up non-existent suite"""
        with self.assertRaises(SuiteRepositoryError) as context:
            self.repository.backup_suite("non-existent")
        
        self.assertIn("Suite not found", str(context.exception))
    
    def test_import_suite(self):
        """Test importing suite from external file"""
        # Create a temporary XML file
        temp_xml = os.path.join(self.temp_dir, "external.xml")
        self.repository.save_suite(self.sample_suite)
        
        # Copy to external location
        source_path = os.path.join(self.temp_dir, "test-suite.xml")
        shutil.copy2(source_path, temp_xml)
        
        # Delete original
        self.repository.delete_suite("test-suite")
        
        # Import with new name
        imported_name = self.repository.import_suite(temp_xml, "imported-suite")
        
        self.assertEqual(imported_name, "imported-suite")
        self.assertTrue(self.repository.suite_exists("imported-suite"))
    
    def test_import_suite_name_conflict(self):
        """Test importing suite with existing name"""
        # Save original suite
        self.repository.save_suite(self.sample_suite)
        
        # Create external file
        temp_xml = os.path.join(self.temp_dir, "external.xml")
        source_path = os.path.join(self.temp_dir, "test-suite.xml")
        shutil.copy2(source_path, temp_xml)
        
        # Try to import with same name
        with self.assertRaises(SuiteRepositoryError) as context:
            self.repository.import_suite(temp_xml, "test-suite")
        
        self.assertIn("Suite already exists", str(context.exception))
    
    def test_import_suite_file_not_found(self):
        """Test importing non-existent file"""
        with self.assertRaises(SuiteRepositoryError) as context:
            self.repository.import_suite("non-existent.xml")
        
        self.assertIn("Source file not found", str(context.exception))
    
    def test_get_repository_stats(self):
        """Test getting repository statistics"""
        # Save some suites
        suite1 = SuiteConfiguration(name="suite1", scenario_paths=["tests"])
        suite2 = SuiteConfiguration(name="suite2", include_tags=["smoke"])
        
        self.repository.save_suite(suite1)
        self.repository.save_suite(suite2)
        
        # Get stats
        stats = self.repository.get_repository_stats()
        
        self.assertEqual(stats['total_suites'], 2)
        self.assertIn('suite1', stats['suite_names'])
        self.assertIn('suite2', stats['suite_names'])
        self.assertGreater(stats['total_size_bytes'], 0)
        self.assertTrue(stats['directory_exists'])
        self.assertIn(self.temp_dir, stats['repository_path'])
    
    def test_get_repository_stats_empty(self):
        """Test getting stats for empty repository"""
        stats = self.repository.get_repository_stats()
        
        self.assertEqual(stats['total_suites'], 0)
        self.assertEqual(len(stats['suite_names']), 0)
        self.assertEqual(stats['total_size_bytes'], 0)
        self.assertTrue(stats['directory_exists'])


if __name__ == '__main__':
    unittest.main()