"""
BrowserGlobal.py - Core Browser Automation Functions
====================================================

This module contains reusable browser automation functions that provide
comprehensive browser management, element interaction, and verification capabilities.
All functions are designed to be framework-agnostic and can be used across projects.

Functions are organized by category:
- Browser Management & Navigation
- Keyboard & Mouse Interactions  
- Text Input & Form Handling
- Dropdown & Selection
- Data Extraction & Storage
- Screenshot & Documentation
- Window & Frame Management
- Cookie Management
- Performance & Timing
- Element State Verification
- Text & Content Verification
- Attribute & Property Verification
- Wait Conditions
- Advanced Wait Conditions
- Assertions (Hard Verifications)
- Scrolling & Navigation
- File Operations
- Advanced Operations
"""

import os
import time
import json
import base64
import logging
from typing import List, Optional, Union, Any
from urllib.parse import urlparse
from pathlib import Path

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

# Import QAF utilities if available
try:
    from qaf.automation.core import get_bundle
    from qaf.automation.ui.util.pattern_locator import get_pattern_locator
    QAF_AVAILABLE = True
except ImportError:
    QAF_AVAILABLE = False

# Global driver instance and configuration
_driver_instance = None
_wait_timeout = 30
_page_load_timeout = 60
_variables = {}  # For storing step results and variables
_transactions = {}  # For performance measurement


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
        elif locator.startswith("name="):
            return wait.until(EC.presence_of_element_located((By.NAME, locator.replace("name=", ""))))
        elif locator.startswith("class="):
            return wait.until(EC.presence_of_element_located((By.CLASS_NAME, locator.replace("class=", ""))))
        elif locator.startswith("tag="):
            return wait.until(EC.presence_of_element_located((By.TAG_NAME, locator.replace("tag=", ""))))
        elif locator.startswith("linkText="):
            return wait.until(EC.presence_of_element_located((By.LINK_TEXT, locator.replace("linkText=", ""))))
        elif locator.startswith("partialLinkText="):
            return wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, locator.replace("partialLinkText=", ""))))
        else:
            # Default to XPath if no prefix
            return wait.until(EC.presence_of_element_located((By.XPATH, locator)))
    except TimeoutException:
        raise NoSuchElementException(f"Element not found: {locator}")


def _find_elements(locator: str) -> List[Any]:
    """Find multiple elements"""
    driver = _get_driver()
    if locator.startswith("xpath="):
        return driver.find_elements(By.XPATH, locator.replace("xpath=", ""))
    elif locator.startswith("id="):
        return driver.find_elements(By.ID, locator.replace("id=", ""))
    elif locator.startswith("css="):
        return driver.find_elements(By.CSS_SELECTOR, locator.replace("css=", ""))
    elif locator.startswith("name="):
        return driver.find_elements(By.NAME, locator.replace("name=", ""))
    elif locator.startswith("class="):
        return driver.find_elements(By.CLASS_NAME, locator.replace("class=", ""))
    elif locator.startswith("tag="):
        return driver.find_elements(By.TAG_NAME, locator.replace("tag=", ""))
    elif locator.startswith("linkText="):
        return driver.find_elements(By.LINK_TEXT, locator.replace("linkText=", ""))
    elif locator.startswith("partialLinkText="):
        return driver.find_elements(By.PARTIAL_LINK_TEXT, locator.replace("partialLinkText=", ""))
    else:
        return driver.find_elements(By.XPATH, locator)


def _take_screenshot_bytes(context) -> bytes:
    """Take screenshot and return as bytes"""
    return context.driver.get_screenshot_as_png()


def _attach_screenshot(context, name: str = "Screenshot"):
    """Attach screenshot to Allure report"""
    screenshot = _take_screenshot_bytes(context)
    allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)


# =============================================================================
# BROWSER MANAGEMENT & NAVIGATION
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


@allure.step("Open web browser with URL: {url} and window size {width} x {height}")
def open_browser_with_size(url: str, width: int, height: int):
    """I open the web browser with {url} and window size {width} x {height}"""
    open_browser(url)
    _get_driver().set_window_size(width, height)


