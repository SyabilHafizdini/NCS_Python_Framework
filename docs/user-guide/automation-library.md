# Automation Library - Complete User Guide

## Overview

The Automation Library provides 245+ reusable functions for web testing automation, designed to be used across any project without modification. The library integrates core browser operations with advanced pattern-based locator systems.

## Library Architecture

```
tests/automation_library/
├── BrowserGlobal.py      # 182+ core browser functions
├── Web.py                # 63+ pattern-based functions
└── README.md             # Library documentation

tests/steps/
└── automation_library_steps.py  # Complete BDD step definitions
```

## Quick Start

### 1. Basic Browser Automation
```python
from tests.automation_library.BrowserGlobal import open_browser, click_element, fill_text

# Open browser and interact with elements
open_browser("https://example.com")
fill_text("xpath=//input[@id='username']", "user@test.com")
click_element("xpath=//button[@type='submit']")
```

### 2. Pattern-Based Interactions
```python
from tests.automation_library.Web import click_button_pattern, input_text_pattern, set_page_name

# Set page context and use dynamic locators
set_page_name("loginPage")
input_text_pattern("user@test.com", "Email")
click_button_pattern("Submit")
```

### 3. BDD Step Definitions
```gherkin
Feature: Your Application Test
  Scenario: Login Test
    Given I open web browser with https://yourapp.com and maximise window
    When I input text using pattern value user@test.com field Email
    And I click button using pattern field Login
    Then I verify element using pattern text field Welcome is present
```

## Core Modules

### BrowserGlobal.py - Core Browser Functions

**Categories** (182+ functions total):

#### Browser Management (12 functions)
```python
# Browser initialization with different options
open_browser(url)                                    # Basic browser opening
open_browser_maximized(url)                         # Open with maximized window  
open_browser_with_screenshot(url)                   # Open and capture screenshot
open_browser_maximized_with_screenshot(url)         # Combined maximize + screenshot
close_browser()                                      # Clean browser shutdown
```

#### Element Interactions (15+ functions)
```python
# Basic interactions
click_element(locator)                               # Standard click action
fill_text(locator, text)                           # Input text into field
clear_and_fill(locator, text)                      # Clear field then input text

# Advanced interactions  
scroll_to_element(locator)                          # Scroll element into view
wait_until_element_visible(locator)                 # Wait for element visibility
```

#### Verification & Validation (10+ functions)
```python
# Soft verifications (return boolean)
verify_element_present(locator) -> bool             # Check element presence
verify_element_text_is(locator, text) -> bool      # Check text content

# Hard assertions (fail test on failure)
assert_element_present(locator)                     # Assert element exists
assert_element_text_is(locator, text)              # Assert exact text match
```

#### Documentation & Reporting (5+ functions)
```python
# Screenshot capture
take_screenshot()                                   # Basic screenshot
take_screenshot_with_comment(comment)               # Screenshot with description

# Test documentation
# Note: Additional Allure logging handled automatically by environment hooks
```

#### Timing & Synchronization (5+ functions)
```python
# Basic waits
wait_seconds(seconds)                               # Simple time delay
wait_until_element_visible(locator, timeout=None)  # Element-based waiting

# Advanced synchronization handled by framework
```

**Key Functions Reference**:
```python
from tests.automation_library.BrowserGlobal import *

# Browser lifecycle
open_browser_maximized("https://app.com")           # Most common startup
close_browser()                                      # Clean shutdown

# Element interaction patterns
click_element("xpath=//button[@id='submit']")       # Direct clicking
fill_text("id=username", "john.doe")               # Text input
clear_and_fill("css=.search-box", "search term")   # Replace text

# Verification patterns
if verify_element_present("xpath=//div[@class='error']"):
    error_text = get_text_from_element("xpath=//div[@class='error']")
    take_screenshot_with_comment(f"Error found: {error_text}")

# Assertion patterns (fail test on mismatch)
assert_element_present("xpath=//div[@id='results']")
assert_element_text_is("css=.welcome-msg", "Welcome!")
```

### Web.py - Pattern-Based Functions

**Categories** (63+ functions total):

