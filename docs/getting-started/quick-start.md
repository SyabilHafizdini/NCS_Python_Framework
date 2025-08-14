# Quick Start Guide

Get up and running with the QAF Python Automation Framework in 5 minutes!

## 1. Project Setup

Create a new project directory:
```bash
mkdir my-qaf-project
cd my-qaf-project
```

Initialize the basic structure:
```
my-qaf-project/
├── tests/
│   ├── __init__.py
│   ├── steps/
│   │   └── __init__.py
│   └── features/
├── resources/
│   ├── locators/
│   │   └── loc_pattern.properties
│   └── project_config.properties
└── requirements.txt
```

## 2. Configuration Files

### requirements.txt
```
selenium~=4.9.1
pytest~=7.3.1
behave~=1.2.6
allure-pytest~=2.13.2
allure-behave~=2.13.2
webdriver-manager~=3.8.6
```

### resources/project_config.properties
```properties
# Framework settings
loc.pattern.code=loc.qaf
loc.pattern.enabled=true

# Driver configuration
driver.name=chromeDriver
selenium.wait.timeout=30

# Application settings
env.baseurl=https://www.saucedemo.com/v1/
env.resources=resources

# Reporting
allure.results.directory=allure-results
```

### resources/locators/loc_pattern.properties
```properties
# Button patterns
loc.qaf.pattern.button=xpath=//button[contains(text(),'${loc.auto.fieldName}')] | //input[@value='${loc.auto.fieldName}' and @type='submit'] | //*[@data-test='${loc.auto.fieldValue}']

# Input field patterns  
loc.qaf.pattern.input=xpath=//input[@placeholder='${loc.auto.fieldName}'] | //*[@data-test='${loc.auto.fieldValue}'] | //input[@name='${loc.auto.fieldValue}']

# Text patterns
loc.qaf.pattern.text=xpath=//*[contains(text(),'${loc.auto.fieldName}')] | //*[@data-test='${loc.auto.fieldValue}']

# Link patterns
loc.qaf.pattern.link=xpath=//a[contains(text(),'${loc.auto.fieldName}')] | //a[@href='${loc.auto.fieldValue}']
```

## 3. Create Your First Test

### tests/simple_demo.feature
```gherkin
Feature: Login Functionality
  As a user
  I want to login to the application
  So that I can access my account

  Scenario: Valid User Login
    Given I navigate to the login page
    When I enter username "standard_user" using pattern locator
    And I enter password "secret_sauce" using pattern locator  
    And I click "Login" button using pattern locator
    Then I verify page contains text "Products"
```

### tests/steps/demo_steps.py
```python
from behave import given, when, then, step
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import allure

@given('I navigate to the login page')
def navigate_to_login_page(context):
    with allure.step("Setup browser and navigate to application"):
        if not hasattr(context, 'driver'):
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            context.driver = webdriver.Chrome(service=service, options=options)
            context.wait = WebDriverWait(context.driver, 10)
        
        context.driver.get("https://www.saucedemo.com/v1/")

@when('I enter username "{username}" using pattern locator')  
def enter_username(context, username):
    with allure.step(f"Enter username: {username}"):
        username_field = context.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='username']"))
        )
        username_field.clear()
        username_field.send_keys(username)

@when('I enter password "{password}" using pattern locator')
def enter_password(context, password):
    with allure.step("Enter password"):
        password_field = context.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='password']"))
        )
        password_field.clear()
        password_field.send_keys(password)

@when('I click "{button_name}" button using pattern locator')
def click_button(context, button_name):
    with allure.step(f"Click {button_name} button"):
        login_button = context.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
        )
        login_button.click()

@then('I verify page contains text "{expected_text}"')
def verify_text(context, expected_text):
    with allure.step(f"Verify page contains: {expected_text}"):
        text_element = context.wait.until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(),'{expected_text}')]"))
        )
        assert text_element.is_displayed()

def after_scenario(context, scenario):
    if hasattr(context, 'driver'):
        context.driver.quit()
```

## 4. Running Tests

### Using Behave (BDD)
```bash
# Run all features
behave tests/

# Run specific feature
behave tests/simple_demo.feature

# Run with Allure reporting
behave tests/ -f allure_behave.formatter:AllureFormatter -o allure-results
allure serve allure-results
```

### Using pytest
```bash
# Run tests with Allure
pytest tests/ --alluredir=allure-results
allure serve allure-results
```

## 5. View Test Reports

### Generate Allure Report
```bash
# Serve report (opens browser automatically)
allure serve allure-results

# Generate static report
allure generate allure-results -o allure-report --clean
```

## 6. Expected Output

Your first test run should:
1. Open Chrome browser
2. Navigate to SauceDemo
3. Enter credentials using pattern locators
4. Verify successful login
5. Generate Allure report with screenshots

## Project Structure After Setup

```
my-qaf-project/
├── tests/
│   ├── __init__.py
│   ├── simple_demo.feature
│   └── steps/
│       ├── __init__.py
│       └── demo_steps.py
├── resources/
│   ├── locators/
│   │   └── loc_pattern.properties
│   └── project_config.properties
├── allure-results/
├── allure-report/
├── requirements.txt
└── README.md
```

## Next Steps

Now that you have a working setup:

1. **Explore Pattern Locators**: Learn about [dynamic element identification](../tutorials/pattern-locators.md)
2. **Write More Tests**: Check out [writing tests guide](../tutorials/writing-tests.md)  
3. **Advanced Features**: Dive into [advanced scenarios](../examples/advanced-scenarios.md)
4. **Automation Library**: Use the [245+ reusable functions](../user-guide/automation-library.md)

## Common Issues

**Test not found**: Ensure your step definitions are in the `steps/` directory
**WebDriver issues**: Framework handles drivers automatically via webdriver-manager
**Import errors**: Check that all `__init__.py` files are present

For more help, see the [Troubleshooting Guide](../reference/troubleshooting.md)