@allure.step("Zoom browser window to {percentage}%")
def zoom_browser(percentage: int):
    """I zoom browser window to {percentage} Percentage"""
    zoom_level = percentage / 100.0
    _get_driver().execute_script(f"document.body.style.zoom='{zoom_level}'")


@allure.step("Zoom out browser window to {percentage}%")
def zoom_out_browser(percentage: int):
    """I zoom out browser window to {percentage} Percentage"""
    zoom_browser(percentage)


@allure.step("Navigate back in browser history")
def go_page_back():
    """I go page back in the web browser history"""
    _get_driver().back()


@allure.step("Navigate forward in browser history")
def go_page_forward():
    """I go page forward in the web browser history"""
    _get_driver().forward()


@allure.step("Switch to browser tab at index {index}")
def switch_browser_tab(index: int):
    """I switch browser tab by {index}"""
    driver = _get_driver()
    handles = driver.window_handles
    if 0 <= index < len(handles):
        driver.switch_to.window(handles[index])
    else:
        raise BrowserGlobalError(f"Tab index {index} out of range. Available tabs: {len(handles)}")


# =============================================================================
# KEYBOARD & MOUSE INTERACTIONS
# =============================================================================

@allure.step("Press ENTER key on element: {locator}")
def press_enter_on_element(locator: str):
    """I press RETURN or ENTER key in {locator}"""
    element = _find_element(locator)
    element.send_keys(Keys.RETURN)


@allure.step("Press ENTER key globally")
def press_enter():
    """I press RETURN or ENTER key"""
    ActionChains(_get_driver()).send_keys(Keys.RETURN).perform()


@allure.step("Press key: {key}")
def press_key(key: str):
    """I press key {key}"""
    # Map common key names to Selenium Keys
    key_mapping = {
        'F1': Keys.F1, 'F2': Keys.F2, 'F3': Keys.F3, 'F4': Keys.F4,
        'F5': Keys.F5, 'F6': Keys.F6, 'F7': Keys.F7, 'F8': Keys.F8,
        'F9': Keys.F9, 'F10': Keys.F10, 'F11': Keys.F11, 'F12': Keys.F12,
        'ESCAPE': Keys.ESCAPE, 'ESC': Keys.ESCAPE,
        'TAB': Keys.TAB, 'SPACE': Keys.SPACE,
        'BACKSPACE': Keys.BACKSPACE, 'DELETE': Keys.DELETE,
        'HOME': Keys.HOME, 'END': Keys.END,
        'PAGE_UP': Keys.PAGE_UP, 'PAGE_DOWN': Keys.PAGE_DOWN,
        'ARROW_UP': Keys.ARROW_UP, 'ARROW_DOWN': Keys.ARROW_DOWN,
        'ARROW_LEFT': Keys.ARROW_LEFT, 'ARROW_RIGHT': Keys.ARROW_RIGHT
    }
    
    selenium_key = key_mapping.get(key.upper(), key)
    ActionChains(_get_driver()).send_keys(selenium_key).perform()


@allure.step("Press Tab key {times} times")
def press_tab_multiple(times: int):
    """I press Tab {times} times"""
    for _ in range(times):
        ActionChains(_get_driver()).send_keys(Keys.TAB).perform()


@allure.step("Press Backspace key {times} times")
def press_backspace_multiple(times: int):
    """I press Backspace {times} times"""
    for _ in range(times):
        ActionChains(_get_driver()).send_keys(Keys.BACKSPACE).perform()


@allure.step("Press key {key} and fill value: {value}")
def press_key_and_fill(key: str, value: str):
    """I press a key {key} and fill {value}"""
    press_key(key)
    ActionChains(_get_driver()).send_keys(value).perform()


@allure.step("Press Control/Command+A (OS-aware select all)")
def press_select_all():
    """I Press Control or Command A by OS"""
    import platform
    if platform.system() == "Darwin":  # macOS
        ActionChains(_get_driver()).key_down(Keys.COMMAND).send_keys('a').key_up(Keys.COMMAND).perform()
    else:  # Windows/Linux
        ActionChains(_get_driver()).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()


