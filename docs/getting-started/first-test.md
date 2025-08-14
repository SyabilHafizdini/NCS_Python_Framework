# Writing Your First Test

This guide walks you through creating your first automated test using the QAF Python Framework with pattern locators and BDD approach.

## Test Planning

Before writing code, let's plan our first test:

**What we'll test**: Login functionality on SauceDemo
**Test approach**: BDD (Behavior Driven Development) 
**Element strategy**: QAF Pattern Locators
**Reporting**: Allure with automatic screenshots

## Step 1: Create Feature File

Create `tests/first_test.feature`:

```gherkin
Feature: User Authentication
  As a user of the application
  I want to be able to login
  So that I can access the system

  Background:
    Given I navigate to the application

  Scenario: Successful login with valid credentials
    When I enter username "standard_user" in field "username"
    And I enter password "secret_sauce" in field "password"  
    And I click "Login" button
    Then I should see "Products" text on the page
    And I should be on the "inventory.html" page

  Scenario: Failed login with invalid credentials
    When I enter username "invalid_user" in field "username"
    And I enter password "wrong_password" in field "password"
    And I click "Login" button  
    Then I should see "Epic sadface" error message
    And I should remain on the login page
```

## Step 2: Configure Pattern Locators

Update `resources/locators/loc_pattern.properties`:

```properties
# Input field patterns - multiple fallback strategies
loc.qaf.pattern.input=xpath=//input[@data-test='${loc.auto.fieldValue}'] | //input[@name='${loc.auto.fieldValue}'] | //input[@id='${loc.auto.fieldValue}'] | //input[@placeholder='${loc.auto.fieldName}']

# Button patterns with comprehensive coverage
loc.qaf.pattern.button=xpath=//input[@type='submit' and @value='${loc.auto.fieldName}'] | //button[contains(text(),'${loc.auto.fieldName}')] | //*[@data-test='${loc.auto.fieldValue}'] | //input[@type='submit']

# Text verification patterns
loc.qaf.pattern.text=xpath=//*[contains(text(),'${loc.auto.fieldName}')] | //*[@data-test='${loc.auto.fieldValue}'] | //h1[contains(text(),'${loc.auto.fieldName}')]

# Error message patterns
loc.qaf.pattern.error=xpath=//*[@data-test='error'] | //*[contains(@class,'error')] | //*[contains(text(),'${loc.auto.fieldName}')]
```

## Step 3: Implement Step Definitions

Create `tests/steps/first_test_steps.py`:

```python
"""
Step definitions for first test - demonstrates QAF pattern locators
"""
from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import allure

# Import QAF pattern locator system
from qaf.automation.ui.util.pattern_locator import get_pattern_locator

@given('I navigate to the application')
def navigate_to_application(context):
    """Initialize browser and navigate to test application"""
    with allure.step("Setup WebDriver and navigate to application"):
        if not hasattr(context, 'driver'):
            # Setup Chrome with optimized options
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            context.driver = webdriver.Chrome(service=service, options=options)
            context.wait = WebDriverWait(context.driver, 10)
            context.pattern_locator = get_pattern_locator()
        
        # Navigate to application
        context.driver.get("https://www.saucedemo.com/v1/")
        allure.attach(context.driver.current_url, name="Application URL", attachment_type=allure.attachment_type.TEXT)
        
        # Take initial screenshot
        allure.attach(
            context.driver.get_screenshot_as_png(),
            name="Initial Page",
            attachment_type=allure.attachment_type.PNG
        )

@when('I enter username "{username}" in field "{field_name}"')
def enter_username(context, username, field_name):
    """Enter username using pattern locator system"""
    with allure.step(f"Enter username '{username}' in {field_name} field"):
        try:
            # Use QAF pattern locator to find element
            locator = context.pattern_locator.input("loginPage", field_name, field_name)
            
            # Find element using generated locator
            if locator.startswith('xpath='):
                element = context.wait.until(
                    EC.presence_of_element_located((By.XPATH, locator[6:]))
                )
            else:
                # Handle other locator types if needed
                element = context.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='username']"))
                )
            
            element.clear()
            element.send_keys(username)
            
            # Allure reporting
            allure.attach(username, name="Username Entered", attachment_type=allure.attachment_type.TEXT)
            allure.attach(locator, name="Locator Used", attachment_type=allure.attachment_type.TEXT)
            
        except Exception as e:
            allure.attach(str(e), name="Error Details", attachment_type=allure.attachment_type.TEXT)
            raise AssertionError(f"Failed to enter username: {str(e)}")

@when('I enter password "{password}" in field "{field_name}"')
def enter_password(context, password, field_name):
    """Enter password using pattern locator system"""
    with allure.step(f"Enter password in {field_name} field"):
        try:
            # Use QAF pattern locator
            locator = context.pattern_locator.input("loginPage", field_name, field_name)
            
            if locator.startswith('xpath='):
                element = context.wait.until(
                    EC.presence_of_element_located((By.XPATH, locator[6:]))
                )
            else:
                element = context.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='password']"))
                )
                
            element.clear()
            element.send_keys(password)
            
            # Allure reporting (mask password)
            allure.attach("***masked***", name="Password Entered", attachment_type=allure.attachment_type.TEXT)
            allure.attach(locator, name="Locator Used", attachment_type=allure.attachment_type.TEXT)
            
        except Exception as e:
            allure.attach(str(e), name="Error Details", attachment_type=allure.attachment_type.TEXT)
            raise AssertionError(f"Failed to enter password: {str(e)}")

@when('I click "{button_name}" button')
def click_button(context, button_name):
    """Click button using pattern locator system"""
    with allure.step(f"Click '{button_name}' button"):
        try:
            # Use QAF pattern locator for button
            locator = context.pattern_locator.button("loginPage", button_name, "login-button")
            
            if locator.startswith('xpath='):
                element = context.wait.until(
                    EC.element_to_be_clickable((By.XPATH, locator[6:]))
                )
            else:
                element = context.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
                )
            
            element.click()
            
            allure.attach(locator, name="Button Locator Used", attachment_type=allure.attachment_type.TEXT)
            
            # Take screenshot after click
            allure.attach(
                context.driver.get_screenshot_as_png(),
                name="After Button Click",
                attachment_type=allure.attachment_type.PNG
            )
            
        except Exception as e:
            allure.attach(str(e), name="Error Details", attachment_type=allure.attachment_type.TEXT)
            raise AssertionError(f"Failed to click button: {str(e)}")

@then('I should see "{expected_text}" text on the page')
def verify_text_on_page(context, expected_text):
    """Verify expected text appears on page using pattern locator"""
    with allure.step(f"Verify '{expected_text}' text is visible"):
        try:
            # Use pattern locator for text verification
            locator = context.pattern_locator.text("resultPage", expected_text, expected_text.lower())
            
            if locator.startswith('xpath='):
                element = context.wait.until(
                    EC.presence_of_element_located((By.XPATH, locator[6:]))
                )
            else:
                element = context.wait.until(
                    EC.presence_of_element_located((By.XPATH, f"//*[contains(text(),'{expected_text}')]"))
                )
            
            assert element.is_displayed(), f"Text '{expected_text}' should be visible"
            
            allure.attach(expected_text, name="Expected Text Found", attachment_type=allure.attachment_type.TEXT)
            allure.attach(locator, name="Text Locator Used", attachment_type=allure.attachment_type.TEXT)
            
        except Exception as e:
            allure.attach(str(e), name="Error Details", attachment_type=allure.attachment_type.TEXT)
            raise AssertionError(f"Text '{expected_text}' not found: {str(e)}")

@then('I should be on the "{expected_page}" page')
def verify_current_page(context, expected_page):
    """Verify current page URL contains expected page"""
    with allure.step(f"Verify current page contains '{expected_page}'"):
        current_url = context.driver.current_url
        allure.attach(current_url, name="Current URL", attachment_type=allure.attachment_type.TEXT)
        
        assert expected_page in current_url, f"Expected '{expected_page}' in URL, but got: {current_url}"

@then('I should see "{error_text}" error message')
def verify_error_message(context, error_text):
    """Verify error message appears using pattern locator"""
    with allure.step(f"Verify error message contains '{error_text}'"):
        try:
            locator = context.pattern_locator.error("loginPage", error_text, "error")
            
            if locator.startswith('xpath='):
                error_element = context.wait.until(
                    EC.presence_of_element_located((By.XPATH, locator[6:]))
                )
            else:
                error_element = context.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='error']"))
                )
            
            assert error_element.is_displayed(), "Error message should be visible"
            assert error_text in error_element.text, f"Expected '{error_text}' in error message"
            
            allure.attach(error_element.text, name="Error Message Text", attachment_type=allure.attachment_type.TEXT)
            
        except Exception as e:
            allure.attach(str(e), name="Error Details", attachment_type=allure.attachment_type.TEXT)
            raise AssertionError(f"Error message verification failed: {str(e)}")

@then('I should remain on the login page')  
def verify_still_on_login_page(context):
    """Verify user is still on login page"""
    with allure.step("Verify still on login page"):
        current_url = context.driver.current_url
        allure.attach(current_url, name="Current URL", attachment_type=allure.attachment_type.TEXT)
        
        # Should not contain inventory.html (success page)
        assert "inventory.html" not in current_url, "Should not be on success page"
        assert "saucedemo.com" in current_url, "Should still be on SauceDemo site"

def after_scenario(context, scenario):
    """Cleanup after each scenario"""
    if hasattr(context, 'driver'):
        # Take final screenshot
        try:
            allure.attach(
                context.driver.get_screenshot_as_png(),
                name="Final Screenshot",
                attachment_type=allure.attachment_type.PNG
            )
        except:
            pass
        
        context.driver.quit()
```

