# Pattern Locators Tutorial - UNDER RENOVATION

**⚠️ NOTICE: This pattern locator system is currently being upgraded to match the Java QAF framework architecture exactly. Please refer to the new implementation guide in `.claude/specs/pattern-locator-system/` for the latest design.**

Learn how to use the QAF Pattern Locator System for dynamic, maintainable element identification.

## What are Pattern Locators?

Pattern locators are a powerful QAF feature that generates XPath locators dynamically at runtime using configurable templates. Instead of hardcoding element selectors, you define reusable patterns that adapt to different elements and pages.

## Benefits

- **Dynamic Generation**: Locators created at runtime based on element attributes
- **Multiple Fallbacks**: Each pattern can include several backup strategies
- **Maintainable**: Change locator strategy in one place, affects all tests
- **Readable**: Test steps use business language, not technical selectors
- **Robust**: Automatic fallback when primary locators fail

## Core Components

### 1. Pattern Configuration File

`resources/locators/locPattern.properties` - defines XPath templates:

```properties
# Button patterns with multiple fallback strategies
loc.qaf.pattern.button=xpath=//button[contains(text(),'${loc.auto.fieldName}')] | //button[@value='${loc.auto.fieldName}'] | //*[@data-test='${loc.auto.fieldValue}'] | //input[@type='submit' and @value='${loc.auto.fieldName}']

# Input field patterns
loc.qaf.pattern.input=xpath=//input[@placeholder='${loc.auto.fieldName}'] | //*[@data-test='${loc.auto.fieldValue}'] | //input[@name='${loc.auto.fieldValue}'] | //input[@id='${loc.auto.fieldValue}']

# Link patterns  
loc.qaf.pattern.link=xpath=//a[contains(text(),'${loc.auto.fieldName}')] | //a[@href='${loc.auto.fieldValue}'] | //*[@data-test='${loc.auto.fieldValue}']

# Text verification patterns
loc.qaf.pattern.text=xpath=//*[contains(text(),'${loc.auto.fieldName}')] | //*[@data-test='${loc.auto.fieldValue}'] | //h1[contains(text(),'${loc.auto.fieldName}')]

# Checkbox patterns
loc.qaf.pattern.checkbox=xpath=//input[@type='checkbox' and @name='${loc.auto.fieldValue}'] | //input[@type='checkbox' and @id='${loc.auto.fieldValue}'] | //*[@data-test='${loc.auto.fieldValue}']

# Select/dropdown patterns
loc.qaf.pattern.select=xpath=//select[@name='${loc.auto.fieldValue}'] | //select[@id='${loc.auto.fieldValue}'] | //*[@data-test='${loc.auto.fieldValue}']
```

### 2. Framework Configuration

`resources/project_config.properties` - enables pattern system:

```properties
# Enable pattern locator system
loc.pattern.enabled=true
loc.pattern.code=loc.qaf

# Resources directory
env.resources=resources
```

### 3. Pattern Locator API

The framework provides `PatternEngine` class with element-specific methods:

```python
from qaf.automation.ui.util.pattern_locator import get_pattern_locator

pattern_locator = get_pattern_locator()

# Generate different types of locators
button_locator = pattern_locator.button("loginPage", "Login", "login-btn")
input_locator = pattern_locator.input("loginPage", "Username", "username")  
text_locator = pattern_locator.text("homePage", "Welcome", "welcome-msg")
```

## Pattern Variables

Pattern templates use placeholder variables that get replaced at runtime:

| Variable | Description | Example |
|----------|-------------|---------|
| `${loc.auto.fieldName}` | Human-readable field name | "Login", "Username", "Submit" |
| `${loc.auto.fieldValue}` | Technical field value | "login-btn", "username", "submit" |

## Practical Examples

### Example 1: Login Form

Let's automate a login form using pattern locators:

**HTML Structure:**
```html
<form>
  <input data-test="username" placeholder="Username" />
  <input data-test="password" placeholder="Password" type="password" />
  <button data-test="login-button">Login</button>
</form>
```

**Pattern Locator Usage:**
```python
from qaf.automation.ui.util.pattern_locator import get_pattern_locator

def test_login_with_patterns():
    pattern_locator = get_pattern_locator()
    
    # Generate locators dynamically
    username_locator = pattern_locator.input("loginPage", "Username", "username") 
    password_locator = pattern_locator.input("loginPage", "Password", "password")
    login_locator = pattern_locator.button("loginPage", "Login", "login-button")
    
    print("Generated locators:")
    print(f"Username: {username_locator}")  
    print(f"Password: {password_locator}")
    print(f"Login: {login_locator}")
```