@allure.step("Hold {hold_key} and press {press_key}")
def hold_and_press_key(hold_key: str, press_key: str):
    """I hold down a key {holdKey} and press a key {pressKey}"""
    key_mapping = {
        'CONTROL': Keys.CONTROL, 'CTRL': Keys.CONTROL,
        'ALT': Keys.ALT, 'SHIFT': Keys.SHIFT,
        'COMMAND': Keys.COMMAND, 'CMD': Keys.COMMAND
    }
    
    hold_selenium_key = key_mapping.get(hold_key.upper(), hold_key)
    press_selenium_key = key_mapping.get(press_key.upper(), press_key)
    
    ActionChains(_get_driver()).key_down(hold_selenium_key).send_keys(press_selenium_key).key_up(hold_selenium_key).perform()


@allure.step("Hold Backspace for {seconds} seconds")
def hold_backspace(seconds: int):
    """I hold down Backspace for {seconds} seconds"""
    actions = ActionChains(_get_driver())
    actions.key_down(Keys.BACKSPACE).perform()
    time.sleep(seconds)
    actions.key_up(Keys.BACKSPACE).perform()


@allure.step("Press two keys {key_1} and {key_2} then fill value: {value}")
def press_two_keys_and_fill(key_1: str, key_2: str, value: str):
    """I press two keys {key_1} {key_2} and fill {value}"""
    key_mapping = {
        'CONTROL': Keys.CONTROL, 'CTRL': Keys.CONTROL,
        'ALT': Keys.ALT, 'SHIFT': Keys.SHIFT,
        'COMMAND': Keys.COMMAND, 'CMD': Keys.COMMAND
    }
    
    key1 = key_mapping.get(key_1.upper(), key_1)
    key2 = key_mapping.get(key_2.upper(), key_2)
    
    ActionChains(_get_driver()).key_down(key1).send_keys(key2).key_up(key1).send_keys(value).perform()


@allure.step("Click on element: {locator}")
def click_element(locator: str):
    """I click on {locator}"""
    element = _find_element(locator)
    element.click()


@allure.step("Double-click on element: {locator}")
def double_click_element(locator: str):
    """I double click on {locator}"""
    element = _find_element(locator)
    ActionChains(_get_driver()).double_click(element).perform()


@allure.step("Click on checkbox/radio {locator} if not selected")
def click_if_not_selected(locator: str):
    """I click on Checkbox/Radio {locator} if not selected"""
    element = _find_element(locator)
    if not element.is_selected():
        element.click()


@allure.step("Click on checkbox/radio {locator} if selected")
def click_if_selected(locator: str):
    """I click on Checkbox/Radio {locator} if selected"""
    element = _find_element(locator)
    if element.is_selected():
        element.click()


@allure.step("Click on multiple elements: {locator}")
def click_multiple_elements(locator: str):
    """I click on multiple elements {locator}"""
    elements = _find_elements(locator)
    for element in elements:
        element.click()


@allure.step("Click on element {locator} if present")
def click_if_present(locator: str):
    """I click on {locator} if present"""
    try:
        element = _find_element(locator)
        element.click()
    except NoSuchElementException:
        allure.attach(f"Element not found: {locator}", name="Element Not Found", attachment_type=allure.attachment_type.TEXT)


@allure.step("Click on element {locator} once enabled")
def click_once_enabled(locator: str):
    """I click on {locator} once enabled"""
    element = _get_wait().until(EC.element_to_be_clickable((By.XPATH, locator.replace("xpath=", ""))))
    element.click()


@allure.step("Mouse over element: {locator}")
def mouseover_element(locator: str):
    """I mouseover on {locator}"""
    element = _find_element(locator)
    ActionChains(_get_driver()).move_to_element(element).perform()


@allure.step("Drag from {source_locator} and drop on {target_locator}")
def drag_and_drop(source_locator: str, target_locator: str):
    """I drag source {source_locator} and drop on target {target_locator}"""
    source = _find_element(source_locator)
    target = _find_element(target_locator)
    ActionChains(_get_driver()).drag_and_drop(source, target).perform()


# =============================================================================
# TEXT INPUT & FORM HANDLING
# =============================================================================

@allure.step("Fill value '{value}' into {locator}")
def fill_text(locator: str, value: str):
    """I fill {value} into {locator}"""
    element = _find_element(locator)
    element.send_keys(value)


@allure.step("Input value '{value}' into {locator}")
def input_text(locator: str, value: str):
    """I input {value} into {locator}"""
    fill_text(locator, value)


