"""
BrowserGlobal.py - Core Browser Automation Functions
====================================================

This module contains reusable browser automation functions that provide
comprehensive browser management, element interaction, and verification capabilities.
All functions are designed to be framework-agnostic and can be used across projects.
"""

import os
import time
import json
import logging
from typing import List, Optional, Union, Any

import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementNotInteractableException,
    StaleElementReferenceException, WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager

# Global driver instance and configuration
_driver_instance = None
_wait_timeout = 30
_page_load_timeout = 60
_variables = {}


class BrowserGlobalError(Exception):
    """Custom exception for BrowserGlobal operations"""
    pass


def _get_driver() -> webdriver.Chrome:
    """Get current WebDriver instance or raise error if not initialized"""
    global _driver_instance
    if _driver_instance is None:
        raise BrowserGlobalError("WebDriver not initialized. Call open_browser() first.")
    return _driver_instance


def _get_wait(timeout: int = None) -> WebDriverWait:
    """Get WebDriverWait instance with specified timeout"""
    timeout = timeout or _wait_timeout
    return WebDriverWait(_get_driver(), timeout)


def _find_element(locator: str, timeout: int = None) -> Any:
    """Find element with timeout and proper error handling"""
    try:
        wait = _get_wait(timeout)
        if locator.startswith("xpath="):
            return wait.until(EC.presence_of_element_located((By.XPATH, locator.replace("xpath=", ""))))
        elif locator.startswith("id="):
            return wait.until(EC.presence_of_element_located((By.ID, locator.replace("id=", ""))))
        elif locator.startswith("css="):
            return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, locator.replace("css=", ""))))
        else:
            # Default to XPath if no prefix
            return wait.until(EC.presence_of_element_located((By.XPATH, locator)))
    except TimeoutException:
        raise NoSuchElementException(f"Element not found: {locator}")


def _take_screenshot_bytes(context) -> bytes:
    """Take screenshot and return as bytes"""
    return context.driver.get_screenshot_as_png()


def _attach_screenshot(context, name: str = "Screenshot"):
    """Attach screenshot to Allure report"""
    screenshot = _take_screenshot_bytes(context)
    allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)


# =============================================================================
# CORE BROWSER FUNCTIONS
# =============================================================================

@allure.step("Open web browser with URL: {url}")
def open_browser(url: str):
    """I open the web browser with {url}"""
    global _driver_instance
    
    if _driver_instance is not None:
        _driver_instance.quit()
    
    service = Service("drivers/chromedriver.exe")
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    _driver_instance = webdriver.Chrome(service=service, options=options)
    _driver_instance.set_page_load_timeout(_page_load_timeout)
    _driver_instance.implicitly_wait(_wait_timeout)
    _driver_instance.get(url)


@allure.step("Open web browser with URL: {url} and maximize window")
def open_browser_maximized(url: str):
    """I open web browser with {url} and maximise window"""
    open_browser(url)
    _get_driver().maximize_window()


@allure.step("Open web browser with URL: {url} and take screenshot")
def open_browser_with_screenshot(url: str):
    """I open web browser with {url} and take screenshot"""
    open_browser(url)
    _attach_screenshot("Browser Opened")


@allure.step("Open web browser with URL: {url}, maximize window and take screenshot")
def open_browser_maximized_with_screenshot(url: str):
    """I open the web browser with {url} maximise window and take screenshot"""
    open_browser_maximized(url)
    _attach_screenshot("Browser Opened - Maximized")


@allure.step("Click on element: {locator}")
def click_element(locator: str):
    """I click on {locator}"""
    element = _find_element(locator)
    element.click()


@allure.step("Fill value '{value}' into {locator}")
def fill_text(locator: str, value: str):
    """I fill {value} into {locator}"""
    element = _find_element(locator)
    element.send_keys(value)


@allure.step("Clear and fill '{value}' into {locator}")
def clear_and_fill(locator: str, value: str):
    """I clear and fill {value} into {locator}"""
    element = _find_element(locator)
    element.clear()
    element.send_keys(value)


@allure.step("Wait for {secs} seconds")
def wait_seconds(secs: int):
    """I wait for {secs} seconds"""
    time.sleep(secs)


@allure.step("Take screenshot")
def take_screenshot():
    """I take screenshot"""
    _attach_screenshot("Manual Screenshot")


@allure.step("Take screenshot with comment: {comment}")
def take_screenshot_with_comment(comment: str):
    """I take screenshot with comment {comment}"""
    _attach_screenshot(f"Screenshot - {comment}")


@allure.step("Verify element {locator} is present")
def verify_element_present(locator: str) -> bool:
    """I verify {locator} is present"""
    try:
        _find_element(locator)
        return True
    except NoSuchElementException:
        return False


@allure.step("Verify element {locator} text is '{text}'")
def verify_element_text_is(locator: str, text: str) -> bool:
    """I verify {locator} text is {text}"""
    try:
        element = _find_element(locator)
        actual_text = element.text
        result = actual_text == text
        allure.attach(f"Expected: {text}\nActual: {actual_text}\nMatch: {result}", 
                     name="Text Verification", attachment_type=allure.attachment_type.TEXT)
        return result
    except NoSuchElementException:
        return False


@allure.step("Assert element {locator} is present")
def assert_element_present(locator: str):
    """I assert {locator} is present"""
    if not verify_element_present(locator):
        raise AssertionError(f"Element not present: {locator}")


@allure.step("Assert element {locator} text is '{text}'")
def assert_element_text_is(locator: str, text: str):
    """I assert {locator} text is {text}"""
    if not verify_element_text_is(locator, text):
        element = _find_element(locator)
        actual_text = element.text
        raise AssertionError(f"Text mismatch. Expected: '{text}', Actual: '{actual_text}'")


@allure.step("Wait until element {locator} is visible")
def wait_until_element_visible(locator: str, timeout: int = None):
    """I wait until element or field {locator} is visible"""
    timeout = timeout or _wait_timeout
    if locator.startswith("xpath="):
        condition = EC.visibility_of_element_located((By.XPATH, locator.replace("xpath=", "")))
    else:
        condition = EC.visibility_of_element_located((By.XPATH, locator))
    WebDriverWait(_get_driver(), timeout).until(condition)


@allure.step("Scroll to element: {locator}")
def scroll_to_element(locator: str):
    """I scroll to an element {locator}"""
    element = _find_element(locator)
    _get_driver().execute_script("arguments[0].scrollIntoView(true);", element)


@allure.step("Close web browser")
def close_browser():
    """I close web browser"""
    global _driver_instance
    if _driver_instance:
        _driver_instance.quit()
        _driver_instance = None


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_variable(name: str) -> Any:
    """Get stored variable value"""
    global _variables
    return _variables.get(name)


def clear_variables():
    """Clear all stored variables"""
    global _variables
    _variables.clear()


def set_wait_timeout(timeout: int):
    """Set default wait timeout"""
    global _wait_timeout
    _wait_timeout = timeout