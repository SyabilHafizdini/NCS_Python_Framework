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
import configparser
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class BehaveConfig:
    """Behave configuration parsed from behave.ini"""
    paths: List[str]
    steps_dir: str
    format: str
    outfiles: str
    logging_format: str
    logging_level: str
    lang: str
    show_timings: bool
    show_source: bool
    color: bool
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]):
        """Create BehaveConfig from dictionary"""
        return cls(
            paths=config_dict.get('paths', ['tests']).split() if isinstance(config_dict.get('paths'), str) else config_dict.get('paths', ['tests']),
            steps_dir=config_dict.get('steps_dir', 'step_definitions'),
            format=config_dict.get('format', ''),
            outfiles=config_dict.get('outfiles', ''),
            logging_format=config_dict.get('logging_format', '%(levelname)s:%(name)s:%(message)s'),
            logging_level=config_dict.get('logging_level', 'INFO'),
            lang=config_dict.get('lang', 'en'),
            show_timings=config_dict.get('show_timings', 'false').lower() == 'true',
            show_source=config_dict.get('show_source', 'false').lower() == 'true',
            color=config_dict.get('color', 'false').lower() == 'true'
        )


@dataclass
class EnvironmentHooks:
    """Environment hooks information from tests/environment.py"""
    file_exists: bool
    has_after_all: bool
    has_after_scenario: bool
    allure_report_generation: bool
    report_directories: List[str]


