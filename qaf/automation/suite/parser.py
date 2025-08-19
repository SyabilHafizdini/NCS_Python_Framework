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
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .validation import SchemaValidator, XMLValidationError


@dataclass
class TimeoutConfig:
    """Timeout configuration for different execution levels"""
    suite_seconds: int = 3600  # 1 hour default
    scenario_seconds: int = 300  # 5 minutes default
    step_seconds: int = 30  # 30 seconds default


@dataclass
class RetryConfig:
    """Retry configuration for failed executions"""
    max_attempts: int = 1
    delay_seconds: int = 5
    retry_on_failure: bool = False
    retry_on_error: bool = True


@dataclass
class EnvironmentProfile:
    """Environment profile with properties"""
    name: str
    properties: Dict[str, str] = None
    extends: Optional[str] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


@dataclass
class EnvironmentConfig:
    """Environment configuration with variables and profiles"""
    default_environment: str = "test"
    variables: Dict[str, str] = None
    profiles: Dict[str, EnvironmentProfile] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}
        if self.profiles is None:
            self.profiles = {}


@dataclass
class ExecutionConfig:
    """Advanced configuration for test suite execution"""
    stop_on_first_failure: bool = False
    continue_on_error: bool = False
    max_parallel_threads: int = 1
    timeout: TimeoutConfig = None
    retry: RetryConfig = None
    environment: EnvironmentConfig = None
    
    # Legacy fields for backward compatibility
    stop_on_failure: bool = False
    max_retries: int = 0
    timeout_seconds: int = 0
    
    def __post_init__(self):
        if self.timeout is None:
            self.timeout = TimeoutConfig()
        if self.retry is None:
            self.retry = RetryConfig()
        if self.environment is None:
            self.environment = EnvironmentConfig()
        
        # Maintain backward compatibility
        if self.stop_on_failure:
            self.stop_on_first_failure = True
        if self.max_retries > 0:
            self.retry.max_attempts = self.max_retries + 1  # max_retries was additional attempts
        if self.timeout_seconds > 0:
            self.timeout.suite_seconds = self.timeout_seconds


@dataclass
class SuiteConfiguration:
    """
    Test suite configuration parsed from XML
    """
    name: str
    description: str = ""
    scenario_paths: List[str] = None
    include_tags: List[str] = None
    exclude_tags: List[str] = None
    execution_config: ExecutionConfig = None
    environment_params: Dict[str, str] = None
    version: str = "1.0"
    
    def __post_init__(self):
        if self.scenario_paths is None:
            self.scenario_paths = []
        if self.include_tags is None:
            self.include_tags = []
        if self.exclude_tags is None:
            self.exclude_tags = []
        if self.execution_config is None:
            self.execution_config = ExecutionConfig()
        if self.environment_params is None:
            self.environment_params = {}


