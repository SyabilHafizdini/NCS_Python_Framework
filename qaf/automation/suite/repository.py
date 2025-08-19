#  Copyright (c) 2022 Infostretch Corporation
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  #
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import os
import glob
import shutil
from typing import List, Dict, Optional, Any
from dataclasses import asdict

from .parser import SuiteConfigurationParser, SuiteConfiguration
from .validation import XMLValidationError


class SuiteRepositoryError(Exception):
    """Exception raised by suite repository operations"""
    pass


class SuiteRepository:
    """
    Repository for CRUD operations on test suite configurations
    """
    
    def __init__(self, suites_directory: str = "test-suites"):
        """
        Initialize suite repository
        
        Args:
            suites_directory: Base directory for suite configurations
        """
        self.suites_directory = suites_directory
        self.parser = SuiteConfigurationParser()
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self) -> None:
        """Ensure the suites directory exists"""
        if not os.path.exists(self.suites_directory):
            os.makedirs(self.suites_directory, exist_ok=True)
    
    def _get_suite_file_path(self, suite_name: str) -> str:
        """
        Get file path for a suite configuration
        
        Args:
            suite_name: Name of the suite
            
        Returns:
            Full path to suite XML file
        """
        # Sanitize suite name for filename
        safe_name = suite_name.replace(' ', '-').replace('_', '-')
        if not safe_name.endswith('.xml'):
            safe_name += '.xml'
        
        return os.path.join(self.suites_directory, safe_name)
    
    def _validate_suite_name(self, suite_name: str) -> None:
        """
        Validate suite name format
        
        Args:
            suite_name: Name to validate
            
        Raises:
            SuiteRepositoryError: If name is invalid
        """
        if not suite_name or not suite_name.strip():
            raise SuiteRepositoryError("Suite name cannot be empty")
        
        if len(suite_name) > 100:
            raise SuiteRepositoryError("Suite name too long (max 100 characters)")
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
        for char in invalid_chars:
            if char in suite_name:
                raise SuiteRepositoryError(f"Suite name contains invalid character: {char}")
    
    def save_suite(self, suite: SuiteConfiguration) -> bool:
        """
        Save suite configuration to repository
        
        Args:
            suite: Suite configuration to save
            
        Returns:
            True if saved successfully
            
        Raises:
            SuiteRepositoryError: If save operation fails
        """
        try:
            self._validate_suite_name(suite.name)
            
            # Validate suite configuration
            if not suite.scenario_paths and not suite.include_tags:
                raise SuiteRepositoryError("Suite must have either scenario paths or include tags")
            
            file_path = self._get_suite_file_path(suite.name)
            
            # Check if file already exists for uniqueness validation
            if os.path.exists(file_path):
                existing_suite = self.load_suite(suite.name)
                if existing_suite and existing_suite.name != suite.name:
                    raise SuiteRepositoryError(f"Suite file conflict for: {suite.name}")
            
            # Export to XML file
            self.parser.export_suite_config(suite, file_path)
            
            # Validate the saved file
            validation_summary = self.parser.validator.get_validation_summary(file_path)
            if not validation_summary['valid']:
                # Remove invalid file
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise SuiteRepositoryError(f"Saved suite configuration is invalid: {validation_summary['errors']}")
            
            return True
            
        except XMLValidationError as e:
            raise SuiteRepositoryError(f"Configuration validation failed: {str(e)}")
        except Exception as e:
            raise SuiteRepositoryError(f"Failed to save suite: {str(e)}")
    
    def load_suite(self, suite_name: str) -> Optional[SuiteConfiguration]:
        """
        Load suite configuration from repository
        
        Args:
            suite_name: Name of suite to load
            
        Returns:
            SuiteConfiguration object or None if not found
            
        Raises:
            SuiteRepositoryError: If load operation fails
        """
        try:
            file_path = self._get_suite_file_path(suite_name)
            
            if not os.path.exists(file_path):
                return None
            
            return self.parser.parse_suite_config(file_path)
            
        except XMLValidationError as e:
            raise SuiteRepositoryError(f"Failed to parse suite configuration: {str(e)}")
        except Exception as e:
            raise SuiteRepositoryError(f"Failed to load suite: {str(e)}")
    
    def delete_suite(self, suite_name: str) -> bool:
        """
        Delete suite configuration from repository
        
        Args:
            suite_name: Name of suite to delete
            
        Returns:
            True if deleted successfully, False if not found
            
        Raises:
            SuiteRepositoryError: If delete operation fails
        """
        try:
            file_path = self._get_suite_file_path(suite_name)
            
            if not os.path.exists(file_path):
                return False
            
            os.remove(file_path)
            return True
            
        except Exception as e:
            raise SuiteRepositoryError(f"Failed to delete suite: {str(e)}")
    
    def list_available_suites(self) -> List[str]:
        """
        List all available suite names in repository
        
        Returns:
            List of suite names
        """
        try:
            suite_files = glob.glob(os.path.join(self.suites_directory, "*.xml"))
            suite_names = []
            
            for file_path in suite_files:
                try:
                    # Try to parse each file to get the actual suite name
                    config = self.parser.parse_suite_config(file_path)
                    suite_names.append(config.name)
                except XMLValidationError:
                    # Skip invalid files but don't fail the entire operation
                    continue
            
            return sorted(suite_names)
            
        except Exception as e:
            raise SuiteRepositoryError(f"Failed to list suites: {str(e)}")
    
    def get_suite_details(self, suite_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a suite
        
        Args:
            suite_name: Name of suite
            
        Returns:
            Dictionary with suite details or None if not found
        """
        suite = self.load_suite(suite_name)
        if not suite:
            return None
        
        file_path = self._get_suite_file_path(suite_name)
        file_stats = os.stat(file_path)
        
        return {
            'name': suite.name,
            'description': suite.description,
            'version': suite.version,
            'scenario_paths': suite.scenario_paths,
            'include_tags': suite.include_tags,
            'exclude_tags': suite.exclude_tags,
            'environment_params': suite.environment_params,
            'execution_config': asdict(suite.execution_config),
            'file_path': file_path,
            'file_size': file_stats.st_size,
            'last_modified': file_stats.st_mtime
        }
    
    def suite_exists(self, suite_name: str) -> bool:
        """
        Check if suite exists in repository
        
        Args:
            suite_name: Name of suite to check
            
        Returns:
            True if suite exists
        """
        file_path = self._get_suite_file_path(suite_name)
        return os.path.exists(file_path)
    
    def validate_suite_integrity(self, suite_name: str) -> Dict[str, Any]:
        """
        Validate integrity of a suite configuration
        
        Args:
            suite_name: Name of suite to validate
            
        Returns:
            Dictionary with validation results
        """
        file_path = self._get_suite_file_path(suite_name)
        
        if not os.path.exists(file_path):
            return {
                'valid': False,
                'errors': ['Suite file not found'],
                'warnings': []
            }
        
        try:
            # Validate XML structure
            validation_summary = self.parser.validator.get_validation_summary(file_path)
            
            if validation_summary['valid']:
                # Additional integrity checks
                suite = self.parser.parse_suite_config(file_path)
                
                # Validate scenario paths exist
                try:
                    self.parser.validate_scenario_paths(suite)
                except XMLValidationError as e:
                    validation_summary['warnings'].append(str(e))
            
            return validation_summary
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': []
            }
    
    def backup_suite(self, suite_name: str, backup_dir: str = None) -> str:
        """
        Create backup of suite configuration
        
        Args:
            suite_name: Name of suite to backup
            backup_dir: Directory for backup (uses default if None)
            
        Returns:
            Path to backup file
            
        Raises:
            SuiteRepositoryError: If backup operation fails
        """
        try:
            source_path = self._get_suite_file_path(suite_name)
            
            if not os.path.exists(source_path):
                raise SuiteRepositoryError(f"Suite not found: {suite_name}")
            
            if backup_dir is None:
                backup_dir = os.path.join(self.suites_directory, "backups")
            
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create timestamped backup filename
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            safe_name = suite_name.replace(' ', '-').replace('_', '-')
            backup_filename = f"{safe_name}_{timestamp}.xml"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            shutil.copy2(source_path, backup_path)
            return backup_path
            
        except Exception as e:
            raise SuiteRepositoryError(f"Failed to backup suite: {str(e)}")
    
    def import_suite(self, source_path: str, suite_name: str = None) -> str:
        """
        Import suite configuration from external file
        
        Args:
            source_path: Path to source XML file
            suite_name: Optional new name for imported suite
            
        Returns:
            Name of imported suite
            
        Raises:
            SuiteRepositoryError: If import operation fails
        """
        try:
            if not os.path.exists(source_path):
                raise SuiteRepositoryError(f"Source file not found: {source_path}")
            
            # Parse and validate source file
            suite = self.parser.parse_suite_config(source_path)
            
            # Use provided name or original name
            if suite_name:
                suite.name = suite_name
            
            # Check for name conflicts
            if self.suite_exists(suite.name):
                raise SuiteRepositoryError(f"Suite already exists: {suite.name}")
            
            # Save to repository
            self.save_suite(suite)
            
            return suite.name
            
        except XMLValidationError as e:
            raise SuiteRepositoryError(f"Invalid source file: {str(e)}")
        except Exception as e:
            raise SuiteRepositoryError(f"Failed to import suite: {str(e)}")
    
    def get_repository_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the repository
        
        Returns:
            Dictionary with repository statistics
        """
        try:
            suites = self.list_available_suites()
            total_size = 0
            
            # Calculate total size
            for suite_name in suites:
                file_path = self._get_suite_file_path(suite_name)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
            
            return {
                'total_suites': len(suites),
                'suite_names': suites,
                'repository_path': os.path.abspath(self.suites_directory),
                'total_size_bytes': total_size,
                'directory_exists': os.path.exists(self.suites_directory)
            }
            
        except Exception as e:
            return {
                'error': f"Failed to get repository stats: {str(e)}"
            }