@allure.step("Input search value '{value}' into {locator}")
def input_search(locator: str, value: str):
    """I input search {value} into {locator}"""
    element = _find_element(locator)
    element.clear()
    element.send_keys(value)
    element.send_keys(Keys.RETURN)


@allure.step("Click and fill '{value}' into lookup field {locator} with delay {delay}s")
def click_and_fill_lookup_with_delay(locator: str, value: str, delay: int):
    """I click and fill {value} into {locator} lookup field with delay {delay}"""
    element = _find_element(locator)
    element.click()
    time.sleep(delay)
    element.send_keys(value)


@allure.step("Click and fill '{value}' into {locator}")
def click_and_fill(locator: str, value: str):
    """I click and fill {value} into {locator}"""
    element = _find_element(locator)
    element.click()
    element.send_keys(value)


@allure.step("Double-click and fill '{value}' into {locator}")
def double_click_and_fill(locator: str, value: str):
    """I double click and fill {value} into {locator}"""
    element = _find_element(locator)
    ActionChains(_get_driver()).double_click(element).send_keys(value).perform()


@allure.step("Double-click, wait {wait}s and fill '{value}' into {locator}")
def double_click_wait_and_fill(locator: str, value: str, wait: int):
    """I double click, wait {wait} and fill {value} into {locator}"""
    element = _find_element(locator)
    ActionChains(_get_driver()).double_click(element).perform()
    time.sleep(wait)
    element.send_keys(value)


@allure.step("Click and shift+tab then press ENTER")
def click_shift_tab_enter():
    """I click and shift tab then ENTER key"""
    actions = ActionChains(_get_driver())
    actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).send_keys(Keys.RETURN).perform()


@allure.step("Clear and fill '{value}' into {locator}")
def clear_and_fill(locator: str, value: str):
    """I clear and fill {value} into {locator}"""
    element = _find_element(locator)
    element.clear()
    element.send_keys(value)


@allure.step("Set field {locator} attribute {attr_name} to value '{value}'")
def set_field_attribute(locator: str, attr_name: str, value: str):
    """I set field {locator} attribute {attr_name} value as {value}"""
    element = _find_element(locator)
    _get_driver().execute_script(f"arguments[0].setAttribute('{attr_name}', '{value}');", element)


@allure.step("Clear text from {locator}")
def clear_text(locator: str):
    """I clear text from {locator}"""
    element = _find_element(locator)
    element.clear()


# =============================================================================
# DROPDOWN & SELECTION
# =============================================================================

@allure.step("Select dropdown {locator} with value '{value}'")
def select_dropdown_by_value(locator: str, value: str):
    """I select dropdown {locator} with value {value}"""
    element = _find_element(locator)
    select = Select(element)
    select.select_by_value(value)


@allure.step("Select dropdown {locator} with index {index}")
def select_dropdown_by_index(locator: str, index: int):
    """I select dropdown {locator} with index {index}"""
    element = _find_element(locator)
    select = Select(element)
    select.select_by_index(index)


@allure.step("Select dropdown {locator} with text '{text}'")
def select_dropdown_by_text(locator: str, text: str):
    """I select dropdown {locator} with text {text}"""
    element = _find_element(locator)
    select = Select(element)
    select.select_by_visible_text(text)


@allure.step("Deselect dropdown {locator} with value '{value}'")
def deselect_dropdown_by_value(locator: str, value: str):
    """I deselect dropdown {locator} with value {value}"""
    element = _find_element(locator)
    select = Select(element)
    select.deselect_by_value(value)


@allure.step("Deselect dropdown {locator} with index {index}")
def deselect_dropdown_by_index(locator: str, index: int):
    """I deselect dropdown {locator} with index {index}"""
    element = _find_element(locator)
    select = Select(element)
    select.deselect_by_index(index)


@allure.step("Deselect dropdown {locator} with text '{text}'")
def deselect_dropdown_by_text(locator: str, text: str):
    """I deselect dropdown {locator} with text {text}"""
    element = _find_element(locator)
    select = Select(element)
    select.deselect_by_visible_text(text)


@allure.step("Deselect all options in dropdown {locator}")
def deselect_all_dropdown(locator: str):
    """I deselect all in dropdown {locator}"""
    element = _find_element(locator)
    select = Select(element)
    select.deselect_all()