#### Pattern-Based Element Interactions (8 functions)
```python
# Dynamic element interactions
click_button_pattern(field_name)                    # Find and click button by name
click_link_pattern(field_name)                     # Find and click link by name
input_text_pattern(text, field_name)               # Smart input field identification
clear_and_fill_pattern(text, field_name)           # Clear and fill using patterns
```

#### Page Context Management (5+ functions)
```python
# Page context control
set_page_name(page_name)                            # Set current page context
get_current_page_context() -> str                   # Get active page context
clear_all_contexts()                                # Reset all context data
```

#### Pattern-Based Verification (7+ functions)
```python
# Content verification
verify_page_contains_text(text) -> bool            # Check page content
verify_element_present_pattern(element, field) -> bool  # Pattern-based presence check

# Advanced verification
# Additional verification functions available for complex scenarios
```

**Key Functions Reference**:
```python
from tests.automation_library.Web import *

# Pattern-based workflow
set_page_name("loginPage")                          # Set context
input_text_pattern("john.doe", "Username")         # Dynamic field location
input_text_pattern("password123", "Password")      # Pattern-based input
click_button_pattern("Login")                       # Dynamic button finding

# Page verification
if verify_page_contains_text("Welcome"):
    set_page_name("dashboardPage")                  # Context switching
    assert verify_element_present_pattern("text", "UserProfile")
```

## Usage Patterns

### 1. Traditional Locator Approach
```python
from tests.automation_library.BrowserGlobal import *

# Direct element targeting with explicit locators
open_browser_maximized("https://app.com")
click_element("xpath=//button[@id='submit-btn']")
fill_text("id=username", "user@test.com")
verify_element_text_is("css=.welcome-msg", "Welcome!")
take_screenshot_with_comment("Login completed")
close_browser()
```

### 2. Pattern Locator Approach  
```python
from tests.automation_library.Web import *
from tests.automation_library.BrowserGlobal import open_browser_maximized, close_browser

# Dynamic element identification
open_browser_maximized("https://app.com")
set_page_name("loginPage")
input_text_pattern("user@test.com", "Email")      # Finds: loginPage.Email.input
click_button_pattern("Submit")                     # Finds: loginPage.Submit.button
verify_page_contains_text("Dashboard")
close_browser()
```

### 3. Mixed Approach (Recommended)
```python
from tests.automation_library import BrowserGlobal as BG, Web

# Combine pattern locators with traditional fallbacks
BG.open_browser_maximized("https://app.com")
Web.set_page_name("loginPage")

try:
    # Try pattern locator first
    Web.input_text_pattern("user@test.com", "Email")
    Web.click_button_pattern("Login")
except Exception:
    # Fallback to traditional locators
    BG.fill_text("xpath=//input[@type='email']", "user@test.com")
    BG.click_element("xpath=//button[contains(text(),'Login')]")

# Verify result
assert Web.verify_page_contains_text("Welcome")
BG.take_screenshot_with_comment("Login successful")
BG.close_browser()
```

### 4. BDD Integration
```gherkin
# In your .feature files - use step definitions directly
Feature: Application Login
  Scenario: Successful User Login
    Given I open web browser with https://app.com and maximise window
    And I set page name loginPage
    When I input text using pattern value user@test.com field Email
    And I input text using pattern value secret123 field Password
    And I click button using pattern field Login
    Then I verify page contains text Welcome
    And I take screenshot with comment Login completed successfully
    And I close web browser
```

## Configuration

### Pattern Locator Setup

#### 1. Create Application-Specific Locators
```properties
# resources/locators/yourapp.properties
loginPage.Username.input=xpath=//input[@id='username']
loginPage.Password.input=xpath=//input[@id='password']
loginPage.Login.button=xpath=//button[@type='submit']
dashboardPage.Welcome.text=xpath=//h1[@class='welcome']
dashboardPage.UserProfile.link=xpath=//a[contains(@href,'profile')]
```

#### 2. Configure Pattern Templates
```properties
# resources/locators/loc_pattern.properties (already configured)
loc.qaf.pattern.input=xpath=//input[@name='${loc.auto.fieldName}'] | //input[@id='${loc.auto.fieldName}']
loc.qaf.pattern.button=xpath=//button[contains(text(),'${loc.auto.fieldName}')] | //button[@value='${loc.auto.fieldName}']
```

#### 3. Project Configuration
```properties
# resources/project_config.properties
loc.pattern.enabled=true
loc.pattern.code=loc.qaf
env.resources=resources/locators/;resources/
```