## Step 4: Configure Test Execution

Create `tests/conftest.py` for pytest configuration:

```python
"""
pytest configuration for QAF framework
"""
import pytest
import allure
from datetime import datetime

@pytest.fixture(scope="session")
def test_start_time():
    return datetime.now()

def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as regression test"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test items during collection"""
    for item in items:
        # Add allure labels automatically
        item.add_marker(pytest.mark.allure_label("framework", "qaf-python"))
```

## Step 5: Run Your First Test

### Execute with Behave
```bash
# Run the specific feature
behave tests/first_test.feature -f allure_behave.formatter:AllureFormatter -o allure-results

# View results
allure serve allure-results
```

### Execute with pytest (if using pytest-bdd)
```bash
# Run with Allure reporting
pytest tests/first_test.feature --alluredir=allure-results

# Generate and serve report
allure serve allure-results
```

## Step 6: Understanding the Output

### Expected Console Output
```
Feature: User Authentication

  Background: 
    Given I navigate to the application ... passed

  Scenario: Successful login with valid credentials
    When I enter username "standard_user" in field "username" ... passed
    And I enter password "secret_sauce" in field "password" ... passed
    And I click "Login" button ... passed
    Then I should see "Products" text on the page ... passed
    And I should be on the "inventory.html" page ... passed

1 feature passed, 0 failed, 0 skipped
2 scenarios passed, 0 failed, 0 skipped
9 steps passed, 0 failed, 0 skipped, 0 undefined
```

### Allure Report Features
Your report will include:
- **Screenshots** at each step
- **Pattern locators** used for each element
- **Test execution timeline**
- **Error details** (if any failures occur)
- **Environment information**

## Troubleshooting Your First Test

### Common Issues

**Pattern locator not working**:
- Check `loc_pattern.properties` syntax
- Verify pattern prefix in `project_config.properties`
- Add debug prints to see generated locators

**Element not found**:
- Use browser dev tools to inspect elements
- Add explicit waits before element interactions
- Try multiple fallback patterns

**Import errors**:
- Ensure QAF framework is properly installed
- Check Python path includes framework modules
- Verify all `__init__.py` files exist

## Next Steps

Congratulations! You've created your first QAF test. Now you can:

1. **Add more scenarios** to your feature file
2. **Explore advanced pattern locators** - [Pattern Locators Tutorial](../tutorials/pattern-locators.md)
3. **Learn about data-driven testing** - [Advanced Scenarios](../examples/advanced-scenarios.md)
4. **Use the automation library** - [245+ Reusable Functions](../user-guide/automation-library.md)

## Best Practices Learned

From this first test, you've learned:
- ✅ **BDD approach** with clear, readable scenarios
- ✅ **Pattern locators** for maintainable element identification  
- ✅ **Automatic reporting** with screenshots and step details
- ✅ **Proper test structure** with clear step definitions
- ✅ **Error handling** with meaningful failure messages

Continue building on these foundations as you create more comprehensive test suites!