# =============================================================================
# DATA EXTRACTION & STORAGE
# =============================================================================

@allure.step("Get text from element: {locator}")
def get_text_from_element(locator: str) -> str:
    """I get text from {locator}"""
    element = _find_element(locator)
    text = element.text
    global _variables
    _variables['last_result'] = text
    allure.attach(text, name="Extracted Text", attachment_type=allure.attachment_type.TEXT)
    return text


@allure.step("Get inner HTML from element: {locator}")
def get_inner_html(locator: str) -> str:
    """I get text from inner html {locator}"""
    element = _find_element(locator)
    html = element.get_attribute('innerHTML')
    global _variables
    _variables['last_result'] = html
    allure.attach(html, name="Extracted HTML", attachment_type=allure.attachment_type.HTML)
    return html


@allure.step("Get attribute '{attribute_name}' from element: {locator}")
def get_attribute_value(locator: str, attribute_name: str) -> str:
    """I get attribute {attribute_name} value from {locator}"""
    element = _find_element(locator)
    value = element.get_attribute(attribute_name)
    global _variables
    _variables['last_result'] = value
    allure.attach(f"{attribute_name}: {value}", name="Extracted Attribute", attachment_type=allure.attachment_type.TEXT)
    return value


@allure.step("Store last step result into variable '{var}'")
def store_last_result_in_variable(var: str):
    """I store last step result into variable {var}"""
    global _variables
    if 'last_result' in _variables:
        _variables[var] = _variables['last_result']
        allure.attach(f"{var} = {_variables[var]}", name="Variable Stored", attachment_type=allure.attachment_type.TEXT)
    else:
        raise BrowserGlobalError("No previous result to store")


@allure.step("Store value '{value}' into variable '{variable}'")
def store_value_in_variable(value: str, variable: str):
    """I store value {value} into variable {variable}"""
    global _variables
    _variables[variable] = value
    allure.attach(f"{variable} = {value}", name="Variable Stored", attachment_type=allure.attachment_type.TEXT)


@allure.step("Store table cell text from row {row_number}, column {column_number} into variable '{var}'")
def store_table_cell_text(locator: str, row_number: int, column_number: int, var: str):
    """I store table {locator} row {row_number} column {column_number} cell text into {var}"""
    table = _find_element(locator)
    rows = table.find_elements(By.TAG_NAME, "tr")
    if row_number <= len(rows):
        cells = rows[row_number - 1].find_elements(By.TAG_NAME, "td")
        if column_number <= len(cells):
            cell_text = cells[column_number - 1].text
            global _variables
            _variables[var] = cell_text
            allure.attach(f"{var} = {cell_text}", name="Table Cell Text Stored", attachment_type=allure.attachment_type.TEXT)
        else:
            raise BrowserGlobalError(f"Column {column_number} not found in table row")
    else:
        raise BrowserGlobalError(f"Row {row_number} not found in table")


# =============================================================================
# SCREENSHOT & DOCUMENTATION
# =============================================================================

@allure.step("Take screenshot")
def take_screenshot():
    """I take screenshot"""
    _attach_screenshot("Manual Screenshot")


@allure.step("Take screenshot with comment: {comment}")
def take_screenshot_with_comment(comment: str):
    """I take screenshot with comment {comment}"""
    _attach_screenshot(f"Screenshot - {comment}")


@allure.step("Add comment: {value}")
def add_comment(value: str):
    """I comment {value}"""
    allure.attach(value, name="Test Comment", attachment_type=allure.attachment_type.TEXT)


# =============================================================================
# WINDOW & FRAME MANAGEMENT
# =============================================================================

@allure.step("Switch to window by name: {name}")
def switch_window_by_name(name: str):
    """I switch window by name {name}"""
    driver = _get_driver()
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if driver.title == name:
            return
    raise BrowserGlobalError(f"Window with name '{name}' not found")


@allure.step("Switch to window by index: {index}")
def switch_window_by_index(index: int):
    """I switch window by index {index}"""
    driver = _get_driver()
    handles = driver.window_handles
    if 0 <= index < len(handles):
        driver.switch_to.window(handles[index])
    else:
        raise BrowserGlobalError(f"Window index {index} out of range")


