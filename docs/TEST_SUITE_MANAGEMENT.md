# Test Suite Management Guide

## Overview

The QAF-Python Test Suite Management feature allows you to organize and execute tests using XML-based suite configurations inspired by QMetry's Test Runner system. This feature enables you to create, manage, and execute test suites with advanced configuration options while maintaining compatibility with your existing behave and Allure workflows.

## Table of Contents

- [Quick Start](#quick-start)
- [Suite Configuration](#suite-configuration)
- [Advanced Features](#advanced-features)
- [CLI Operations](#cli-operations)
- [CI/CD Integration](#cicd-integration)
- [Migration Guide](#migration-guide)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Create Your First Test Suite

Create a simple XML suite configuration:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<suite name="smoke-tests" version="1.0">
    <description>Basic smoke test suite</description>
    
    <parameters>
        <parameter name="base_url" value="https://www.saucedemo.com"/>
        <parameter name="browser" value="chrome"/>
    </parameters>
    
    <test name="smoke-test-execution">
        <groups>
            <run>
                <include name="smoke"/>
                <exclude name="manual"/>
            </run>
        </groups>
        
        <classes>
            <class name="tests.login"/>
            <class name="tests.checkout"/>
        </classes>
    </test>
</suite>
```

### 2. Execute the Suite

```bash
python run_tests.py --suite-config test-suites/smoke-tests.xml
```

### 3. List Available Suites

```bash
python run_tests.py --list-suites
```

## Suite Configuration

### Basic Structure

Every test suite XML file follows this basic structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<suite name="suite-name" version="1.0">
    <description>Suite description</description>
    <parameters><!-- Global parameters --></parameters>
    <execution><!-- Advanced execution config --></execution>
    <test name="test-name">
        <groups><!-- Tag filtering --></groups>
        <classes><!-- Feature file paths --></classes>
    </test>
</suite>
```

### Parameters Section

Define environment variables and configuration:

```xml
<parameters>
    <parameter name="base_url" value="https://staging.example.com"/>
    <parameter name="browser" value="firefox"/>
    <parameter name="timeout" value="30"/>
    <parameter name="screenshot_on_failure" value="true"/>
</parameters>
```

### Test Configuration

#### Tag-Based Filtering

Use behave tags to filter scenarios:

```xml
<groups>
    <run>
        <!-- Include scenarios with these tags -->
        <include name="regression"/>
        <include name="api"/>
        
        <!-- Exclude scenarios with these tags -->
        <exclude name="manual"/>
        <exclude name="experimental"/>
    </run>
</groups>
```

#### Scenario Paths

Specify feature files or directories:

```xml
<classes>
    <!-- Specific feature files -->
    <class name="tests.login.user_authentication"/>
    <class name="tests.api.user_management"/>
    
    <!-- Entire directories -->
    <class name="tests.checkout"/>
    <class name="tests.inventory"/>
</classes>
```

## Advanced Features

### Execution Configuration

Configure advanced execution behaviors:

```xml
<execution stopOnFirstFailure="false" continueOnError="false" maxParallelThreads="1">
    <!-- Timeout configuration -->
    <timeout suite="3600" scenario="300" step="30"/>
    
    <!-- Retry configuration -->
    <retry maxAttempts="2" delaySeconds="10" retryOnFailure="true" retryOnError="true"/>
    
    <!-- Environment configuration -->
    <environment default="staging">
        <!-- Global variables -->
        <variable name="LOG_LEVEL" value="INFO"/>
        <variable name="SCREENSHOT_MODE" value="failure"/>
        
        <!-- Environment-specific variables -->
        <variable name="DB_HOST" value="test-db.example.com" environment="test"/>
        <variable name="DB_HOST" value="staging-db.example.com" environment="staging"/>
        <variable name="DB_HOST" value="prod-db.example.com" environment="production"/>
        
        <!-- Environment profiles -->
        <profile name="test">
            <property name="DEBUG_MODE" value="true"/>
            <property name="VERBOSE_LOGGING" value="true"/>
            <property name="DATA_RESET" value="true"/>
        </profile>
        
        <profile name="staging" extends="test">
            <property name="DEBUG_MODE" value="false"/>
            <property name="PERFORMANCE_MONITORING" value="true"/>
        </profile>
        
        <profile name="production" extends="staging">
            <property name="ERROR_REPORTING" value="true"/>
            <property name="AUDIT_LOGGING" value="true"/>
        </profile>
    </environment>
</execution>
```

### Execution Configuration Options

| Attribute | Description | Default |
|-----------|-------------|---------|
| `stopOnFirstFailure` | Stop execution on first test failure | `false` |
| `continueOnError` | Continue execution even on system errors | `false` |
| `maxParallelThreads` | Maximum parallel execution threads | `1` |

### Timeout Configuration

| Attribute | Description | Default (seconds) |
|-----------|-------------|-------------------|
| `suite` | Maximum time for entire suite | `3600` (1 hour) |
| `scenario` | Maximum time per scenario | `300` (5 minutes) |
| `step` | Maximum time per step | `30` |

### Retry Configuration

| Attribute | Description | Default |
|-----------|-------------|---------|
| `maxAttempts` | Maximum retry attempts | `1` |
| `delaySeconds` | Delay between retries | `5` |
| `retryOnFailure` | Retry on test failures | `false` |
| `retryOnError` | Retry on system errors | `true` |

## CLI Operations

### Suite Management Commands

#### List All Suites
```bash
python run_tests.py --list-suites
```

#### Create New Suite (Interactive)
```bash
python run_tests.py --create-suite
```

#### View Suite Details
```bash
python run_tests.py --suite-details my-test-suite
```

#### Update Existing Suite
```bash
python run_tests.py --update-suite my-test-suite
```

#### Delete Suite
```bash
python run_tests.py --delete-suite my-test-suite
```

#### Validate Suite Configuration
```bash
python run_tests.py --validate-suite test-suites/my-suite.xml
```

### Execution Commands

#### Execute Suite
```bash
python run_tests.py --suite-config test-suites/regression.xml
```

#### Execute with Options
```bash
python run_tests.py --suite-config test-suites/regression.xml --verbose --dry-run
```

#### Preview Command
```bash
python run_tests.py --suite-config test-suites/regression.xml --dry-run
```

## CI/CD Integration

### Environment Variables

Configure CI/CD behavior using environment variables:

```bash
# Basic CI configuration
export QAF_FAIL_FAST=true
export QAF_RETRY_COUNT=2
export QAF_OUTPUT_FORMATS=junit,json,allure
export QAF_TIMEOUT_MINUTES=60

# Custom environment variables (prefixed with QAF_)
export QAF_API_BASE_URL=https://api.staging.example.com
export QAF_BROWSER=headless-chrome
export QAF_PARALLEL_THREADS=4
```

### CI/CD Command Example

```bash
python run_tests.py \
  --suite-config test-suites/ci-regression.xml \
  --ci-mode \
  --fail-fast \
  --output-format junit,json \
  --artifacts-dir reports/ci-artifacts
```

### Jenkins Integration

```groovy
pipeline {
    agent any
    
    environment {
        QAF_FAIL_FAST = 'true'
        QAF_OUTPUT_FORMATS = 'junit,allure'
        QAF_BASE_URL = "${params.ENVIRONMENT_URL}"
    }
    
    stages {
        stage('Test') {
            steps {
                script {
                    sh """
                        python run_tests.py \
                          --suite-config test-suites/regression.xml \
                          --ci-mode \
                          --artifacts-dir reports
                    """
                }
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'reports/**/*.xml'
                    archiveArtifacts artifacts: 'reports/**/*'
                }
            }
        }
    }
}
```

### GitHub Actions Integration

```yaml
name: Test Suite Execution

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        suite: [smoke, regression, api]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Execute Test Suite
      env:
        QAF_FAIL_FAST: 'true'
        QAF_OUTPUT_FORMATS: 'junit,json'
        QAF_BASE_URL: 'https://staging.example.com'
      run: |
        python run_tests.py \
          --suite-config test-suites/${{ matrix.suite }}.xml \
          --ci-mode
    
    - name: Publish Test Results
      uses: dorny/test-reporter@v1
      if: always()
      with:
        name: Test Results (${{ matrix.suite }})
        path: 'reports/**/*.xml'
        reporter: java-junit
```

## Migration Guide

### From Individual Feature Execution

**Before:**
```bash
behave tests/login/user_authentication.feature --tags="smoke and not manual"
```

**After:**
```xml
<!-- Create smoke-login.xml -->
<suite name="smoke-login">
    <test name="login-tests">
        <groups>
            <run>
                <include name="smoke"/>
                <exclude name="manual"/>
            </run>
        </groups>
        <classes>
            <class name="tests.login.user_authentication"/>
        </classes>
    </test>
</suite>
```

```bash
python run_tests.py --suite-config test-suites/smoke-login.xml
```

### From behave.ini Configuration

Your existing `behave.ini` configuration is preserved:

```ini
[behave]
format = allure_behave.formatter:AllureFormatter
outfiles = reports/allure-results
show_timings = true
logging_level = INFO
```

Test suites will automatically use these settings, and your `tests/environment.py` hooks will continue to work.

### Environment Parameter Migration

**Before (behave command):**
```bash
behave tests/ -D base_url=https://staging.example.com -D browser=firefox
```

**After (suite configuration):**
```xml
<parameters>
    <parameter name="base_url" value="https://staging.example.com"/>
    <parameter name="browser" value="firefox"/>
</parameters>
```

## Example Suites

### 1. Basic Smoke Test Suite

```xml
<?xml version="1.0" encoding="UTF-8"?>
<suite name="daily-smoke" version="1.0">
    <description>Daily smoke test execution</description>
    
    <parameters>
        <parameter name="base_url" value="https://www.saucedemo.com"/>
        <parameter name="browser" value="chrome"/>
        <parameter name="timeout" value="30"/>
    </parameters>
    
    <test name="smoke-tests">
        <groups>
            <run>
                <include name="smoke"/>
                <exclude name="manual"/>
                <exclude name="experimental"/>
            </run>
        </groups>
        
        <classes>
            <class name="tests.login"/>
            <class name="tests.inventory"/>
            <class name="tests.cart"/>
        </classes>
    </test>
</suite>
```

### 2. Comprehensive Regression Suite

```xml
<?xml version="1.0" encoding="UTF-8"?>
<suite name="weekly-regression" version="1.0">
    <description>Weekly comprehensive regression testing</description>
    
    <parameters>
        <parameter name="base_url" value="https://staging.saucedemo.com"/>
        <parameter name="browser" value="firefox"/>
        <parameter name="screenshot_on_failure" value="true"/>
        <parameter name="video_recording" value="true"/>
    </parameters>
    
    <execution stopOnFirstFailure="false" continueOnError="false">
        <timeout suite="7200" scenario="600" step="60"/>
        <retry maxAttempts="2" delaySeconds="30" retryOnFailure="true"/>
        
        <environment default="staging">
            <variable name="LOG_LEVEL" value="INFO"/>
            <variable name="PARALLEL_EXECUTION" value="false"/>
            
            <profile name="staging">
                <property name="DB_CLEANUP" value="false"/>
                <property name="MOCK_EXTERNAL_SERVICES" value="true"/>
                <property name="PERFORMANCE_MONITORING" value="true"/>
            </profile>
        </environment>
    </execution>
    
    <test name="regression-tests">
        <groups>
            <run>
                <include name="regression"/>
                <include name="e2e"/>
                <exclude name="manual"/>
                <exclude name="performance"/>
            </run>
        </groups>
        
        <classes>
            <class name="tests.login"/>
            <class name="tests.inventory"/>
            <class name="tests.cart"/>
            <class name="tests.checkout"/>
            <class name="tests.user_management"/>
        </classes>
    </test>
</suite>
```

### 3. API-Only Test Suite

```xml
<?xml version="1.0" encoding="UTF-8"?>
<suite name="api-validation" version="1.0">
    <description>API endpoint validation and testing</description>
    
    <parameters>
        <parameter name="api_base_url" value="https://api.saucedemo.com"/>
        <parameter name="api_version" value="v1"/>
        <parameter name="authentication" value="bearer_token"/>
        <parameter name="rate_limit_delay" value="0.5"/>
    </parameters>
    
    <execution stopOnFirstFailure="false">
        <timeout suite="1800" scenario="300" step="30"/>
        <retry maxAttempts="3" delaySeconds="5" retryOnError="true"/>
        
        <environment default="test">
            <variable name="MOCK_DATABASE" value="true"/>
            <variable name="LOG_API_REQUESTS" value="true"/>
            
            <profile name="test">
                <property name="DB_RESET_BETWEEN_TESTS" value="true"/>
                <property name="CACHE_DISABLED" value="true"/>
            </profile>
        </environment>
    </execution>
    
    <test name="api-tests">
        <groups>
            <run>
                <include name="api"/>
                <include name="integration"/>
                <exclude name="ui"/>
                <exclude name="mobile"/>
            </run>
        </groups>
        
        <classes>
            <class name="tests.api.authentication"/>
            <class name="tests.api.user_management"/>
            <class name="tests.api.product_catalog"/>
            <class name="tests.api.order_processing"/>
        </classes>
    </test>
</suite>
```

### 4. Mobile Test Suite

```xml
<?xml version="1.0" encoding="UTF-8"?>
<suite name="mobile-tests" version="1.0">
    <description>Mobile application testing suite</description>
    
    <parameters>
        <parameter name="platform" value="Android"/>
        <parameter name="device_name" value="Pixel_4"/>
        <parameter name="app_package" value="com.saucelabs.mydemoapp.rn"/>
        <parameter name="automation_name" value="UiAutomator2"/>
        <parameter name="app_activity" value=".MainActivity"/>
    </parameters>
    
    <execution stopOnFirstFailure="true">
        <timeout suite="2400" scenario="480" step="45"/>
        <retry maxAttempts="2" delaySeconds="15" retryOnFailure="true"/>
        
        <environment default="mobile_test">
            <variable name="SCREENSHOT_FREQUENCY" value="all"/>
            <variable name="VIDEO_RECORDING" value="true"/>
            
            <profile name="mobile_test">
                <property name="DEVICE_CLEANUP" value="true"/>
                <property name="APP_RESET" value="true"/>
                <property name="NETWORK_SIMULATION" value="false"/>
            </profile>
        </environment>
    </execution>
    
    <test name="mobile-app-tests">
        <groups>
            <run>
                <include name="mobile"/>
                <include name="smoke"/>
                <exclude name="web"/>
                <exclude name="api"/>
            </run>
        </groups>
        
        <classes>
            <class name="tests.mobile.login"/>
            <class name="tests.mobile.navigation"/>
            <class name="tests.mobile.product_browsing"/>
            <class name="tests.mobile.checkout"/>
        </classes>
    </test>
</suite>
```

## Troubleshooting

### Common Issues

#### 1. Suite Not Found
```
Error: Suite not found: my-test-suite
```
**Solution:** Check that the XML file exists in the `test-suites/` directory and the suite name matches the filename.

#### 2. Invalid XML Format
```
Error: Failed to parse XML: mismatched tag
```
**Solution:** Validate your XML syntax. Common issues:
- Unclosed tags
- Missing namespace declarations
- Invalid attribute values

#### 3. Scenario Paths Not Found
```
Warning: Scenario path not found: tests/invalid_path
```
**Solution:** Verify that feature files exist at the specified paths. Use dot notation for Python module paths.

#### 4. Tag Filtering Issues
```
No scenarios matched the tag expression
```
**Solution:** Check that:
- Tags in your feature files match the include/exclude configuration
- Tag expressions use correct syntax
- Tags are properly formatted (no spaces, alphanumeric)

#### 5. Environment Variables Not Applied
```
Error: Required environment variable not set
```
**Solution:** Ensure:
- Environment variables are defined in suite configuration
- Variable names don't conflict with system variables
- Environment profiles are correctly configured

### Debug Mode

Enable verbose output for troubleshooting:

```bash
python run_tests.py --suite-config my-suite.xml --verbose
```

### Validation

Always validate your suite configuration before execution:

```bash
python run_tests.py --validate-suite test-suites/my-suite.xml
```

### Dry Run

Preview the exact command that will be executed:

```bash
python run_tests.py --suite-config my-suite.xml --dry-run
```

## Best Practices

### 1. Naming Conventions
- Use descriptive suite names: `daily-smoke`, `weekly-regression`, `api-validation`
- Keep filenames consistent with suite names
- Use kebab-case for suite names and file names

### 2. Organization
- Group related suites in subdirectories
- Use consistent parameter naming across suites
- Document suite purposes in descriptions

### 3. Tag Strategy
- Use consistent tagging across feature files
- Create tag hierarchies: `smoke` ⊂ `regression` ⊂ `full`
- Document tag meanings in your team guidelines

### 4. Environment Management
- Use environment profiles for different deployment targets
- Keep environment-specific variables separate
- Use inheritance to reduce duplication

### 5. CI/CD Integration
- Create specific CI suites optimized for speed
- Use appropriate timeout values for CI environments
- Configure artifact collection for debugging

## Support

For additional help:
- Check the [QAF-Python Documentation](README.md)
- Review example configurations in `test-suites/examples/`
- Run `python run_tests.py --help` for CLI options
- Use `--validate-suite` for configuration validation