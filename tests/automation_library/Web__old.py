"""
Web.py - Pattern-Based Web Automation Functions
===============================================

This module contains reusable web automation functions that leverage the QAF pattern 
locator system for dynamic element identification. These functions provide enhanced 
web interaction capabilities with pattern-based element resolution.

Functions are organized by category:
- Browser & Page Operations
- Pattern-Based Element Interactions
- Text Input Operations  
- Mouse Interactions
- Verification & Validation
- Page Header & Title Operations
- Frame & Window Management
- Data Management
- Advanced Pattern Operations
- Timing & Synchronization
- File Operations
- Dropdown Operations
- Utility Functions
"""

import os
import time
import json
import logging
from typing import List, Optional, Union, Any, Dict
from datetime import datetime

import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementNotInteractableException,
    StaleElementReferenceException, WebDriverException
)

# Import QAF system (pattern locator temporarily disabled for new implementation)
try:
    from qaf.automation.core import get_bundle
    from qaf.automation.ui.BrowserGlobal import _get_driver, _get_wait, _attach_screenshot
    QAF_AVAILABLE = True
except ImportError:
    QAF_AVAILABLE = False

# Pattern locator temporarily disabled for new implementation
get_pattern_locator = None

# Global data storage for Web module
_page_context = {}
_field_locations = {}
_execution_datetime = None


class WebError(Exception):
    """Custom exception for Web operations"""
    pass


def _get_pattern_locator():
    """Get QAF pattern locator instance"""
    if not QAF_AVAILABLE:
        raise WebError("QAF Pattern Locator system not available")
    return get_pattern_locator()


def _find_element_by_pattern(element: str, field: str, page: str = None) -> Any:
    """Find element using QAF pattern locator system"""
    try:
        pattern_locator = _get_pattern_locator()
        page_name = page or _page_context.get('current_page', 'genericPage')
        
        # Map element types to pattern locator methods
        element_methods = {
            'button': pattern_locator.button,
            'link': pattern_locator.link,
            'input': pattern_locator.input,
            'text': pattern_locator.text,
            'div': pattern_locator.element,
            'label': pattern_locator.label,
            'icon': pattern_locator.element,
            'checkbox': pattern_locator.checkbox,
            'dropdown': pattern_locator.select,
            'dropdownitem': pattern_locator.element,
            'element': pattern_locator.element
        }
        
        method = element_methods.get(element.lower())
        if not method:
            raise WebError(f"Unsupported element type: {element}")
        
        # Generate locator using pattern system
        locator = method(page_name, field)
        
        # Handle JSON locator arrays (multiple pattern fallbacks)
        if isinstance(locator, str) and locator.startswith('['):
            locators = json.loads(locator)
            last_exception = None
            
            for loc in locators:
                try:
                    xpath = loc.replace('xpath=', '') if loc.startswith('xpath=') else loc
                    element = _get_driver().find_element(By.XPATH, xpath)
                    allure.attach(f"Pattern found element with: {loc}", name="Pattern Locator Success", 
                                attachment_type=allure.attachment_type.TEXT)
                    return element
                except NoSuchElementException as e:
                    last_exception = e
                    continue
            
            raise last_exception or NoSuchElementException(f"No pattern locator found element: {page_name}.{element}.{field}")
        
        else:
            # Single locator pattern
            xpath = locator.replace('xpath=', '') if locator.startswith('xpath=') else locator
            element_found = _get_driver().find_element(By.XPATH, xpath)
            allure.attach(f"Pattern found element with: {xpath}", name="Pattern Locator Success", 
                        attachment_type=allure.attachment_type.TEXT)
            return element_found
            
    except Exception as e:
        error_msg = f"Pattern locator failed for {page_name}.{element}.{field}: {e}"
        allure.attach(error_msg, name="Pattern Locator Error", attachment_type=allure.attachment_type.TEXT)
        raise WebError(error_msg) from e

def _find_elements_by_pattern(element: str, field: str, page: str = None) -> List[Any]:
    """Find multiple elements using QAF pattern locator system"""
    try:
        pattern_locator = _get_pattern_locator()
        page_name = page or _page_context.get('current_page', 'genericPage')
        
        element_methods = {
            'button': pattern_locator.button,
            'link': pattern_locator.link,
            'input': pattern_locator.input,
            'text': pattern_locator.text,
            'div': pattern_locator.element,
            'label': pattern_locator.label,
            'icon': pattern_locator.element,
            'checkbox': pattern_locator.checkbox,
            'dropdown': pattern_locator.select,
            'element': pattern_locator.element
        }
        
        method = element_methods.get(element.lower())
        if not method:
            raise WebError(f"Unsupported element type: {element}")
        
        locator = method(page_name, field)
        
        if isinstance(locator, str) and locator.startswith('['):
            locators = json.loads(locator)
            for loc in locators:
                try:
                    xpath = loc.replace('xpath=', '') if loc.startswith('xpath=') else loc
                    elements = _get_driver().find_elements(By.XPATH, xpath)
                    if elements:
                        return elements
                except:
                    continue
            return []
        else:
            xpath = locator.replace('xpath=', '') if locator.startswith('xpath=') else locator
            return _get_driver().find_elements(By.XPATH, xpath)
            
    except Exception as e:
        allure.attach(f"Pattern locator failed: {e}", name="Pattern Locator Error", 
                     attachment_type=allure.attachment_type.TEXT)
        return []


