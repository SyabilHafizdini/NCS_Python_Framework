# Quick Start: Migrating from Individual Feature Files to Test Suites

This guide helps you quickly migrate from running individual feature files with `behave` to using the Test Suite Management system.

## Before: Individual Feature Execution

### Current Workflow
```bash
# Running individual features
behave tests/login.feature --tags="smoke and not manual"
behave tests/api/user_management.feature --tags="regression"
behave tests/checkout.feature -D base_url=https://staging.example.com
```

### Challenges with Individual Execution
- ❌ Repetitive command-line parameters
- ❌ Difficult to manage multiple test runs
- ❌ No centralized configuration
- ❌ Hard to reproduce exact test conditions
- ❌ Manual coordination of related tests

## After: Test Suite Management

### New Workflow
```bash
# Create once, run many times
python run_tests.py --suite-config test-suites/daily-smoke.xml
python run_tests.py --suite-config test-suites/api-regression.xml
python run_tests.py --suite-config test-suites/staging-checkout.xml
```

### Benefits of Test Suites
- ✅ Centralized configuration management
- ✅ Repeatable test execution
- ✅ Environment-specific parameters
- ✅ Advanced retry and timeout options
- ✅ Comprehensive reporting and CI/CD integration

## 5-Minute Migration Guide

### Step 1: Identify Your Current Commands

First, document your current behave commands:

```bash
# Example current commands:
behave tests/login.feature --tags="smoke and not manual"
behave tests/inventory.feature --tags="smoke" -D browser=firefox
behave tests/api/ --tags="api and regression" -D api_url=https://api.staging.com
```

### Step 2: Create Your First Suite

Create `test-suites/my-first-suite.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<suite name="my-first-suite" version="1.0">
    <description>Migrated from my daily test runs</description>
    
    <!-- Replace -D parameters with suite parameters -->
    <parameters>
        <parameter name="browser" value="firefox"/>
        <parameter name="api_url" value="https://api.staging.com"/>
    </parameters>
    
    <test name="daily-tests">
        <groups>
            <run>
                <!-- Replace --tags with include/exclude -->
                <include name="smoke"/>
                <exclude name="manual"/>
            </run>
        </groups>
        
        <classes>
            <!-- Replace feature file paths -->
            <class name="tests.login"/>
            <class name="tests.inventory"/>
            <class name="tests.api"/>
        </classes>
    </test>
</suite>
```

### Step 3: Test Your Migration

```bash
# Validate your new suite
python run_tests.py --validate-suite test-suites/my-first-suite.xml

# Preview the command (dry run)
python run_tests.py --suite-config test-suites/my-first-suite.xml --dry-run

# Execute your suite
python run_tests.py --suite-config test-suites/my-first-suite.xml
```

### Step 4: Verify Reports Still Work

Your existing Allure reports will continue to work automatically:
- Reports still go to `reports/allure-results/`
- `behave.ini` configuration is preserved
- `tests/environment.py` hooks still function

## Common Migration Patterns

### Pattern 1: Single Feature File
**Before:**
```bash
behave tests/login.feature --tags="smoke"
```

**After:**
```xml
<suite name="login-smoke">
    <test name="login-tests">
        <groups>
            <run><include name="smoke"/></run>
        </groups>
        <classes>
            <class name="tests.login"/>
        </classes>
    </test>
</suite>
```

### Pattern 2: Multiple Features with Parameters
**Before:**
```bash
behave tests/checkout/ tests/payment/ --tags="e2e" -D env=staging -D timeout=60
```

**After:**
```xml
<suite name="checkout-e2e">
    <parameters>
        <parameter name="env" value="staging"/>
        <parameter name="timeout" value="60"/>
    </parameters>
    <test name="checkout-tests">
        <groups>
            <run><include name="e2e"/></run>
        </groups>
        <classes>
            <class name="tests.checkout"/>
            <class name="tests.payment"/>
        </classes>
    </test>
</suite>
```

### Pattern 3: Complex Tag Expression
**Before:**
```bash
behave tests/ --tags="(smoke or critical) and not manual and not slow"
```

**After:**
```xml
<suite name="fast-critical">
    <test name="critical-tests">
        <groups>
            <run>
                <include name="smoke"/>
                <include name="critical"/>
                <exclude name="manual"/>
                <exclude name="slow"/>
            </run>
        </groups>
        <classes>
            <class name="tests"/>
        </classes>
    </test>
</suite>
```

## Migration Checklist

### ✅ Pre-Migration
- [ ] Document all current behave commands
- [ ] Note all `-D` parameters used
- [ ] List all `--tags` expressions
- [ ] Identify feature file paths

### ✅ During Migration
- [ ] Create XML suite configuration
- [ ] Map parameters to `<parameters>` section
- [ ] Convert tags to `<include>`/`<exclude>`
- [ ] Convert paths to `<class>` elements
- [ ] Validate suite configuration

### ✅ Post-Migration
- [ ] Test dry-run execution
- [ ] Verify actual execution works
- [ ] Confirm reports are generated
- [ ] Update CI/CD scripts if needed
- [ ] Document new workflow for team

## Advanced Migration Features

### Adding Retry Logic
Enhance your migrated suites with automatic retry:

```xml
<execution>
    <retry maxAttempts="2" delaySeconds="10" retryOnFailure="true"/>
</execution>
```

### Environment-Specific Configuration
Create different suites for different environments:

```xml
<environment default="staging">
    <variable name="API_URL" value="https://api.staging.com" environment="staging"/>
    <variable name="API_URL" value="https://api.prod.com" environment="production"/>
</environment>
```

### Timeout Management
Add comprehensive timeout control:

```xml
<execution>
    <timeout suite="3600" scenario="300" step="30"/>
</execution>
```

## Troubleshooting Migration

### Common Issues and Solutions

#### Issue: "No scenarios found"
**Cause:** Incorrect feature file paths
**Solution:** 
```bash
# Check your actual file structure
find tests/ -name "*.feature"
# Update <class> paths accordingly
```

#### Issue: "Tag not found"
**Cause:** Tag mismatch between suite and feature files  
**Solution:**
```bash
# Search for actual tags in your features
grep -r "@" tests/ | grep -E "@\w+"
# Update include/exclude tags accordingly
```

#### Issue: "Parameter not applied"
**Cause:** Parameter name mismatch  
**Solution:**
```bash
# Check how parameters are used in your steps
grep -r "context.config.userdata" tests/
# Ensure parameter names match
```

## Next Steps

1. **Start with Simple Migration:** Begin with your most common behave commands
2. **Gradually Add Features:** Add retry, timeouts, and environment configs as needed
3. **Update CI/CD:** Modify your automated scripts to use suite execution
4. **Team Training:** Share the new workflow with your team
5. **Create Multiple Suites:** Organize tests into logical suites (smoke, regression, api, etc.)

## Getting Help

- **Validate Issues:** Use `--validate-suite` for configuration problems
- **Debug Commands:** Use `--dry-run` to see generated behave commands
- **Check Documentation:** See [Test Suite Management Guide](TEST_SUITE_MANAGEMENT.md)
- **Example Reference:** Check `test-suites/examples/` for working examples

## Migration Success Indicators

You've successfully migrated when:
- ✅ All previous test executions work as suites
- ✅ Reports continue to generate normally
- ✅ CI/CD pipelines use suite execution
- ✅ Team adopts suite-based workflow
- ✅ Configuration is centralized and maintainable

**Congratulations!** You've successfully migrated to the Test Suite Management system and can now benefit from centralized configuration, advanced execution options, and improved test organization.