@dataclass
class ReportIntegrationStatus:
    """Status of report integration validation"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    behave_config: Optional[BehaveConfig]
    environment_hooks: Optional[EnvironmentHooks]
    allure_configured: bool
    report_directories_valid: bool


class ReportIntegratorError(Exception):
    """Exception raised by report integrator operations"""
    pass


class ReportIntegrator:
    """
    Report integration system to validate existing report configuration
    and ensure suite execution doesn't interfere with current report generation
    """
    
    def __init__(self, behave_ini_path: str = "behave.ini", environment_py_path: str = "tests/environment.py"):
        """
        Initialize report integrator
        
        Args:
            behave_ini_path: Path to behave.ini configuration file
            environment_py_path: Path to tests/environment.py file
        """
        self.behave_ini_path = behave_ini_path
        self.environment_py_path = environment_py_path
        self.reports_base_dir = "reports"
    
    def validate_report_integration(self) -> ReportIntegrationStatus:
        """
        Validate the complete report integration setup
        
        Returns:
            ReportIntegrationStatus with comprehensive validation results
        """
        status = ReportIntegrationStatus(
            valid=True,
            errors=[],
            warnings=[],
            behave_config=None,
            environment_hooks=None,
            allure_configured=False,
            report_directories_valid=False
        )
        
        try:
            # Validate behave.ini configuration
            behave_validation = self._validate_behave_config()
            status.behave_config = behave_validation.get('config')
            
            if behave_validation['errors']:
                status.errors.extend(behave_validation['errors'])
                status.valid = False
            
            if behave_validation['warnings']:
                status.warnings.extend(behave_validation['warnings'])
            
            status.allure_configured = behave_validation.get('allure_configured', False)
            
            # Validate environment.py hooks
            env_validation = self._validate_environment_hooks()
            status.environment_hooks = env_validation.get('hooks')
            
            if env_validation['errors']:
                status.errors.extend(env_validation['errors'])
                status.valid = False
            
            if env_validation['warnings']:
                status.warnings.extend(env_validation['warnings'])
            
            # Validate report directories
            dir_validation = self._validate_report_directories()
            status.report_directories_valid = dir_validation['valid']
            
            if dir_validation['errors']:
                status.errors.extend(dir_validation['errors'])
                status.valid = False
            
            if dir_validation['warnings']:
                status.warnings.extend(dir_validation['warnings'])
            
            # Overall validation
            if not status.allure_configured:
                status.warnings.append("Allure formatter not properly configured in behave.ini")
            
            if not status.environment_hooks or not status.environment_hooks.allure_report_generation:
                status.warnings.append("Environment hooks may not generate proper Allure reports")
            
        except Exception as e:
            status.valid = False
            status.errors.append(f"Unexpected error during validation: {str(e)}")
        
        return status
    
    def _validate_behave_config(self) -> Dict[str, Any]:
        """
        Validate behave.ini configuration file
        
        Returns:
            Dictionary with validation results and parsed config
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'config': None,
            'allure_configured': False
        }
        
        if not os.path.exists(self.behave_ini_path):
            result['valid'] = False
            result['errors'].append(f"behave.ini not found at {self.behave_ini_path}")
            return result
        
        try:
            config = configparser.ConfigParser()
            config.read(self.behave_ini_path)
            
            if 'behave' not in config.sections():
                result['warnings'].append("No [behave] section found in behave.ini")
                return result
            
            behave_section = dict(config['behave'])
            result['config'] = BehaveConfig.from_dict(behave_section)
            
            # Check for Allure formatter
            format_value = behave_section.get('format', '')
            if 'allure_behave.formatter:AllureFormatter' in format_value:
                result['allure_configured'] = True
            else:
                result['warnings'].append("Allure formatter not found in behave.ini format setting")
            
            # Check for output directory
            outfiles = behave_section.get('outfiles', '')
            if 'allure-results' in outfiles:
                if not outfiles.startswith('reports/'):
                    result['warnings'].append("Allure output directory not in reports/ folder")
            else:
                result['warnings'].append("Allure output directory not configured in behave.ini")
            
            # Check other important settings
            if not behave_section.get('paths'):
                result['warnings'].append("No test paths configured in behave.ini")
            
            if not behave_section.get('steps_dir'):
                result['warnings'].append("No steps directory configured in behave.ini")
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Failed to parse behave.ini: {str(e)}")
        
        return result
    
    def _validate_environment_hooks(self) -> Dict[str, Any]:
        """
        Validate tests/environment.py hooks
        
        Returns:
            Dictionary with validation results and hooks information
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'hooks': None
        }
        
        if not os.path.exists(self.environment_py_path):
            result['warnings'].append(f"Environment file not found at {self.environment_py_path}")
            result['hooks'] = EnvironmentHooks(
                file_exists=False,
                has_after_all=False,
                has_after_scenario=False,
                allure_report_generation=False,
                report_directories=[]
            )
            return result
        
        try:
            with open(self.environment_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required hooks
            has_after_all = 'def after_all(' in content
            has_after_scenario = 'def after_scenario(' in content
            
            # Check for Allure report generation
            allure_report_generation = (
                'allure generate' in content or
                'allure-results' in content or
                'allure-history' in content
            )
            
            # Extract report directories mentioned
            report_directories = []
            if 'reports/' in content:
                # Simple extraction of report directory patterns
                lines = content.split('\n')
                for line in lines:
                    if 'reports/' in line and ('=' in line or '"' in line or "'" in line):
                        # Extract directory paths (simplified)
                        if 'reports/allure-results' in line:
                            report_directories.append('reports/allure-results')
                        if 'reports/test_reports' in line:
                            report_directories.append('reports/test_reports')
                        if 'reports/allure-history' in line:
                            report_directories.append('reports/allure-history')
            
            result['hooks'] = EnvironmentHooks(
                file_exists=True,
                has_after_all=has_after_all,
                has_after_scenario=has_after_scenario,
                allure_report_generation=allure_report_generation,
                report_directories=list(set(report_directories))  # Remove duplicates
            )
            
            # Validation warnings
            if not has_after_all:
                result['warnings'].append("No after_all hook found in environment.py")
            
            if not allure_report_generation:
                result['warnings'].append("No Allure report generation detected in environment.py")
            
            if not report_directories:
                result['warnings'].append("No report directories detected in environment.py")
            
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Failed to analyze environment.py: {str(e)}")
        
        return result
    
    def _validate_report_directories(self) -> Dict[str, Any]:
        """
        Validate report directory structure
        
        Returns:
            Dictionary with validation results
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check base reports directory
        if not os.path.exists(self.reports_base_dir):
            result['warnings'].append(f"Reports directory {self.reports_base_dir} does not exist")
        else:
            # Check specific subdirectories
            expected_dirs = [
                'allure-results',
                'test_reports',
                'allure-history'
            ]
            
            for subdir in expected_dirs:
                full_path = os.path.join(self.reports_base_dir, subdir)
                if not os.path.exists(full_path):
                    result['warnings'].append(f"Expected directory {full_path} does not exist")
        
        return result
    
    def ensure_report_directories(self) -> Dict[str, Any]:
        """
        Ensure all required report directories exist
        
        Returns:
            Dictionary with operation results
        """
        result = {
            'created': [],
            'already_existed': [],
            'errors': []
        }
        
        required_dirs = [
            self.reports_base_dir,
            os.path.join(self.reports_base_dir, 'allure-results'),
            os.path.join(self.reports_base_dir, 'test_reports'),
            os.path.join(self.reports_base_dir, 'allure-history')
        ]
        
        for directory in required_dirs:
            try:
                if os.path.exists(directory):
                    result['already_existed'].append(directory)
                else:
                    os.makedirs(directory, exist_ok=True)
                    result['created'].append(directory)
            except Exception as e:
                result['errors'].append(f"Failed to create directory {directory}: {str(e)}")
        
        return result
    
    def preserve_allure_config(self) -> bool:
        """
        Verify that the current configuration preserves Allure setup
        
        Returns:
            True if Allure configuration is preserved
        """
        validation = self.validate_report_integration()
        return validation.allure_configured and validation.valid
    
    def get_report_configuration_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of report configuration
        
        Returns:
            Dictionary with complete configuration summary
        """
        validation = self.validate_report_integration()
        
        summary = {
            'overall_status': 'valid' if validation.valid else 'invalid',
            'allure_configured': validation.allure_configured,
            'report_directories_valid': validation.report_directories_valid,
            'errors': validation.errors,
            'warnings': validation.warnings
        }
        
        # Behave configuration summary
        if validation.behave_config:
            summary['behave_config'] = {
                'format': validation.behave_config.format,
                'outfiles': validation.behave_config.outfiles,
                'paths': validation.behave_config.paths,
                'allure_formatter_present': 'allure_behave.formatter' in validation.behave_config.format
            }
        else:
            summary['behave_config'] = None
        
        # Environment hooks summary
        if validation.environment_hooks:
            summary['environment_hooks'] = {
                'file_exists': validation.environment_hooks.file_exists,
                'has_after_all': validation.environment_hooks.has_after_all,
                'has_after_scenario': validation.environment_hooks.has_after_scenario,
                'allure_report_generation': validation.environment_hooks.allure_report_generation,
                'report_directories': validation.environment_hooks.report_directories
            }
        else:
            summary['environment_hooks'] = None
        
        # Report directories status
        summary['report_directories'] = self._get_directory_status()
        
        return summary
    
    def _get_directory_status(self) -> Dict[str, Any]:
        """
        Get status of all report directories
        
        Returns:
            Dictionary with directory status information
        """
        directories = {
            'base': self.reports_base_dir,
            'allure_results': os.path.join(self.reports_base_dir, 'allure-results'),
            'test_reports': os.path.join(self.reports_base_dir, 'test_reports'),
            'allure_history': os.path.join(self.reports_base_dir, 'allure-history')
        }
        
        status = {}
        for name, path in directories.items():
            status[name] = {
                'path': path,
                'exists': os.path.exists(path),
                'is_directory': os.path.isdir(path) if os.path.exists(path) else False
            }
            
            if status[name]['exists'] and status[name]['is_directory']:
                try:
                    contents = os.listdir(path)
                    status[name]['file_count'] = len([f for f in contents if os.path.isfile(os.path.join(path, f))])
                    status[name]['dir_count'] = len([f for f in contents if os.path.isdir(os.path.join(path, f))])
                except Exception:
                    status[name]['file_count'] = 0
                    status[name]['dir_count'] = 0
        
        return status
    
    def validate_integration_with_existing_workflow(self) -> Dict[str, Any]:
        """
        Validate that suite execution will integrate properly with existing workflow
        
        Returns:
            Dictionary with integration validation results
        """
        result = {
            'compatible': True,
            'issues': [],
            'recommendations': []
        }
        
        validation = self.validate_report_integration()
        
        # Check for potential conflicts
        if not validation.allure_configured:
            result['compatible'] = False
            result['issues'].append("Allure formatter not configured - suite execution may not generate proper reports")
            result['recommendations'].append("Configure allure_behave.formatter:AllureFormatter in behave.ini")
        
        if not validation.environment_hooks or not validation.environment_hooks.allure_report_generation:
            result['issues'].append("Environment hooks may not generate expected report structure")
            result['recommendations'].append("Ensure tests/environment.py contains proper Allure report generation logic")
        
        # Check for missing directories
        dir_status = self._get_directory_status()
        for name, status in dir_status.items():
            if not status['exists']:
                result['recommendations'].append(f"Create missing directory: {status['path']}")
        
        # Check for configuration consistency
        if validation.behave_config and validation.behave_config.outfiles:
            expected_outfiles = os.path.join(self.reports_base_dir, 'allure-results')
            if expected_outfiles not in validation.behave_config.outfiles:
                result['issues'].append("behave.ini outfiles setting may not match expected report directory")
                result['recommendations'].append(f"Ensure behave.ini outfiles includes {expected_outfiles}")
        
        return result