# =============================================================================
# BROWSER & PAGE OPERATIONS
# =============================================================================

@allure.step("Verify page contains text: {text}")
def verify_page_contains_text(text: str) -> bool:
    """Web: Verify page contains Text {text}"""
    try:
        page_source = _get_driver().page_source
        result = text in page_source
        allure.attach(f"Search text: {text}\nFound: {result}", name="Page Text Verification", 
                     attachment_type=allure.attachment_type.TEXT)
        return result
    except Exception as e:
        allure.attach(f"Error: {e}", name="Page Text Verification Error", 
                     attachment_type=allure.attachment_type.TEXT)
        return False


@allure.step("Wait for page to load")
def wait_for_page_load():
    """Web: I wait for Page to load"""
    try:
        _get_wait().until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        time.sleep(0.5)  # Small buffer for dynamic content
    except TimeoutException:
        allure.attach("Page load timeout reached", name="Page Load Warning", 
                     attachment_type=allure.attachment_type.TEXT)


@allure.step("Open browser with URL: {url}")
def open_browser_url(url: str):
    """Web: Open-Browser Url:{url}"""
    from qaf.automation.ui.BrowserGlobal import open_browser
    open_browser(url)


@allure.step("Open browser and maximize with URL: {url}")
def open_browser_and_maximize(url: str):
    """Web: Open-Browser-And-Maximise Url:{url}"""
    from qaf.automation.ui.BrowserGlobal import open_browser_maximized
    open_browser_maximized(url)


@allure.step("Open browser with custom size - Width: {width}, Height: {height}, URL: {url}")
def open_browser_with_window_size(width: int, height: int, url: str):
    """Web: Open-Browser-With-Set-Window-Size Width:{width} Height:{height} Url:{url}"""
    from qaf.automation.ui.BrowserGlobal import open_browser_with_size
    open_browser_with_size(url, width, height)


# =============================================================================
# PATTERN-BASED ELEMENT INTERACTIONS
# =============================================================================

@allure.step("Click element using pattern - Element: {pattern}, Field: {field}")
def click_element_pattern(pattern: str, field: str):
    """Web: Click-Element Pattern:{pattern} Field:{field}"""
    element = _find_element_by_pattern(pattern, field)
    element.click()
    _attach_screenshot(f"Clicked {pattern} - {field}")


@allure.step("Click link using pattern - Field: {field}")
def click_link_pattern(field: str):
    """Web: Click-Link Field:{field}"""
    element = _find_element_by_pattern('link', field)
    element.click()
    _attach_screenshot(f"Clicked Link - {field}")


@allure.step("Click button using pattern - Field: {field}")
def click_button_pattern(field: str):
    """Web: Click-Button Field:{field}"""
    element = _find_element_by_pattern('button', field)
    element.click()
    _attach_screenshot(f"Clicked Button - {field}")


@allure.step("Click div using pattern - Field: {field}")
def click_div_pattern(field: str):
    """Web: Click-Div Field:{field}"""
    element = _find_element_by_pattern('div', field)
    element.click()
    _attach_screenshot(f"Clicked Div - {field}")


@allure.step("Click label using pattern - Field: {field}")
def click_label_pattern(field: str):
    """Web: Click-Label Field:{field}"""
    element = _find_element_by_pattern('label', field)
    element.click()
    _attach_screenshot(f"Clicked Label - {field}")


@allure.step("Click icon using pattern - Field: {field}")
def click_icon_pattern(field: str):
    """Web: Click-Icon Field:{field}"""
    element = _find_element_by_pattern('icon', field)
    element.click()
    _attach_screenshot(f"Clicked Icon - {field}")


@allure.step("Click checkbox using pattern - Field: {field}")
def click_checkbox_pattern(field: str):
    """Web: Click-Checkbox Field:{field}"""
    element = _find_element_by_pattern('checkbox', field)
    element.click()
    _attach_screenshot(f"Clicked Checkbox - {field}")


@allure.step("Click dropdown item using pattern - Field: {field}")
def click_dropdown_item_pattern(field: str):
    """Web: Click-DropdownItem Field:{field}"""
    element = _find_element_by_pattern('dropdownitem', field)
    element.click()
    _attach_screenshot(f"Clicked Dropdown Item - {field}")


# =============================================================================
# TEXT INPUT OPERATIONS
# =============================================================================

