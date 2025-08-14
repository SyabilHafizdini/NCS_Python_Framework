"""
QAF Pattern Locator Example
Demonstrates usage of the dynamic pattern locator system
"""

from qaf.automation.ui.util.pattern_locator import get_pattern_locator, input_locator, button_locator
from qaf.automation.step_def.pattern_steps import *


def demonstrate_pattern_usage():
    """Demonstrate various ways to use pattern locators"""
    
    # Get the pattern locator instance
    pattern_loc = get_pattern_locator()
    
    # Example 1: Generate locators for different element types
    print("=== Pattern Locator Examples ===")
    
    # Input field locators
    username_input = pattern_loc.input("loginPage", "Username")
    password_input = pattern_loc.input("loginPage", "Password") 
    email_input = pattern_loc.input("registrationPage", "Email", "user@example.com")
    
    print(f"Username input locator: {username_input}")
    print(f"Password input locator: {password_input}")
    print(f"Email input locator: {email_input}")
    
    # Button locators
    login_button = pattern_loc.button("loginPage", "Login")
    submit_button = pattern_loc.button("registrationPage", "Submit", "Register Now")
    
    print(f"Login button locator: {login_button}")
    print(f"Submit button locator: {submit_button}")
    
    # Link locators
    forgot_password_link = pattern_loc.link("loginPage", "Forgot Password")
    terms_link = pattern_loc.link("registrationPage", "Terms", "terms-conditions")
    
    print(f"Forgot password link locator: {forgot_password_link}")
    print(f"Terms link locator: {terms_link}")
    
    # Checkbox locators
    remember_me_checkbox = pattern_loc.checkbox("loginPage", "Remember Me")
    newsletter_checkbox = pattern_loc.checkbox("registrationPage", "Newsletter", "subscribe")
    
    print(f"Remember me checkbox locator: {remember_me_checkbox}")
    print(f"Newsletter checkbox locator: {newsletter_checkbox}")
    
    # Select dropdown locators
    country_select = pattern_loc.select("registrationPage", "Country")
    timezone_select = pattern_loc.select("settingsPage", "Timezone", "UTC")
    
    print(f"Country select locator: {country_select}")
    print(f"Timezone select locator: {timezone_select}")
    
    # Example 2: Using convenience functions
    print("\n=== Convenience Functions ===")
    
    user_input = input_locator("profilePage", "Username")
    save_button = button_locator("profilePage", "Save")
    
    print(f"User input (convenience): {user_input}")
    print(f"Save button (convenience): {save_button}")
    
    # Example 3: Custom patterns
    print("\n=== Custom Patterns ===")
    
    # Add custom pattern for modal elements
    pattern_loc.add_custom_pattern("modal", [
        "xpath=//div[contains(@class,'modal')]//h4[text()='${loc.auto.fieldName}']",
        "xpath=//div[@role='dialog']//span[contains(text(),'${loc.auto.fieldName}')]"
    ])
    
    modal_locator = pattern_loc._get_locator("confirmPage", "modal", "Confirm Action")
    print(f"Custom modal locator: {modal_locator}")
    
    # Example 4: Check available pattern types
    print("\n=== Available Pattern Types ===")
    pattern_types = pattern_loc.get_pattern_types()
    print(f"Available patterns: {', '.join(pattern_types)}")
    
    # Example 5: Check if patterns are enabled
    print(f"Pattern system enabled: {pattern_loc.is_pattern_enabled()}")


