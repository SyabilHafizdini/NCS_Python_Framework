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
from typing import List, Dict, Optional, Any, Union
from dataclasses import asdict, replace

from .repository import SuiteRepository, SuiteRepositoryError
from .parser import SuiteConfiguration, SuiteConfigurationParser, ExecutionConfig
from .validation import XMLValidationError


class SuiteManagerError(Exception):
    """Exception raised by suite manager operations"""
    pass


class SuiteManager:
    """
    Core suite manager that orchestrates suite operations between repository and configuration
    """
    
    def __init__(self, repository: Optional[SuiteRepository] = None):
        """
        Initialize suite manager
        
        Args:
            repository: Optional custom repository, uses default if None
        """
        self.repository = repository or SuiteRepository()
        self.parser = SuiteConfigurationParser()
    
    def create_suite(self, 
                    name,  # Can be str or SuiteConfiguration
                    description: str = "",
                    scenario_paths: List[str] = None,
                    include_tags: List[str] = None,
                    exclude_tags: List[str] = None,
                    environment_params: Dict[str, str] = None,
                    execution_config: ExecutionConfig = None) -> bool:
        """
        Create a new test suite
        
        Args:
            name: Suite name (str) or SuiteConfiguration object
            description: Suite description (ignored if name is SuiteConfiguration)
            scenario_paths: List of scenario file/directory paths (ignored if name is SuiteConfiguration)
            include_tags: List of tags to include (ignored if name is SuiteConfiguration)
            exclude_tags: List of tags to exclude (ignored if name is SuiteConfiguration)
            environment_params: Environment parameters (ignored if name is SuiteConfiguration)
            execution_config: Execution configuration (ignored if name is SuiteConfiguration)
            
        Returns:
            True if creation successful, False otherwise
            
        Raises:
            SuiteManagerError: If creation fails
        """
        try:
            # Handle SuiteConfiguration object directly
            if isinstance(name, SuiteConfiguration):
                suite = name
                suite_name = suite.name
            else:
                # Handle individual parameters
                suite_name = name
                
                # Check if suite already exists
                if self.repository.suite_exists(suite_name):
                    raise SuiteManagerError(f"Suite already exists: {suite_name}")
                
                # Create configuration object
                suite = SuiteConfiguration(
                    name=suite_name,
                    description=description,
                    scenario_paths=scenario_paths or [],
                    include_tags=include_tags or [],
                    exclude_tags=exclude_tags or [],
                    environment_params=environment_params or {},
                    execution_config=execution_config or ExecutionConfig()
                )
            
            # Check if suite already exists (for SuiteConfiguration objects)
            if isinstance(name, SuiteConfiguration) and self.repository.suite_exists(suite_name):
                raise SuiteManagerError(f"Suite already exists: {suite_name}")
            
            # Validate configuration
            self._validate_suite_configuration(suite)
            
            # Save to repository
            self.repository.save_suite(suite)
            
            return True
            
        except SuiteRepositoryError as e:
            raise SuiteManagerError(f"Failed to create suite: {str(e)}")
        except Exception as e:
            raise SuiteManagerError(f"Unexpected error creating suite: {str(e)}")
    
    def update_suite(self, 
                    name: str,
                    **updates) -> SuiteConfiguration:
        """
        Update an existing test suite
        
        Args:
            name: Suite name to update
            **updates: Fields to update (description, scenario_paths, include_tags, etc.)
            
        Returns:
            Updated SuiteConfiguration object
            
        Raises:
            SuiteManagerError: If update fails
        """
        try:
            # Load existing suite
            existing_suite = self.repository.load_suite(name)
            if not existing_suite:
                raise SuiteManagerError(f"Suite not found: {name}")
            
            # Create updated suite with changes
            updated_suite = replace(existing_suite, **updates)
            
            # Validate updated configuration
            self._validate_suite_configuration(updated_suite)
            
            # Save updated configuration
            self.repository.save_suite(updated_suite)
            
            return updated_suite
            
        except SuiteRepositoryError as e:
            raise SuiteManagerError(f"Failed to update suite: {str(e)}")
        except Exception as e:
            raise SuiteManagerError(f"Unexpected error updating suite: {str(e)}")
    
    def delete_suite(self, name: str, force: bool = False) -> bool:
        """
        Delete a test suite
        
        Args:
            name: Suite name to delete
            force: If True, skip confirmation checks
            
        Returns:
            True if deleted successfully
            
        Raises:
            SuiteManagerError: If deletion fails
        """
        try:
            # Check if suite exists
            if not self.repository.suite_exists(name):
                if force:
                    return False
                raise SuiteManagerError(f"Suite not found: {name}")
            
            # Additional safety checks if not forced
            if not force:
                suite = self.repository.load_suite(name)
                if suite and len(suite.scenario_paths) > 10:
                    raise SuiteManagerError(
                        f"Suite has many scenario paths ({len(suite.scenario_paths)}). "
                        f"Use force=True to confirm deletion."
                    )
            
            # Create backup before deletion
            try:
                backup_path = self.repository.backup_suite(name)
                print(f"Suite backed up to: {backup_path}")
            except SuiteRepositoryError:
                if not force:
                    raise SuiteManagerError("Failed to create backup before deletion")
            
            # Delete the suite
            return self.repository.delete_suite(name)
            
        except SuiteRepositoryError as e:
            raise SuiteManagerError(f"Failed to delete suite: {str(e)}")
        except Exception as e:
            raise SuiteManagerError(f"Unexpected error deleting suite: {str(e)}")
    
    def get_suite(self, name: str) -> Optional[SuiteConfiguration]:
        """
        Get a test suite configuration
        
        Args:
            name: Suite name
            
        Returns:
            SuiteConfiguration object or None if not found
        """
        try:
            return self.repository.load_suite(name)
        except SuiteRepositoryError as e:
            raise SuiteManagerError(f"Failed to get suite: {str(e)}")
    
    def list_suites(self, include_details: bool = False) -> Union[List[str], List[Dict[str, Any]]]:
        """
        List all available test suites
        
        Args:
            include_details: If True, return detailed information for each suite
            
        Returns:
            List of suite names or detailed information
        """
        try:
            suite_names = self.repository.list_available_suites()
            
            if not include_details:
                return suite_names
            
            # Get details for each suite
            detailed_suites = []
            for name in suite_names:
                try:
                    details = self.repository.get_suite_details(name)
                    if details:
                        detailed_suites.append(details)
                except SuiteRepositoryError:
                    # Skip invalid suites but continue
                    continue
            
            return detailed_suites
            
        except SuiteRepositoryError as e:
            raise SuiteManagerError(f"Failed to list suites: {str(e)}")
    
    def validate_suite(self, name: str) -> Dict[str, Any]:
        """
        Validate a test suite configuration
        
        Args:
            name: Suite name to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Check basic integrity
            integrity_result = self.repository.validate_suite_integrity(name)
            
            if not integrity_result['valid']:
                return integrity_result
            
            # Additional validation checks
            suite = self.repository.load_suite(name)
            if suite:
                validation_warnings = []
                
                # Validate scenario paths exist
                try:
                    validated_paths = self.parser.validate_scenario_paths(suite)
                    if not validated_paths:
                        validation_warnings.append("No valid scenario paths found")
                except XMLValidationError as e:
                    validation_warnings.append(f"Scenario path validation: {str(e)}")
                
                # Check for logical issues
                if suite.include_tags and suite.exclude_tags:
                    overlapping = set(suite.include_tags) & set(suite.exclude_tags)
                    if overlapping:
                        validation_warnings.append(f"Overlapping include/exclude tags: {overlapping}")
                
                if not suite.scenario_paths and not suite.include_tags:
                    validation_warnings.append("Suite has no scenario paths or include tags - may not execute any tests")
                
                # Add warnings to result
                integrity_result['warnings'].extend(validation_warnings)
            
            return integrity_result
            
        except SuiteRepositoryError as e:
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': []
            }
    
    def get_suite_metadata(self, name: str) -> Dict[str, Any]:
        """
        Get comprehensive metadata about a suite
        
        Args:
            name: Suite name
            
        Returns:
            Dictionary with suite metadata
        """
        try:
            details = self.repository.get_suite_details(name)
            if not details:
                raise SuiteManagerError(f"Suite not found: {name}")
            
            # Add additional metadata
            suite = self.repository.load_suite(name)
            if suite:
                # Get behave tags expression
                tags_expression = self.parser.get_behave_tags_expression(suite)
                
                # Count scenario paths
                scenario_count = len(suite.scenario_paths)
                
                # Validation status
                validation = self.validate_suite(name)
                
                details.update({
                    'behave_tags_expression': tags_expression,
                    'scenario_count': scenario_count,
                    'validation_status': validation['valid'],
                    'validation_warnings': len(validation['warnings']),
                    'validation_errors': len(validation['errors'])
                })
            
            return details
            
        except SuiteRepositoryError as e:
            raise SuiteManagerError(f"Failed to get suite metadata: {str(e)}")
    
    def duplicate_suite(self, source_name: str, target_name: str, 
                       description: str = None) -> SuiteConfiguration:
        """
        Duplicate an existing test suite with a new name
        
        Args:
            source_name: Name of suite to duplicate
            target_name: Name for the new suite
            description: Optional new description
            
        Returns:
            New SuiteConfiguration object
            
        Raises:
            SuiteManagerError: If duplication fails
        """
        try:
            # Load source suite
            source_suite = self.repository.load_suite(source_name)
            if not source_suite:
                raise SuiteManagerError(f"Source suite not found: {source_name}")
            
            # Check target doesn't exist
            if self.repository.suite_exists(target_name):
                raise SuiteManagerError(f"Target suite already exists: {target_name}")
            
            # Create new suite with updated name and description
            new_description = description or f"Copy of {source_suite.description}"
            new_suite = replace(source_suite, name=target_name, description=new_description)
            
            # Save new suite
            self.repository.save_suite(new_suite)
            
            return new_suite
            
        except SuiteRepositoryError as e:
            raise SuiteManagerError(f"Failed to duplicate suite: {str(e)}")
    
    def import_suite_from_file(self, file_path: str, suite_name: str = None) -> str:
        """
        Import a suite from an external XML file
        
        Args:
            file_path: Path to XML file to import
            suite_name: Optional new name for imported suite
            
        Returns:
            Name of imported suite
            
        Raises:
            SuiteManagerError: If import fails
        """
        try:
            return self.repository.import_suite(file_path, suite_name)
        except SuiteRepositoryError as e:
            raise SuiteManagerError(f"Failed to import suite: {str(e)}")
    
    def export_suite_to_file(self, suite_name: str, output_path: str) -> str:
        """
        Export a suite to an external XML file
        
        Args:
            suite_name: Name of suite to export
            output_path: Path for output file
            
        Returns:
            Path to exported file
            
        Raises:
            SuiteManagerError: If export fails
        """
        try:
            suite = self.repository.load_suite(suite_name)
            if not suite:
                raise SuiteManagerError(f"Suite not found: {suite_name}")
            
            self.parser.export_suite_config(suite, output_path)
            return output_path
            
        except SuiteRepositoryError as e:
            raise SuiteManagerError(f"Failed to export suite: {str(e)}")
        except Exception as e:
            raise SuiteManagerError(f"Unexpected error exporting suite: {str(e)}")
    
    def get_manager_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the suite manager and repository
        
        Returns:
            Dictionary with manager statistics
        """
        try:
            repo_stats = self.repository.get_repository_stats()
            
            # Add manager-level statistics
            suite_names = self.repository.list_available_suites()
            
            # Count suites by validation status
            valid_suites = 0
            invalid_suites = 0
            
            for name in suite_names:
                try:
                    validation = self.validate_suite(name)
                    if validation['valid']:
                        valid_suites += 1
                    else:
                        invalid_suites += 1
                except:
                    invalid_suites += 1
            
            manager_stats = {
                'total_suites': len(suite_names),
                'valid_suites': valid_suites,
                'invalid_suites': invalid_suites,
                'repository_path': repo_stats.get('repository_path'),
                'total_size_bytes': repo_stats.get('total_size_bytes', 0)
            }
            
            return manager_stats
            
        except Exception as e:
            return {'error': f"Failed to get manager statistics: {str(e)}"}
    
    def _validate_suite_configuration(self, suite: SuiteConfiguration) -> None:
        """
        Validate suite configuration for logical consistency
        
        Args:
            suite: Suite configuration to validate
            
        Raises:
            SuiteManagerError: If validation fails
        """
        if not suite.name or not suite.name.strip():
            raise SuiteManagerError("Suite name is required")
        
        if not suite.scenario_paths and not suite.include_tags:
            raise SuiteManagerError("Suite must have either scenario paths or include tags")
        
        # Check for conflicting tags
        if suite.include_tags and suite.exclude_tags:
            overlapping = set(suite.include_tags) & set(suite.exclude_tags)
            if overlapping:
                raise SuiteManagerError(f"Tags cannot be both included and excluded: {overlapping}")
        
        # Validate environment parameters
        if suite.environment_params:
            for key, value in suite.environment_params.items():
                if not key or not isinstance(key, str):
                    raise SuiteManagerError("Environment parameter keys must be non-empty strings")
                if not isinstance(value, str):
                    raise SuiteManagerError("Environment parameter values must be strings")
    
    def search_suites(self, 
                     name_pattern: str = None,
                     include_tag: str = None,
                     exclude_tag: str = None,
                     environment: str = None) -> List[Dict[str, Any]]:
        """
        Search for suites matching criteria
        
        Args:
            name_pattern: Pattern to match in suite names (case-insensitive)
            include_tag: Tag that must be in include_tags
            exclude_tag: Tag that must be in exclude_tags  
            environment: Environment parameter value
            
        Returns:
            List of matching suite details
        """
        try:
            all_suites = self.list_suites(include_details=True)
            matching_suites = []
            
            for suite_details in all_suites:
                match = True
                
                # Check name pattern
                if name_pattern and name_pattern.lower() not in suite_details['name'].lower():
                    match = False
                
                # Check include tag
                if include_tag and include_tag not in suite_details.get('include_tags', []):
                    match = False
                
                # Check exclude tag
                if exclude_tag and exclude_tag not in suite_details.get('exclude_tags', []):
                    match = False
                
                # Check environment
                if environment:
                    env_params = suite_details.get('environment_params', {})
                    if env_params.get('env') != environment:
                        match = False
                
                if match:
                    matching_suites.append(suite_details)
            
            return matching_suites
            
        except Exception as e:
            raise SuiteManagerError(f"Failed to search suites: {str(e)}")