**Output:**
```
Username: xpath=//input[@placeholder='Username'] | //*[@data-test='username'] | //input[@name='username']
Password: xpath=//input[@placeholder='Password'] | //*[@data-test='password'] | //input[@name='password']  
Login: xpath=//button[contains(text(),'Login')] | //*[@data-test='login-button'] | //input[@type='submit' and @value='Login']
```

### Example 2: E-commerce Product Page

**HTML Structure:**
```html
<div class="product">
  <h3>iPhone 12</h3>
  <button data-test="add-to-cart">Add to Cart</button>
  <a href="/product/iphone12" data-test="view-details">View Details</a>
  <input type="checkbox" name="compare" id="compare-iphone12" />
  <label for="compare-iphone12">Compare</label>
</div>
```

**Pattern Usage:**
```python
def test_product_interactions():
    pattern_locator = get_pattern_locator()
    
    # Different element types, same pattern approach
    product_title = pattern_locator.text("productPage", "iPhone 12", "product-title")
    add_to_cart = pattern_locator.button("productPage", "Add to Cart", "add-to-cart") 
    view_details = pattern_locator.link("productPage", "View Details", "view-details")
    compare_checkbox = pattern_locator.checkbox("productPage", "Compare", "compare-iphone12")
```

### Example 3: BDD Step Definitions

Integration with Behave step definitions:

```python
from behave import given, when, then
from qaf.automation.ui.util.pattern_locator import get_pattern_locator
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

@when('I enter "{text}" in "{field_name}" field on "{page_name}"')
def enter_text_in_field(context, text, field_name, page_name):
    pattern_locator = get_pattern_locator()
    
    # Generate locator for input field
    locator = pattern_locator.input(page_name, field_name, field_name.lower().replace(' ', '-'))
    
    # Handle multiple locator strategies
    if locator.startswith('xpath='):
        element = context.wait.until(
            EC.presence_of_element_located((By.XPATH, locator[6:]))
        )
    
    element.clear()
    element.send_keys(text)

@when('I click "{button_name}" button on "{page_name}"')  
def click_button_on_page(context, button_name, page_name):
    pattern_locator = get_pattern_locator()
    
    locator = pattern_locator.button(page_name, button_name, button_name.lower().replace(' ', '-'))
    
    if locator.startswith('xpath='):
        element = context.wait.until(
            EC.element_to_be_clickable((By.XPATH, locator[6:]))
        )
    
    element.click()

@then('I verify "{text}" is displayed on "{page_name}"')
def verify_text_displayed(context, text, page_name):
    pattern_locator = get_pattern_locator()
    
    locator = pattern_locator.text(page_name, text, text.lower().replace(' ', '-'))
    
    if locator.startswith('xpath='):
        element = context.wait.until(
            EC.presence_of_element_located((By.XPATH, locator[6:]))
        )
    
    assert element.is_displayed()
```

**Feature File Usage:**
```gherkin
Feature: E-commerce Shopping

  Scenario: Add product to cart
    Given I navigate to the product page
    When I click "Add to Cart" button on "productPage"  
    Then I verify "Added to cart" is displayed on "productPage"
    
  Scenario: User registration
    Given I navigate to registration page
    When I enter "john.doe@email.com" in "Email" field on "registrationPage"
    And I enter "John Doe" in "Full Name" field on "registrationPage"
    And I click "Register" button on "registrationPage" 
    Then I verify "Registration successful" is displayed on "confirmationPage"
```

## Advanced Pattern Techniques

### 1. Custom Pattern Methods

Extend the PatternLocator class for specific needs:

```python
from qaf.automation.ui.util.pattern_locator import PatternLocator

class CustomPatternLocator(PatternLocator):
    
    def modal_button(self, page: str, button_name: str, button_value: str = None):
        """Generate locator specifically for modal dialog buttons"""
        field_value = button_value or button_name.lower().replace(' ', '-')
        
        # Custom modal-specific patterns
        pattern = f"xpath=//div[contains(@class,'modal')]//button[contains(text(),'{button_name}')] | " \
                 f"//div[@role='dialog']//button[@data-test='{field_value}'] | " \
                 f"//*[@class='modal-footer']//button[contains(text(),'{button_name}')]"
                 
        return pattern
    
    def table_cell(self, page: str, row_text: str, column_header: str):
        """Generate locator for table cell based on row content and column"""
        pattern = f"xpath=//tr[contains(.,'{row_text}')]//td[position()=" \
                 f"count(//th[contains(text(),'{column_header}')]/preceding-sibling::th)+1]"
        return pattern
```

### 2. Pattern Inheritance

Organize patterns by page or component:

```properties
# Base patterns
loc.qaf.pattern.button=xpath=//button[contains(text(),'${loc.auto.fieldName}')]

# Page-specific overrides  
loc.qaf.pattern.loginPage.button=xpath=//form[@id='login']//button[contains(text(),'${loc.auto.fieldName}')]
loc.qaf.pattern.checkoutPage.button=xpath=//div[@class='checkout']//button[@data-test='${loc.auto.fieldValue}']
```

