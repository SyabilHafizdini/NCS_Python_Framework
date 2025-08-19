# Test Suite Management - Commands to Test and Run

Here are the **CORRECT** commands to test and validate the Test Suite Management feature using **behave** (not pytest).

## 🧪 Testing the Framework

### 1. Direct behave Execution (Original Method)
```bash
# Execute specific feature with tags (original method)
venv_msvc/Scripts/python.exe -m behave tests/simple_demo.feature --tags syabil

# Execute with different tags
venv_msvc/Scripts/python.exe -m behave tests/simple_demo.feature --tags demo

# Execute multiple tags
venv_msvc/Scripts/python.exe -m behave tests/simple_demo.feature --tags "syabil or demo"

# Execute without tags (all scenarios)
venv_msvc/Scripts/python.exe -m behave tests/simple_demo.feature
```

### 2. Legacy run_tests.py Execution (Still Works!)
```bash
# Execute demo suite (legacy method)
venv_msvc/Scripts/python.exe run_tests.py --suite demo

# Execute with different environments
venv_msvc/Scripts/python.exe run_tests.py --suite demo --env DEV
venv_msvc/Scripts/python.exe run_tests.py --suite demo --env UAT
venv_msvc/Scripts/python.exe run_tests.py --suite demo --env PROD

# Execute with tags
venv_msvc/Scripts/python.exe run_tests.py --suite smoke --tags smoke,demo

# Dry run (preview command)
venv_msvc/Scripts/python.exe run_tests.py --suite demo --dry-run
```

## 🚀 New Suite Management Commands

### 1. List Available Test Suites
```bash
venv_msvc/Scripts/python.exe run_tests.py --list-suites
```

### 2. Create New Test Suite (Interactive)
```bash
venv_msvc/Scripts/python.exe run_tests.py --create-suite my-new-suite
```

### 3. View Suite Details
```bash
venv_msvc/Scripts/python.exe run_tests.py --suite-details demo
venv_msvc/Scripts/python.exe run_tests.py --suite-details comprehensive-test-suite
```

### 4. Validate Suite Configuration
```bash
venv_msvc/Scripts/python.exe run_tests.py --validate-suite test-suites/demo.xml
venv_msvc/Scripts/python.exe run_tests.py --validate-suite test-suites/examples/basic-smoke.xml
```

### 5. Update Existing Suite
```bash
venv_msvc/Scripts/python.exe run_tests.py --update-suite demo
```

### 6. Delete Suite (with confirmation)
```bash
venv_msvc/Scripts/python.exe run_tests.py --delete-suite my-test-suite
```

## 🎯 Suite Execution Commands

### 1. Execute XML-Based Test Suites
```bash
# Execute demo suite using XML configuration
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/demo.xml

# Execute comprehensive suite
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/comprehensive-test-suite.xml

# Execute example suites (after creating them)
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/examples/basic-smoke.xml
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/examples/api-validation.xml
```

### 2. Dry Run Execution (Preview Commands)
```bash
# Preview what behave command would be executed
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/demo.xml --dry-run
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/comprehensive-test-suite.xml --dry-run
```

### 3. CI/CD Mode Execution
```bash
# Execute with CI/CD enhancements
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/demo.xml --ci-mode --fail-fast

# With custom output formats
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/demo.xml --ci-mode --output-format junit --output-format json

# With retry and timeout
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/demo.xml --ci-mode --retry-count 2 --timeout-minutes 30
```

## 🔧 Understanding the Generated Commands

### Example 1: Demo Suite Execution
```bash
# Your command:
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/demo.xml

# Generated behave command:
C:\Users\syabz\Downloads\NCS_Python_Framework\venv_msvc\Scripts\python.exe -m behave tests\simple_demo.feature --tags syabil -D env=UAT -D browser=chrome -D timeout=30 --logging-level INFO
```

### Example 2: Comprehensive Suite with Multiple Tags
```bash
# Your command:
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/comprehensive-test-suite.xml

# Generated behave command:
C:\Users\syabz\Downloads\NCS_Python_Framework\venv_msvc\Scripts\python.exe -m behave tests\simple_demo.feature --include tests\automation_library_demo.feature --tags (syabil or regression) and not slow and not unstable -D env=UAT -D browser=chrome -D timeout=30 --logging-level INFO
```

### Example 3: Legacy Execution
```bash
# Your command:
venv_msvc/Scripts/python.exe run_tests.py --suite demo

# Generated behave command:
C:\Users\syabz\Downloads\NCS_Python_Framework\venv_msvc\Scripts\python.exe -m behave tests/simple_demo.feature --tags demo
```

## 📋 Quick Validation Sequence

### Complete Feature Test (5 minutes)
```bash
# 1. Test original behave execution
venv_msvc/Scripts/python.exe -m behave tests/simple_demo.feature --tags syabil

# 2. Test legacy execution
venv_msvc/Scripts/python.exe run_tests.py --suite demo

# 3. List available suites
venv_msvc/Scripts/python.exe run_tests.py --list-suites

# 4. Test new suite execution
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/demo.xml

# 5. Test dry run functionality
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/demo.xml --dry-run

# 6. Test comprehensive suite
venv_msvc/Scripts/python.exe run_tests.py --suite-config test-suites/comprehensive-test-suite.xml --dry-run
```

## 🎯 Expected Results

When running these commands, you should see:

1. **Direct behave**: Test execution with behave output and HTML reports generated
2. **Legacy execution**: Same behavior as before with `run_tests.py --suite demo`
3. **Suite Management**: Proper listing, creation, and management of XML-based suites
4. **New Suite Execution**: XML suites properly converted to behave commands with:
   - Correct Python executable path
   - Proper tag expressions
   - Environment parameters as `-D` options
   - Feature file paths resolved correctly
5. **Result Parsing**: Accurate scenario counts (passed/failed/skipped) displayed
6. **Report Generation**: Reports generated in `reports/test_reports/` and `reports/allure-results/`

## 🔍 Current Test Suite Configurations

Based on your current setup:

### Demo Suite (`test-suites/demo.xml`)
- **Feature**: `tests.simple_demo.feature`
- **Tag**: `syabil`
- **Environment**: UAT
- **Parameters**: browser=chrome, timeout=30

### Comprehensive Suite (`test-suites/comprehensive-test-suite.xml`)
- **Features**: `tests.simple_demo.feature`, `tests.automation_library_demo.feature`
- **Tags**: Include `syabil` and `regression`, Exclude `slow` and `unstable`
- **Environment**: UAT
- **Parameters**: browser=chrome, timeout=30

## ✅ Framework Status

The Test Suite Management feature is **fully operational** with:
- ✅ **Correct behave Integration**: Uses proper virtual environment Python executable
- ✅ **Tag Processing**: Properly converts XML tag configuration to behave tag expressions
- ✅ **Parameter Injection**: Environment parameters passed as `-D` options to behave
- ✅ **Result Parsing**: Accurate parsing of behave output for scenario counts
- ✅ **Report Preservation**: Maintains existing report generation workflow
- ✅ **Backward Compatibility**: Legacy `--suite demo` commands work unchanged

The framework correctly uses **behave for test execution** (not pytest) and maintains full compatibility with your existing QAF-Python framework setup.