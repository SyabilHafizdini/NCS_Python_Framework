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
import subprocess
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from .parser import SuiteConfiguration, SuiteConfigurationParser
from .manager import SuiteManager
from .validation import XMLValidationError


@dataclass
class ExecutionResult:
    """Result of suite execution"""
    suite_name: str
    total_scenarios: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    execution_time: float = 0.0
    error_details: List[str] = None
    report_paths: List[str] = None
    exit_code: int = 0
    command_executed: str = ""
    stdout: str = ""
    
    def __post_init__(self):
        if self.error_details is None:
            self.error_details = []
        if self.report_paths is None:
            self.report_paths = []
    
    @property
    def success(self) -> bool:
        """Check if execution was successful"""
        return self.exit_code == 0 and self.failed == 0
    
    @property
    def total_executed(self) -> int:
        """Total scenarios executed (passed + failed + skipped)"""
        return self.passed + self.failed + self.skipped


class SuiteExecutorError(Exception):
    """Exception raised by suite executor operations"""
    pass


class SuiteExecutor:
    """
    Suite executor that builds behave commands based on suite configuration
    while respecting existing Allure reporting workflow
    """
    
    def __init__(self, suite_manager: Optional[SuiteManager] = None):
        """
        Initialize suite executor
        
        Args:
            suite_manager: Optional custom suite manager, uses default if None
        """
        self.suite_manager = suite_manager or SuiteManager()
        self.parser = SuiteConfigurationParser()
    
    def execute_suite(self, suite_name, **kwargs) -> ExecutionResult:
        """
        Execute a test suite by name or configuration object
        
        Args:
            suite_name: Name of suite to execute (str) or SuiteConfiguration object
            **kwargs: Additional execution options (dry_run, verbose, etc.)
            
        Returns:
            ExecutionResult object with execution details
            
        Raises:
            SuiteExecutorError: If execution setup fails
        """
        try:
            # Handle SuiteConfiguration object directly
            if isinstance(suite_name, SuiteConfiguration):
                return self.execute_suite_config(suite_name, **kwargs)
            
            # Handle suite name string
            suite_config = self.suite_manager.get_suite(suite_name)
            if not suite_config:
                raise SuiteExecutorError(f"Suite not found: {suite_name}")
            
            # Validate suite before execution
            validation = self.suite_manager.validate_suite(suite_name)
            if not validation['valid']:
                raise SuiteExecutorError(f"Suite validation failed: {validation['errors']}")
            
            return self.execute_suite_config(suite_config, **kwargs)
            
        except Exception as e:
            if isinstance(e, SuiteExecutorError):
                raise
            raise SuiteExecutorError(f"Failed to execute suite: {str(e)}")
    
    def execute_suite_config(self, suite_config: SuiteConfiguration, **kwargs) -> ExecutionResult:
        """
        Execute a suite based on configuration object
        
        Args:
            suite_config: Suite configuration to execute
            **kwargs: Additional execution options
            
        Returns:
            ExecutionResult object with execution details
        """
        start_time = time.time()
        
        try:
            # Build behave command
            command = self._build_behave_command(suite_config, **kwargs)
            
            # Check for dry run
            if kwargs.get('dry_run', False):
                return ExecutionResult(
                    suite_name=suite_config.name,
                    command_executed=' '.join(command),
                    execution_time=0.0,
                    exit_code=0
                )
            
            # Execute command
            result = self._execute_command(command, suite_config, **kwargs)
            
            # Calculate execution time
            result.execution_time = time.time() - start_time
            
            # Parse execution results if available
            self._parse_execution_results(result, **kwargs)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                suite_name=suite_config.name,
                execution_time=execution_time,
                exit_code=1,
                error_details=[str(e)]
            )
    
    def _build_behave_command(self, suite_config: SuiteConfiguration, **kwargs) -> List[str]:
        """
        Build behave command based on suite configuration
        
        Args:
            suite_config: Suite configuration
            **kwargs: Additional options
            
        Returns:
            List of command arguments
        """
        # Start with base behave command using the virtual environment Python
        import sys
        python_executable = sys.executable
        cmd = [python_executable, '-m', 'behave']
        
        # Add scenario paths - convert from class notation to file paths
        scenario_paths = self._resolve_scenario_paths(suite_config)
        if scenario_paths:
            # Add first path as main argument, others as additional paths
            cmd.append(scenario_paths[0])
            for path in scenario_paths[1:]:
                cmd.extend(['--include', path])
        else:
            # Default to tests directory if no specific paths
            cmd.append('tests')
        
        # Add tag filtering
        tags_expression = self.parser.get_behave_tags_expression(suite_config)
        if tags_expression:
            cmd.extend(['--tags', tags_expression])
        
        # Add environment parameters as defines
        if suite_config.environment_params:
            for key, value in suite_config.environment_params.items():
                cmd.extend(['-D', f'{key}={value}'])
        
        # Add execution configuration options
        if suite_config.execution_config:
            # Legacy stop_on_failure or new stop_on_first_failure
            if (suite_config.execution_config.stop_on_failure or 
                suite_config.execution_config.stop_on_first_failure):
                cmd.append('--stop')
            
            # Apply environment variables for current execution
            self._apply_environment_config(suite_config.execution_config)
            
            # Note: Other advanced options like timeouts and retries are handled
            # at the suite execution level, not in the behave command itself
        
        # Add verbose option if requested
        if kwargs.get('verbose', False):
            cmd.append('--verbose')
        
        # Add dry run option if requested  
        if kwargs.get('dry_run', False):
            cmd.append('--dry-run')
        
        # Add no-capture option for better debugging
        if kwargs.get('no_capture', False):
            cmd.append('--no-capture')
        
        # Add logging level
        log_level = kwargs.get('log_level', 'INFO')
        cmd.extend(['--logging-level', log_level])
        
        # IMPORTANT: DO NOT add formatter options here
        # The existing behave.ini configuration already specifies:
        # format = allure_behave.formatter:AllureFormatter
        # outfiles = reports/allure-results
        # This preserves the existing Allure reporting workflow
        
        return cmd
    
    def _resolve_scenario_paths(self, suite_config: SuiteConfiguration) -> List[str]:
        """
        Convert suite scenario paths to actual file system paths
        
        Args:
            suite_config: Suite configuration
            
        Returns:
            List of resolved file paths
        """
        resolved_paths = []
        
        for scenario_path in suite_config.scenario_paths:
            # Convert class notation to file path
            if scenario_path.endswith('.feature'):
                # Direct feature file: tests.simple_demo.feature -> tests/simple_demo.feature
                # Split on dots but preserve the .feature extension
                parts = scenario_path.split('.')
                if len(parts) > 1 and parts[-1] == 'feature':
                    # Rejoin all parts except the last with os.sep, then add .feature
                    file_path = os.sep.join(parts[:-1]) + '.feature'
                else:
                    file_path = scenario_path.replace('.', os.sep)
            else:
                # Directory reference: tests -> tests/
                file_path = scenario_path.replace('.', os.sep)
            
            # Check if path exists
            if os.path.exists(file_path):
                resolved_paths.append(file_path)
            else:
                # Log warning but continue with other paths
                print(f"Warning: Scenario path not found: {file_path}")
        
        return resolved_paths
    
    def _execute_command(self, command: List[str], suite_config: SuiteConfiguration, **kwargs) -> ExecutionResult:
        """
        Execute the behave command
        
        Args:
            command: Command to execute
            suite_config: Suite configuration
            **kwargs: Additional options
            
        Returns:
            ExecutionResult with basic execution info
        """
        result = ExecutionResult(
            suite_name=suite_config.name,
            command_executed=' '.join(command)
        )
        
        try:
            # Print command if verbose
            if kwargs.get('verbose', False):
                print(f"Executing: {' '.join(command)}")
            
            # Determine timeout from advanced configuration
            timeout = self._get_execution_timeout(suite_config.execution_config)
            
            # Execute the command
            process_result = subprocess.run(
                command,
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            result.exit_code = process_result.returncode
            
            # Store stdout/stderr for analysis
            if process_result.stdout:
                print("STDOUT:", process_result.stdout)
                result.stdout = process_result.stdout  # Store for later parsing
            
            if process_result.stderr:
                print("STDERR:", process_result.stderr)
                if process_result.stderr.strip():
                    result.error_details.append(process_result.stderr)
            
            # Parse behave output for scenario counts
            self._parse_behave_output(result, process_result.stdout)
            
            return result
            
        except subprocess.TimeoutExpired:
            result.exit_code = 124  # Standard timeout exit code
            result.error_details.append("Execution timed out")
            return result
        except Exception as e:
            result.exit_code = 1
            result.error_details.append(f"Command execution failed: {str(e)}")
            return result
    
    def _parse_behave_output(self, result: ExecutionResult, stdout: str) -> None:
        """
        Parse behave output to extract scenario counts
        
        Args:
            result: ExecutionResult to update
            stdout: Command stdout
        """
        if not stdout:
            return
        
        lines = stdout.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for behave summary line like:
            # "1 feature passed, 0 failed, 0 skipped"
            # "3 scenarios passed, 1 failed, 0 skipped"
            if 'scenarios' in line and ('passed' in line or 'failed' in line):
                # Remove commas and extra spaces for easier parsing
                clean_line = line.replace(',', '').replace('  ', ' ')
                parts = clean_line.split()
                
                i = 0
                while i < len(parts):
                    if parts[i].isdigit():
                        count = int(parts[i])
                        # Look for the status keyword after this digit
                        for j in range(i + 1, min(i + 3, len(parts))):
                            status = parts[j]
                            if status.startswith('passed'):
                                result.passed = count
                                break
                            elif status.startswith('failed'):
                                result.failed = count
                                break
                            elif status.startswith('skipped'):
                                result.skipped = count
                                break
                        i += 1
                    else:
                        i += 1
                break
    
    def _parse_execution_results(self, result: ExecutionResult, **kwargs) -> None:
        """
        Parse execution results from behave output and generated reports
        
        Args:
            result: ExecutionResult to update with report information
            **kwargs: Additional options
        """
        import re
        
        # Parse behave output to extract scenario counts
        if hasattr(result, 'stdout') and result.stdout:
            stdout = result.stdout
            
            # Parse scenario summary line like: "1 scenario passed, 0 failed, 0 skipped"
            scenario_pattern = r'(\d+) scenario[s]? passed, (\d+) failed, (\d+) skipped'
            scenario_match = re.search(scenario_pattern, stdout)
            
            if scenario_match:
                result.passed = int(scenario_match.group(1))
                result.failed = int(scenario_match.group(2))
                result.skipped = int(scenario_match.group(3))
                result.total_scenarios = result.passed + result.failed + result.skipped
        
        # Add expected report paths based on existing workflow
        expected_reports = []
        
        # Allure results directory (from behave.ini)
        allure_results_dir = "reports/allure-results"
        if os.path.exists(allure_results_dir):
            expected_reports.append(allure_results_dir)
        
        # Generated HTML reports (from tests/environment.py)
        reports_dir = "reports/test_reports"
        if os.path.exists(reports_dir):
            # Find the most recent report directory
            subdirs = [d for d in os.listdir(reports_dir) if os.path.isdir(os.path.join(reports_dir, d))]
            if subdirs:
                latest_dir = max(subdirs)
                latest_report = os.path.join(reports_dir, latest_dir, "index.html")
                if os.path.exists(latest_report):
                    expected_reports.append(latest_report)
        
        # Full execution history report
        history_report = "reports/full-execution-history.html"
        if os.path.exists(history_report):
            expected_reports.append(history_report)
        
        result.report_paths = expected_reports
    
    def get_execution_command_preview(self, suite_name: str, **kwargs) -> str:
        """
        Get preview of command that would be executed without running it
        
        Args:
            suite_name: Name of suite
            **kwargs: Additional execution options
            
        Returns:
            Command string that would be executed
            
        Raises:
            SuiteExecutorError: If suite not found or invalid
        """
        try:
            suite_config = self.suite_manager.get_suite(suite_name)
            if not suite_config:
                raise SuiteExecutorError(f"Suite not found: {suite_name}")
            
            command = self._build_behave_command(suite_config, **kwargs)
            return ' '.join(command)
            
        except Exception as e:
            raise SuiteExecutorError(f"Failed to generate command preview: {str(e)}")
    
    def validate_execution_environment(self) -> Dict[str, Any]:
        """
        Validate that the execution environment is properly configured
        
        Returns:
            Dictionary with validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'environment_info': {}
        }
        
        # Check if behave is available
        try:
            result = subprocess.run(['python', '-m', 'behave', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                validation['environment_info']['behave_version'] = result.stdout.strip()
            else:
                validation['valid'] = False
                validation['errors'].append("Behave is not properly installed")
        except Exception as e:
            validation['valid'] = False
            validation['errors'].append(f"Failed to check behave installation: {str(e)}")
        
        # Check behave.ini configuration
        behave_ini_path = "behave.ini"
        if os.path.exists(behave_ini_path):
            validation['environment_info']['behave_ini_exists'] = True
            
            # Read and validate behave.ini content
            try:
                with open(behave_ini_path, 'r') as f:
                    content = f.read()
                    if 'allure_behave.formatter:AllureFormatter' in content:
                        validation['environment_info']['allure_formatter_configured'] = True
                    else:
                        validation['warnings'].append("Allure formatter not found in behave.ini")
                    
                    if 'reports/allure-results' in content:
                        validation['environment_info']['allure_output_configured'] = True
                    else:
                        validation['warnings'].append("Allure output directory not configured in behave.ini")
            except Exception as e:
                validation['warnings'].append(f"Failed to read behave.ini: {str(e)}")
        else:
            validation['warnings'].append("behave.ini not found - using default behave configuration")
        
        # Check tests/environment.py
        env_py_path = "tests/environment.py"
        if os.path.exists(env_py_path):
            validation['environment_info']['environment_py_exists'] = True
        else:
            validation['warnings'].append("tests/environment.py not found - report generation hooks may not work")
        
        # Check reports directory structure
        reports_dir = "reports"
        if os.path.exists(reports_dir):
            validation['environment_info']['reports_directory_exists'] = True
            
            # Check for allure-results directory
            allure_dir = os.path.join(reports_dir, "allure-results")
            if os.path.exists(allure_dir):
                validation['environment_info']['allure_results_directory_exists'] = True
            else:
                validation['warnings'].append("reports/allure-results directory does not exist")
        else:
            validation['warnings'].append("reports directory does not exist")
        
        # Check for tests directory
        tests_dir = "tests"
        if os.path.exists(tests_dir):
            validation['environment_info']['tests_directory_exists'] = True
            
            # Count feature files
            feature_files = []
            for root, dirs, files in os.walk(tests_dir):
                for file in files:
                    if file.endswith('.feature'):
                        feature_files.append(os.path.join(root, file))
            
            validation['environment_info']['feature_files_count'] = len(feature_files)
            if len(feature_files) == 0:
                validation['warnings'].append("No .feature files found in tests directory")
        else:
            validation['valid'] = False
            validation['errors'].append("tests directory does not exist")
        
        return validation
    
    def get_available_execution_options(self) -> Dict[str, Any]:
        """
        Get information about available execution options
        
        Returns:
            Dictionary with available options and their descriptions
        """
        return {
            'basic_options': {
                'dry_run': 'Preview command without executing (boolean)',
                'verbose': 'Enable verbose output (boolean)',
                'no_capture': 'Disable output capture for debugging (boolean)',
                'log_level': 'Set logging level (DEBUG, INFO, WARNING, ERROR)'
            },
            'suite_options': {
                'Note': 'Suite-specific options are configured in the XML suite definition',
                'tags': 'Configured via <include>/<exclude> in suite XML',
                'environment': 'Configured via <parameters> in suite XML',
                'scenario_paths': 'Configured via <classes> in suite XML'
            },
            'reporting_options': {
                'Note': 'Reporting is automatically configured via behave.ini and tests/environment.py',
                'allure_results': 'reports/allure-results/ (configured in behave.ini)',
                'current_execution': 'reports/test_reports/{timestamp}/ (via environment.py)',
                'full_history': 'reports/full-execution-history.html (via environment.py)'
            }
        }
    
    def _apply_environment_config(self, execution_config) -> None:
        """
        Apply environment configuration variables to the current process
        
        Args:
            execution_config: ExecutionConfig with environment settings
        """
        if not execution_config or not execution_config.environment:
            return
        
        env_config = execution_config.environment
        
        # Apply environment variables
        for var_name, var_value in env_config.variables.items():
            # Handle environment-specific variables
            if '.' in var_name:
                env_name, name = var_name.split('.', 1)
                # Only apply if the environment matches the default or current environment
                current_env = os.getenv('ENVIRONMENT', env_config.default_environment)
                if env_name == current_env:
                    os.environ[name] = var_value
            else:
                # Apply global variables
                os.environ[var_name] = var_value
        
        # Apply environment profile properties
        current_env = os.getenv('ENVIRONMENT', env_config.default_environment)
        if current_env in env_config.profiles:
            profile = env_config.profiles[current_env]
            
            # Apply inherited properties first if profile extends another
            if profile.extends and profile.extends in env_config.profiles:
                parent_profile = env_config.profiles[profile.extends]
                for prop_name, prop_value in parent_profile.properties.items():
                    os.environ[prop_name] = prop_value
            
            # Apply profile properties
            for prop_name, prop_value in profile.properties.items():
                os.environ[prop_name] = prop_value
    
    def _get_execution_timeout(self, execution_config) -> Optional[int]:
        """
        Get the appropriate timeout for execution
        
        Args:
            execution_config: ExecutionConfig with timeout settings
            
        Returns:
            Timeout in seconds or None for no timeout
        """
        if not execution_config:
            return None
        
        # Use advanced timeout configuration if available
        if hasattr(execution_config, 'timeout') and execution_config.timeout:
            # Only use timeout if it's not the default value or if legacy timeout was set
            if (execution_config.timeout.suite_seconds != 3600 or 
                execution_config.timeout_seconds > 0):
                return execution_config.timeout.suite_seconds
        
        # Fall back to legacy timeout configuration
        if execution_config.timeout_seconds > 0:
            return execution_config.timeout_seconds
        
        return None
    
    def execute_suite_with_retry(self, suite_config: SuiteConfiguration, **kwargs) -> ExecutionResult:
        """
        Execute a suite with retry logic based on configuration
        
        Args:
            suite_config: Suite configuration to execute
            **kwargs: Additional execution options
            
        Returns:
            ExecutionResult with final execution details
        """
        if not suite_config.execution_config or not suite_config.execution_config.retry:
            # No retry configuration, execute normally
            return self.execute_suite_config(suite_config, **kwargs)
        
        retry_config = suite_config.execution_config.retry
        last_result = None
        
        for attempt in range(retry_config.max_attempts):
            result = self.execute_suite_config(suite_config, **kwargs)
            last_result = result
            
            # Check if we should retry
            should_retry = False
            
            if result.exit_code != 0:
                # System-level error occurred
                if retry_config.retry_on_error:
                    should_retry = True
            elif result.failed > 0:
                # Test failures occurred
                if retry_config.retry_on_failure:
                    should_retry = True
            
            # If successful or no more attempts, break
            if not should_retry or attempt == retry_config.max_attempts - 1:
                break
            
            # Wait before retry
            if retry_config.delay_seconds > 0:
                print(f"Retrying in {retry_config.delay_seconds} seconds...")
                time.sleep(retry_config.delay_seconds)
        
        return last_result
    
    def check_stop_on_first_failure(self, suite_config: SuiteConfiguration, current_result: ExecutionResult) -> bool:
        """
        Check if execution should stop based on stop-on-first-failure configuration
        
        Args:
            suite_config: Suite configuration
            current_result: Current execution result
            
        Returns:
            True if execution should stop, False otherwise
        """
        if not suite_config.execution_config:
            return False
        
        stop_on_failure = (suite_config.execution_config.stop_on_failure or 
                          suite_config.execution_config.stop_on_first_failure)
        
        return stop_on_failure and (current_result.failed > 0 or current_result.exit_code != 0)
    
    def get_environment_variables_for_execution(self, suite_config: SuiteConfiguration) -> Dict[str, str]:
        """
        Get all environment variables that would be applied for execution
        
        Args:
            suite_config: Suite configuration
            
        Returns:
            Dictionary of environment variables
        """
        env_vars = {}
        
        if not suite_config.execution_config or not suite_config.execution_config.environment:
            return env_vars
        
        env_config = suite_config.execution_config.environment
        current_env = os.getenv('ENVIRONMENT', env_config.default_environment)
        
        # Add global variables
        for var_name, var_value in env_config.variables.items():
            if '.' in var_name:
                env_name, name = var_name.split('.', 1)
                if env_name == current_env:
                    env_vars[name] = var_value
            else:
                env_vars[var_name] = var_value
        
        # Add profile properties
        if current_env in env_config.profiles:
            profile = env_config.profiles[current_env]
            
            # Add inherited properties first
            if profile.extends and profile.extends in env_config.profiles:
                parent_profile = env_config.profiles[profile.extends]
                env_vars.update(parent_profile.properties)
            
            # Add profile properties
            env_vars.update(profile.properties)
        
        return env_vars