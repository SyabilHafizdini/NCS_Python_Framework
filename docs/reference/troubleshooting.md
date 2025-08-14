# Troubleshooting Guide

This guide helps you diagnose and resolve common issues encountered when using the QAF Python Automation Framework.

## Installation Issues

### Python Version Conflicts

**Problem:** ImportError or module compatibility issues
```
ImportError: No module named 'selenium'
SyntaxError: invalid syntax (Python 2.x code)
```

**Solutions:**
```bash
# Check Python version (must be 3.6+)
python --version
python3 --version

# Use Python 3 explicitly
python3 -m pip install -r requirements.txt

# Create virtual environment with specific Python version
python3 -m venv qaf-env
source qaf-env/bin/activate  # Linux/Mac
# or
qaf-env\Scripts\activate  # Windows
```

---

### Package Installation Failures

**Problem:** pip install errors or dependency conflicts
```
ERROR: Could not install packages due to an EnvironmentError
pip._vendor.packaging.version.InvalidVersion
```

**Solutions:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Clear pip cache
pip cache purge

# Install with user permissions
pip install --user -r requirements.txt

# Force reinstall
pip install --force-reinstall selenium

# Install specific versions
pip install selenium==4.9.1
```

---

### WebDriver Issues

**Problem:** WebDriver not found or version mismatch
```
selenium.common.exceptions.WebDriverException: 
Message: 'chromedriver' executable needs to be in PATH
```

**Solutions:**
```bash
# Framework uses webdriver-manager (automatic)
pip install webdriver-manager

# Manual WebDriver setup (if needed)
# Download ChromeDriver from https://chromedriver.chromium.org/
# Add to PATH or specify location:
```

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service("/path/to/chromedriver")
driver = webdriver.Chrome(service=service)
```

---

## Configuration Issues

### Pattern Locator Not Working

**Problem:** Pattern locators not generating or finding elements
```
AttributeError: module has no attribute 'get_pattern_locator'
Exception: Pattern locator not enabled
```

**Solutions:**

1. **Check Configuration:**
```properties
# resources/project_config.properties
loc.pattern.enabled=true
loc.pattern.code=loc.qaf
env.resources=resources
```

2. **Verify Pattern File:**
```bash
# Ensure file exists
ls resources/locators/loc_pattern.properties
```

3. **Debug Pattern Generation:**
```python
from qaf.automation.ui.util.pattern_locator import get_pattern_locator

# Debug pattern loading
try:
    pattern_locator = get_pattern_locator()
    locator = pattern_locator.input("testPage", "Username", "username")
    print(f"Generated locator: {locator}")
except Exception as e:
    print(f"Pattern error: {e}")
```

---

### Configuration File Not Found

**Problem:** Properties file not loading
```
FileNotFoundError: [Errno 2] No such file or directory: 'resources/project_config.properties'
```

**Solutions:**

1. **Check File Path:**
```bash
# Verify file structure
├── resources/
│   ├── project_config.properties
│   └── locators/
│       └── loc_pattern.properties
```

2. **Set Working Directory:**
```python
import os
os.chdir('/path/to/project/root')

# Or use absolute paths in configuration
```

3. **Environment Variable:**
```bash
export QAF_RESOURCES_PATH=/absolute/path/to/resources
```

---

## WebDriver Issues

### Browser Not Starting

**Problem:** Browser fails to launch
```
selenium.common.exceptions.WebDriverException: unknown error: Chrome failed to start
selenium.common.exceptions.SessionNotCreatedException
```

**Solutions:**

1. **Update Browser and Driver:**
```bash
# Update Chrome/Firefox to latest version
# Framework auto-updates driver via webdriver-manager
```

2. **Add Browser Options:**
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
# options.add_argument('--headless')  # For headless mode

driver = webdriver.Chrome(options=options)
```

3. **Check System Resources:**
```bash
# Check available memory
free -h  # Linux
# Task Manager -> Performance  # Windows

# Close unnecessary applications
```

---

### Element Not Found

**Problem:** Elements not being located
```
selenium.common.exceptions.NoSuchElementException
selenium.common.exceptions.TimeoutException
```

**Solutions:**

1. **Add Explicit Waits:**
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(driver, 10)
element = wait.until(
    EC.presence_of_element_located((By.XPATH, "//button[@id='submit']"))
)
```

2. **Debug Locator Strategy:**
```python
# Test locator in browser console
# F12 -> Console
$x("//button[@id='submit']")  # XPath
document.querySelector("#submit")  # CSS

# Try multiple strategies
locators = [
    "//button[@id='submit']",
    "//input[@type='submit']", 
    "//button[contains(text(),'Submit')]"
]

for locator in locators:
    try:
        element = driver.find_element(By.XPATH, locator)
        print(f"Found with: {locator}")
        break
    except:
        continue
```