### 3. Multiple Locator Strategies

Handle complex scenarios with comprehensive fallbacks:

```properties
loc.qaf.pattern.input=xpath=//input[@data-test='${loc.auto.fieldValue}'] | \
                      //input[@placeholder='${loc.auto.fieldName}'] | \
                      //input[@name='${loc.auto.fieldValue}'] | \
                      //input[@id='${loc.auto.fieldValue}'] | \
                      //label[contains(text(),'${loc.auto.fieldName}')]/following-sibling::input | \
                      //label[contains(text(),'${loc.auto.fieldName}')]/parent::*/input
```

## Best Practices

### 1. Pattern Design
- **Start generic, get specific**: Begin with broad patterns, add specific ones for edge cases
- **Multiple fallbacks**: Always include 2-3 backup strategies
- **Consistent naming**: Use predictable fieldName and fieldValue conventions

### 2. Pattern Organization  
- **Group by element type**: Keep similar patterns together
- **Page-specific patterns**: Override base patterns for unique page structures
- **Document patterns**: Comment complex XPath expressions

### 3. Testing Patterns
- **Test pattern generation**: Verify patterns produce expected XPath
- **Validate fallbacks**: Ensure backup strategies work when primary fails
- **Monitor pattern usage**: Track which patterns are used most often

### 4. Maintenance
- **Regular reviews**: Update patterns as application UI changes  
- **Pattern metrics**: Monitor which locators fail most often
- **Version patterns**: Track pattern changes alongside application versions

## Troubleshooting

### Common Issues

**Pattern not found**:
```python
# Debug pattern generation
pattern_locator = get_pattern_locator()
locator = pattern_locator.input("testPage", "Username", "username")
print(f"Generated locator: {locator}")

# Test individual XPath parts
xpath_parts = locator.replace('xpath=', '').split(' | ')
for i, xpath in enumerate(xpath_parts):
    try:
        elements = driver.find_elements(By.XPATH, xpath.strip())
        print(f"XPath {i+1}: {xpath} - Found {len(elements)} elements")
    except Exception as e:
        print(f"XPath {i+1}: {xpath} - Error: {e}")
```

**Pattern not working**:
- Check `project_config.properties` has correct `loc.pattern.code`
- Verify `loc.pattern.enabled=true`
- Ensure pattern file path is correct in `env.resources`

**Element not found with pattern**:
- Inspect HTML to understand actual element structure
- Add more specific patterns for the element type
- Use browser dev tools to test XPath expressions

## Integration Examples

### Complete Test Example

```python
"""
Complete example showing pattern locator integration
"""
from behave import given, when, then
from qaf.automation.ui.util.pattern_locator import get_pattern_locator
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import allure

class PatternLocatorTest:
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.pattern_locator = None
    
    def setup(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.pattern_locator = get_pattern_locator()
    
    def test_complete_user_journey(self):
        """Test complete user journey using pattern locators"""
        
        # Navigate to application
        self.driver.get("https://demo-store.com")
        
        # Search for product using pattern locator
        search_locator = self.pattern_locator.input("homePage", "Search", "search")
        search_field = self._find_element(search_locator)
        search_field.send_keys("laptop")
        
        # Click search button
        search_btn_locator = self.pattern_locator.button("homePage", "Search", "search-btn")
        search_button = self._find_element(search_btn_locator)
        search_button.click()
        
        # Select product from results
        product_locator = self.pattern_locator.link("searchPage", "MacBook Pro", "product-macbook")
        product_link = self._find_element(product_locator)
        product_link.click()
        
        # Add to cart
        add_cart_locator = self.pattern_locator.button("productPage", "Add to Cart", "add-to-cart")
        add_cart_btn = self._find_element(add_cart_locator)
        add_cart_btn.click()
        
        # Verify success message
        success_locator = self.pattern_locator.text("productPage", "Added to cart", "success-message")
        success_msg = self._find_element(success_locator)
        assert success_msg.is_displayed()
    
    def _find_element(self, locator):
        """Helper method to find element using pattern locator"""
        if locator.startswith('xpath='):
            # Handle multiple XPath strategies
            xpath_parts = locator[6:].split(' | ')
            
            for xpath in xpath_parts:
                try:
                    element = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, xpath.strip()))
                    )
                    return element
                except:
                    continue
                    
            raise Exception(f"Element not found with any pattern: {locator}")
        else:
            raise Exception(f"Unsupported locator type: {locator}")
    
    def teardown(self):
        if self.driver:
            self.driver.quit()
```

This comprehensive tutorial covers the QAF Pattern Locator system from basic concepts to advanced implementation. The pattern approach provides a robust, maintainable solution for element identification in automated tests.