class SuiteConfigurationParser:
    """
    XML configuration parser for QAF-style test suites
    """
    
    def __init__(self, validator: Optional[SchemaValidator] = None):
        """
        Initialize parser with optional custom validator
        
        Args:
            validator: Custom schema validator, uses default if None
        """
        self.validator = validator or SchemaValidator()
    
    def parse_suite_config(self, xml_path: str) -> SuiteConfiguration:
        """
        Parse XML suite configuration file into SuiteConfiguration object
        
        Args:
            xml_path: Path to XML configuration file
            
        Returns:
            SuiteConfiguration object with parsed values
            
        Raises:
            XMLValidationError: If XML is invalid or parsing fails
        """
        # Validate XML syntax and content first
        self.validator.validate_xml_syntax(xml_path)
        warnings = self.validator.validate_xml_content(xml_path)
        
        if warnings:
            # Log warnings but continue parsing
            print(f"Warnings for {xml_path}: {warnings}")
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Parse suite attributes
            suite_name = root.get('name')
            if not suite_name:
                raise XMLValidationError("Suite name is required")
            
            suite_version = root.get('version', '1.0')
            
            # Parse description
            description_elem = root.find('description')
            description = description_elem.text.strip() if description_elem is not None else ""
            
            # Parse parameters
            environment_params = self._parse_parameters(root)
            
            # Parse execution config from XML (new style) or parameters (legacy)
            execution_config = self._parse_execution_config_xml(root) or self._parse_execution_config_legacy(environment_params)
            
            # Parse test elements
            scenario_paths = []
            include_tags = []
            exclude_tags = []
            
            test_elements = root.findall('test')
            for test in test_elements:
                # Parse classes (scenario paths)
                classes_elem = test.find('classes')
                if classes_elem is not None:
                    for class_elem in classes_elem.findall('class'):
                        class_name = class_elem.get('name')
                        if class_name:
                            scenario_paths.append(class_name)
                
                # Parse groups (tags)
                groups_elem = test.find('groups')
                if groups_elem is not None:
                    run_elem = groups_elem.find('run')
                    if run_elem is not None:
                        # Parse include tags
                        for include_elem in run_elem.findall('include'):
                            tag_name = include_elem.get('name')
                            if tag_name:
                                include_tags.append(tag_name)
                        
                        # Parse exclude tags
                        for exclude_elem in run_elem.findall('exclude'):
                            tag_name = exclude_elem.get('name')
                            if tag_name:
                                exclude_tags.append(tag_name)
            
            return SuiteConfiguration(
                name=suite_name,
                description=description,
                scenario_paths=scenario_paths,
                include_tags=include_tags,
                exclude_tags=exclude_tags,
                execution_config=execution_config,
                environment_params=environment_params,
                version=suite_version
            )
            
        except ET.ParseError as e:
            raise XMLValidationError(f"Failed to parse XML: {str(e)}")
        except Exception as e:
            raise XMLValidationError(f"Unexpected error parsing suite configuration: {str(e)}")
    
    def _parse_parameters(self, root: ET.Element) -> Dict[str, str]:
        """
        Parse parameters section from XML
        
        Args:
            root: Root XML element
            
        Returns:
            Dictionary of parameter name-value pairs
        """
        params = {}
        
        parameters_elem = root.find('parameters')
        if parameters_elem is not None:
            for param_elem in parameters_elem.findall('parameter'):
                name = param_elem.get('name')
                value = param_elem.get('value')
                if name and value:
                    params[name] = value
        
        return params
    
    def _parse_execution_config_xml(self, root: ET.Element) -> Optional[ExecutionConfig]:
        """
        Parse execution configuration from XML execution element
        
        Args:
            root: Root XML element
            
        Returns:
            ExecutionConfig object or None if no execution element found
        """
        execution_elem = root.find('execution')
        if execution_elem is None:
            return None
        
        # Parse execution attributes
        stop_on_first_failure = execution_elem.get('stopOnFirstFailure', 'false').lower() == 'true'
        continue_on_error = execution_elem.get('continueOnError', 'false').lower() == 'true'
        max_parallel_threads = int(execution_elem.get('maxParallelThreads', '1'))
        
        # Parse timeout configuration
        timeout_config = TimeoutConfig()
        timeout_elem = execution_elem.find('timeout')
        if timeout_elem is not None:
            timeout_config.suite_seconds = int(timeout_elem.get('suite', '3600'))
            timeout_config.scenario_seconds = int(timeout_elem.get('scenario', '300'))
            timeout_config.step_seconds = int(timeout_elem.get('step', '30'))
        
        # Parse retry configuration
        retry_config = RetryConfig()
        retry_elem = execution_elem.find('retry')
        if retry_elem is not None:
            retry_config.max_attempts = int(retry_elem.get('maxAttempts', '1'))
            retry_config.delay_seconds = int(retry_elem.get('delaySeconds', '5'))
            retry_config.retry_on_failure = retry_elem.get('retryOnFailure', 'false').lower() == 'true'
            retry_config.retry_on_error = retry_elem.get('retryOnError', 'true').lower() == 'true'
        
        # Parse environment configuration
        environment_config = EnvironmentConfig()
        env_elem = execution_elem.find('environment')
        if env_elem is not None:
            environment_config.default_environment = env_elem.get('default', 'test')
            
            # Parse environment variables
            for var_elem in env_elem.findall('variable'):
                name = var_elem.get('name')
                value = var_elem.get('value')
                env_name = var_elem.get('environment')
                
                if name and value:
                    # If environment-specific, prefix with environment name
                    if env_name:
                        key = f"{env_name}.{name}"
                    else:
                        key = name
                    environment_config.variables[key] = value
            
            # Parse environment profiles
            for profile_elem in env_elem.findall('profile'):
                profile_name = profile_elem.get('name')
                profile_extends = profile_elem.get('extends')
                
                if profile_name:
                    profile = EnvironmentProfile(
                        name=profile_name,
                        extends=profile_extends
                    )
                    
                    # Parse profile properties
                    for prop_elem in profile_elem.findall('property'):
                        prop_name = prop_elem.get('name')
                        prop_value = prop_elem.get('value')
                        if prop_name and prop_value:
                            profile.properties[prop_name] = prop_value
                    
                    environment_config.profiles[profile_name] = profile
        
        return ExecutionConfig(
            stop_on_first_failure=stop_on_first_failure,
            continue_on_error=continue_on_error,
            max_parallel_threads=max_parallel_threads,
            timeout=timeout_config,
            retry=retry_config,
            environment=environment_config
        )
    
    def _parse_execution_config_legacy(self, params: Dict[str, str]) -> ExecutionConfig:
        """
        Parse execution configuration from parameters (legacy support)
        
        Args:
            params: Dictionary of parameters
            
        Returns:
            ExecutionConfig object
        """
        return ExecutionConfig(
            stop_on_failure=params.get('stop_on_failure', 'false').lower() == 'true',
            max_retries=int(params.get('retry_count', '0')),
            timeout_seconds=int(params.get('timeout', '0'))
        )
    
    def validate_scenario_paths(self, config: SuiteConfiguration, base_path: str = ".") -> List[str]:
        """
        Validate that scenario paths exist and convert to actual file paths
        
        Args:
            config: Suite configuration to validate
            base_path: Base directory for relative path resolution
            
        Returns:
            List of validated file paths
            
        Raises:
            XMLValidationError: If any paths are invalid
        """
        validated_paths = []
        missing_paths = []
        
        for scenario_path in config.scenario_paths:
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
            
            # Make path relative to base_path
            full_path = os.path.join(base_path, file_path)
            
            if os.path.exists(full_path):
                if os.path.isfile(full_path):
                    validated_paths.append(full_path)
                elif os.path.isdir(full_path):
                    # Find all .feature files in directory
                    for root, dirs, files in os.walk(full_path):
                        for file in files:
                            if file.endswith('.feature'):
                                validated_paths.append(os.path.join(root, file))
                else:
                    missing_paths.append(scenario_path)
            else:
                missing_paths.append(scenario_path)
        
        if missing_paths:
            raise XMLValidationError(f"Missing scenario paths: {missing_paths}")
        
        return validated_paths
    
    def get_behave_tags_expression(self, config: SuiteConfiguration) -> Optional[str]:
        """
        Convert include/exclude tags to behave tags expression
        
        Args:
            config: Suite configuration
            
        Returns:
            Behave tags expression string or None if no tags
        """
        if not config.include_tags and not config.exclude_tags:
            return None
        
        expressions = []
        
        # Add include tags
        if config.include_tags:
            if len(config.include_tags) == 1:
                expressions.append(config.include_tags[0])
            else:
                # Multiple include tags: tag1 or tag2 or tag3
                include_expr = " or ".join(config.include_tags)
                expressions.append(f"({include_expr})")
        
        # Add exclude tags
        if config.exclude_tags:
            for exclude_tag in config.exclude_tags:
                expressions.append(f"not {exclude_tag}")
        
        # Combine with AND logic
        return " and ".join(expressions)
    
    def export_suite_config(self, config: SuiteConfiguration, output_path: str) -> None:
        """
        Export SuiteConfiguration to XML file
        
        Args:
            config: Suite configuration to export
            output_path: Path for output XML file
        """
        # Create root element
        root = ET.Element('suite')
        root.set('name', config.name)
        root.set('version', config.version)
        
        # Add description
        if config.description:
            desc_elem = ET.SubElement(root, 'description')
            desc_elem.text = config.description
        
        # Add parameters
        if config.environment_params:
            params_elem = ET.SubElement(root, 'parameters')
            for name, value in config.environment_params.items():
                param_elem = ET.SubElement(params_elem, 'parameter')
                param_elem.set('name', name)
                param_elem.set('value', value)
        
        # Add execution configuration
        if config.execution_config:
            self._export_execution_config(root, config.execution_config)
        
        # Add test element
        test_elem = ET.SubElement(root, 'test')
        test_elem.set('name', f"{config.name}-tests")
        
        # Add groups if tags exist
        if config.include_tags or config.exclude_tags:
            groups_elem = ET.SubElement(test_elem, 'groups')
            run_elem = ET.SubElement(groups_elem, 'run')
            
            for tag in config.include_tags:
                include_elem = ET.SubElement(run_elem, 'include')
                include_elem.set('name', tag)
            
            for tag in config.exclude_tags:
                exclude_elem = ET.SubElement(run_elem, 'exclude')
                exclude_elem.set('name', tag)
        
        # Add classes
        if config.scenario_paths:
            classes_elem = ET.SubElement(test_elem, 'classes')
            for path in config.scenario_paths:
                class_elem = ET.SubElement(classes_elem, 'class')
                class_elem.set('name', path)
        
        # Write to file
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        # Format the file for readability
        self.validator.format_xml_file(output_path)
    
    def _export_execution_config(self, root: ET.Element, exec_config: ExecutionConfig) -> None:
        """
        Export execution configuration to XML
        
        Args:
            root: Root XML element
            exec_config: Execution configuration to export
        """
        execution_elem = ET.SubElement(root, 'execution')
        
        # Set execution attributes
        if exec_config.stop_on_first_failure:
            execution_elem.set('stopOnFirstFailure', 'true')
        if exec_config.continue_on_error:
            execution_elem.set('continueOnError', 'true')
        if exec_config.max_parallel_threads != 1:
            execution_elem.set('maxParallelThreads', str(exec_config.max_parallel_threads))
        
        # Add timeout configuration
        if (exec_config.timeout.suite_seconds != 3600 or 
            exec_config.timeout.scenario_seconds != 300 or 
            exec_config.timeout.step_seconds != 30):
            timeout_elem = ET.SubElement(execution_elem, 'timeout')
            timeout_elem.set('suite', str(exec_config.timeout.suite_seconds))
            timeout_elem.set('scenario', str(exec_config.timeout.scenario_seconds))
            timeout_elem.set('step', str(exec_config.timeout.step_seconds))
        
        # Add retry configuration
        if (exec_config.retry.max_attempts != 1 or 
            exec_config.retry.delay_seconds != 5 or 
            exec_config.retry.retry_on_failure or 
            not exec_config.retry.retry_on_error):
            retry_elem = ET.SubElement(execution_elem, 'retry')
            retry_elem.set('maxAttempts', str(exec_config.retry.max_attempts))
            retry_elem.set('delaySeconds', str(exec_config.retry.delay_seconds))
            if exec_config.retry.retry_on_failure:
                retry_elem.set('retryOnFailure', 'true')
            if not exec_config.retry.retry_on_error:
                retry_elem.set('retryOnError', 'false')
        
        # Add environment configuration
        if (exec_config.environment.variables or 
            exec_config.environment.profiles or 
            exec_config.environment.default_environment != 'test'):
            env_elem = ET.SubElement(execution_elem, 'environment')
            if exec_config.environment.default_environment != 'test':
                env_elem.set('default', exec_config.environment.default_environment)
            
            # Add environment variables
            for var_name, var_value in exec_config.environment.variables.items():
                var_elem = ET.SubElement(env_elem, 'variable')
                
                # Handle environment-specific variables
                if '.' in var_name:
                    env_name, name = var_name.split('.', 1)
                    var_elem.set('name', name)
                    var_elem.set('value', var_value)
                    var_elem.set('environment', env_name)
                else:
                    var_elem.set('name', var_name)
                    var_elem.set('value', var_value)
            
            # Add environment profiles
            for profile_name, profile in exec_config.environment.profiles.items():
                profile_elem = ET.SubElement(env_elem, 'profile')
                profile_elem.set('name', profile_name)
                if profile.extends:
                    profile_elem.set('extends', profile.extends)
                
                # Add profile properties
                for prop_name, prop_value in profile.properties.items():
                    prop_elem = ET.SubElement(profile_elem, 'property')
                    prop_elem.set('name', prop_name)
                    prop_elem.set('value', prop_value)