@allure.step("Input text using pattern - Value: '{value}', Field: {field}")
def input_text_pattern(value: str, field: str):
    """Web: Input-Text Value:{value} Field:{field}"""
    element = _find_element_by_pattern('input', field)
    element.send_keys(value)
    _attach_screenshot(f"Input Text - {field}")


@allure.step("Clear and fill text using pattern - Value: '{value}', Field: {field}")
def clear_and_fill_pattern(value: str, field: str):
    """Web: Clear and fill Input-Text Value:{value} Field:{field}"""
    element = _find_element_by_pattern('input', field)
    element.clear()
    element.send_keys(value)
    _attach_screenshot(f"Clear and Fill - {field}")


@allure.step("Click and input text using pattern - Value: '{value}', Field: {field}")
def click_and_input_text_pattern(value: str, field: str):
    """Web: Click-And-Input-Text Value:{value} Field:{field}"""
    element = _find_element_by_pattern('input', field)
    element.click()
    element.send_keys(value)
    _attach_screenshot(f"Click and Input - {field}")


@allure.step("Input text with placeholder identification - Value: '{value}', Field: {field}")
def input_text_with_placeholder_or_no_label(value: str, field: str):
    """Web: Input-Text-With-Placeholder-Or-No-Label Value:{value} Field:{field}"""
    try:
        # Try to find by placeholder attribute first
        element = _get_driver().find_element(By.XPATH, f"//input[@placeholder='{field}' or contains(@placeholder, '{field}')]")
        element.send_keys(value)
        _attach_screenshot(f"Input with Placeholder - {field}")
    except NoSuchElementException:
        # Fallback to pattern locator
        input_text_pattern(value, field)


@allure.step("Input text with placeholder - Value: '{value}', Field: {field}")
def input_text_with_placeholder(value: str, field: str):
    """Web: Input-Text-With-Placeholder Value:{value} Field:{field}"""
    element = _get_driver().find_element(By.XPATH, f"//input[@placeholder='{field}']")
    element.send_keys(value)
    _attach_screenshot(f"Input with Placeholder - {field}")


@allure.step("Clear then input text using pattern - Value: '{value}', Field: {field}")
def clear_then_input_text_pattern(value: str, field: str):
    """Web: Clear-Then-Input-Text Value:{value} Field:{field}"""
    clear_and_fill_pattern(value, field)


# =============================================================================
# MOUSE INTERACTIONS
# =============================================================================

@allure.step("Mouseover button using pattern - Field: {field}")
def mouseover_button_pattern(field: str):
    """Web: Mouseover-On-Button Field:{field}"""
    element = _find_element_by_pattern('button', field)
    ActionChains(_get_driver()).move_to_element(element).perform()
    _attach_screenshot(f"Mouseover Button - {field}")


@allure.step("Mouseover link using pattern - Field: {field}")
def mouseover_link_pattern(field: str):
    """Web: Mouseover-On-Link Field:{field}"""
    element = _find_element_by_pattern('link', field)
    ActionChains(_get_driver()).move_to_element(element).perform()
    _attach_screenshot(f"Mouseover Link - {field}")


# =============================================================================
# VERIFICATION & VALIDATION
# =============================================================================

@allure.step("Assert text field {field} with partial text '{text}' is present (case insensitive)")
def assert_text_field_partial_text_present_ignore_case(field: str, text: str) -> bool:
    """Web: I assert text field {field} with partial text {text} is present ignoring case"""
    try:
        element = _find_element_by_pattern('text', field)
        element_text = element.text.lower()
        search_text = text.lower()
        result = search_text in element_text
        
        allure.attach(f"Field: {field}\nSearch text: {text}\nElement text: {element.text}\nFound: {result}",
                     name="Text Field Verification", attachment_type=allure.attachment_type.TEXT)
        
        if not result:
            raise AssertionError(f"Text field '{field}' does not contain '{text}' (case insensitive)")
        
        return result
    except NoSuchElementException:
        raise AssertionError(f"Text field '{field}' not found")


@allure.step("Assert field {field} with partial text '{text}' is NOT present (case insensitive)")
def assert_field_partial_text_not_present_ignore_case(field: str, text: str) -> bool:
    """I assert field {field} with partial text {text} is not present ignoring case"""
    try:
        element = _find_element_by_pattern('element', field)
        element_text = element.text.lower()
        search_text = text.lower()
        result = search_text not in element_text
        
        allure.attach(f"Field: {field}\nSearch text: {text}\nElement text: {element.text}\nNot found: {result}",
                     name="Field Absence Verification", attachment_type=allure.attachment_type.TEXT)
        
        if not result:
            raise AssertionError(f"Field '{field}' unexpectedly contains '{text}' (case insensitive)")
        
        return result
    except NoSuchElementException:
        return True  # Field not found means text is not present


