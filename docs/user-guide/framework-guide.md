# QAF Python Automation Framework - Complete User Guide

## Table of Contents
1. [Framework Overview](#framework-overview)
2. [Creating New Test Cases](#creating-new-test-cases)
3. [Pattern Locator System](#pattern-locator-system)
4. [Step Definition Linking](#step-definition-linking)
5. [Report Generation](#report-generation)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Framework Overview

The QAF Python Automation Framework is a comprehensive BDD (Behavior Driven Development) testing framework that uses:
- **Behave** for BDD test execution
- **QAF Pattern Locators** for dynamic element identification
- **Allure** for rich test reporting
- **Selenium WebDriver** for browser automation

### Architecture Components
```
QAF_Python_Framework/
├── tests/                          # BDD Feature files and test components
│   ├── *.feature                   # Gherkin test scenarios
│   ├── steps/                      # Step definitions
│   │   └── spf_ngen_steps.py      # Pattern-based step implementations
│   ├── automation_library/        # Reusable automation functions
│   │   ├── BrowserGlobal.py       # Core browser operations
│   │   └── Web.py                 # Pattern-based interactions
│   └── environment.py              # Behave hooks for auto-logging
├── resources/                      # Configuration & locators
│   ├── locators/
│   │   ├── loc_pattern.properties  # Dynamic XPath patterns
│   │   └── saucedemo.properties   # Page-specific locators
│   └── project_config.properties  # Framework configuration
├── test_data/                      # Test data & environment configs
├── allure-results/                 # Generated test results
└── venv_msvc/                     # Python virtual environment
```

---

## Creating New Test Cases

### Step 1: Write Feature File

Create a new `.feature` file in the `tests/` directory following Gherkin syntax:

```gherkin
# tests/new_feature.feature
@smoke @regression
Feature: User Management
  As an administrator
  I want to manage user accounts
  So that I can control access to the system

  Background:
    Given I set page name userManagementPage
    And I open web browser with https://yourapp.com and maximise window

  @TestCaseId:USER_001 @PRIORITY:HIGH
  Scenario: Create New User Account
    When I click button using pattern field CreateUser
    And I input text using pattern value newuser123 field Username
    And I input text using pattern value newuser@test.com field Email
    And I click button using pattern field Save
    Then I verify page contains text User created successfully
    And I take screenshot with comment User creation completed
```

### Step 2: Add Page-Specific Locators

Add locators to `resources/locators/yourapp.properties`:

```properties
# resources/locators/yourapp.properties
# User Management Page Locators
userManagementPage.CreateUser.button=xpath=//button[@id='create-user-btn']
userManagementPage.Username.input=xpath=//input[@name='username']
userManagementPage.Email.input=xpath=//input[@name='email']
userManagementPage.Save.button=xpath=//button[@type='submit']

# Navigation Page Locators
navigationPage.UserManagement.link=xpath=//a[contains(text(),'User Management')]
```

### Step 3: Create Step Definitions (if needed)

Most common steps are already implemented. Add new steps only if needed:

```python
# tests/steps/custom_steps.py
from behave import when, then
from tests.automation_library import BrowserGlobal as BG, Web

@when('I navigate to user management page')
def step_navigate_to_user_management(context):
    """Navigate to user management page"""
    with allure.step("Navigate to user management page"):
        Web.click_link_pattern("UserManagement")

@then('I should see "{page_name}" page')
def step_verify_page(context, page_name):
    """Verify specific page is displayed"""
    with allure.step(f"Verify {page_name} page is displayed"):
        Web.verify_page_contains_text(page_name)
```

### Step 4: Run Your Tests

```bash
# Run specific feature file
venv_msvc/Scripts/python.exe -m behave tests/new_feature.feature

# Run with tags
venv_msvc/Scripts/python.exe -m behave tests/ -t @smoke

# Run with Allure reporting
venv_msvc/Scripts/python.exe -m behave tests/new_feature.feature -f allure_behave.formatter:AllureFormatter -o allure-results
```

---

## Pattern Locator System

### How Pattern Locators Work

The QAF Pattern Locator System generates dynamic XPath locators at runtime using a 3-tier approach:

```
1. Hardcoded Locators (Highest Priority)
   ↓
2. Dynamic Pattern Generation
   ↓
3. Fallback Generic Patterns (Lowest Priority)
```

### 1. Hardcoded Locators

**File**: `resources/locators/{yourapp}.properties`
**Format**: `{page}.{fieldName}.{elementType}=locator`

```properties
# Specific locators for your application
loginPage.Username.input=xpath=//input[@id='username-field']
loginPage.Login.button=xpath=//button[@class='login-btn']
dashboardPage.Welcome.text=xpath=//h1[@class='welcome-msg']
```

### 2. Dynamic Pattern Generation

**File**: `resources/locators/loc_pattern.properties`
**Format**: Uses placeholder variables that get replaced at runtime

```properties
# Dynamic patterns with variables
loc.qaf.pattern.input=xpath=//input[@name='${loc.auto.fieldName}'] | //input[@id='${loc.auto.fieldName}'] | //input[contains(@placeholder,'${loc.auto.fieldName}')]

loc.qaf.pattern.button=xpath=//button[contains(text(),'${loc.auto.fieldName}')] | //button[@value='${loc.auto.fieldName}'] | //button[@id='${loc.auto.fieldName}']
```

**Variable Substitution**:
- `${loc.auto.fieldName}` → Replaced with field name (e.g., "Username", "Login")
- `${loc.auto.fieldValue}` → Replaced with field value (e.g., "login-btn", "user-input")

### 3. Pattern Locator Usage in Steps

```python
# In step definitions, use the Web module functions
from tests.automation_library import Web

# Set page context
Web.set_page_name("loginPage")

# Use pattern-based interactions
Web.input_text_pattern("user@test.com", "Username")  # Uses pattern system
Web.click_button_pattern("Login")                     # Finds button dynamically
```

### Adding New Element Types

To support new element types, add patterns to `loc_pattern.properties`:

```properties
# Custom element patterns
loc.qaf.pattern.dropdown=xpath=//select[@name='${loc.auto.fieldName}'] | //div[@class='dropdown'][contains(text(),'${loc.auto.fieldName}')]
loc.qaf.pattern.modal=xpath=//div[@class='modal'][contains(.,'${loc.auto.fieldName}')] | //dialog[@title='${loc.auto.fieldName}']
```

---

## Step Definition Linking

### IDE Integration (Ctrl+Click Navigation)

**✅ Correct Parameter Format** (enables IDE linking):
```python
@when('I enter username {string} using pattern locator')
def step_enter_username(context, username):
    # Implementation
```

**❌ Incorrect Format** (breaks IDE linking):
```python
@when('I enter username "{username}" using pattern locator')  # Don't use this
```

### Step Definition Categories

#### 1. Navigation Steps
```python
@given('I open web browser with {url} and maximise window')
@when('I set page name {page_name}')
@when('I navigate to {page_name} page')
```

#### 2. Input Steps  
```python
@when('I input text using pattern value {value} field {field}')
@when('I clear and fill using pattern value {value} field {field}')
@when('I fill {value} into {locator}')
```

#### 3. Action Steps
```python
@when('I click button using pattern field {field}')
@when('I click link using pattern field {field}')
@when('I click on {locator}')
```

#### 4. Verification Steps
```python
@then('I verify page contains text {text}')
@then('I verify element using pattern {element} field {field} is present')
@then('I verify {locator} is present')
@then('I assert {locator} text is {text}')
```

### Adding Custom Step Definitions

```python
@when('I upload file {file_path} to {field_name} field using pattern')
def step_upload_file_pattern(context, file_path, field_name):
    """Upload file using pattern locator"""
    with allure.step(f"Upload file {file_path} to {field_name} field"):
        # Use automation library functions
        upload_field = Web._find_element_by_pattern("input", field_name)
        upload_field.send_keys(file_path)

@then('I should see {expected_count:d} items in {list_name} list')
def step_verify_list_count(context, expected_count, list_name):
    """Verify list item count"""
    with allure.step(f"Verify {expected_count} items in {list_name} list"):
        from tests.automation_library.BrowserGlobal import _find_element
        list_element = _find_element(f"xpath=//ul[contains(@class,'{list_name}')]")
        items = list_element.find_elements(By.XPATH, ".//li")
        assert len(items) == expected_count, f"Expected {expected_count} items, found {len(items)}"
```

---

## Report Generation

### Automatic Allure Reporting

The framework includes **automatic logging** through Behave environment hooks in `tests/environment.py`:

#### What Gets Logged Automatically:
- 📸 **Screenshots** at each step (before/after)
- 🔗 **Pattern Locator Usage** (generated locators, success/failure)
- 📝 **Step Execution Details** (parameters, duration, status)
- 🌐 **Browser Information** (URL, title, page source)
- 🏷️ **Test Metadata** (tags, scenario info, feature details)
- ❌ **Error Details** (stack traces, failure reasons)

#### Environment Hook Flow:
```python
# tests/environment.py

def before_all(context):
    """Initialize test execution with Allure environment info"""

def before_feature(context, feature):
    """Log feature start with tags and description"""

def before_scenario(context, scenario):
    """Log scenario start with test case ID and priority"""

def before_step(context, step):
    """Take screenshot and log step start"""

def after_step(context, step):
    """Log step completion, take screenshot, attach details"""

def after_scenario(context, scenario):
    """Log final scenario status and cleanup"""

def after_feature(context, feature):
    """Log feature completion summary"""

def after_all(context):
    """Generate final execution summary"""
```

### Report Artifacts

#### Generated Files in `allure-results/`:
```
allure-results/
├── {uuid}-result.json          # Test execution results
├── {uuid}-attachment.png       # Screenshots
├── {uuid}-attachment.txt       # Logs and details
├── environment.properties      # Test environment info
└── categories.json            # Test categorization
```

#### Report Content:
1. **Overview Dashboard**
   - Total tests, pass/fail rates
   - Execution timeline
   - Environment details

2. **Test Suites**
   - Feature-wise test organization
   - Scenario execution details
   - Step-by-step execution flow

3. **Behaviors (BDD View)**
   - Feature stories with scenarios
   - Tags and priority filtering
   - Requirements traceability

4. **Packages**
   - Step definition usage
   - Code coverage insights

5. **Timeline**
   - Execution sequence
   - Parallel execution visualization

6. **Trend Analysis**
   - Historical execution data
   - Performance trends

### Viewing Reports

#### Method 1: Direct File Access
Generated Allure results are stored in `allure-results/` directory. Each test execution creates JSON result files and attachments.

#### Method 2: HTML Report Generation (if Allure CLI available)
```bash
# Install Allure CLI (requires Java)
# Download from: https://docs.qameta.io/allure/#_installing_a_commandline

# Generate and serve HTML report
allure serve allure-results

# Generate static HTML report
allure generate allure-results -o allure-report
```

#### Method 3: CI/CD Integration
```yaml
# Example GitHub Actions integration
- name: Run Tests
  run: |
    venv_msvc/Scripts/python.exe -m behave tests/ -f allure_behave.formatter:AllureFormatter -o allure-results

- name: Generate Allure Report
  uses: simple-elf/allure-report-action@master
  with:
    allure_results: allure-results
    allure_history: allure-history
```

### Custom Report Attachments

While automatic logging handles most scenarios, you can add custom attachments:

```python
import allure
from tests.automation_library import BrowserGlobal as BG

@when('I perform complex operation {operation_name}')
def step_complex_operation(context, operation_name):
    with allure.step(f"Perform complex operation: {operation_name}"):
        # Custom data attachment
        operation_data = {"operation": operation_name, "timestamp": time.time()}
        allure.attach(
            json.dumps(operation_data, indent=2),
            name="Operation Details",
            attachment_type=allure.attachment_type.JSON
        )
        
        # Use automation library for screenshot
        BG.take_screenshot_with_comment(f"Operation_{operation_name}_Screenshot")
```

---

## Best Practices

### 1. Feature File Organization
```gherkin
# Use descriptive feature names and clear scenarios
@smoke @regression @module:login
Feature: Authentication System
  Clear feature description explaining the business value

  Background:
    # Common setup steps for all scenarios
    
  @TestCaseId:AUTH_001 @PRIORITY:CRITICAL @positive
  Scenario: Successful login with valid credentials
    # Clear, actionable steps
    
  @TestCaseId:AUTH_002 @PRIORITY:HIGH @negative  
  Scenario: Login fails with invalid credentials
    # Clear error handling validation
```

### 2. Tagging Strategy
```gherkin
# Functional tags
@smoke          # Critical path tests
@regression     # Full test suite
@sanity         # Basic functionality

# Priority tags  
@PRIORITY:CRITICAL   # Must pass
@PRIORITY:HIGH       # Important
@PRIORITY:MEDIUM     # Standard
@PRIORITY:LOW        # Nice to have

# Test type tags
@positive       # Happy path scenarios
@negative       # Error handling scenarios
@boundary       # Edge case testing

# Module tags
@module:login   @module:dashboard   @module:reports

# Test case tracking
@TestCaseId:AUTH_001   @TestCaseId:DASH_015
```

### 3. Pattern Locator Best Practices

#### Naming Conventions
```properties
# Use clear, consistent naming
{pageName}.{elementFunction}.{elementType}=locator

# Good examples
loginPage.Username.input=xpath=//input[@id='username']
dashboardPage.WelcomeMessage.text=xpath=//h1[@class='welcome']
navigationPage.UserManagement.link=xpath=//a[text()='User Management']

# Avoid generic names
page.field.element=locator  # Too generic
loginPage.input1.input=locator  # Not descriptive
```

#### Locator Priority
```properties
# 1. Use ID when available (fastest, most reliable)
elementId.button=xpath=//button[@id='submit-btn']

# 2. Use name attributes
elementName.input=xpath=//input[@name='username']

# 3. Use class with specific context
elementClass.text=xpath=//div[@class='error-message']

# 4. Use text content (last resort, language-dependent)
elementText.link=xpath=//a[text()='Click Here']
```

### 4. Step Definition Guidelines

```python
# Use descriptive step names
@when('I enter valid login credentials')  # ✅ Clear intent
@when('I do login stuff')                 # ❌ Vague

# Group related functionality
@when('I input text using pattern value {value} field {field}')  # ✅ Reusable

# Use appropriate allure steps
with allure.step("Clear business action description"):
    # Technical implementation
    
# Handle errors gracefully
try:
    element = Web._find_element_by_pattern(...)
except Exception as e:
    allure.attach(str(e), name="Error Details", attachment_type=allure.attachment_type.TEXT)
    raise AssertionError(f"Element not found: {e}")
```

### 5. Test Data Management

```python
# Use environment-specific test data
# test_data/environment_config.py
ENVIRONMENTS = {
    "DEV": {
        "base_url": "https://dev.yourapp.com",
        "users": {
            "admin_user": {"username": "dev_admin", "password": "dev_pass"},
            "standard_user": {"username": "dev_user", "password": "dev_pass"}
        }
    },
    "QA": {
        "base_url": "https://qa.yourapp.com", 
        "users": {
            "admin_user": {"username": "qa_admin", "password": "qa_pass"},
            "standard_user": {"username": "qa_user", "password": "qa_pass"}
        }
    }
}
```

---

## Troubleshooting

### Common Issues

#### 1. Pattern Locator Not Found
**Error**: `Pattern locator failed for loginPage.input.Username`

**Solutions**:
```bash
# Check if locator exists in properties files
grep -r "loginPage.Username.input" resources/locators/

# Verify pattern configuration
grep "loc.qaf.pattern.input" resources/locators/loc_pattern.properties

# Check QAF bundle loading
# Look for: "QAF Pattern Locator System loaded successfully"
```

#### 2. Step Definition Not Found
**Error**: `No step definition found for "When I click the Save button"`

**Solutions**:
```python
# Check parameter format
@when('I click the {string} button using pattern field {field}')  # ✅ Correct

# Verify step import
from behave import given, when, then

# Check step file location
tests/steps/automation_library_steps.py
```

#### 3. WebDriver Issues
**Error**: `WebDriver instance not created`

**Solutions**:
```python
# Check driver initialization
from tests.automation_library.BrowserGlobal import open_browser
open_browser("https://example.com")

# Verify ChromeDriver installation
from webdriver_manager.chrome import ChromeDriverManager
```

#### 4. Allure Report Not Generated
**Error**: `allure-results directory empty`

**Solutions**:
```bash
# Run with explicit Allure formatter
venv_msvc/Scripts/python.exe -m behave tests/ -f allure_behave.formatter:AllureFormatter -o allure-results

# Check allure-behave installation
venv_msvc/Scripts/pip install allure-behave

# Verify environment hooks are working
# Look for: "Starting test execution with automatic Allure reporting..."
```

### Debug Mode

Enable debug logging:
```python
# In tests/steps/custom_steps.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
def debug_step(context):
    print(f"DEBUG: Current page context: {Web.get_current_page_context()}")
    BG.take_screenshot_with_comment("Debug checkpoint")
```

### Performance Optimization

```python
# Use explicit waits instead of sleep
from tests.automation_library.BrowserGlobal import wait_until_element_visible

wait_until_element_visible("xpath=//button[@id='submit']")

# Reuse browser instance when possible
# Don't close browser between related test steps
```

---

## Summary

This QAF Python framework provides:
- 🎯 **BDD-driven** test development with Gherkin syntax
- 🔍 **Dynamic pattern locators** for maintainable element identification  
- 📊 **Rich Allure reporting** with automatic logging
- 🔗 **IDE integration** with proper step definition linking
- 🏗️ **Scalable architecture** supporting multiple applications

**Key Benefits**:
- No hardcoded locators in step definitions
- Automatic screenshot and logging
- Pattern-based element identification
- Environment-specific configuration
- Comprehensive test reporting

Follow this guide to create robust, maintainable test automation that scales with your application development.