def create_sample_feature_file():
    """Create a sample BDD feature file using pattern steps"""
    
    feature_content = """
@web @mobile
Feature: Login functionality with pattern locators

  Scenario: User should be able to login using pattern-based steps
    Given user is on application home
    When enter 'john.doe@example.com' in 'Username' on 'loginPage'
    And enter 'password123' in 'Password' on 'loginPage'
    And click 'Login' button on 'loginPage'
    Then verify 'Welcome' text is displayed on 'dashboardPage'
    And verify 'Logout' button is present on 'dashboardPage'

  Scenario: User registration with various field types
    Given user navigates to registration page
    When enter 'John Doe' in 'Full Name' on 'registrationPage'
    And enter 'john.doe@example.com' in 'Email' on 'registrationPage'
    And enter 'password123' in 'Password' on 'registrationPage'
    And enter 'password123' in 'Confirm Password' on 'registrationPage'
    And select 'United States' from 'Country' dropdown on 'registrationPage'
    And check 'Terms and Conditions' checkbox on 'registrationPage'
    And check 'Newsletter' checkbox on 'registrationPage'
    And click 'Register' button on 'registrationPage'
    Then verify 'Registration successful' text is displayed on 'confirmationPage'

  Scenario: Form validation with pattern locators
    Given user is on registration page
    When click 'Register' button on 'registrationPage'
    Then verify 'Email is required' text is present in 'Error Message' on 'registrationPage'
    And verify 'Password is required' text is present in 'Error Message' on 'registrationPage'
    
  Scenario: Dynamic element interaction
    Given user is on product page
    When enter 'iPhone' in 'Search' with value 'product-search' on 'productPage'
    And click 'Search' button with value 'search-btn' on 'productPage'
    And click 'Add to Cart' link with href 'add-to-cart' on 'productPage'
    Then verify 'Item added to cart' text is displayed on 'productPage'
    """
    
    with open('features/pattern_login.feature', 'w') as f:
        f.write(feature_content.strip())
    
    print("Sample feature file created: features/pattern_login.feature")


def create_sample_test_case():
    """Create a sample pytest test case using pattern locators"""
    
    test_content = """
import pytest
from qaf.automation.ui.util.pattern_locator import get_pattern_locator
from qaf.automation.ui.webdriver.qaf_web_element import QAFWebElement
from qaf.automation.core.test_base import get_driver


class TestPatternLocators:
    
    def setup_method(self):
        self.pattern_loc = get_pattern_locator()
    
    @pytest.mark.web
    def test_login_with_pattern_locators(self):
        # Navigate to login page
        get_driver().get("https://example.com/login")
        
        # Use pattern locators to interact with elements
        username_locator = self.pattern_loc.input("loginPage", "Username")
        password_locator = self.pattern_loc.input("loginPage", "Password")
        login_button_locator = self.pattern_loc.button("loginPage", "Login")
        
        # Interact with elements
        username_field = QAFWebElement(get_driver(), username_locator)
        password_field = QAFWebElement(get_driver(), password_locator)
        login_button = QAFWebElement(get_driver(), login_button_locator)
        
        username_field.send_keys("test@example.com")
        password_field.send_keys("password123")
        login_button.click()
        
        # Verify login success
        welcome_locator = self.pattern_loc.text("dashboardPage", "Welcome")
        welcome_element = QAFWebElement(get_driver(), welcome_locator)
        assert welcome_element.is_displayed()
    
    @pytest.mark.web
    def test_registration_form(self):
        # Navigate to registration page
        get_driver().get("https://example.com/register")
        
        # Fill registration form using pattern locators
        fields = {
            "Full Name": "John Doe",
            "Email": "john.doe@example.com",
            "Password": "password123",
            "Confirm Password": "password123"
        }
        
        for field_name, field_value in fields.items():
            locator = self.pattern_loc.input("registrationPage", field_name)
            element = QAFWebElement(get_driver(), locator)
            element.send_keys(field_value)
        
        # Select country
        country_locator = self.pattern_loc.select("registrationPage", "Country")
        country_element = QAFWebElement(get_driver(), country_locator)
        from selenium.webdriver.support.ui import Select
        select = Select(country_element)
        select.select_by_visible_text("United States")
        
        # Check terms checkbox
        terms_locator = self.pattern_loc.checkbox("registrationPage", "Terms")
        terms_element = QAFWebElement(get_driver(), terms_locator)
        terms_element.click()
        
        # Submit form
        submit_locator = self.pattern_loc.button("registrationPage", "Register")
        submit_button = QAFWebElement(get_driver(), submit_locator)
        submit_button.click()
        
        # Verify registration success
        success_locator = self.pattern_loc.text("confirmationPage", "Registration successful")
        success_element = QAFWebElement(get_driver(), success_locator)
        assert success_element.is_displayed()
    """
    
    with open('tests/test_pattern_locators.py', 'w') as f:
        f.write(test_content.strip())
    
    print("Sample test file created: tests/test_pattern_locators.py")


if __name__ == "__main__":
    demonstrate_pattern_usage()
    
    # Uncomment to create sample files
    # create_sample_feature_file()
    # create_sample_test_case()