@allure.step("Assert button field {field} with partial text '{text}' is present (case insensitive)")
def assert_button_field_partial_text_present_ignore_case(field: str, text: str) -> bool:
    """Web: I assert button field {field} with partial text {text} is present ignoring case"""
    try:
        element = _find_element_by_pattern('button', field)
        element_text = element.text.lower()
        search_text = text.lower()
        result = search_text in element_text
        
        allure.attach(f"Button: {field}\nSearch text: {text}\nButton text: {element.text}\nFound: {result}",
                     name="Button Text Verification", attachment_type=allure.attachment_type.TEXT)
        
        if not result:
            raise AssertionError(f"Button field '{field}' does not contain '{text}' (case insensitive)")
        
        return result
    except NoSuchElementException:
        raise AssertionError(f"Button field '{field}' not found")


@allure.step("Verify dropdown item '{item}' is NOT present")
def verify_dropdown_item_not_present(item: str) -> bool:
    """Web: Verify dropdown-item {item} is not present"""
    try:
        dropdown_items = _get_driver().find_elements(By.XPATH, f"//option[text()='{item}'] | //li[text()='{item}']")
        result = len(dropdown_items) == 0
        allure.attach(f"Dropdown item: {item}\nNot present: {result}", 
                     name="Dropdown Item Absence Verification", attachment_type=allure.attachment_type.TEXT)
        return result
    except Exception as e:
        allure.attach(f"Error: {e}", name="Dropdown Verification Error", attachment_type=allure.attachment_type.TEXT)
        return True


@allure.step("Verify dropdown item '{item}' is present")
def verify_dropdown_item_present(item: str) -> bool:
    """Web: Verify dropdown-item {item} is present"""
    try:
        dropdown_items = _get_driver().find_elements(By.XPATH, f"//option[text()='{item}'] | //li[text()='{item}']")
        result = len(dropdown_items) > 0
        allure.attach(f"Dropdown item: {item}\nPresent: {result}", 
                     name="Dropdown Item Presence Verification", attachment_type=allure.attachment_type.TEXT)
        return result
    except Exception as e:
        allure.attach(f"Error: {e}", name="Dropdown Verification Error", attachment_type=allure.attachment_type.TEXT)
        return False


@allure.step("Verify element presence using pattern - Element: {element}, Field: {field}")
def verify_element_present_pattern(element: str, field: str) -> bool:
    """Web: Verify-Element-Present Element:{element} Field:{field}"""
    try:
        _find_element_by_pattern(element, field)
        allure.attach(f"Element: {element}\nField: {field}\nPresent: True", 
                     name="Element Presence Verification", attachment_type=allure.attachment_type.TEXT)
        return True
    except Exception as e:
        allure.attach(f"Element: {element}\nField: {field}\nPresent: False\nError: {e}", 
                     name="Element Presence Verification", attachment_type=allure.attachment_type.TEXT)
        return False


@allure.step("Verify element absence using pattern - Element: {element}, Field: {field}")
def verify_element_not_present_pattern(element: str, field: str) -> bool:
    """Web: Verify-Element-Not-Present Element:{element} Field:{field}"""
    result = not verify_element_present_pattern(element, field)
    allure.attach(f"Element: {element}\nField: {field}\nNot present: {result}", 
                 name="Element Absence Verification", attachment_type=allure.attachment_type.TEXT)
    return result


@allure.step("Verify element text value using pattern - Element: {element}, Field: {field}, Text: '{text}'")
def verify_element_value_text_is_pattern(element: str, field: str, text: str) -> bool:
    """Web: Verify-Element-Value-Text-Is Element:{element} Field:{field} Text:{text}"""
    try:
        element_obj = _find_element_by_pattern(element, field)
        if element_obj.tag_name.lower() == 'input':
            actual_text = element_obj.get_attribute('value')
        else:
            actual_text = element_obj.text
        
        result = actual_text == text
        allure.attach(f"Element: {element}\nField: {field}\nExpected: {text}\nActual: {actual_text}\nMatch: {result}",
                     name="Element Value Verification", attachment_type=allure.attachment_type.TEXT)
        return result
    except Exception as e:
        allure.attach(f"Element: {element}\nField: {field}\nError: {e}", 
                     name="Element Value Verification Error", attachment_type=allure.attachment_type.TEXT)
        return False


# =============================================================================
# PAGE HEADER & TITLE OPERATIONS
# =============================================================================

@allure.step("Verify page header text using pattern - Field: {field}, Page: {page}")
def verify_page_header_text_pattern(field: str, page: str) -> bool:
    """Web: Verify-Page-Header-Text Field:{field} Page-Name:{page}"""
    try:
        set_page_name(page)
        element = _find_element_by_pattern('text', field, page)
        header_text = element.text
        allure.attach(f"Page: {page}\nField: {field}\nHeader text: {header_text}", 
                     name="Page Header Verification", attachment_type=allure.attachment_type.TEXT)
        return len(header_text) > 0
    except Exception as e:
        allure.attach(f"Page: {page}\nField: {field}\nError: {e}", 
                     name="Page Header Verification Error", attachment_type=allure.attachment_type.TEXT)
        return False


