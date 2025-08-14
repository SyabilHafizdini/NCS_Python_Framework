# BrowserGlobal API Reference

The BrowserGlobal module provides comprehensive browser automation functions for web testing. This module contains 182+ functions covering all aspects of browser interaction, navigation, and verification.

## Module Import

```python
from tests.automation_library import BrowserGlobal as BG
```

## Core Browser Functions

### Browser Management

#### `open_browser(url: str)`
Opens a web browser and navigates to the specified URL.

```python
# Open browser and navigate to URL
BG.open_browser("https://www.example.com")
```

**Parameters:**
- `url` (str): The URL to navigate to

**Allure Integration:** Automatically logs the URL and takes screenshot

---

#### `close_browser()`
Closes the current browser session.

```python
# Close current browser
BG.close_browser()
```

**Allure Integration:** Takes final screenshot before closing

---

#### `maximize_window()`
Maximizes the browser window to full screen.

```python
# Maximize browser window
BG.maximize_window()
```

---

#### `minimize_window()`
Minimizes the browser window.

```python
# Minimize browser window  
BG.minimize_window()
```

---

#### `set_window_size(width: int, height: int)`
Sets the browser window to specific dimensions.

```python
# Set window to specific size
BG.set_window_size(1920, 1080)
```

**Parameters:**
- `width` (int): Window width in pixels
- `height` (int): Window height in pixels

---

### Navigation Functions

#### `navigate_to(url: str)`
Navigates to the specified URL.

```python
# Navigate to URL
BG.navigate_to("https://www.newpage.com")
```

**Parameters:**
- `url` (str): The URL to navigate to

---

#### `go_back()`
Navigates to the previous page in browser history.

```python
# Go back to previous page
BG.go_back()
```

---

#### `go_forward()`
Navigates to the next page in browser history.

```python
# Go forward to next page  
BG.go_forward()
```

---

#### `refresh_page()`
Refreshes the current page.

```python
# Refresh current page
BG.refresh_page()
```

---

#### `get_current_url() -> str`
Returns the current page URL.

```python
# Get current URL
current_url = BG.get_current_url()
print(f"Current URL: {current_url}")
```

**Returns:** Current page URL as string

---

#### `get_page_title() -> str`
Returns the current page title.

```python
# Get page title
title = BG.get_page_title()
print(f"Page title: {title}")
```

**Returns:** Page title as string

---

### Wait and Timeout Functions

#### `wait_for_page_load(timeout: int = 30)`
Waits for the page to fully load.

```python
# Wait for page to load (default 30 seconds)
BG.wait_for_page_load()

# Wait with custom timeout
BG.wait_for_page_load(timeout=60)
```

**Parameters:**
- `timeout` (int, optional): Maximum wait time in seconds. Default: 30

---

#### `wait_for_element_visible(locator: str, timeout: int = 30)`
Waits for an element to become visible.

```python
# Wait for element to be visible
BG.wait_for_element_visible("//button[@id='submit']", timeout=20)
```

**Parameters:**
- `locator` (str): XPath locator for the element
- `timeout` (int, optional): Maximum wait time in seconds. Default: 30

---

#### `wait_for_element_clickable(locator: str, timeout: int = 30)`
Waits for an element to become clickable.

```python
# Wait for element to be clickable
BG.wait_for_element_clickable("//button[@id='submit']")
```

**Parameters:**
- `locator` (str): XPath locator for the element  
- `timeout` (int, optional): Maximum wait time in seconds. Default: 30

---

#### `wait_for_text_present(text: str, timeout: int = 30)`
Waits for specific text to appear on the page.

```python
# Wait for text to appear
BG.wait_for_text_present("Welcome to Dashboard", timeout=15)
```

**Parameters:**
- `text` (str): Text to wait for
- `timeout` (int, optional): Maximum wait time in seconds. Default: 30

---

### Element Interaction Functions

#### `click_element(locator: str)`
Clicks on the specified element.

```python
# Click element by XPath
BG.click_element("//button[@id='login']")
```

**Parameters:**
- `locator` (str): XPath locator for the element

**Allure Integration:** Logs the locator and takes screenshot

---

#### `double_click_element(locator: str)`
Double-clicks on the specified element.

```python
# Double click element
BG.double_click_element("//div[@class='file-item']")
```

**Parameters:**
- `locator` (str): XPath locator for the element

---

#### `right_click_element(locator: str)`
Right-clicks on the specified element to show context menu.

```python
# Right click element
BG.right_click_element("//div[@class='menu-item']")
```

**Parameters:**
- `locator` (str): XPath locator for the element

