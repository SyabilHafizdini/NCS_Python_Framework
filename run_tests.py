#!/usr/bin/env python3
"""
SPF NGEN Test Runner - Python QAF Framework
Execution script that mimics Java QAF test runner functionality

This script provides command-line execution of feature files with:
- XML configuration support
- Tag-based filtering
- Environment selection
- Rich reporting
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path

# Import suite management components
try:
    from qaf.automation.suite.manager import SuiteManager
    from qaf.automation.suite.executor import SuiteExecutor
    from qaf.automation.suite.report_integrator import ReportIntegrator
    from qaf.automation.suite.ci_integration import CIIntegrator, CIExecutionConfig, create_ci_config_from_env
    SUITE_SUPPORT_AVAILABLE = True
except ImportError:
    SUITE_SUPPORT_AVAILABLE = False


def handle_list_suites():
    """Handle --list-suites command"""
    print("=" * 60)
    print("Available Test Suites")
    print("=" * 60)
    
    try:
        manager = SuiteManager()
        suite_details = manager.list_suites(include_details=True)
        
        if not suite_details:
            print("No test suites found in test-suites/ directory.")
            print("Create XML suite configuration files in test-suites/ to get started.")
            return 0
        
        for suite_info in suite_details:
            suite_name = suite_info['name']
            suite_path = suite_info['file_path']
            print(f"Suite: {suite_name}")
            print(f"  Path: {suite_path}")
            
            # Get suite details from the suite_info instead of loading config again
            print(f"  Description: {suite_info.get('description') or 'No description'}")
            print(f"  Scenario Paths: {len(suite_info.get('scenario_paths', []))} path(s)")
            
            # Show tags
            include_tags = suite_info.get('include_tags', [])
            exclude_tags = suite_info.get('exclude_tags', [])
            if include_tags:
                print(f"  Include Tags: {', '.join(include_tags)}")
            if exclude_tags:
                print(f"  Exclude Tags: {', '.join(exclude_tags)}")
            print()
        
        print("=" * 60)
        print(f"Total: {len(suite_details)} suite(s) available")
        
    except Exception as e:
        print(f"Error listing suites: {str(e)}")
        return 1
    
    return 0


def handle_validate_suite(suite_path):
    """Handle --validate-suite command"""
    print("=" * 60)
    print(f"Validating Suite: {suite_path}")
    print("=" * 60)
    
    try:
        manager = SuiteManager()
        
        # Check if file exists
        if not os.path.exists(suite_path):
            print(f"ERROR: Suite file not found: {suite_path}")
            return 1
        
        # Load and validate suite
        suite_name = os.path.splitext(os.path.basename(suite_path))[0]
        config = manager.get_suite(suite_name)
        
        print("[OK] XML syntax is valid")
        print("[OK] Schema validation passed")
        print(f"[OK] Suite name: {config.name}")
        print(f"[OK] Description: {config.description or 'None'}")
        print(f"[OK] Scenario paths: {len(config.scenario_paths)}")
        
        # Validate test files exist
        missing_files = []
        for scenario_path in config.scenario_paths:
            feature_path = scenario_path.replace('.', '/') + '.feature'
            if not os.path.exists(feature_path):
                missing_files.append(feature_path)
        
        if missing_files:
            print("\n[WARNING] Missing feature files:")
            for file_path in missing_files:
                print(f"  - {file_path}")
        
        # Validate report integration
        print("\nValidating report integration...")
        integrator = ReportIntegrator()
        status = integrator.validate_report_integration()
        
        if status.valid:
            print("[OK] Report integration is valid")
            if status.allure_configured:
                print("[OK] Allure reporting configured")
            else:
                print("[WARNING] Allure reporting not configured")
        else:
            print("[ERROR] Report integration issues found:")
            for error in status.errors:
                print(f"  - {error}")
        
        print("\n" + "=" * 60)
        print("Suite validation completed successfully!")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Validation failed: {str(e)}")
        return 1


def handle_suite_execution(args):
    """Handle suite execution with XML configuration"""
    print("=" * 60)
    print("XML Suite Execution")
    print("=" * 60)
    
    try:
        # Load suite configuration
        manager = SuiteManager()
        suite_name = os.path.splitext(os.path.basename(args.suite_config))[0]
        config = manager.get_suite(suite_name)
        
        print(f"Suite: {config.name}")
        print(f"Description: {config.description or 'No description'}")
        print(f"Scenario Paths: {len(config.scenario_paths)} path(s)")
        print("=" * 60)
        
        # Validate report integration
        integrator = ReportIntegrator()
        if not integrator.preserve_allure_config():
            print("[WARNING] Allure configuration issues detected")
            print("Report generation may not work as expected")
        
        # Execute suite
        executor = SuiteExecutor()
        
        if args.dry_run:
            print("DRY RUN - Command that would be executed:")
            command = executor._build_behave_command(config)
            print(f"Command: {' '.join(command)}")
            return 0
        
        print("Starting suite execution...")
        result = executor.execute_suite(config)
        
        print("=" * 60)
        print("Execution Results:")
        print(f"Duration: {result.execution_time:.2f} seconds")
        print(f"Exit Code: {result.exit_code}")
        print(f"Scenarios Passed: {result.passed}")
        print(f"Scenarios Failed: {result.failed}")
        print(f"Scenarios Skipped: {result.skipped}")
        
        if result.exit_code == 0:
            print("SUCCESS: Suite execution completed successfully!")
        else:
            print("FAILURE: Suite execution completed with failures!")
        
        # Print report locations
        print_suite_report_locations(args)
        print("=" * 60)
        
        return result.exit_code
        
    except Exception as e:
        print(f"ERROR: Suite execution failed: {str(e)}")
        return 1


def print_suite_report_locations(args):
    """Print information about generated reports for suite execution"""
    print("\nGenerated Reports:")
    
    # Check standard report locations
    report_locations = [
        "reports/allure-results",
        "reports/test_reports", 
        "reports/allure-history"
    ]
    
    for location in report_locations:
        if os.path.exists(location):
            abs_path = os.path.abspath(location)
            print(f"Report Directory: {abs_path}")
            
            # Count files
            try:
                file_count = len([f for f in os.listdir(location) 
                                if os.path.isfile(os.path.join(location, f))])
                print(f"  Files: {file_count}")
            except Exception:
                pass
    
    # Allure serve command
    if os.path.exists("reports/allure-results"):
        print(f"View Allure Report: allure serve reports/allure-results")


def handle_create_suite(suite_name):
    """Handle --create-suite command with interactive configuration"""
    print("=" * 60)
    print(f"Creating New Test Suite: {suite_name}")
    print("=" * 60)
    
    try:
        manager = SuiteManager()
        
        # Check if suite already exists
        if manager.repository.suite_exists(suite_name):
            print(f"ERROR: Suite '{suite_name}' already exists!")
            print("Use --update-suite to modify existing suites or choose a different name.")
            return 1
        
        print("Interactive Suite Configuration")
        print("-" * 30)
        
        # Collect suite information interactively
        description = input("Suite description (optional): ").strip()
        
        # Collect scenario paths
        print("\nScenario paths (feature files without .feature extension):")
        print("Examples: tests.simple_demo, tests.login, features.smoke")
        print("Enter one path per line, press Enter twice when done:")
        
        scenario_paths = []
        while True:
            path = input("Scenario path: ").strip()
            if not path:
                break
            scenario_paths.append(path)
        
        if not scenario_paths:
            print("WARNING: No scenario paths specified. Adding default 'tests' path.")
            scenario_paths = ["tests"]
        
        # Collect include tags
        print("\nInclude tags (comma-separated, optional):")
        print("Examples: smoke, regression, demo")
        include_tags_input = input("Include tags: ").strip()
        include_tags = [tag.strip() for tag in include_tags_input.split(",")] if include_tags_input else []
        
        # Collect exclude tags
        print("\nExclude tags (comma-separated, optional):")
        print("Examples: slow, unstable, manual")
        exclude_tags_input = input("Exclude tags: ").strip()
        exclude_tags = [tag.strip() for tag in exclude_tags_input.split(",")] if exclude_tags_input else []
        
        # Environment parameters
        print("\nEnvironment parameters (optional):")
        print("Enter key=value pairs, one per line, press Enter twice when done:")
        
        environment_params = {}
        while True:
            param = input("Parameter (key=value): ").strip()
            if not param:
                break
            if "=" in param:
                key, value = param.split("=", 1)
                environment_params[key.strip()] = value.strip()
            else:
                print("Invalid format. Use key=value format.")
        
        # Confirmation
        print("\n" + "=" * 60)
        print("Suite Configuration Summary")
        print("=" * 60)
        print(f"Name: {suite_name}")
        print(f"Description: {description or 'None'}")
        print(f"Scenario Paths: {', '.join(scenario_paths)}")
        print(f"Include Tags: {', '.join(include_tags) if include_tags else 'None'}")
        print(f"Exclude Tags: {', '.join(exclude_tags) if exclude_tags else 'None'}")
        print(f"Environment Params: {len(environment_params)} parameter(s)")
        print("=" * 60)
        
        confirm = input("Create this suite? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Suite creation cancelled.")
            return 0
        
        # Create the suite
        config = manager.create_suite(
            name=suite_name,
            description=description,
            scenario_paths=scenario_paths,
            include_tags=include_tags,
            exclude_tags=exclude_tags,
            environment_params=environment_params
        )
        
        print(f"\n[OK] Suite '{suite_name}' created successfully!")
        print(f"Location: {os.path.abspath(f'test-suites/{suite_name}.xml')}")
        print(f"Use: python run_tests.py --suite-config test-suites/{suite_name}.xml")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Failed to create suite: {str(e)}")
        return 1


def handle_delete_suite(suite_name):
    """Handle --delete-suite command with confirmation"""
    print("=" * 60)
    print(f"Deleting Test Suite: {suite_name}")
    print("=" * 60)
    
    try:
        manager = SuiteManager()
        
        # Check if suite exists
        if not manager.repository.suite_exists(suite_name):
            print(f"ERROR: Suite '{suite_name}' not found!")
            print("Use --list-suites to see available suites.")
            return 1
        
        # Show suite details before deletion
        try:
            config = manager.get_suite(suite_name)
            print(f"Suite: {config.name}")
            print(f"Description: {config.description or 'None'}")
            print(f"Scenario Paths: {len(config.scenario_paths)} path(s)")
            print(f"Include Tags: {', '.join(config.include_tags) if config.include_tags else 'None'}")
            print(f"Exclude Tags: {', '.join(config.exclude_tags) if config.exclude_tags else 'None'}")
        except Exception:
            print("Warning: Could not load suite details")
        
        print("\n" + "=" * 60)
        print("DANGER: This action cannot be undone!")
        print("=" * 60)
        
        # Double confirmation for safety
        confirm1 = input(f"Are you sure you want to delete suite '{suite_name}'? (y/N): ").strip().lower()
        if confirm1 not in ['y', 'yes']:
            print("Deletion cancelled.")
            return 0
        
        confirm2 = input("Type 'DELETE' to confirm: ").strip()
        if confirm2 != 'DELETE':
            print("Deletion cancelled. Confirmation text did not match.")
            return 0
        
        # Delete the suite
        success = manager.delete_suite(suite_name)
        
        if success:
            print(f"\n[OK] Suite '{suite_name}' deleted successfully!")
        else:
            print(f"\n[ERROR] Failed to delete suite '{suite_name}'")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Failed to delete suite: {str(e)}")
        return 1


def handle_suite_details(suite_name):
    """Handle --suite-details command"""
    print("=" * 60)
    print(f"Suite Details: {suite_name}")
    print("=" * 60)
    
    try:
        manager = SuiteManager()
        
        # Check if suite exists
        if not manager.repository.suite_exists(suite_name):
            print(f"ERROR: Suite '{suite_name}' not found!")
            print("Use --list-suites to see available suites.")
            return 1
        
        # Get detailed suite information
        suite_details = manager.repository.get_suite_details(suite_name)
        config = manager.get_suite(suite_name)
        
        # Basic information
        print(f"Name: {config.name}")
        print(f"Description: {config.description or 'None'}")
        print(f"Version: {config.version}")
        
        # File information
        print(f"\nFile Information:")
        print(f"  Path: {suite_details['file_path']}")
        print(f"  Size: {suite_details['file_size']} bytes")
        
        # Convert timestamp to readable format
        import datetime
        last_modified = datetime.datetime.fromtimestamp(suite_details['last_modified'])
        print(f"  Last Modified: {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Configuration details
        print(f"\nConfiguration:")
        print(f"  Scenario Paths: {len(config.scenario_paths)} path(s)")
        for i, path in enumerate(config.scenario_paths, 1):
            print(f"    {i}. {path}")
            # Check if feature file exists
            feature_path = path.replace('.', '/') + '.feature'
            if os.path.exists(feature_path):
                print(f"       -> {feature_path} [EXISTS]")
            else:
                print(f"       -> {feature_path} [MISSING]")
        
        # Tags
        if config.include_tags:
            print(f"  Include Tags: {', '.join(config.include_tags)}")
        else:
            print(f"  Include Tags: None")
        
        if config.exclude_tags:
            print(f"  Exclude Tags: {', '.join(config.exclude_tags)}")
        else:
            print(f"  Exclude Tags: None")
        
        # Environment parameters
        if config.environment_params:
            print(f"  Environment Parameters:")
            for key, value in config.environment_params.items():
                print(f"    {key} = {value}")
        else:
            print(f"  Environment Parameters: None")
        
        # Execution configuration
        if config.execution_config:
            print(f"\nExecution Configuration:")
            print(f"  Stop on Failure: {config.execution_config.stop_on_failure}")
            print(f"  Timeout: {config.execution_config.timeout_seconds} seconds")
            print(f"  Max Retries: {config.execution_config.max_retries}")
            print(f"  Environment: {config.execution_config.environment}")
        
        # Quick validation
        print(f"\nQuick Validation:")
        integrator = ReportIntegrator()
        status = integrator.validate_report_integration()
        
        if status.allure_configured:
            print("  [OK] Allure reporting configured")
        else:
            print("  [WARNING] Allure reporting not configured")
        
        missing_count = sum(1 for path in config.scenario_paths 
                          if not os.path.exists(path.replace('.', '/') + '.feature'))
        if missing_count == 0:
            print("  [OK] All scenario files exist")
        else:
            print(f"  [WARNING] {missing_count} scenario file(s) missing")
        
        print("\n" + "=" * 60)
        print("Suite details completed successfully!")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Failed to get suite details: {str(e)}")
        return 1


def handle_update_suite(suite_name):
    """Handle --update-suite command"""
    print("=" * 60)
    print(f"Updating Test Suite: {suite_name}")
    print("=" * 60)
    
    try:
        manager = SuiteManager()
        
        # Check if suite exists
        if not manager.repository.suite_exists(suite_name):
            print(f"ERROR: Suite '{suite_name}' not found!")
            print("Use --list-suites to see available suites or --create-suite to create a new one.")
            return 1
        
        # Load current configuration
        config = manager.get_suite(suite_name)
        
        print("Current Configuration:")
        print(f"  Description: {config.description or 'None'}")
        print(f"  Scenario Paths: {', '.join(config.scenario_paths)}")
        print(f"  Include Tags: {', '.join(config.include_tags) if config.include_tags else 'None'}")
        print(f"  Exclude Tags: {', '.join(config.exclude_tags) if config.exclude_tags else 'None'}")
        print(f"  Environment Params: {len(config.environment_params)} parameter(s)")
        
        print("\n" + "-" * 30)
        print("Update Configuration (press Enter to keep current value)")
        print("-" * 30)
        
        # Update description
        new_description = input(f"Description [{config.description or ''}]: ").strip()
        if new_description:
            config.description = new_description
        
        # Update scenario paths
        print(f"\nCurrent scenario paths: {', '.join(config.scenario_paths)}")
        update_paths = input("Update scenario paths? (y/N): ").strip().lower()
        if update_paths in ['y', 'yes']:
            print("Enter new scenario paths (one per line, press Enter twice when done):")
            new_paths = []
            while True:
                path = input("Scenario path: ").strip()
                if not path:
                    break
                new_paths.append(path)
            if new_paths:
                config.scenario_paths = new_paths
        
        # Update include tags
        print(f"\nCurrent include tags: {', '.join(config.include_tags) if config.include_tags else 'None'}")
        new_include_tags = input("Include tags (comma-separated): ").strip()
        if new_include_tags:
            config.include_tags = [tag.strip() for tag in new_include_tags.split(",")]
        
        # Update exclude tags
        print(f"\nCurrent exclude tags: {', '.join(config.exclude_tags) if config.exclude_tags else 'None'}")
        new_exclude_tags = input("Exclude tags (comma-separated): ").strip()
        if new_exclude_tags:
            config.exclude_tags = [tag.strip() for tag in new_exclude_tags.split(",")]
        
        # Confirmation
        print("\n" + "=" * 60)
        print("Updated Configuration Summary")
        print("=" * 60)
        print(f"Name: {config.name}")
        print(f"Description: {config.description or 'None'}")
        print(f"Scenario Paths: {', '.join(config.scenario_paths)}")
        print(f"Include Tags: {', '.join(config.include_tags) if config.include_tags else 'None'}")
        print(f"Exclude Tags: {', '.join(config.exclude_tags) if config.exclude_tags else 'None'}")
        print("=" * 60)
        
        confirm = input("Save these changes? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Update cancelled.")
            return 0
        
        # Save the updated suite
        success = manager.update_suite(suite_name, config)
        
        if success:
            print(f"\n[OK] Suite '{suite_name}' updated successfully!")
        else:
            print(f"\n[ERROR] Failed to update suite '{suite_name}'")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"ERROR: Failed to update suite: {str(e)}")
        return 1


def handle_ci_info():
    """Handle --ci-info command"""
    print("=" * 60)
    print("CI/CD Environment Information")
    print("=" * 60)
    
    try:
        integrator = CIIntegrator()
        ci_info = integrator.get_ci_environment_info()
        
        print(f"Detected Provider: {ci_info['detected_provider']}")
        print()
        
        # Environment details
        print("Environment Details:")
        env_details = ci_info['environment_details']
        for key, value in env_details.items():
            if value:
                print(f"  {key}: {value}")
        print()
        
        # Available CI variables
        ci_vars = ci_info['available_variables']
        if ci_vars:
            print(f"Available CI Variables ({len(ci_vars)}):")
            for key, value in sorted(ci_vars.items()):
                # Truncate long values
                display_value = value[:50] + "..." if len(value) > 50 else value
                print(f"  {key}: {display_value}")
        else:
            print("No CI-specific environment variables detected")
        print()
        
        # Recommendations
        print("Recommendations:")
        for i, recommendation in enumerate(ci_info['recommendations'], 1):
            print(f"  {i}. {recommendation}")
        
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"ERROR: Failed to get CI information: {str(e)}")
        return 1


def handle_ci_suite_execution(args):
    """Handle CI/CD suite execution with enhanced features"""
    print("=" * 60)
    print("CI/CD Suite Execution")
    print("=" * 60)
    
    try:
        # Load suite configuration
        manager = SuiteManager()
        suite_name = os.path.splitext(os.path.basename(args.suite_config))[0]
        config = manager.get_suite(suite_name)
        
        print(f"Suite: {config.name}")
        print(f"Description: {config.description or 'No description'}")
        print(f"CI Mode: Enabled")
        
        # Create CI integrator
        integrator = CIIntegrator()
        
        # Display CI environment info
        print(f"CI Provider: {integrator.ci_environment.provider}")
        if integrator.ci_environment.build_number:
            print(f"Build Number: {integrator.ci_environment.build_number}")
        if integrator.ci_environment.branch:
            print(f"Branch: {integrator.ci_environment.branch}")
        
        print("=" * 60)
        
        # Create CI configuration
        ci_config = create_ci_config_from_env()
        
        # Apply command line arguments
        if args.fail_fast:
            ci_config.fail_fast = True
        if args.continue_on_error:
            ci_config.continue_on_error = True
        if args.retry_count:
            ci_config.retry_count = args.retry_count
        if args.timeout_minutes:
            ci_config.timeout_minutes = args.timeout_minutes
        if args.output_format:
            ci_config.output_formats.extend(args.output_format)
        if args.artifacts_dir:
            ci_config.report_artifacts = [
                os.path.join(args.artifacts_dir, 'allure-results'),
                os.path.join(args.artifacts_dir, 'test_reports')
            ]
        
        # Load custom CI config if provided
        if args.ci_config:
            try:
                with open(args.ci_config, 'r') as f:
                    custom_config = json.load(f)
                
                # Update ci_config with custom values
                for key, value in custom_config.items():
                    if hasattr(ci_config, key):
                        setattr(ci_config, key, value)
                
                print(f"Loaded CI configuration from: {args.ci_config}")
            except Exception as e:
                print(f"[WARNING] Failed to load CI config file: {e}")
        
        # Display CI configuration
        print(f"Fail Fast: {ci_config.fail_fast}")
        print(f"Continue on Error: {ci_config.continue_on_error}")
        print(f"Retry Count: {ci_config.retry_count}")
        print(f"Timeout: {ci_config.timeout_minutes} minutes")
        print(f"Output Formats: {', '.join(ci_config.output_formats)}")
        print(f"Artifacts: {len(ci_config.report_artifacts)} location(s)")
        
        if args.dry_run:
            print("\nDRY RUN - CI execution configuration displayed above")
            return 0
        
        print("\nStarting CI suite execution...")
        
        # Execute suite with CI configuration
        ci_result = integrator.execute_suite_for_ci(config, ci_config)
        
        print("=" * 60)
        print("CI Execution Results:")
        print(f"Success: {ci_result.success}")
        print(f"Exit Code: {ci_result.exit_code}")
        print(f"Duration: {ci_result.duration_seconds:.2f} seconds")
        print(f"Scenarios Passed: {ci_result.execution_result.passed}")
        print(f"Scenarios Failed: {ci_result.execution_result.failed}")
        print(f"Scenarios Skipped: {ci_result.execution_result.skipped}")
        
        if ci_result.retry_count > 0:
            print(f"Retries Used: {ci_result.retry_count}")
        
        if ci_result.error_message:
            print(f"Error: {ci_result.error_message}")
        
        # Display generated artifacts
        if ci_result.artifacts_generated:
            print(f"\nGenerated Artifacts ({len(ci_result.artifacts_generated)}):")
            for artifact in ci_result.artifacts_generated:
                abs_path = os.path.abspath(artifact)
                print(f"  - {abs_path}")
        
        # Display CI-specific information
        print(f"\nCI Environment:")
        print(f"  Provider: {ci_result.ci_environment.provider}")
        if ci_result.ci_environment.build_url:
            print(f"  Build URL: {ci_result.ci_environment.build_url}")
        
        print("=" * 60)
        
        if ci_result.success:
            print("SUCCESS: CI suite execution completed successfully!")
        else:
            print("FAILURE: CI suite execution completed with issues!")
        
        # Generate additional CI artifacts
        try:
            # Save detailed CI result
            ci_result_path = os.path.join(args.artifacts_dir, 'ci-execution-result.json')
            os.makedirs(os.path.dirname(ci_result_path), exist_ok=True)
            with open(ci_result_path, 'w') as f:
                f.write(ci_result.to_json())
            print(f"CI result saved to: {os.path.abspath(ci_result_path)}")
            
            # Generate JUnit XML if not already generated
            if 'junit' not in ci_config.output_formats:
                junit_path = os.path.join(args.artifacts_dir, 'junit-results.xml')
                with open(junit_path, 'w') as f:
                    f.write(ci_result.to_junit_xml())
                print(f"JUnit XML saved to: {os.path.abspath(junit_path)}")
            
        except Exception as e:
            print(f"[WARNING] Failed to save additional CI artifacts: {e}")
        
        print("=" * 60)
        
        return ci_result.exit_code
        
    except Exception as e:
        print(f"ERROR: CI suite execution failed: {str(e)}")
        return 1


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='SPF NGEN Test Runner - Python QAF Framework')
    
    # Test suite selection (legacy)
    parser.add_argument('--suite', '-s', 
                       choices=['demo', 'smoke', 'regression'],
                       default='demo',
                       help='Test suite to run (default: demo)')
    
    # XML-based suite configuration (new feature)
    if SUITE_SUPPORT_AVAILABLE:
        parser.add_argument('--suite-config',
                           help='Path to XML suite configuration file (e.g., test-suites/smoke.xml)')
        
        parser.add_argument('--list-suites',
                           action='store_true',
                           help='List all available test suites')
        
        parser.add_argument('--validate-suite',
                           help='Validate suite configuration file')
        
        # Suite creation and management commands
        parser.add_argument('--create-suite',
                           help='Create a new test suite with interactive configuration')
        
        parser.add_argument('--delete-suite',
                           help='Delete an existing test suite with confirmation')
        
        parser.add_argument('--suite-details',
                           help='Show detailed information about a specific suite')
        
        parser.add_argument('--update-suite',
                           help='Update an existing suite configuration')
        
        # CI/CD integration commands
        parser.add_argument('--ci-mode',
                           action='store_true',
                           help='Enable CI/CD mode with enhanced error handling and reporting')
        
        parser.add_argument('--ci-config',
                           help='Path to CI/CD configuration file (JSON format)')
        
        parser.add_argument('--fail-fast',
                           action='store_true',
                           help='Stop execution on first test failure (useful for CI/CD)')
        
        parser.add_argument('--continue-on-error',
                           action='store_true',
                           help='Continue execution even if suite fails (useful for reporting)')
        
        parser.add_argument('--output-format',
                           choices=['allure', 'junit', 'json'],
                           action='append',
                           help='Additional output formats for CI/CD (can be specified multiple times)')
        
        parser.add_argument('--ci-info',
                           action='store_true',
                           help='Display CI/CD environment information')
        
        parser.add_argument('--artifacts-dir',
                           default='reports',
                           help='Directory for CI/CD artifacts (default: reports)')
        
        parser.add_argument('--retry-count',
                           type=int,
                           default=0,
                           help='Number of retries for failed suite execution')
        
        parser.add_argument('--timeout-minutes',
                           type=int,
                           default=60,
                           help='Timeout for suite execution in minutes')
    
    # Environment selection
    parser.add_argument('--env', '-e',
                       choices=['DEV', 'UAT', 'PROD'],
                       default='DEV', 
                       help='Environment to test against (default: DEV)')
    
    # Tag filtering
    parser.add_argument('--tags', '-t',
                       help='Comma-separated list of tags to include (e.g., smoke,regression)')
    
    # Exclude tags
    parser.add_argument('--exclude-tags',
                       help='Comma-separated list of tags to exclude')
    
    # Feature file path
    parser.add_argument('--features',
                       default='tests',
                       help='Path to feature files directory (default: tests)')
    
    # Reporting options
    parser.add_argument('--allure-dir',
                       default='allure-results',
                       help='Allure results directory (default: allure-results)')
    
    parser.add_argument('--html-report',
                       default='test-results/report.html',
                       help='HTML report file path')
    
    # Verbose output
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Verbose output')
    
    # Dry run
    parser.add_argument('--dry-run',
                       action='store_true',
                       help='Show what would be executed without running tests')
    
    args = parser.parse_args()
    
    # Handle suite management commands
    if SUITE_SUPPORT_AVAILABLE:
        if args.ci_info:
            return handle_ci_info()
        
        if args.list_suites:
            return handle_list_suites()
        
        if args.validate_suite:
            return handle_validate_suite(args.validate_suite)
        
        if args.create_suite:
            return handle_create_suite(args.create_suite)
        
        if args.delete_suite:
            return handle_delete_suite(args.delete_suite)
        
        if args.suite_details:
            return handle_suite_details(args.suite_details)
        
        if args.update_suite:
            return handle_update_suite(args.update_suite)
        
        if args.suite_config:
            # Check if CI mode is enabled
            if args.ci_mode or any([args.fail_fast, args.continue_on_error, args.output_format, args.retry_count > 0]):
                return handle_ci_suite_execution(args)
            else:
                return handle_suite_execution(args)
    
    # Build test execution command
    cmd = build_test_command(args)
    
    print("=" * 60)
    print("SPF NGEN Test Runner - Python QAF Framework")
    print("=" * 60)
    print(f"Suite: {args.suite}")
    print(f"Environment: {args.env}")
    print(f"Features: {args.features}")
    print(f"Tags: {args.tags or 'All'}")
    print("=" * 60)
    
    if args.dry_run:
        print("DRY RUN - Command that would be executed:")
        print(" ".join(cmd))
        return 0
    
    # Execute tests
    try:
        print("Starting test execution...")
        result = subprocess.run(cmd, cwd=os.getcwd())
        
        print("=" * 60)
        if result.returncode == 0:
            print("SUCCESS: Test execution completed successfully!")
        else:
            print("FAILURE: Test execution completed with failures!")
        
        print_report_locations(args)
        print("=" * 60)
        
        return result.returncode
        
    except Exception as e:
        print(f"Error executing tests: {e}")
        return 1


def build_test_command(args):
    """Build pytest/behave command based on arguments"""
    
    # Use behave for BDD feature file execution
    return build_behave_command(args)


def build_pytest_command(args):
    """Build pytest command with QAF integration"""
    cmd = ['python', '-m', 'pytest']
    
    # Add verbosity
    if args.verbose:
        cmd.append('-v')
    
    # Add test directory or specific test runner XML
    xml_config = f"test-runner/{args.suite}.xml"
    if os.path.exists(xml_config):
        cmd.append(xml_config)
    else:
        cmd.append(args.features)
    
    # Add tag filtering
    if args.tags:
        tags = args.tags.split(',')
        cmd.extend(['-m', ' or '.join(tags)])
    
    if args.exclude_tags:
        exclude_tags = args.exclude_tags.split(',')
        cmd.extend(['-m', f'not ({" or ".join(exclude_tags)})'])
    
    # Add environment
    cmd.extend(['--env', args.env])
    
    # Add reporting
    cmd.extend(['--alluredir', args.allure_dir])
    cmd.extend(['--html', args.html_report])
    cmd.append('--self-contained-html')
    cmd.append('--clean-alluredir')
    
    return cmd


def build_behave_command(args):
    """Build behave command for BDD execution - Allure formatter is now default in behave.ini"""
    import sys
    python_executable = sys.executable
    cmd = [python_executable, '-m', 'behave']
    
    # Add specific feature file based on suite
    if args.suite == 'demo':
        cmd.append('tests/simple_demo.feature')
    else:
        cmd.append(args.features)
    
    # Add tag filtering based on suite
    suite_tags = {
        'demo': ['demo'],
        'smoke': ['smoke'], 
        'regression': ['regression', 'demo', 'smoke']
    }
    
    if args.suite in suite_tags:
        for tag in suite_tags[args.suite]:
            cmd.extend(['--tags', tag])
    elif args.tags:
        tags = args.tags.split(',')
        for tag in tags:
            cmd.extend(['--tags', tag])
    
    if args.exclude_tags:
        exclude_tags = args.exclude_tags.split(',')
        for tag in exclude_tags:
            cmd.extend(['--tags', f'~{tag}'])
    
    # Note: Allure formatter is now configured by default in behave.ini
    # No need to add it explicitly - it will always be included
    
    return cmd


def print_report_locations(args):
    """Print information about generated reports"""
    print("\nGenerated Reports:")
    
    # HTML Report
    if os.path.exists(args.html_report):
        html_path = os.path.abspath(args.html_report)
        print(f"HTML Report: {html_path}")
    
    # Allure Results
    if os.path.exists(args.allure_dir):
        allure_path = os.path.abspath(args.allure_dir)
        print(f"Allure Results: {allure_path}")
        print(f"   View with: allure serve {allure_path}")
    
    # QAF JSON Reports
    test_results_dir = "test-results"
    if os.path.exists(test_results_dir):
        json_reports = list(Path(test_results_dir).rglob("*.json"))
        if json_reports:
            print(f"QAF JSON Reports: {len(json_reports)} files in {test_results_dir}/")


def run_suite_by_name(suite_name, environment='DEV'):
    """
    Convenience function to run test suite programmatically
    
    Args:
        suite_name: Name of test suite (demo, smoke, regression)
        environment: Environment to test against (DEV, UAT, PROD)
    """
    args = argparse.Namespace(
        suite=suite_name,
        env=environment,
        tags=None,
        exclude_tags=None,
        features='tests',
        allure_dir='allure-results',
        html_report='test-results/report.html',
        verbose=True,
        dry_run=False
    )
    
    cmd = build_test_command(args)
    
    print(f"Running {suite_name} test suite in {environment} environment...")
    
    try:
        result = subprocess.run(cmd, cwd=os.getcwd())
        return result.returncode == 0
    except Exception as e:
        print(f"Error running test suite: {e}")
        return False


if __name__ == '__main__':
    sys.exit(main())