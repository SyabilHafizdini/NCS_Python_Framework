# Configuration Reference

This guide covers all configuration options available in the QAF Python Automation Framework.

## Configuration Files Overview

The framework uses multiple configuration files to manage different aspects of test execution:

```
resources/
├── project_config.properties    # Main framework configuration  
├── locators/
│   └── loc_pattern.properties  # Pattern locator definitions
├── test_data/
│   └── test_data.properties    # Test data configuration
└── environments/
    ├── dev.properties          # Development environment
    ├── staging.properties      # Staging environment  
    └── prod.properties         # Production environment
```

## Main Configuration File

### `resources/project_config.properties`

This is the primary configuration file that controls framework behavior.

#### Framework Settings

```properties
# Pattern Locator System
loc.pattern.enabled=true
loc.pattern.code=loc.qaf

# Resources Directory
env.resources=resources

# Test Data Settings
test.data.enabled=true
test.data.file=test_data/test_data.properties
```

#### WebDriver Configuration

```properties
# Browser Selection
driver.name=chromeDriver
# Options: chromeDriver, firefoxDriver, edgeDriver, safariDriver

# Browser Options (Chrome)
chrome.options=--no-sandbox,--disable-dev-shm-usage,--window-size=1920x1080
# chrome.options=--headless  # Uncomment for headless mode

# Firefox Options  
firefox.options=--width=1920,--height=1080
# firefox.options=--headless  # Uncomment for headless mode

# Edge Options
edge.options=--no-sandbox,--disable-dev-shm-usage

# WebDriver Timeouts
selenium.wait.timeout=30
selenium.implicit.wait.timeout=10
selenium.page.load.timeout=60
selenium.script.timeout=30
```

#### Remote WebDriver Configuration

```properties
# Remote Selenium Grid
remote.server=localhost
remote.port=4444
remote.protocol=http

# Cloud Providers (BrowserStack, Sauce Labs, etc.)
# remote.server=hub-cloud.browserstack.com
# remote.port=443  
# remote.protocol=https
# browserstack.username=your_username
# browserstack.accessKey=your_access_key

# Desired Capabilities for Remote
remote.browser=chrome
remote.browser.version=latest
remote.platform=WINDOWS
```

#### Application Settings

```properties
# Base URLs
env.baseurl=https://www.saucedemo.com/v1/
env.api.baseurl=https://api.saucedemo.com/v1/

# Environment Selection
env.name=dev
# Options: dev, staging, prod

# Database Configuration (if needed)
db.driver=com.mysql.cj.jdbc.Driver
db.url=jdbc:mysql://localhost:3306/testdb  
db.username=testuser
db.password=testpass
```

#### Test Execution Settings

```properties
# Test Categories
test.categories=smoke,regression,integration

# Parallel Execution
test.parallel.execution=true
test.parallel.threads=4

# Retry Configuration
test.retry.count=2
test.retry.on.failure=true

# Screenshot Settings
screenshot.on.failure=true
screenshot.on.success=false
screenshot.dir=screenshots
```

#### Reporting Configuration

```properties
# Allure Reporting
allure.results.directory=allure-results
allure.report.directory=allure-report

# Test Report Settings
report.dir=test-results
report.format=html,json,xml

# Logging Configuration
log.level=INFO
log.file=test_execution.log
log.console.output=true
```

## Pattern Locator Configuration

### `resources/locators/loc_pattern.properties`

Defines XPath patterns for dynamic element identification.

#### Basic Element Patterns

```properties
# Input Field Patterns
loc.qaf.pattern.input=xpath=//input[@data-test='${loc.auto.fieldValue}'] | //input[@name='${loc.auto.fieldValue}'] | //input[@id='${loc.auto.fieldValue}'] | //input[@placeholder='${loc.auto.fieldName}']

# Button Patterns
loc.qaf.pattern.button=xpath=//button[contains(text(),'${loc.auto.fieldName}')] | //button[@data-test='${loc.auto.fieldValue}'] | //input[@type='submit' and @value='${loc.auto.fieldName}'] | //*[@role='button' and contains(text(),'${loc.auto.fieldName}')]

# Link Patterns
loc.qaf.pattern.link=xpath=//a[contains(text(),'${loc.auto.fieldName}')] | //a[@data-test='${loc.auto.fieldValue}'] | //a[@href='${loc.auto.fieldValue}']

# Text Verification Patterns
loc.qaf.pattern.text=xpath=//*[contains(text(),'${loc.auto.fieldName}')] | //*[@data-test='${loc.auto.fieldValue}'] | //h1[contains(text(),'${loc.auto.fieldName}')] | //span[contains(text(),'${loc.auto.fieldName}')]
```

#### Form Element Patterns