---

#### `hover_over_element(locator: str)`
Moves the mouse cursor over the specified element.

```python
# Hover over element to show tooltip
BG.hover_over_element("//span[@class='help-icon']")
```

**Parameters:**
- `locator` (str): XPath locator for the element

---

### Text Input Functions

#### `type_text(locator: str, text: str)`
Types text into the specified input field.

```python
# Type text in field
BG.type_text("//input[@id='username']", "john.doe")
```

**Parameters:**
- `locator` (str): XPath locator for the input element
- `text` (str): Text to type

**Allure Integration:** Logs the text entered (sensitive data is masked)

---

#### `clear_text(locator: str)`
Clears text from the specified input field.

```python
# Clear text field
BG.clear_text("//input[@id='search']")
```

**Parameters:**
- `locator` (str): XPath locator for the input element

---

#### `append_text(locator: str, text: str)`
Appends text to existing content in the input field.

```python
# Append text to existing content
BG.append_text("//textarea[@id='comments']", " Additional information")
```

**Parameters:**
- `locator` (str): XPath locator for the input element
- `text` (str): Text to append

---

### Form Interaction Functions

#### `select_dropdown_by_value(locator: str, value: str)`
Selects dropdown option by its value attribute.

```python
# Select dropdown option by value
BG.select_dropdown_by_value("//select[@id='country']", "us")
```

**Parameters:**
- `locator` (str): XPath locator for the select element
- `value` (str): Value attribute of the option to select

---

#### `select_dropdown_by_text(locator: str, text: str)`
Selects dropdown option by its visible text.

```python
# Select dropdown option by text
BG.select_dropdown_by_text("//select[@id='country']", "United States")
```

**Parameters:**
- `locator` (str): XPath locator for the select element
- `text` (str): Visible text of the option to select

---

#### `select_dropdown_by_index(locator: str, index: int)`
Selects dropdown option by its index position.

```python
# Select dropdown option by index (0-based)
BG.select_dropdown_by_index("//select[@id='priority']", 2)
```

**Parameters:**
- `locator` (str): XPath locator for the select element
- `index` (int): Zero-based index of the option to select

---

#### `check_checkbox(locator: str)`
Checks the specified checkbox if not already checked.

```python
# Check checkbox
BG.check_checkbox("//input[@type='checkbox' and @id='terms']")
```

**Parameters:**
- `locator` (str): XPath locator for the checkbox element

---

#### `uncheck_checkbox(locator: str)`
Unchecks the specified checkbox if currently checked.

```python
# Uncheck checkbox
BG.uncheck_checkbox("//input[@type='checkbox' and @id='newsletter']")
```

**Parameters:**
- `locator` (str): XPath locator for the checkbox element

---

#### `select_radio_button(locator: str)`
Selects the specified radio button.

```python
# Select radio button
BG.select_radio_button("//input[@type='radio' and @value='male']")
```

**Parameters:**
- `locator` (str): XPath locator for the radio button element

---

### File Upload Functions

#### `upload_file(locator: str, file_path: str)`
Uploads a file using the file input element.

```python
# Upload file
BG.upload_file("//input[@type='file']", "C:/Documents/resume.pdf")
```

**Parameters:**
- `locator` (str): XPath locator for the file input element
- `file_path` (str): Absolute path to the file to upload

---

### Alert and Dialog Functions

#### `accept_alert()`
Accepts (clicks OK on) a JavaScript alert dialog.

```python
# Accept alert
BG.accept_alert()
```

---

#### `dismiss_alert()`
Dismisses (clicks Cancel on) a JavaScript alert dialog.

```python
# Dismiss alert
BG.dismiss_alert()
```

---

#### `get_alert_text() -> str`
Gets the text content of a JavaScript alert dialog.

```python
# Get alert text
alert_text = BG.get_alert_text()
print(f"Alert says: {alert_text}")
```

**Returns:** Alert text as string

---

#### `type_in_alert(text: str)`
Types text into a JavaScript prompt dialog.

```python
# Type in alert prompt
BG.type_in_alert("John Doe")
```

**Parameters:**
- `text` (str): Text to type in the prompt

---

### Frame and Window Functions

#### `switch_to_frame(locator: str)`
Switches context to the specified iframe.

```python
# Switch to frame
BG.switch_to_frame("//iframe[@id='content-frame']")
```

**Parameters:**
- `locator` (str): XPath locator for the iframe element

---

#### `switch_to_default_content()`
Switches context back to the main document from any iframe.

```python
# Switch back to main content
BG.switch_to_default_content()
```