@allure.step("Verify page header contains text - Text: '{text}', Page: {page}")
def verify_page_header_text_contains(text: str, page: str) -> bool:
    """Web: Verify-Page-Header-Text-Contains Text:{text} Page-Name:{page}"""
    try:
        set_page_name(page)
        # Look for header elements that might contain the text
        header_elements = _get_driver().find_elements(By.XPATH, 
            f"//h1[contains(text(), '{text}')] | //h2[contains(text(), '{text}')] | //h3[contains(text(), '{text}')]")
        result = len(header_elements) > 0
        allure.attach(f"Page: {page}\nSearch text: {text}\nFound: {result}", 
                     name="Page Header Contains Verification", attachment_type=allure.attachment_type.TEXT)
        return result
    except Exception as e:
        allure.attach(f"Page: {page}\nText: {text}\nError: {e}", 
                     name="Page Header Contains Error", attachment_type=allure.attachment_type.TEXT)
        return False


@allure.step("Verify page header field - Field: {field}, Page: {page}")
def verify_page_header_pattern(field: str, page: str) -> bool:
    """Web: Verify-Page-Header Field:{field} Page-Name:{page}"""
    return verify_page_header_text_pattern(field, page)


@allure.step("Verify page header field contains text - Field: {field}, Text: '{text}', Page: {page}")
def verify_page_header_field_text_contains(field: str, text: str, page: str) -> bool:
    """Web: Verify-Page-Header-Field-Text-Contains Field:{field} Text:{text} Page-Name:{page}"""
    try:
        set_page_name(page)
        element = _find_element_by_pattern('text', field, page)
        element_text = element.text
        result = text in element_text
        allure.attach(f"Page: {page}\nField: {field}\nSearch text: {text}\nElement text: {element_text}\nContains: {result}",
                     name="Header Field Text Contains Verification", attachment_type=allure.attachment_type.TEXT)
        return result
    except Exception as e:
        allure.attach(f"Page: {page}\nField: {field}\nText: {text}\nError: {e}", 
                     name="Header Field Verification Error", attachment_type=allure.attachment_type.TEXT)
        return False


@allure.step("Verify page title - Title: '{title}', Page: {page}")
def verify_page_title_text(title: str, page: str) -> bool:
    """Web: Verify-Page-Title-Text Title:{title} Page-Name:{page}"""
    try:
        set_page_name(page)
        actual_title = _get_driver().title
        result = actual_title == title
        allure.attach(f"Page: {page}\nExpected title: {title}\nActual title: {actual_title}\nMatch: {result}",
                     name="Page Title Verification", attachment_type=allure.attachment_type.TEXT)
        return result
    except Exception as e:
        allure.attach(f"Page: {page}\nTitle: {title}\nError: {e}", 
                     name="Page Title Verification Error", attachment_type=allure.attachment_type.TEXT)
        return False


# =============================================================================
# FRAME & WINDOW MANAGEMENT
# =============================================================================

@allure.step("Move to iframe by ID/name: {iframe}")
def move_to_iframe(iframe: str):
    """Web: Move to iframe by Id or Name {iframe}"""
    _get_driver().switch_to.frame(iframe)
    allure.attach(f"Switched to iframe: {iframe}", name="Frame Switch", attachment_type=allure.attachment_type.TEXT)


@allure.step("Switch iframe and click element - Iframe: {iframe}, Pattern: {pattern}, Field: {field}")
def switch_iframe_click_element(iframe: str, pattern: str, field: str):
    """Web: Switch-iframe-Click-Element iframe:{iframe} Pattern:{pattern} Field:{field}"""
    move_to_iframe(iframe)
    click_element_pattern(pattern, field)
    _get_driver().switch_to.default_content()


@allure.step("Move to header field: {field}")
def move_to_header(field: str):
    """Web: Move to Header {field}"""
    try:
        element = _find_element_by_pattern('text', field)
        ActionChains(_get_driver()).move_to_element(element).perform()
        _attach_screenshot(f"Moved to Header - {field}")
    except Exception as e:
        allure.attach(f"Field: {field}\nError: {e}", name="Move to Header Error", 
                     attachment_type=allure.attachment_type.TEXT)


@allure.step("Move to and hover input field: {field}")
def move_to_and_hover_input_field(field: str):
    """Web: Move to and hover input field {field}"""
    element = _find_element_by_pattern('input', field)
    ActionChains(_get_driver()).move_to_element(element).perform()
    _attach_screenshot(f"Moved and Hovered - {field}")


# =============================================================================
# DATA MANAGEMENT
# =============================================================================

