# Test Suites Directory

This directory contains XML-based test suite configurations for the QAF-Python framework, inspired by QMetry's Test Runner system.

## Directory Structure

```
test-suites/
├── schemas/           # XSD schema files for validation
│   └── suite.xsd     # Main test suite schema
├── examples/         # Sample test suite configurations
│   ├── smoke-suite.xml
│   └── regression-suite.xml
└── README.md         # This file
```

## XML Configuration Format

Test suite configurations follow this XML structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<suite name="suite-name" version="1.0">
    <description>Suite description</description>
    
    <parameters>
        <parameter name="env" value="DEV"/>
        <parameter name="browser" value="chrome"/>
    </parameters>
    
    <test name="test-name">
        <groups>
            <run>
                <include name="smoke"/>
                <exclude name="slow"/>
            </run>
        </groups>
        
        <classes>
            <class name="tests.feature_file.feature"/>
            <class name="tests"/>  <!-- Directory reference -->
        </classes>
    </test>
</suite>
```

## Key Elements

- **suite**: Root element with required `name` attribute
- **description**: Optional suite description
- **parameters**: Environment and execution parameters
- **test**: Test configuration (can have multiple)
- **groups**: Behave tag filtering (include/exclude)
- **classes**: Feature file or directory references

## Usage

Test suites are executed using the suite management CLI:

```bash
# Execute a specific suite
python run_tests.py --suite-config test-suites/smoke-suite.xml

# List available suites
python run_tests.py --list-suites

# Validate suite configuration
python run_tests.py --validate-suite smoke-suite.xml
```

## Tag-Based Filtering

The `groups` section uses behave tag syntax:
- `include`: Only run scenarios with these tags
- `exclude`: Skip scenarios with these tags

Tags are combined with behave's `--tags` parameter during execution.

## Feature File References

The `classes` section can reference:
- Specific feature files: `tests.simple_demo.feature`
- Directories: `tests` (includes all .feature files recursively)
- Multiple entries for complex test organization

## Validation

All XML files are validated against `schemas/suite.xsd` for:
- Syntax correctness
- Required elements and attributes
- Proper structure and content

## Report Integration

Test suites maintain full compatibility with existing Allure reporting:
- Results go to `reports/allure-results/`
- Current execution reports: `reports/test_reports/{timestamp}/`
- Historical reports: `reports/full-execution-history.html`