---

#### `switch_to_window(window_handle: str)`
Switches to a specific browser window or tab.

```python
# Get window handles and switch
handles = BG.get_window_handles()
BG.switch_to_window(handles[1])  # Switch to second window
```

**Parameters:**
- `window_handle` (str): Window handle to switch to

---

#### `get_window_handles() -> list`
Gets all current window handles.

```python
# Get all window handles
handles = BG.get_window_handles()
print(f"Number of windows: {len(handles)}")
```

**Returns:** List of window handle strings

---

#### `close_window()`
Closes the current window or tab.

```python
# Close current window
BG.close_window()
```

---

### Screenshot and Capture Functions

#### `take_screenshot(filename: str = None)`
Takes a screenshot of the current page.

```python
# Take screenshot with auto-generated name
BG.take_screenshot()

# Take screenshot with custom filename  
BG.take_screenshot("login_page.png")
```

**Parameters:**
- `filename` (str, optional): Custom filename for the screenshot

**Allure Integration:** Automatically attaches screenshot to test report

---

#### `take_element_screenshot(locator: str, filename: str = None)`
Takes a screenshot of a specific element.

```python
# Screenshot specific element
BG.take_element_screenshot("//div[@id='error-message']", "error.png")
```

**Parameters:**
- `locator` (str): XPath locator for the element
- `filename` (str, optional): Custom filename for the screenshot

---

### JavaScript Execution Functions

#### `execute_javascript(script: str) -> Any`
Executes JavaScript code in the browser.

```python
# Execute JavaScript
result = BG.execute_javascript("return document.title;")
print(f"Page title via JS: {result}")

# Scroll to bottom of page
BG.execute_javascript("window.scrollTo(0, document.body.scrollHeight);")
```

**Parameters:**
- `script` (str): JavaScript code to execute

**Returns:** Result of JavaScript execution

---

#### `scroll_to_element(locator: str)`
Scrolls the page to bring the specified element into view.

```python
# Scroll to element
BG.scroll_to_element("//footer[@id='page-footer']")
```

**Parameters:**
- `locator` (str): XPath locator for the element

---

#### `scroll_to_top()`
Scrolls to the top of the page.

```python
# Scroll to top
BG.scroll_to_top()
```

---

#### `scroll_to_bottom()`
Scrolls to the bottom of the page.

```python
# Scroll to bottom
BG.scroll_to_bottom()
```

---

### Element Information Functions

#### `get_element_text(locator: str) -> str`
Gets the visible text content of the specified element.

```python
# Get element text
error_message = BG.get_element_text("//div[@class='error']")
print(f"Error: {error_message}")
```

**Parameters:**
- `locator` (str): XPath locator for the element

**Returns:** Element text as string

---

#### `get_element_attribute(locator: str, attribute: str) -> str`
Gets the value of a specific attribute from the element.

```python
# Get attribute value
href_value = BG.get_element_attribute("//a[@id='home-link']", "href")
class_value = BG.get_element_attribute("//div[@id='container']", "class")
```

**Parameters:**
- `locator` (str): XPath locator for the element
- `attribute` (str): Name of the attribute to retrieve

**Returns:** Attribute value as string

---

#### `is_element_present(locator: str) -> bool`
Checks if the specified element exists on the page.

```python
# Check if element exists
if BG.is_element_present("//div[@id='success-message']"):
    print("Success message is present")
```

**Parameters:**
- `locator` (str): XPath locator for the element

**Returns:** True if element exists, False otherwise

---

#### `is_element_visible(locator: str) -> bool`
Checks if the specified element is visible on the page.

```python
# Check if element is visible
if BG.is_element_visible("//button[@id='submit']"):
    print("Submit button is visible")
```

**Parameters:**
- `locator` (str): XPath locator for the element

**Returns:** True if element is visible, False otherwise

---

#### `is_element_enabled(locator: str) -> bool`
Checks if the specified element is enabled for interaction.

```python
# Check if element is enabled
if BG.is_element_enabled("//input[@id='username']"):
    print("Username field is enabled")
```

**Parameters:**
- `locator` (str): XPath locator for the element

**Returns:** True if element is enabled, False otherwise

---

#### `is_element_selected(locator: str) -> bool`
Checks if the specified element is selected (for checkboxes, radio buttons).

```python
# Check if checkbox is selected
if BG.is_element_selected("//input[@type='checkbox' and @id='terms']"):
    print("Terms checkbox is selected")
```

**Parameters:**
- `locator` (str): XPath locator for the element

**Returns:** True if element is selected, False otherwise

---