@allure.step("Get stored page name")
def get_stored_page_name() -> str:
    """Web: Get stored page name"""
    return _page_context.get('current_page', 'Unknown')


@allure.step("Set page name: {name}")
def set_page_name(name: str):
    """Web: Set-Page-Name Value:{name}"""
    global _page_context
    _page_context['current_page'] = name
    allure.attach(f"Page name set to: {name}", name="Page Context", attachment_type=allure.attachment_type.TEXT)


@allure.step("Get page name")
def get_page_name() -> str:
    """Web: Get-Page-Name"""
    return get_stored_page_name()


@allure.step("Set field location: {name}")
def set_field_location(name: str):
    """Web: Set-Field-Location Name:{name}"""
    global _field_locations
    _field_locations['current_field'] = name
    allure.attach(f"Field location set to: {name}", name="Field Context", attachment_type=allure.attachment_type.TEXT)


@allure.step("Set field location and value - Name: {name}, Value: '{value}'")
def set_field_location_and_value(name: str, value: str):
    """Web: Set-Field-Location-And-Value Name:{name} Value:{value}"""
    global _field_locations
    _field_locations['current_field'] = name
    _field_locations['current_value'] = value
    allure.attach(f"Field location: {name}\nField value: {value}", name="Field Context", 
                 attachment_type=allure.attachment_type.TEXT)


@allure.step("Remove field location")
def remove_field_location():
    """Web: Remove-Field-Location"""
    global _field_locations
    _field_locations.pop('current_field', None)
    _field_locations.pop('current_value', None)
    allure.attach("Field location context cleared", name="Field Context", attachment_type=allure.attachment_type.TEXT)


@allure.step("Set current execution date/time")
def set_current_execution_datetime():
    """Web: Set-Current-Execution-Date-Time"""
    global _execution_datetime
    _execution_datetime = datetime.now()
    allure.attach(f"Execution time set to: {_execution_datetime}", name="Execution Time", 
                 attachment_type=allure.attachment_type.TEXT)


@allure.step("Get execution date/time")
def get_execution_datetime() -> datetime:
    """Web: Get-Execution-Date-Time"""
    global _execution_datetime
    if _execution_datetime is None:
        set_current_execution_datetime()
    return _execution_datetime


# =============================================================================
# ADVANCED PATTERN OPERATIONS
# =============================================================================

@allure.step("JavaScript click using pattern - Pattern: {pattern}, Field: {field}")
def javascript_executor_click_pattern(pattern: str, field: str):
    """Web: JavaScript-Executor-Click-Pattern Pattern:{pattern} Field:{field}"""
    element = _find_element_by_pattern(pattern, field)
    _get_driver().execute_script("arguments[0].click();", element)
    _attach_screenshot(f"JavaScript Click - {pattern} - {field}")


@allure.step("JavaScript clear element using pattern - Element: {element}, Field: {field}")
def javascript_executor_clear_element_pattern(element: str, field: str):
    """Web: JavaScript-Executor-Clear-Element Element:{element} Field:{field}"""
    element_obj = _find_element_by_pattern(element, field)
    _get_driver().execute_script("arguments[0].value = '';", element_obj)
    _attach_screenshot(f"JavaScript Clear - {element} - {field}")


@allure.step("Highlight element and take screenshot - Element: {element}, Pattern: {pattern}")
def highlight_element_and_screenshot(element: str, pattern: str):
    """Web: Highlight element {element} with pattern {pattern} and take screenshot"""
    try:
        element_obj = _find_element_by_pattern(element, pattern)
        # Highlight element with JavaScript
        _get_driver().execute_script(
            "arguments[0].style.border='3px solid red'; arguments[0].style.backgroundColor='yellow';", 
            element_obj
        )
        _attach_screenshot(f"Highlighted {element} - {pattern}")
        # Remove highlight
        _get_driver().execute_script(
            "arguments[0].style.border=''; arguments[0].style.backgroundColor='';", 
            element_obj
        )
    except Exception as e:
        allure.attach(f"Element: {element}\nPattern: {pattern}\nError: {e}", 
                     name="Highlight Error", attachment_type=allure.attachment_type.TEXT)


@allure.step("Wait until element not visible using pattern - Element: {element}, Field: {field}")
def wait_until_element_not_visible_pattern(element: str, field: str, timeout: int = 30):
    """Web: Wait-Until-Element-Not-Visible Element:{element} Field:{field}"""
    try:
        # First find the element to get its locator
        element_obj = _find_element_by_pattern(element, field)
        locator = element_obj._parent._driver.find_elements(By.XPATH, f"*[@*='{element_obj.get_attribute('id')}']")
        
        # Wait for invisibility
        wait = WebDriverWait(_get_driver(), timeout)
        wait.until(EC.invisibility_of_element_located((By.XPATH, f"//*[@id='{element_obj.get_attribute('id')}']")))
        
        allure.attach(f"Element: {element}\nField: {field}\nNow invisible", 
                     name="Element Invisibility Wait", attachment_type=allure.attachment_type.TEXT)
    except TimeoutException:
        allure.attach(f"Element: {element}\nField: {field}\nTimeout waiting for invisibility", 
                     name="Element Invisibility Timeout", attachment_type=allure.attachment_type.TEXT)
    except Exception as e:
        allure.attach(f"Element: {element}\nField: {field}\nError: {e}", 
                     name="Element Invisibility Error", attachment_type=allure.attachment_type.TEXT)