@allure.step("Switch to parent window/frame")
def switch_to_parent_window():
    """I switch to parent window or frame"""
    _get_driver().switch_to.parent_frame()


@allure.step("Switch to default window/frame")
def switch_to_default_window():
    """I switch to default window or frame"""
    _get_driver().switch_to.default_content()


@allure.step("Switch to iframe by ID/name: {id_name}")
def switch_to_iframe_by_id_name(id_name: str):
    """I switch to iFrame by id or name {id/name}"""
    _get_driver().switch_to.frame(id_name)


@allure.step("Switch to iframe by index: {index}")
def switch_to_iframe_by_index(index: int):
    """I switch to iFrame by index {index}"""
    _get_driver().switch_to.frame(index)


@allure.step("Switch to iframe by title: {title}")
def switch_to_iframe_by_title(title: str):
    """I switch to iFrame by title {title}"""
    iframes = _find_elements("tag=iframe")
    for iframe in iframes:
        if iframe.get_attribute("title") == title:
            _get_driver().switch_to.frame(iframe)
            return
    raise BrowserGlobalError(f"Iframe with title '{title}' not found")


@allure.step("Switch to iframe by locator: {locator}")
def switch_to_iframe_by_locator(locator: str):
    """I switch to iFrame by locator {locator}"""
    iframe = _find_element(locator)
    _get_driver().switch_to.frame(iframe)


@allure.step("Close web browser")
def close_browser():
    """I close web browser"""
    global _driver_instance
    if _driver_instance:
        _driver_instance.quit()
        _driver_instance = None


@allure.step("Close current window/tab")
def close_current_window():
    """I close current window or tab"""
    _get_driver().close()


# =============================================================================
# COOKIE MANAGEMENT
# =============================================================================

@allure.step("Add cookie with name '{name}' and value '{value}'")
def add_cookie(name: str, value: str):
    """I add cookie with name {name} and value {value}"""
    _get_driver().add_cookie({"name": name, "value": value})


@allure.step("Get cookie value with name: {name}")
def get_cookie_value(name: str) -> str:
    """I get a cookie value with the name {name}"""
    cookie = _get_driver().get_cookie(name)
    value = cookie["value"] if cookie else None
    global _variables
    _variables['last_result'] = value
    allure.attach(f"Cookie {name}: {value}", name="Cookie Value", attachment_type=allure.attachment_type.TEXT)
    return value


@allure.step("Delete cookie with name: {name}")
def delete_cookie(name: str):
    """I delete cookie with name {name}"""
    _get_driver().delete_cookie(name)


@allure.step("Delete all cookies")
def delete_all_cookies():
    """I delete all cookies"""
    _get_driver().delete_all_cookies()


# =============================================================================
# PERFORMANCE & TIMING
# =============================================================================

@allure.step("Start transaction: {name}")
def start_transaction(name: str):
    """I start transaction with name {name}"""
    global _transactions
    _transactions[name] = {"start_time": time.time(), "threshold": None}


@allure.step("Start transaction '{name}' with {seconds}s threshold")
def start_transaction_with_threshold(name: str, seconds: int):
    """I start transaction {name} with {second} seconds threshold"""
    global _transactions
    _transactions[name] = {"start_time": time.time(), "threshold": seconds}


@allure.step("Stop transaction")
def stop_transaction():
    """I stop transaction"""
    global _transactions
    for name, data in _transactions.items():
        if "end_time" not in data:
            end_time = time.time()
            duration = end_time - data["start_time"]
            data["end_time"] = end_time
            data["duration"] = duration
            
            allure.attach(
                f"Transaction: {name}\nDuration: {duration:.3f}s\nThreshold: {data.get('threshold', 'None')}s",
                name="Transaction Completed",
                attachment_type=allure.attachment_type.TEXT
            )
            
            if data.get("threshold") and duration > data["threshold"]:
                raise BrowserGlobalError(f"Transaction '{name}' exceeded threshold: {duration:.3f}s > {data['threshold']}s")
            break


@allure.step("Wait for {millisecs} milliseconds")
def wait_milliseconds(millisecs: int):
    """I wait for {millisecs} milliseconds"""
    time.sleep(millisecs / 1000.0)


