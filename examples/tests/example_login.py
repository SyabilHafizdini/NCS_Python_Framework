"""
Example test demonstrating QAF framework usage
This example shows how to write clean, maintainable Selenium tests
"""
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@allure.epic("Example Tests")
@allure.feature("Login Functionality")
class TestLoginExample:
    
    def setup_method(self):
        """Setup method called before each test method"""
        with allure.step("Initialize WebDriver"):
            service = Service("drivers/chromedriver.exe")
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 10)
        
    def teardown_method(self):
        """Cleanup method called after each test method"""
        if hasattr(self, 'driver'):
            with allure.step("Close WebDriver"):
                self.driver.quit()
            
    @pytest.mark.smoke  
    @allure.story("Successful Login")
    @allure.title("Login with Valid Credentials")
    @allure.description("This test verifies successful login with valid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_success(self):
        """Test successful login flow"""
        with allure.step("Navigate to demo application"):
            self.driver.get("https://www.saucedemo.com/v1/")
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="Login Page",
                attachment_type=allure.attachment_type.PNG
            )
        
        with allure.step("Enter username"):
            username_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='username']"))
            )
            username_field.clear()
            username_field.send_keys("standard_user")
        
        with allure.step("Enter password"):
            password_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='password']"))
            )
            password_field.clear()
            password_field.send_keys("secret_sauce")
        
        with allure.step("Click login button"):
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
            )
            login_button.click()
        
        with allure.step("Verify successful login"):
            self.wait.until(lambda driver: "inventory.html" in driver.current_url)
            assert "inventory.html" in self.driver.current_url
            
            products_title = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Products')]"))
            )
            assert products_title.is_displayed()
            
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="Success Page",
                attachment_type=allure.attachment_type.PNG
            )