@allure.step("Get element text using pattern - Element: {element}, Field: {field}")
def get_element_text_by_pattern(element: str, field: str) -> str:
    """Web: Get-Element-Text-By-Pattern Element:{element} Field:{field}"""
    try:
        element_obj = _find_element_by_pattern(element, field)
        text = element_obj.text
        allure.attach(f"Element: {element}\nField: {field}\nText: {text}", 
                     name="Element Text Extraction", attachment_type=allure.attachment_type.TEXT)
        return text
    except Exception as e:
        allure.attach(f"Element: {element}\nField: {field}\nError: {e}", 
                     name="Element Text Extraction Error", attachment_type=allure.attachment_type.TEXT)
        return ""


@allure.step("Click element using stored property - Element: {element}, Property: {property}")
def click_element_using_property_for_field(element: str, property: str):
    """Web: Click-Element-Using-Property-For-Field Element:{element} Get-Property:{property}"""
    try:
        # Get property value from stored variables or bundle
        property_value = _field_locations.get(property) or get_bundle().get_string(property)
        if property_value:
            element_obj = _find_element_by_pattern(element, property_value)
            element_obj.click()
            _attach_screenshot(f"Click using Property - {element} - {property}")
        else:
            raise WebError(f"Property '{property}' not found")
    except Exception as e:
        allure.attach(f"Element: {element}\nProperty: {property}\nError: {e}", 
                     name="Property-based Click Error", attachment_type=allure.attachment_type.TEXT)


@allure.step("Input text using stored property - Field: {field}, Property: {property}")
def input_text_using_property_as_value(field: str, property: str):
    """Web: Input-Text-Using-Property-As-Value Field:{field} Get-Property:{property}"""
    try:
        # Get property value from stored variables or bundle
        property_value = _field_locations.get(property) or get_bundle().get_string(property)
        if property_value:
            input_text_pattern(property_value, field)
        else:
            raise WebError(f"Property '{property}' not found")
    except Exception as e:
        allure.attach(f"Field: {field}\nProperty: {property}\nError: {e}", 
                     name="Property-based Input Error", attachment_type=allure.attachment_type.TEXT)


@allure.step("Scroll up and click element using pattern - Element: {element}, Field: {field}")
def scroll_up_and_click_element_pattern(element: str, field: str):
    """Web: Scroll-Up-And-Click-Element Element:{element} Field:{field}"""
    # Scroll up first
    _get_driver().execute_script("window.scrollBy(0, -300);")
    time.sleep(0.5)
    
    # Then click the element
    click_element_pattern(element, field)


# =============================================================================
# TIMING & SYNCHRONIZATION
# =============================================================================

@allure.step("Wait for {seconds} seconds")
def wait_for_seconds(seconds: int):
    """Web: Wait-For-Seconds Value:{seconds}"""
    time.sleep(seconds)


@allure.step("Wait for {milliseconds} milliseconds")
def wait_for_milliseconds(milliseconds: int):
    """Web: Wait-For-Milliseconds Value:{milliseconds}"""
    time.sleep(milliseconds / 1000.0)


# =============================================================================
# FILE OPERATIONS
# =============================================================================

@allure.step("Upload file using pattern - Filename: {filename}, Field: {field}")
def upload_file_pattern(filename: str, field: str):
    """Web: Upload-File File-Name:{filename} Input-Field:{field}"""
    if not os.path.exists(filename):
        raise WebError(f"File not found: {filename}")
    
    file_input = _find_element_by_pattern('input', field)
    file_input.send_keys(os.path.abspath(filename))
    _attach_screenshot(f"File Upload - {field}")


# =============================================================================
# DROPDOWN OPERATIONS
# =============================================================================

@allure.step("Select value from dropdown - Label: {label}, Value: '{value}'")
def select_value_from_dropdown(label: str, value: str):
    """Web: Select-Value-From-Dropdown DropdownLabel:{label} DropdownValue:{value}"""
    try:
        dropdown = _find_element_by_pattern('dropdown', label)
        select = Select(dropdown)
        select.select_by_value(value)
        _attach_screenshot(f"Dropdown Selection - {label}: {value}")
    except Exception as e:
        allure.attach(f"Label: {label}\nValue: {value}\nError: {e}", 
                     name="Dropdown Selection Error", attachment_type=allure.attachment_type.TEXT)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