3. **Check for Dynamic Content:**
```python
# Wait for page to load completely
time.sleep(2)  # Not recommended, but for debugging

# Wait for specific conditions
wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
```

---

## Test Execution Issues

### Tests Not Running

**Problem:** No tests discovered or executed
```
collected 0 items
No tests ran
```

**Solutions:**

1. **Check Test Discovery:**
```bash
# Ensure proper file naming
test_*.py or *_test.py  # For pytest
*_steps.py              # For Behave step definitions

# Verify test structure
def test_function():  # Must start with 'test_'
    pass
```

2. **Check Imports:**
```python
# Ensure proper imports
from behave import given, when, then  # For BDD
import pytest  # For pytest
```

3. **Run with Verbose Mode:**
```bash
# Pytest verbose
pytest -v tests/

# Behave verbose  
behave -v features/
```

---

### Import Errors

**Problem:** Module import failures
```
ModuleNotFoundError: No module named 'tests.automation_library'
ImportError: cannot import name 'BrowserGlobal'
```

**Solutions:**

1. **Check Python Path:**
```python
import sys
print(sys.path)

# Add project root to path
sys.path.insert(0, '/path/to/project/root')
```

2. **Verify File Structure:**
```bash
tests/
├── __init__.py           # Required
├── automation_library/
│   ├── __init__.py       # Required
│   ├── BrowserGlobal.py
│   └── Web.py
└── steps/
    ├── __init__.py       # Required
    └── automation_library_steps.py
```

3. **Use Relative Imports:**
```python
# From tests/steps/automation_library_steps.py
from tests.automation_library import BrowserGlobal as BG
from tests.automation_library import Web

# Or absolute imports
from automation_library import BrowserGlobal as BG
```

---

### BDD Step Linking Issues

**Problem:** Steps not linking to definitions in IDE
```
Step 'I enter username "test"' is not defined
Unimplemented step: When I click "Login" button
```

**Solutions:**

1. **Correct Step Definition Format:**
```python
# ❌ Wrong format - doesn't link in IDE
@when('I enter username "{username}"')
def enter_username(context, username):
    pass

# ✅ Correct format - links in IDE
@when('I enter username {string}')
def enter_username(context, username):
    pass
```

2. **Check Step File Location:**
```bash
# Steps must be in steps/ directory
tests/steps/automation_library_steps.py
# Or
features/steps/step_definitions.py
```

3. **Verify Step Registration:**
```python
# Ensure proper imports
from behave import given, when, then, step

# Use @step for generic steps
@step('I wait for {seconds:d} seconds')
def wait_seconds(context, seconds):
    time.sleep(seconds)
```

---

## Reporting Issues

### Allure Reports Not Generated

**Problem:** Empty allure-results or report not opening
```
Allure results directory is empty
No allure report generated
```

**Solutions:**

1. **Check Allure Installation:**
```bash
# Install Allure
npm install -g allure-commandline
# Or download from: https://github.com/allure-framework/allure2/releases

# Verify installation
allure --version
```

2. **Correct Test Execution:**
```bash
# Behave with Allure
behave tests/ -f allure_behave.formatter:AllureFormatter -o allure-results

# Pytest with Allure
pytest tests/ --alluredir=allure-results

# Check results directory
ls -la allure-results/
```

3. **Report Generation:**
```bash
# Serve report (temporary)
allure serve allure-results

# Generate static report
allure generate allure-results -o allure-report --clean

# Open report
allure open allure-report
```

---

### Screenshots Not Captured

**Problem:** No screenshots in test reports
```
Screenshot attachment missing
Image not found in report
```

**Solutions:**

1. **Check Configuration:**
```properties
# resources/project_config.properties
screenshot.on.failure=true
screenshot.on.success=false
screenshot.dir=screenshots
```

2. **Manual Screenshot Debugging:**
```python
import allure
from selenium import webdriver

def take_debug_screenshot(driver, name="debug"):
    try:
        # Test screenshot capability
        screenshot = driver.get_screenshot_as_png()
        
        # Save to file
        with open(f"{name}.png", "wb") as f:
            f.write(screenshot)
            
        # Attach to Allure
        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG
        )
        print("Screenshot captured successfully")
        
    except Exception as e:
        print(f"Screenshot error: {e}")
```

---

## Performance Issues

### Slow Test Execution

**Problem:** Tests running slowly
```
Test suite taking too long to complete
Individual tests timing out
```

**Solutions:**