```properties
# Checkbox Patterns
loc.qaf.pattern.checkbox=xpath=//input[@type='checkbox' and @name='${loc.auto.fieldValue}'] | //input[@type='checkbox' and @data-test='${loc.auto.fieldValue}'] | //input[@type='checkbox' and @id='${loc.auto.fieldValue}']

# Radio Button Patterns
loc.qaf.pattern.radio=xpath=//input[@type='radio' and @name='${loc.auto.fieldValue}'] | //input[@type='radio' and @value='${loc.auto.fieldValue}'] | //input[@type='radio' and @data-test='${loc.auto.fieldValue}']

# Select Dropdown Patterns  
loc.qaf.pattern.select=xpath=//select[@name='${loc.auto.fieldValue}'] | //select[@data-test='${loc.auto.fieldValue}'] | //select[@id='${loc.auto.fieldValue}']

# Textarea Patterns
loc.qaf.pattern.textarea=xpath=//textarea[@name='${loc.auto.fieldValue}'] | //textarea[@data-test='${loc.auto.fieldValue}'] | //textarea[@placeholder='${loc.auto.fieldName}']
```

#### Advanced Element Patterns

```properties
# Table Cell Patterns
loc.qaf.pattern.table.cell=xpath=//tr[contains(.,'${loc.auto.fieldName}')]//td[${loc.auto.fieldValue}] | //table//td[contains(text(),'${loc.auto.fieldName}')]

# Modal Dialog Patterns
loc.qaf.pattern.modal=xpath=//div[contains(@class,'modal') and contains(.,'${loc.auto.fieldName}')] | //*[@role='dialog' and contains(.,'${loc.auto.fieldName}')]

# Navigation Menu Patterns
loc.qaf.pattern.menu=xpath=//nav//a[contains(text(),'${loc.auto.fieldName}')] | //*[contains(@class,'menu')]//a[contains(text(),'${loc.auto.fieldName}')]

# Error Message Patterns
loc.qaf.pattern.error=xpath=//*[contains(@class,'error') and contains(text(),'${loc.auto.fieldName}')] | //*[@data-test='error'] | //*[contains(@class,'alert-error')]
```

#### Page-Specific Pattern Overrides

```properties
# Login Page Specific Patterns
loc.qaf.pattern.loginPage.input=xpath=//form[@id='login-form']//input[@name='${loc.auto.fieldValue}'] | //div[contains(@class,'login')]//input[@placeholder='${loc.auto.fieldName}']

loc.qaf.pattern.loginPage.button=xpath=//form[@id='login-form']//button[contains(text(),'${loc.auto.fieldName}')] | //div[contains(@class,'login')]//input[@type='submit']

# Checkout Page Specific Patterns
loc.qaf.pattern.checkoutPage.input=xpath=//form[contains(@class,'checkout')]//input[@name='${loc.auto.fieldValue}']

loc.qaf.pattern.checkoutPage.button=xpath=//div[contains(@class,'checkout')]//button[contains(text(),'${loc.auto.fieldName}')]
```

## Environment-Specific Configuration

### Development Environment (`resources/environments/dev.properties`)

```properties
# Development Environment Settings
env.name=dev
env.baseurl=https://dev.saucedemo.com/
env.api.baseurl=https://dev-api.saucedemo.com/

# Dev-specific WebDriver Settings
selenium.wait.timeout=15
screenshot.on.failure=true
screenshot.on.success=true

# Logging for Development
log.level=DEBUG
log.console.output=true

# Database Connection (Dev)
db.url=jdbc:mysql://dev-db:3306/testdb
db.username=dev_user
db.password=dev_pass
```

### Staging Environment (`resources/environments/staging.properties`)

```properties
# Staging Environment Settings  
env.name=staging
env.baseurl=https://staging.saucedemo.com/
env.api.baseurl=https://staging-api.saucedemo.com/

# Staging-specific Settings
selenium.wait.timeout=30
screenshot.on.failure=true
screenshot.on.success=false

# Logging for Staging
log.level=INFO
log.console.output=true

# Database Connection (Staging)
db.url=jdbc:mysql://staging-db:3306/testdb
db.username=staging_user
db.password=staging_pass
```

### Production Environment (`resources/environments/prod.properties`)

```properties
# Production Environment Settings
env.name=prod  
env.baseurl=https://www.saucedemo.com/
env.api.baseurl=https://api.saucedemo.com/

# Production-specific Settings
selenium.wait.timeout=45
screenshot.on.failure=true
screenshot.on.success=false

# Conservative Logging for Production
log.level=WARN
log.console.output=false

# Database Connection (Production)
db.url=jdbc:mysql://prod-db:3306/testdb
db.username=prod_user
db.password=prod_pass
```

## Test Data Configuration

### `resources/test_data/test_data.properties`

```properties
# User Credentials
test.user.standard.username=standard_user
test.user.standard.password=secret_sauce

test.user.locked.username=locked_out_user
test.user.locked.password=secret_sauce

test.user.problem.username=problem_user
test.user.problem.password=secret_sauce

# Product Information
test.product.backpack.name=Sauce Labs Backpack
test.product.backpack.price=29.99

test.product.bikelight.name=Sauce Labs Bike Light
test.product.bikelight.price=9.99

# Form Data
test.checkout.firstname=John
test.checkout.lastname=Doe
test.checkout.zipcode=12345

# API Endpoints
api.endpoint.users=/users
api.endpoint.products=/products
api.endpoint.orders=/orders

# Test Timeouts
test.timeout.short=5
test.timeout.medium=15
test.timeout.long=30
```