### Environment-Specific Configuration
```python
# test_data/environment_config.py
ENVIRONMENTS = {
    "DEV": {
        "base_url": "https://dev-app.com",
        "database": "dev_db",
        "timeout": 30
    },
    "QA": {
        "base_url": "https://qa-app.com",
        "database": "qa_db", 
        "timeout": 60
    },
    "PROD": {
        "base_url": "https://app.com",
        "database": "prod_db",
        "timeout": 45
    }
}
```

## Examples & Use Cases

### Basic Login Flow
```python
from tests.automation_library import BrowserGlobal as BG, Web

def login_user(username, password):
    """Reusable login function"""
    BG.open_browser_maximized("https://app.com")
    Web.set_page_name("loginPage")
    
    Web.input_text_pattern(username, "Username")
    Web.input_text_pattern(password, "Password")
    Web.click_button_pattern("Login")
    
    # Verify successful login
    assert Web.verify_page_contains_text("Dashboard")
    BG.take_screenshot_with_comment("Login successful")
    
    return True

# Usage
login_user("john.doe@test.com", "secret123")
```

### Data-Driven Testing
```python
import csv
from tests.automation_library import BrowserGlobal as BG, Web

def test_multiple_users():
    """Test login with multiple user accounts"""
    BG.open_browser_maximized("https://app.com")
    
    with open('test_data/users.csv', 'r') as file:
        users = csv.DictReader(file)
        
        for user in users:
            Web.set_page_name("loginPage")
            
            # Clear previous data
            BG.clear_and_fill("xpath=//input[@id='username']", user['username'])
            BG.clear_and_fill("xpath=//input[@id='password']", user['password'])
            
            Web.click_button_pattern("Login")
            
            if user['expected_result'] == 'success':
                assert Web.verify_page_contains_text("Dashboard")
                BG.take_screenshot_with_comment(f"Login success: {user['username']}")
                # Logout for next iteration
                Web.click_button_pattern("Logout")
            else:
                assert Web.verify_page_contains_text("Invalid")
                BG.take_screenshot_with_comment(f"Login failed: {user['username']}")
    
    BG.close_browser()
```

### Error Handling & Recovery
```python
from tests.automation_library import BrowserGlobal as BG, Web
import logging

def robust_element_interaction(element_type, field_name, action_data=None):
    """Robust element interaction with multiple fallback strategies"""
    
    try:
        # Strategy 1: Pattern locator
        if action_data:
            if element_type == "input":
                Web.input_text_pattern(action_data, field_name)
            elif element_type == "button":
                Web.click_button_pattern(field_name)
        else:
            if element_type == "button":
                Web.click_button_pattern(field_name)
                
        BG.take_screenshot_with_comment(f"Pattern locator success: {field_name}")
        return True
        
    except Exception as e:
        logging.warning(f"Pattern locator failed for {field_name}: {e}")
        BG.take_screenshot_with_comment(f"Pattern locator failed: {field_name}")
        
        try:
            # Strategy 2: Generic XPath fallback
            if element_type == "input" and action_data:
                BG.fill_text(f"xpath=//input[contains(@placeholder,'{field_name}')]", action_data)
            elif element_type == "button":
                BG.click_element(f"xpath=//button[contains(text(),'{field_name}')]")
                
            BG.take_screenshot_with_comment(f"Fallback locator success: {field_name}")
            return True
            
        except Exception as e2:
            logging.error(f"All strategies failed for {field_name}: {e2}")
            BG.take_screenshot_with_comment(f"All strategies failed: {field_name}")
            raise Exception(f"Could not interact with {field_name}: {e2}")

# Usage
robust_element_interaction("input", "Username", "john.doe")
robust_element_interaction("button", "Login")
```

## Advanced Features