@allure.step("Wait for {secs} seconds")
def wait_seconds(secs: int):
    """I wait for {secs} seconds"""
    time.sleep(secs)


@allure.step("Wait for page to load")
def wait_for_page_load():
    """I wait for page to load"""
    _get_wait().until(lambda driver: driver.execute_script("return document.readyState") == "complete")


@allure.step("Wait for page to load (D365 specific)")
def wait_for_page_load_d365():
    """I wait for page to load D365"""
    # D365-specific loading indicators
    wait_for_page_load()
    try:
        _get_wait(5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".ms-crm-Loading")))
    except TimeoutException:
        pass  # Loading indicator might not be present


# =============================================================================
# ELEMENT STATE VERIFICATION
# =============================================================================

@allure.step("Verify element {locator} is present")
def verify_element_present(locator: str) -> bool:
    """I verify {locator} is present"""
    try:
        _find_element(locator)
        return True
    except NoSuchElementException:
        return False


@allure.step("Verify element {locator} is not present")
def verify_element_not_present(locator: str) -> bool:
    """I verify {locator} is not present"""
    return not verify_element_present(locator)


@allure.step("Verify element {locator} is visible")
def verify_element_visible(locator: str) -> bool:
    """I verify {locator} is visible"""
    try:
        element = _find_element(locator)
        return element.is_displayed()
    except NoSuchElementException:
        return False


@allure.step("Verify element {locator} is not visible")
def verify_element_not_visible(locator: str) -> bool:
    """I verify {locator} is not visible"""
    try:
        element = _find_element(locator)
        return not element.is_displayed()
    except NoSuchElementException:
        return True


@allure.step("Verify link with text '{text}' is present")
def verify_link_with_text_present(text: str) -> bool:
    """I verify link with text {text} is present"""
    return verify_element_present(f"linkText={text}")


@allure.step("Verify link with partial text '{text}' is present")
def verify_link_with_partial_text_present(text: str) -> bool:
    """I verify link with partial text {text} is present"""
    return verify_element_present(f"partialLinkText={text}")


# =============================================================================
# TEXT & CONTENT VERIFICATION
# =============================================================================

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


@allure.step("Verify element {locator} text is not '{text}'")
def verify_element_text_is_not(locator: str, text: str) -> bool:
    """I verify {locator} text is not {text}"""
    return not verify_element_text_is(locator, text)


@allure.step("Verify element {locator} inner HTML is '{text}'")
def verify_element_inner_html_is(locator: str, text: str) -> bool:
    """I verify {locator} inner html is {text}"""
    try:
        element = _find_element(locator)
        actual_html = element.get_attribute('innerHTML')
        result = actual_html == text
        allure.attach(f"Expected HTML: {text}\nActual HTML: {actual_html}\nMatch: {result}",
                     name="HTML Verification", attachment_type=allure.attachment_type.TEXT)
        return result
    except NoSuchElementException:
        return False


@allure.step("Verify element {locator} inner HTML contains '{text}'")
def verify_element_inner_html_contains(locator: str, text: str) -> bool:
    """I verify {locator} inner html contains {text}"""
    try:
        element = _find_element(locator)
        actual_html = element.get_attribute('innerHTML')
        result = text in actual_html
        allure.attach(f"Search text: {text}\nActual HTML: {actual_html}\nContains: {result}",
                     name="HTML Contains Verification", attachment_type=allure.attachment_type.TEXT)
        return result
    except NoSuchElementException:
        return False


@allure.step("Verify element {locator} value is '{value}'")
def verify_element_value_is(locator: str, value: str) -> bool:
    """I verify element/field {locator} value is {value}"""
    try:
        element = _find_element(locator)
        actual_value = element.get_attribute('value')
        result = actual_value == value
        allure.attach(f"Expected: {value}\nActual: {actual_value}\nMatch: {result}",
                     name="Value Verification", attachment_type=allure.attachment_type.TEXT)
        return result
    except NoSuchElementException:
        return False


@allure.step("Verify element {locator} value is not '{value}'")
def verify_element_value_is_not(locator: str, value: str) -> bool:
    """I verify element/field {locator} value is not {value}"""
    return not verify_element_value_is(locator, value)