## Advanced Configuration Options

### Browser-Specific Options

#### Chrome Configuration

```properties
# Chrome Driver Settings
driver.name=chromeDriver

# Chrome Options
chrome.options=--no-sandbox,--disable-dev-shm-usage,--disable-extensions,--window-size=1920x1080

# Chrome Headless Mode
# chrome.options=--headless,--no-sandbox,--disable-dev-shm-usage

# Chrome Mobile Emulation  
chrome.mobile.device=iPhone X
chrome.mobile.enabled=false

# Chrome Download Settings
chrome.download.dir=/path/to/downloads
chrome.download.default_directory=/tmp/downloads
```

#### Firefox Configuration

```properties
# Firefox Driver Settings
driver.name=firefoxDriver

# Firefox Options
firefox.options=--width=1920,--height=1080

# Firefox Profile Settings
firefox.profile.preference.browser.download.dir=/tmp/downloads
firefox.profile.preference.browser.helperApps.neverAsk.saveToDisk=application/pdf,text/csv

# Firefox Headless Mode
# firefox.options=--headless
```

### Parallel Execution Configuration

```properties
# Parallel Test Execution
test.parallel.execution=true
test.parallel.threads=4
test.parallel.methods=false
test.parallel.classes=true

# Thread Safety
webdriver.thread.local=true
test.data.thread.safe=true

# Resource Management
test.parallel.max.memory=4096m
test.parallel.timeout=300
```

### Reporting and Logging

```properties
# Allure Configuration
allure.results.directory=allure-results
allure.report.directory=allure-report
allure.serve.port=8080

# Report Content
allure.include.environment=true
allure.include.categories=true
allure.include.trends=true

# Logging Configuration
log.level=INFO
log.file=logs/test_execution.log
log.max.file.size=50MB
log.max.files=10

# Console Output
log.console.output=true
log.console.pattern=%d{HH:mm:ss} [%level] %msg%n
```

## Environment Variable Overrides

You can override configuration properties using environment variables:

```bash
# Override base URL
export ENV_BASEURL=https://custom-env.com

# Override browser
export DRIVER_NAME=firefoxDriver

# Override wait timeout
export SELENIUM_WAIT_TIMEOUT=45

# Override environment
export ENV_NAME=custom
```

## Configuration Loading Order

The framework loads configuration in this priority order:

1. **Environment Variables** (highest priority)
2. **Command Line Parameters**  
3. **Environment-Specific Properties** (`dev.properties`, `staging.properties`, etc.)
4. **Main Configuration** (`project_config.properties`)
5. **Default Values** (lowest priority)

## Usage Examples

### Loading Configuration in Tests

```python
from qaf.automation.core.config_manager import ConfigManager

# Get configuration instance
config = ConfigManager.get_instance()

# Access configuration values
base_url = config.get_property('env.baseurl')
wait_timeout = config.get_property('selenium.wait.timeout', 30)  # with default
browser_name = config.get_property('driver.name')

# Check boolean properties  
if config.get_boolean_property('screenshot.on.failure'):
    take_screenshot()

# Access environment-specific values
if config.get_property('env.name') == 'prod':
    # Production-specific logic
    pass
```

### Dynamic Configuration

```python
# Set properties at runtime
config.set_property('test.current.user', 'john.doe')
config.set_property('test.execution.id', str(uuid.uuid4()))

# Environment-based configuration
env_name = config.get_property('env.name', 'dev')
config.load_environment_properties(f'environments/{env_name}.properties')
```

### Configuration Validation

```python
def validate_configuration():
    """Validate required configuration properties"""
    required_props = [
        'env.baseurl',
        'driver.name', 
        'selenium.wait.timeout'
    ]
    
    for prop in required_props:
        if not config.get_property(prop):
            raise ValueError(f"Required property '{prop}' is not configured")
    
    # Validate URL format
    base_url = config.get_property('env.baseurl')
    if not base_url.startswith(('http://', 'https://')):
        raise ValueError("Base URL must start with http:// or https://")
```

## Best Practices

### 1. Environment Separation
- Keep sensitive data (passwords, API keys) in environment variables
- Use different configuration files for each environment
- Never commit production credentials to version control

### 2. Configuration Organization
- Group related properties together
- Use consistent naming conventions
- Document all configuration options

### 3. Default Values
- Always provide sensible defaults
- Make configuration optional where possible
- Validate configuration at startup

### 4. Security
- Encrypt sensitive configuration data
- Use secure methods to pass credentials
- Audit configuration access

This configuration reference provides comprehensive coverage of all settings available in the QAF Python framework, enabling you to customize the framework behavior for your specific testing needs.