### 1. Custom Function Extensions
```python
# tests/automation_library/CustomExtensions.py
from tests.automation_library import BrowserGlobal as BG, Web
import allure

@allure.step("Perform business login for user type: {user_type}")
def business_login(user_type):
    """Business-specific login function"""
    
    # User type mapping
    user_credentials = {
        "admin": {"username": "admin@test.com", "password": "admin123"},
        "manager": {"username": "manager@test.com", "password": "mgr123"},
        "employee": {"username": "emp@test.com", "password": "emp123"}
    }
    
    if user_type not in user_credentials:
        raise ValueError(f"Unknown user type: {user_type}")
    
    creds = user_credentials[user_type]
    
    Web.set_page_name("loginPage")
    Web.input_text_pattern(creds["username"], "Username")
    Web.input_text_pattern(creds["password"], "Password")
    Web.click_button_pattern("Login")
    
    # Verify access level
    if user_type == "admin":
        assert Web.verify_page_contains_text("Admin Panel")
    elif user_type == "manager":
        assert Web.verify_page_contains_text("Manager Dashboard")
    else:
        assert Web.verify_page_contains_text("Employee Portal")
    
    BG.take_screenshot_with_comment(f"{user_type} login completed")

@allure.step("Navigate through application workflow: {workflow_steps}")
def execute_workflow(workflow_steps):
    """Execute a series of navigation steps"""
    for step in workflow_steps:
        page_name = step["page"]
        action = step["action"]
        element = step["element"]
        
        Web.set_page_name(page_name)
        BG.take_screenshot_with_comment(f"Before {action} on {element}")
        
        if action == "click":
            Web.click_button_pattern(element)
        elif action == "input":
            Web.input_text_pattern(step["data"], element)
        elif action == "verify":
            assert Web.verify_element_present_pattern("text", element)
        
        BG.take_screenshot_with_comment(f"After {action} on {element}")

# Usage
workflow = [
    {"page": "dashboardPage", "action": "click", "element": "Reports"},
    {"page": "reportsPage", "action": "click", "element": "GenerateReport"},
    {"page": "reportsPage", "action": "verify", "element": "ReportGenerated"}
]

business_login("manager")
execute_workflow(workflow)
```

### 2. Integration with Test Data
```python
# tests/automation_library/DataDrivenHelpers.py
import json
import csv
from tests.automation_library import BrowserGlobal as BG, Web

class TestDataManager:
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self):
        """Load test data from file"""
        if self.data_file.endswith('.json'):
            with open(self.data_file, 'r') as f:
                return json.load(f)
        elif self.data_file.endswith('.csv'):
            with open(self.data_file, 'r') as f:
                return list(csv.DictReader(f))
        else:
            raise ValueError("Unsupported file format")
    
    def execute_data_driven_test(self, test_function):
        """Execute test function with each data set"""
        for i, data_set in enumerate(self.data):
            try:
                BG.take_screenshot_with_comment(f"Starting test iteration {i+1}")
                result = test_function(data_set)
                BG.take_screenshot_with_comment(f"Test iteration {i+1} completed")
                
            except Exception as e:
                BG.take_screenshot_with_comment(f"Test iteration {i+1} failed: {str(e)}")
                raise

def form_filling_test(test_data):
    """Example data-driven form filling"""
    Web.set_page_name(test_data["page"])
    
    for field, value in test_data["form_data"].items():
        Web.input_text_pattern(value, field)
    
    Web.click_button_pattern(test_data["submit_button"])
    
    # Verify result
    assert Web.verify_page_contains_text(test_data["expected_result"])

# Usage
data_manager = TestDataManager("test_data/form_tests.json")
BG.open_browser_maximized("https://app.com")
data_manager.execute_data_driven_test(form_filling_test)
BG.close_browser()
```

## Best Practices

### 1. Function Selection Guidelines
```python
# Use appropriate verification types
if BG.verify_element_present("xpath=//optional-element"):
    print("Optional element found")  # Soft check, continues test

BG.assert_element_present("xpath=//required-element")  # Hard check, fails test

# Prefer pattern locators for maintainability
Web.set_page_name("loginPage")
Web.click_button_pattern("Submit")  # ✅ Maintainable, readable

# Use traditional locators for complex selectors
BG.click_element("xpath=//button[@class='btn'][position()=2]")  # ✅ When patterns insufficient
```

