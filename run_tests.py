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

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='SPF NGEN Test Runner - Python QAF Framework')
    
    # Test suite selection
    parser.add_argument('--suite', '-s', 
                       choices=['demo', 'smoke', 'regression'],
                       default='demo',
                       help='Test suite to run (default: demo)')
    
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
    cmd = ['python', '-m', 'behave']
    
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