1. **Optimize Waits:**
```python
# ❌ Avoid fixed waits
time.sleep(5)

# ✅ Use explicit waits
wait = WebDriverWait(driver, 10)
wait.until(EC.element_to_be_clickable((By.ID, "button")))

# ✅ Reduce default timeout for faster failure
wait = WebDriverWait(driver, 3)  # Faster for negative tests
```

2. **Parallel Execution:**
```bash
# Pytest parallel
pip install pytest-xdist
pytest -n 4 tests/  # 4 parallel workers

# Behave parallel
pip install behave-parallel
behave --parallel-processes 4 tests/
```

3. **Browser Optimization:**
```python
options = webdriver.ChromeOptions()
options.add_argument('--disable-extensions')
options.add_argument('--disable-plugins')
options.add_argument('--disable-images')  # Skip image loading
options.add_argument('--disable-javascript')  # If JS not needed
```

---

### Memory Issues

**Problem:** Out of memory errors during test execution
```
MemoryError: Unable to allocate memory
Process killed due to memory usage
```

**Solutions:**

1. **Driver Cleanup:**
```python
def teardown_method(self):
    """Ensure proper cleanup"""
    if hasattr(self, 'driver') and self.driver:
        try:
            self.driver.quit()  # Not just close()
        except:
            pass
        finally:
            self.driver = None
```

2. **Resource Management:**
```python
# Use context managers
from contextlib import contextmanager

@contextmanager
def browser_session():
    driver = None
    try:
        driver = webdriver.Chrome()
        yield driver
    finally:
        if driver:
            driver.quit()

# Usage
with browser_session() as driver:
    driver.get("https://example.com")
    # Automatic cleanup
```

3. **System Monitoring:**
```bash
# Monitor memory usage
htop  # Linux
# Task Manager  # Windows

# Set memory limits
ulimit -v 4194304  # 4GB limit (Linux)
```

---

## Network and Connection Issues

### Timeout Errors

**Problem:** Network-related timeouts
```
requests.exceptions.ConnectTimeout
selenium.common.exceptions.TimeoutException
```

**Solutions:**

1. **Increase Timeouts:**
```python
# Page load timeout
driver.set_page_load_timeout(60)

# Script timeout
driver.set_script_timeout(30)

# Implicit wait
driver.implicitly_wait(10)
```

2. **Network Debugging:**
```python
import requests

# Test connectivity
try:
    response = requests.get("https://www.google.com", timeout=5)
    print(f"Network OK: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Network issue: {e}")
```

3. **Proxy Configuration:**
```python
# If behind corporate proxy
proxy = {
    'http': 'http://proxy.company.com:8080',
    'https': 'https://proxy.company.com:8080'
}

options = webdriver.ChromeOptions()
options.add_argument('--proxy-server=proxy.company.com:8080')
```

---

## Debugging Techniques

### Logging and Debug Information

```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def debug_element_location(driver, locator):
    """Debug helper for element location"""
    try:
        # Check if element exists
        elements = driver.find_elements(By.XPATH, locator)
        logger.info(f"Found {len(elements)} elements with locator: {locator}")
        
        # Get page source for analysis
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        # Take screenshot for visual debugging  
        driver.save_screenshot('debug_screenshot.png')
        
    except Exception as e:
        logger.error(f"Debug error: {e}")
```

### Interactive Debugging

```python
import pdb

def test_with_breakpoint():
    driver.get("https://example.com")
    
    # Set breakpoint for interactive debugging
    pdb.set_trace()
    
    # Continue with test...
    element = driver.find_element(By.ID, "button")
```

### Common Debug Commands

```python
# In pdb or IDE debugger:
# Check current URL
print(driver.current_url)

# Check page title  
print(driver.title)

# Check if element exists
print(len(driver.find_elements(By.XPATH, "//button")))

# Get element attributes
element = driver.find_element(By.ID, "test")
print(element.get_attribute("class"))
print(element.text)
print(element.is_displayed())

# Execute JavaScript for debugging
result = driver.execute_script("return document.readyState;")
print(f"Page ready state: {result}")
```

## Getting Additional Help

If you're still experiencing issues:

1. **Check Framework Documentation:** Review the [User Guide](../user-guide/framework-guide.md)
2. **Search Known Issues:** Check GitHub issues for similar problems
3. **Enable Debug Logging:** Set log level to DEBUG for detailed output
4. **Create Minimal Reproduction:** Isolate the issue to smallest possible test case
5. **Community Support:** Post questions with full error details and environment info

Remember to include this information when seeking help:
- Python version
- Framework version
- Browser and OS details
- Complete error message and stack trace
- Minimal code that reproduces the issue