### 2. Error Handling Patterns
```python
def safe_interaction(interaction_func, *args, **kwargs):
    """Safe wrapper for automation library functions"""
    try:
        result = interaction_func(*args, **kwargs)
        BG.take_screenshot_with_comment("Interaction successful")
        return result
    except Exception as e:
        BG.take_screenshot_with_comment(f"Interaction failed: {str(e)}")
        # Log error details
        allure.attach(str(e), name="Error Details", attachment_type=allure.attachment_type.TEXT)
        # Re-raise or handle as appropriate
        raise

# Usage
safe_interaction(Web.click_button_pattern, "Submit")
safe_interaction(BG.assert_element_text_is, "xpath=//h1", "Welcome")
```

### 3. Performance Considerations
```python
# Reuse browser instances when possible
def test_suite_with_shared_browser():
    """Multiple tests sharing browser instance"""
    BG.open_browser_maximized("https://app.com")
    
    try:
        # Test 1
        login_test()
        # Don't close browser
        
        # Test 2
        navigation_test()
        # Don't close browser
        
        # Test 3
        logout_test()
        
    finally:
        # Close browser only at the end
        BG.close_browser()

# Use efficient waits
def wait_for_page_state():
    """Efficient page state waiting"""
    # Instead of arbitrary sleeps
    # BG.wait_seconds(5)  # ❌ Inefficient
    
    # Use conditional waits
    BG.wait_until_element_visible("xpath=//div[@class='content']")  # ✅ Efficient
```

## Migration & Integration

### Migrating from Existing Frameworks
```python
# From traditional Selenium
# OLD:
# driver.get("https://app.com")
# driver.find_element(By.ID, "username").send_keys("user")
# driver.find_element(By.ID, "submit").click()

# NEW:
BG.open_browser("https://app.com")
BG.fill_text("id=username", "user") 
BG.click_element("id=submit")

# From other BDD frameworks
# OLD:
# @when('I login with {user} and {password}')
# def step_login(context, user, password):
#     # Custom implementation

# NEW: Use existing step definitions
# @when('I input text using pattern value {password} field Password')
# Already implemented - no custom code needed
```

### Extending for New Projects
```python
# Create project-specific wrapper module
# tests/automation_library/ProjectSpecific.py

from tests.automation_library import BrowserGlobal as BG, Web

class ProjectAutomation:
    def __init__(self, environment="QA"):
        self.environment = environment
        self.base_url = self._get_base_url()
    
    def _get_base_url(self):
        urls = {
            "DEV": "https://dev.yourapp.com",
            "QA": "https://qa.yourapp.com", 
            "PROD": "https://yourapp.com"
        }
        return urls.get(self.environment, urls["QA"])
    
    def start_session(self):
        """Project-specific session initialization"""
        BG.open_browser_maximized(self.base_url)
        BG.take_screenshot_with_comment("Session started")
    
    def login_as_user_type(self, user_type):
        """Project-specific login"""
        # Use your user management system
        credentials = self._get_user_credentials(user_type)
        Web.set_page_name("loginPage")
        Web.input_text_pattern(credentials["username"], "Username")
        Web.input_text_pattern(credentials["password"], "Password")
        Web.click_button_pattern("Login")
        BG.take_screenshot_with_comment(f"Logged in as {user_type}")
    
    def end_session(self):
        """Project-specific cleanup"""
        BG.take_screenshot_with_comment("Session ending")
        BG.close_browser()

# Usage in tests
automation = ProjectAutomation("QA")
automation.start_session()
automation.login_as_user_type("admin")
# Perform test actions
automation.end_session()
```

## Support & Troubleshooting

### Common Issues & Solutions

#### Import Errors
```python
# If imports fail, check Python path
import sys
sys.path.append('/path/to/tests')

from tests.automation_library import BrowserGlobal as BG, Web
```

#### Step Definition Issues
```bash
# Verify step definitions are found
venv_msvc/Scripts/python.exe -m behave tests/your_feature.feature --dry-run
```

#### Pattern Locator Issues  
```python
# Debug pattern locator resolution
Web.set_page_name("loginPage")
try:
    Web.click_button_pattern("Submit")
except Exception as e:
    print(f"Pattern failed: {e}")
    # Check if hardcoded locator exists in yourapp.properties
    # Check if pattern templates exist in loc_pattern.properties
```

For additional support:
- Check the comprehensive examples in test files
- Review configuration in `resources/` directory
- Use debug screenshots to diagnose issues
- Refer to Allure reports for detailed execution logs

This automation library provides a complete foundation for web automation testing that scales across projects while maintaining consistency and reliability.