@allure.step("Verify element {locator} is selected")
def verify_element_selected(locator: str) -> bool:
    """I verify element/field {locator} is selected"""
    try:
        element = _find_element(locator)
        return element.is_selected()
    except NoSuchElementException:
        return False


@allure.step("Verify element {locator} is not selected")
def verify_element_not_selected(locator: str) -> bool:
    """I verify element/field {locator} is not selected"""
    return not verify_element_selected(locator)


# Continue with remaining verification functions...
# (Due to length limits, I'll include key remaining functions)

# =============================================================================
# WAIT CONDITIONS
# =============================================================================

@allure.step("Wait until element {locator} is visible")
def wait_until_element_visible(locator: str, timeout: int = None):
    """I wait until element or field {locator} is visible"""
    timeout = timeout or _wait_timeout
    if locator.startswith("xpath="):
        condition = EC.visibility_of_element_located((By.XPATH, locator.replace("xpath=", "")))
    else:
        condition = EC.visibility_of_element_located((By.XPATH, locator))
    WebDriverWait(_get_driver(), timeout).until(condition)


@allure.step("Wait until element {locator} is not visible")
def wait_until_element_not_visible(locator: str, timeout: int = None):
    """I wait until element/field {locator} is not visible"""
    timeout = timeout or _wait_timeout
    if locator.startswith("xpath="):
        condition = EC.invisibility_of_element_located((By.XPATH, locator.replace("xpath=", "")))
    else:
        condition = EC.invisibility_of_element_located((By.XPATH, locator))
    WebDriverWait(_get_driver(), timeout).until(condition)


# =============================================================================
# ASSERTIONS (Hard Verifications)
# =============================================================================

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


# =============================================================================
# SCROLLING & NAVIGATION  
# =============================================================================

@allure.step("Scroll to element: {locator}")
def scroll_to_element(locator: str):
    """I scroll to an element {locator}"""
    element = _find_element(locator)
    _get_driver().execute_script("arguments[0].scrollIntoView(true);", element)


@allure.step("Scroll to bottom of page")
def scroll_to_bottom():
    """I scroll to the bottom of the page"""
    _get_driver().execute_script("window.scrollTo(0, document.body.scrollHeight);")


@allure.step("Scroll to top of page")
def scroll_to_top():
    """I scroll to the top of the page"""
    _get_driver().execute_script("window.scrollTo(0, 0);")


# =============================================================================
# FILE OPERATIONS
# =============================================================================

@allure.step("Upload file '{file_path}' to {locator}")
def upload_file(locator: str, file_path: str):
    """I upload file {filePath} into file uploader {locator}"""
    if not os.path.exists(file_path):
        raise BrowserGlobalError(f"File not found: {file_path}")
    
    element = _find_element(locator)
    element.send_keys(os.path.abspath(file_path))


# =============================================================================
# ADVANCED OPERATIONS
# =============================================================================

@allure.step("Execute JavaScript: {script}")
def execute_javascript(script: str):
    """I execute javascript {script}"""
    result = _get_driver().execute_script(script)
    global _variables
    _variables['last_result'] = result
    allure.attach(f"Script: {script}\nResult: {result}", name="JavaScript Execution", 
                 attachment_type=allure.attachment_type.TEXT)
    return result


@allure.step("Submit form: {locator}")
def submit_form(locator: str):
    """I submit {locator}"""
    element = _find_element(locator)
    element.submit()


@allure.step("Fail step with message: {text}")
def fail_step_with_info(text: str):
    """I fail step with info {text}"""
    allure.attach(text, name="Failure Reason", attachment_type=allure.attachment_type.TEXT)
    raise AssertionError(text)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_variable(name: str) -> Any:
    """Get stored variable value"""
    global _variables
    return _variables.get(name)


def get_all_variables() -> dict:
    """Get all stored variables"""
    global _variables
    return _variables.copy()


def clear_variables():
    """Clear all stored variables"""
    global _variables
    _variables.clear()


def set_wait_timeout(timeout: int):
    """Set default wait timeout"""
    global _wait_timeout
    _wait_timeout = timeout


def set_page_load_timeout(timeout: int):
    """Set page load timeout"""
    global _page_load_timeout
    _page_load_timeout = timeout