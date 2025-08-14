"""
BDD Test Factory - Python QAF Framework
Equivalent to Java QAF BDDTestFactory2 class

Provides Cucumber feature file discovery and execution
with tag-based filtering and XML configuration support
"""

import os
import pytest
import allure
import json
from typing import List, Dict, Any
from pathlib import Path

try:
    from behave import runner
    from behave.configuration import Configuration
    from behave.parser import parse_feature
    from behave.model import Feature
except ImportError:
    print("Behave not installed. Install with: pip install behave")
    raise


class BDDTestFactory:
    """
    BDD Test Factory for feature file discovery and execution
    
    Mimics Java QAF BDDTestFactory2 functionality:
    - Feature file discovery
    - Tag-based filtering
    - Environment configuration
    - Test data integration
    """
    
    def __init__(self, config_file=None):
        """
        Initialize BDD Test Factory
        
        Args:
            config_file: Path to XML configuration file
        """
        self.config_file = config_file
        self.feature_files = []
        self.test_config = {}
        self.env_config = {}
        
    def discover_features(self, feature_dir="tests", include_tags=None, exclude_tags=None):
        """
        Discover feature files with tag filtering
        
        Args:
            feature_dir: Directory containing feature files
            include_tags: Tags to include (from XML config)
            exclude_tags: Tags to exclude
            
        Returns:
            List of feature files to execute
        """
        feature_files = []
        feature_path = Path(feature_dir)
        
        if not feature_path.exists():
            return feature_files
        
        # Find all .feature files
        for feature_file in feature_path.rglob("*.feature"):
            try:
                with open(feature_file, 'r', encoding='utf-8') as f:
                    feature_content = f.read()
                
                # Parse feature for tag analysis
                feature = parse_feature(feature_content, str(feature_file))
                
                if self._should_include_feature(feature, include_tags, exclude_tags):
                    feature_files.append({
                        'file': str(feature_file),
                        'feature': feature,
                        'tags': self._extract_feature_tags(feature)
                    })
                    
            except Exception as e:
                print(f"Error parsing feature file {feature_file}: {e}")
                continue
        
        return feature_files
    
    def _should_include_feature(self, feature: Feature, include_tags=None, exclude_tags=None):
        """
        Determine if feature should be included based on tags
        
        Args:
            feature: Parsed feature object
            include_tags: Tags that must be present
            exclude_tags: Tags that should not be present
            
        Returns:
            bool: True if feature should be included
        """
        if not include_tags and not exclude_tags:
            return True
        
        feature_tags = set()
        
        # Collect tags from feature and scenarios
        if hasattr(feature, 'tags'):
            feature_tags.update(tag.name for tag in feature.tags)
        
        for scenario in feature.scenarios:
            if hasattr(scenario, 'tags'):
                feature_tags.update(tag.name for tag in scenario.tags)
        
        # Check include tags
        if include_tags:
            if isinstance(include_tags, str):
                include_tags = [include_tags]
            if not any(tag in feature_tags for tag in include_tags):
                return False
        
        # Check exclude tags
        if exclude_tags:
            if isinstance(exclude_tags, str):
                exclude_tags = [exclude_tags]
            if any(tag in feature_tags for tag in exclude_tags):
                return False
        
        return True
    
    def _extract_feature_tags(self, feature: Feature):
        """Extract all tags from feature and scenarios"""
        tags = set()
        
        if hasattr(feature, 'tags'):
            tags.update(tag.name for tag in feature.tags)
        
        for scenario in feature.scenarios:
            if hasattr(scenario, 'tags'):
                tags.update(tag.name for tag in scenario.tags)
        
        return list(tags)
    
    def load_xml_configuration(self, xml_file):
        """
        Load test configuration from XML file
        
        Simulates TestNG XML parameter parsing for Python
        
        Args:
            xml_file: Path to XML configuration file
        """
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            config = {}
            
            # Extract parameters
            for param in root.findall('.//parameter'):
                name = param.get('name')
                value = param.get('value')
                config[name] = value
            
            # Extract group configurations
            groups = root.findall('.//groups')
            if groups:
                config['groups'] = self._parse_group_config(groups[0])
            
            self.test_config = config
            return config
            
        except Exception as e:
            print(f"Error loading XML configuration: {e}")
            return {}
    
    def _parse_group_config(self, groups_element):
        """Parse group configuration from XML"""
        group_config = {'include': [], 'exclude': []}
        
        # Parse include groups
        run_element = groups_element.find('.//run')
        if run_element is not None:
            for include in run_element.findall('include'):
                group_name = include.get('name')
                if group_name:
                    group_config['include'].append(group_name)
            
            for exclude in run_element.findall('exclude'):
                group_name = exclude.get('name')
                if group_name:
                    group_config['exclude'].append(group_name)
        
        return group_config
    
    def create_pytest_tests(self, feature_files):
        """
        Create pytest test methods from feature files
        
        Args:
            feature_files: List of feature file information
            
        Returns:
            List of pytest test functions
        """
        test_methods = []
        
        for feature_info in feature_files:
            feature_file = feature_info['file']
            feature = feature_info['feature']
            tags = feature_info['tags']
            
            # Create test method for each scenario
            for scenario in feature.scenarios:
                test_method = self._create_test_method(feature_file, feature, scenario, tags)
                test_methods.append(test_method)
        
        return test_methods
    
    def _create_test_method(self, feature_file, feature, scenario, tags):
        """Create individual pytest test method for scenario"""
        
        def test_scenario():
            """Generated test method for BDD scenario"""
            with allure.step(f"Execute scenario: {scenario.name}"):
                # Attach feature file info
                allure.attach(
                    f"Feature: {feature.name}\nScenario: {scenario.name}\nFile: {feature_file}",
                    name="BDD Test Information",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                # Run scenario using behave
                self._execute_scenario(feature_file, scenario)
        
        # Set test metadata
        test_scenario.__name__ = f"test_{self._sanitize_name(scenario.name)}"
        test_scenario.feature_file = feature_file
        test_scenario.scenario_name = scenario.name
        test_scenario.tags = tags
        
        # Add pytest marks for tags
        for tag in tags:
            test_scenario = getattr(pytest.mark, tag)(test_scenario)
        
        # Add Allure annotations
        test_scenario = allure.feature(feature.name)(test_scenario)
        test_scenario = allure.story(scenario.name)(test_scenario)
        
        return test_scenario
    
    def _execute_scenario(self, feature_file, scenario):
        """Execute individual scenario using behave"""
        try:
            # Configure behave to run single scenario
            config = Configuration()
            config.paths = [os.path.dirname(feature_file)]
            config.steps_dir = "step_definitions"
            
            # Create behave runner
            behave_runner = runner.Runner(config)
            
            # This would need more implementation to properly execute
            # individual scenarios. For now, we'll simulate execution.
            
            # In a full implementation, you would:
            # 1. Set up the scenario context
            # 2. Execute each step
            # 3. Handle step results
            # 4. Capture screenshots and logs
            
            pass
            
        except Exception as e:
            pytest.fail(f"Scenario execution failed: {e}")
    
    def _sanitize_name(self, name):
        """Sanitize name for use as Python method name"""
        import re
        # Replace non-alphanumeric characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        return sanitized.strip('_')


def generate_bdd_tests(xml_config_file=None, feature_dir="tests"):
    """
    Generate BDD tests from feature files
    
    This function is called by pytest to discover and create BDD tests
    
    Args:
        xml_config_file: XML configuration file path
        feature_dir: Directory containing feature files
        
    Returns:
        List of test methods
    """
    factory = BDDTestFactory(xml_config_file)
    
    # Load configuration if provided
    if xml_config_file and os.path.exists(xml_config_file):
        config = factory.load_xml_configuration(xml_config_file)
    else:
        config = {}
    
    # Extract tag filters from configuration
    include_tags = None
    exclude_tags = None
    
    if 'include' in config:
        try:
            # Parse JSON-like include parameter
            include_config = json.loads(config['include'].replace("'", '"'))
            include_tags = include_config.get('groups', [])
        except:
            pass
    
    if 'exclude' in config:
        try:
            exclude_config = json.loads(config['exclude'].replace("'", '"'))
            exclude_tags = exclude_config.get('groups', [])
        except:
            pass
    
    # Discover feature files
    feature_files = factory.discover_features(feature_dir, include_tags, exclude_tags)
    
    # Create pytest test methods
    test_methods = factory.create_pytest_tests(feature_files)
    
    return test_methods


# Pytest plugin hooks for BDD test discovery
def pytest_collect_file(parent, path):
    """Pytest hook to collect BDD test files"""
    if path.ext == ".xml" and "test-runner" in str(path):
        return BDDXMLFile.from_parent(parent, fspath=path)
    return None


class BDDXMLFile(pytest.File):
    """Pytest file collector for XML configuration files"""
    
    def collect(self):
        """Collect tests from XML configuration"""
        xml_file = str(self.fspath)
        test_methods = generate_bdd_tests(xml_file)
        
        for test_method in test_methods:
            yield BDDTestItem.from_parent(self, name=test_method.__name__, test_method=test_method)


class BDDTestItem(pytest.Item):
    """Pytest test item for BDD scenarios"""
    
    def __init__(self, name, parent, test_method):
        super().__init__(name, parent)
        self.test_method = test_method
    
    def runtest(self):
        """Run the BDD test"""
        self.test_method()
    
    def repr_failure(self, excinfo):
        """Represent test failure"""
        return f"BDD Test Failure in {self.name}: {excinfo.value}"