@allure.step("Business verification: {text}")
def business_verification(text: str):
    """Web: Business verification: I verify {text}"""
    allure.attach(f"Business verification: {text}", name="Business Rule Verification", 
                 attachment_type=allure.attachment_type.TEXT)
    # This is a placeholder for business logic verification
    # Implementation would depend on specific business rules


@allure.step("Scroll to element: {element}")
def scroll_to_element_web(element: str):
    """Web: I scroll to an element {element}"""
    try:
        # Try to find element using various locator strategies
        if element.startswith(('xpath=', 'id=', 'css=')):
            from qaf.automation.ui.BrowserGlobal import _find_element
            element_obj = _find_element(element)
        else:
            # Try as pattern locator
            element_obj = _find_element_by_pattern('element', element)
        
        _get_driver().execute_script("arguments[0].scrollIntoView(true);", element_obj)
        _attach_screenshot(f"Scrolled to Element - {element}")
    except Exception as e:
        allure.attach(f"Element: {element}\nError: {e}", name="Scroll Error", attachment_type=allure.attachment_type.TEXT)


@allure.step("Get text from element using locator: {locator}")
def get_text_from_element_locator(locator: str) -> str:
    """Web: Get-Text-From-Element Locator:{locator}"""
    try:
        from qaf.automation.ui.BrowserGlobal import _find_element
        element = _find_element(locator)
        text = element.text
        allure.attach(f"Locator: {locator}\nText: {text}", name="Text Extraction", 
                     attachment_type=allure.attachment_type.TEXT)
        return text
    except Exception as e:
        allure.attach(f"Locator: {locator}\nError: {e}", name="Text Extraction Error", 
                     attachment_type=allure.attachment_type.TEXT)
        return ""


@allure.step("Verify element text at regular intervals for duration using property")
def verify_element_text_at_regular_intervals_for_duration_using_property(
    seconds_interval: int, 
    duration_minutes: int, 
    element: str, 
    property_name: str, 
    text_to_verify: str, 
    action_todo: str
):
    """Web: Verify-Element-Text-At-Regular-Intervals-For-A-Duration-Using-Property
    Seconds-Interval: {seconds_interval}
    Duration-Minutes: {duration_minutes} 
    Element: {element}
    Property: {property_name}
    Text-To-Verify: {text_to_verify}
    Action-todo: {action_todo}"""
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    verification_count = 0
    
    allure.attach(f"Starting monitoring:\nInterval: {seconds_interval}s\nDuration: {duration_minutes}m\nElement: {element}\nProperty: {property_name}\nExpected text: {text_to_verify}\nAction: {action_todo}",
                 name="Monitoring Configuration", attachment_type=allure.attachment_type.TEXT)
    
    while time.time() < end_time:
        try:
            verification_count += 1
            
            # Get current text from element
            element_text = get_element_text_by_pattern('element', element)
            
            verification_result = text_to_verify in element_text
            
            allure.attach(f"Verification #{verification_count}\nTime: {datetime.now()}\nElement text: {element_text}\nExpected: {text_to_verify}\nMatch: {verification_result}",
                         name=f"Monitoring Check {verification_count}", attachment_type=allure.attachment_type.TEXT)
            
            if verification_result and action_todo.lower() == 'stop':
                allure.attach(f"Text verification successful. Stopping monitoring after {verification_count} checks.",
                             name="Monitoring Completed", attachment_type=allure.attachment_type.TEXT)
                break
            elif not verification_result and action_todo.lower() == 'fail':
                raise AssertionError(f"Text verification failed on check #{verification_count}. Expected: '{text_to_verify}', Found: '{element_text}'")
            
            time.sleep(seconds_interval)
            
        except Exception as e:
            allure.attach(f"Monitoring error on check #{verification_count}: {e}",
                         name="Monitoring Error", attachment_type=allure.attachment_type.TEXT)
            if action_todo.lower() == 'fail':
                raise
            time.sleep(seconds_interval)
    
    allure.attach(f"Monitoring completed. Total checks: {verification_count}\nDuration: {duration_minutes} minutes",
                 name="Monitoring Summary", attachment_type=allure.attachment_type.TEXT)


# =============================================================================
# CONTEXT MANAGEMENT FUNCTIONS
# =============================================================================

def get_current_page_context() -> str:
    """Get current page context"""
    return _page_context.get('current_page', 'genericPage')


def get_field_location_context() -> Dict[str, str]:
    """Get current field location context"""
    return _field_locations.copy()


def clear_all_contexts():
    """Clear all stored contexts"""
    global _page_context, _field_locations, _execution_datetime
    _page_context.clear()
    _field_locations.clear()
    _execution_datetime = None


def set_web_timeout(timeout: int):
    """Set default timeout for web operations"""
    # This would integrate with the BrowserGlobal timeout settings
    from qaf.automation.ui.BrowserGlobal import set_wait_timeout
    set_wait_timeout(timeout)