### Cookie Management Functions

#### `add_cookie(name: str, value: str)`
Adds a cookie to the current session.

```python
# Add cookie
BG.add_cookie("user_preference", "dark_mode")
```

**Parameters:**
- `name` (str): Cookie name
- `value` (str): Cookie value

---

#### `get_cookie(name: str) -> dict`
Gets a specific cookie by name.

```python
# Get cookie
cookie = BG.get_cookie("session_id")
print(f"Session ID: {cookie['value']}")
```

**Parameters:**
- `name` (str): Cookie name to retrieve

**Returns:** Cookie dictionary with name, value, and other properties

---

#### `delete_cookie(name: str)`
Deletes a specific cookie by name.

```python
# Delete cookie
BG.delete_cookie("temp_data")
```

**Parameters:**
- `name` (str): Cookie name to delete

---

#### `delete_all_cookies()`
Deletes all cookies from the current session.

```python
# Delete all cookies
BG.delete_all_cookies()
```

---

### Browser Information Functions

#### `get_browser_name() -> str`
Gets the name of the current browser.

```python
# Get browser name
browser = BG.get_browser_name()
print(f"Using browser: {browser}")
```

**Returns:** Browser name as string

---

#### `get_browser_version() -> str`
Gets the version of the current browser.

```python
# Get browser version
version = BG.get_browser_version()
print(f"Browser version: {version}")
```

**Returns:** Browser version as string

---

### Page Content Functions

#### `get_page_source() -> str`
Gets the complete HTML source of the current page.

```python
# Get page source
source = BG.get_page_source()
print(f"Page source length: {len(source)}")
```

**Returns:** HTML source as string

---

#### `verify_page_contains_text(text: str) -> bool`
Verifies if the page contains the specified text.

```python
# Verify page contains text
if BG.verify_page_contains_text("Welcome to Dashboard"):
    print("Successfully logged in")
```

**Parameters:**
- `text` (str): Text to search for on the page

**Returns:** True if text is found, False otherwise

---

## Usage Examples

### Complete Test Scenario

```python
from tests.automation_library import BrowserGlobal as BG

def test_complete_user_journey():
    """Complete test demonstrating BrowserGlobal functions"""
    
    # Browser setup
    BG.open_browser("https://demo-store.com")
    BG.maximize_window()
    
    # Navigation and verification
    assert BG.verify_page_contains_text("Welcome")
    title = BG.get_page_title()
    assert "Demo Store" in title
    
    # User interaction
    BG.type_text("//input[@id='search']", "laptop")
    BG.click_element("//button[@type='submit']")
    
    # Wait for results
    BG.wait_for_text_present("Search Results", timeout=10)
    
    # Product selection
    BG.click_element("//div[@class='product'][1]//a")
    BG.wait_for_page_load()
    
    # Add to cart
    BG.select_dropdown_by_text("//select[@id='quantity']", "2")
    BG.click_element("//button[@id='add-to-cart']")
    
    # Verification
    BG.wait_for_text_present("Added to cart")
    BG.take_screenshot("cart_added.png")
    
    # Cleanup
    BG.close_browser()
```

### Error Handling Example

```python
def test_with_error_handling():
    """Test with proper error handling"""
    try:
        BG.open_browser("https://example.com")
        
        # Check if element exists before interacting
        if BG.is_element_present("//button[@id='login']"):
            BG.click_element("//button[@id='login']")
        else:
            print("Login button not found")
        
        # Wait with timeout
        try:
            BG.wait_for_text_present("Dashboard", timeout=5)
        except Exception:
            print("Dashboard not loaded in time")
            BG.take_screenshot("timeout_error.png")
            
    finally:
        BG.close_browser()
```

## Integration with Pattern Locators

The BrowserGlobal functions work seamlessly with the QAF Pattern Locator system:

```python
from tests.automation_library import BrowserGlobal as BG
from qaf.automation.ui.util.pattern_locator import get_pattern_locator

def test_with_pattern_integration():
    """Test combining BrowserGlobal with Pattern Locators"""
    pattern_locator = get_pattern_locator()
    
    BG.open_browser("https://demo-app.com")
    
    # Generate locator using patterns
    username_locator = pattern_locator.input("loginPage", "Username", "username")
    
    # Use BrowserGlobal function with pattern locator
    BG.type_text(username_locator.replace("xpath=", ""), "john.doe")
    
    BG.close_browser()
```

This API reference covers all the core functions available in the BrowserGlobal module. Each function includes proper error handling, Allure integration for reporting, and comprehensive documentation to help you build robust automation tests.