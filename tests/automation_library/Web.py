"""
Web.py - Pattern-Based Web Automation Functions
===============================================

This module contains reusable web automation functions that leverage the QAF pattern 
locator system for dynamic element identification.
"""

import os
import time
import json
import logging
from typing import List, Optional, Union, Any, Dict

import allure
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException, WebDriverException
)

# Import QAF system and PatternEngine
try:
    from qaf.automation.core import get_bundle
    from qaf.automation.ui.util.pattern_engine import get_pattern_engine
    QAF_AVAILABLE = True
except ImportError:
    QAF_AVAILABLE = False
    get_pattern_engine = None

# Import BrowserGlobal functions from same directory
try:
    from tests.automation_library.BrowserGlobal import _get_driver, _attach_screenshot
except ImportError:
    try:
        from .BrowserGlobal import _get_driver, _attach_screenshot
    except ImportError:
        print("Warning: Could not import BrowserGlobal functions")

# Global data storage
_page_context = {}


class WebError(Exception):
    """Custom exception for Web operations"""
    pass


def _get_pattern_engine():
    """Get QAF PatternEngine instance"""
    if not QAF_AVAILABLE or not get_pattern_engine:
        raise WebError("QAF PatternEngine system not available")
    return get_pattern_engine()


def _find_element_by_pattern(element: str, field: str, page: str = None) -> Any:
    """Find element using QAF PatternEngine with reflection"""
    try:
        pattern_engine = _get_pattern_engine()
        page_name = page or _page_context.get('current_page', 'genericPage')
        
        # Use reflection to dynamically call PatternEngine methods
        element_type = element.lower()
        
        # Check if the PatternEngine has the method for this element type
        if not hasattr(pattern_engine, element_type):
            raise WebError(f"PatternEngine does not support element type: {element_type}")
        
        method = getattr(pattern_engine, element_type)
        if not callable(method):
            raise WebError(f"PatternEngine.{element_type} is not callable")
        
        allure.attach(f"Found function {element_type} in PatternEngine!", 
                     name="Pattern Method Resolution", attachment_type=allure.attachment_type.TEXT)
        
        # Generate locator using reflection-based pattern system
        locator = method(page_name, field)
        
        # Handle QAF JSON format: {"locator":[...], "desc":"..."}
        if isinstance(locator, str) and locator.startswith('{"locator":'):
            qaf_data = json.loads(locator)
            locators = qaf_data.get('locator', [])
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
            
            raise last_exception or NoSuchElementException(f"No pattern locator found element: {page_name}.{element_type}.{field}")
        
        else:
            # Single locator pattern (fallback)
            xpath = locator.replace('xpath=', '') if locator.startswith('xpath=') else locator
            element_found = _get_driver().find_element(By.XPATH, xpath)
            allure.attach(f"Pattern found element with: {xpath}", name="Pattern Locator Success", 
                        attachment_type=allure.attachment_type.TEXT)
            return element_found
            
    except Exception as e:
        error_msg = f"Pattern locator failed for {page_name}.{element}.{field}: {e}"
        allure.attach(error_msg, name="Pattern Locator Error", attachment_type=allure.attachment_type.TEXT)
        raise WebError(error_msg) from e


# =============================================================================
# PATTERN-BASED ELEMENT INTERACTIONS
# =============================================================================

@allure.step("Click button using pattern - Field: {field}")
def click_button_pattern(field: str):
    """Click button using pattern - Field: {field}"""
    element = _find_element_by_pattern('button', field)
    element.click()
    _attach_screenshot(f"Clicked Button - {field}")


@allure.step("Click link using pattern - Field: {field}")
def click_link_pattern(field: str):
    """Click link using pattern - Field: {field}"""
    element = _find_element_by_pattern('link', field)
    element.click()
    _attach_screenshot(f"Clicked Link - {field}")


@allure.step("Input text using pattern - Value: '{value}', Field: {field}")
def input_text_pattern(value: str, field: str):
    """Input text using pattern - Value: {value}, Field: {field}"""
    element = _find_element_by_pattern('input', field)
    element.send_keys(value)
    _attach_screenshot(f"Input Text - {field}")


@allure.step("Clear and fill text using pattern - Value: '{value}', Field: {field}")
def clear_and_fill_pattern(value: str, field: str):
    """Clear and fill text using pattern - Value: {value}, Field: {field}"""
    element = _find_element_by_pattern('input', field)
    element.clear()
    element.send_keys(value)
    _attach_screenshot(f"Clear and Fill - {field}")


# =============================================================================
# VERIFICATION & VALIDATION
# =============================================================================

@allure.step("Verify page contains text: {text}")
def verify_page_contains_text(text: str) -> bool:
    """Verify page contains text: {text}"""
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


@allure.step("Verify element presence using pattern - Element: {element}, Field: {field}")
def verify_element_present_pattern(element: str, field: str) -> bool:
    """Verify element presence using pattern - Element: {element}, Field: {field}"""
    try:
        _find_element_by_pattern(element, field)
        allure.attach(f"Element: {element}\nField: {field}\nPresent: True", 
                     name="Element Presence Verification", attachment_type=allure.attachment_type.TEXT)
        return True
    except Exception as e:
        allure.attach(f"Element: {element}\nField: {field}\nPresent: False\nError: {e}", 
                     name="Element Presence Verification", attachment_type=allure.attachment_type.TEXT)
        return False


# =============================================================================
# DATA MANAGEMENT
# =============================================================================

@allure.step("Set page name: {name}")
def set_page_name(name: str):
    """Set page name: {name}"""
    global _page_context
    _page_context['current_page'] = name
    allure.attach(f"Page name set to: {name}", name="Page Context", attachment_type=allure.attachment_type.TEXT)


@allure.step("Get stored page name")
def get_stored_page_name() -> str:
    """Get stored page name"""
    return _page_context.get('current_page', 'Unknown')


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_current_page_context() -> str:
    """Get current page context"""
    return _page_context.get('current_page', 'genericPage')


def clear_all_contexts():
    """Clear all stored contexts"""
    global _page_context
    _page_context.clear()


# =============================================================================
# REFLECTION-BASED STEP DEFINITIONS FOR PATTERN LOCATORS
# =============================================================================

@allure.step("Web: Click-Element Pattern:{pattern_name} Field:{field_name}")
def click_element_pattern_reflection(pattern_name: str, field_name: str, page: str = None):
    """
    Web: Click-Element Pattern:{pattern_name} Field:{field_name}
    
    Reflection-based step definition that dynamically calls PatternEngine methods
    based on the pattern_name parameter.
    
    Args:
        pattern_name: Element type name (button, link, checkbox, etc.)
        field_name: Field name to locate 
        page: Optional page name (uses current page context if not provided)
    """
    try:
        pattern_engine = _get_pattern_engine()
        page_name = page or _page_context.get('current_page', 'genericPage')
        
        # Use reflection to dynamically find the method
        if not hasattr(pattern_engine, pattern_name.lower()):
            available_methods = [method for method in dir(pattern_engine) 
                               if not method.startswith('_') and callable(getattr(pattern_engine, method))]
            raise WebError(f"NoSuchMethodException: PatternEngine has no method '{pattern_name}'. "
                          f"Available methods: {available_methods}")
        
        method = getattr(pattern_engine, pattern_name.lower())
        if not callable(method):
            raise WebError(f"PatternEngine.{pattern_name} is not callable")
        
        # Log successful method resolution (matching Java implementation)
        allure.attach(f"Found function {pattern_name} in PatternEngine!", 
                     name="Method Resolution Success", attachment_type=allure.attachment_type.TEXT)
        
        # Generate locator and find element
        locator = method(page_name, field_name)
        element = _find_element_using_locator(locator, pattern_name, field_name, page_name)
        
        # Perform click action
        element.click()
        _attach_screenshot(f"Clicked {pattern_name} - {field_name}")
        
        allure.attach(f"Successfully clicked {pattern_name} '{field_name}' on page '{page_name}'", 
                     name="Click Action Success", attachment_type=allure.attachment_type.TEXT)
        
    except Exception as e:
        error_msg = f"Failed to click {pattern_name} '{field_name}': {e}"
        allure.attach(error_msg, name="Click Action Error", attachment_type=allure.attachment_type.TEXT)
        _attach_screenshot(f"Error - Click {pattern_name} {field_name}")
        raise WebError(error_msg) from e


def _find_element_using_locator(locator: str, element_type: str, field_name: str, page_name: str) -> Any:
    """
    Helper function to find element using generated locator
    Handles both QAF JSON format and simple xpath locators
    """
    try:
        # Handle QAF JSON format: {"locator":[...], "desc":"..."}
        if isinstance(locator, str) and locator.startswith('{"locator":'):
            qaf_data = json.loads(locator)
            locators = qaf_data.get('locator', [])
            last_exception = None
            
            for i, loc in enumerate(locators):
                try:
                    xpath = loc.replace('xpath=', '') if loc.startswith('xpath=') else loc
                    element = _get_driver().find_element(By.XPATH, xpath)
                    allure.attach(f"Pattern {i+1}/{len(locators)} found element: {loc}", 
                                name="Pattern Locator Success", attachment_type=allure.attachment_type.TEXT)
                    return element
                except NoSuchElementException as e:
                    allure.attach(f"Pattern {i+1}/{len(locators)} failed: {loc}", 
                                name="Pattern Locator Attempt", attachment_type=allure.attachment_type.TEXT)
                    last_exception = e
                    continue
            
            raise last_exception or NoSuchElementException(
                f"No pattern locator found element: {page_name}.{element_type}.{field_name}")
        
        else:
            # Single locator pattern (fallback)
            xpath = locator.replace('xpath=', '') if locator.startswith('xpath=') else locator
            element = _get_driver().find_element(By.XPATH, xpath)
            allure.attach(f"Single pattern found element: {xpath}", 
                        name="Pattern Locator Success", attachment_type=allure.attachment_type.TEXT)
            return element
            
    except Exception as e:
        error_msg = f"Element location failed for {page_name}.{element_type}.{field_name}: {e}"
        allure.attach(error_msg, name="Element Location Error", attachment_type=allure.attachment_type.TEXT)
        raise NoSuchElementException(error_msg) from e


@allure.step("Web: Input-Text Value:{input_value} Field:{field_name}")
def input_text_pattern_reflection(input_value: str, field_name: str, page: str = None):
    """
    Web: Input-Text Value:{input_value} Field:{field_name}
    
    Reflection-based step definition for text input using PatternEngine.input() method
    
    Args:
        input_value: Text value to input
        field_name: Field name to locate 
        page: Optional page name (uses current page context if not provided)
    """
    try:
        pattern_engine = _get_pattern_engine()
        page_name = page or _page_context.get('current_page', 'genericPage')
        
        # Use reflection to get the input method from PatternEngine
        if not hasattr(pattern_engine, 'input'):
            raise WebError("NoSuchMethodException: PatternEngine has no method 'input'")
        
        input_method = getattr(pattern_engine, 'input')
        if not callable(input_method):
            raise WebError("PatternEngine.input is not callable")
        
        # Log successful method resolution
        allure.attach("Found function input in PatternEngine!", 
                     name="Method Resolution Success", attachment_type=allure.attachment_type.TEXT)
        
        # Generate locator and find element
        locator = input_method(page_name, field_name)
        element = _find_element_using_locator(locator, 'input', field_name, page_name)
        
        # Clear field and enter value
        element.clear()
        element.send_keys(input_value)
        _attach_screenshot(f"Input Text - {field_name}")
        
        allure.attach(f"Successfully input '{input_value}' into field '{field_name}' on page '{page_name}'", 
                     name="Input Action Success", attachment_type=allure.attachment_type.TEXT)
        
    except Exception as e:
        error_msg = f"Failed to input text into field '{field_name}': {e}"
        allure.attach(error_msg, name="Input Action Error", attachment_type=allure.attachment_type.TEXT)
        _attach_screenshot(f"Error - Input {field_name}")
        raise WebError(error_msg) from e


@allure.step("Web: Business verification: I verify {text}")
def business_verification_with_screenshot(text: str):
    """
    Web: Business verification: I verify {text}
    
    Business verification step with page load waiting and screenshot capture.
    Equivalent to BrowserGlobal.iWaitForPageToLoad_d365() and iTakeScreenshotWithComment()
    
    Args:
        text: Text to verify on the page
    """
    try:
        # Wait for page to load (equivalent to BrowserGlobal.iWaitForPageToLoad_d365())
        _wait_for_page_to_load()
        
        # Verify text exists on the page
        page_source = _get_driver().page_source
        text_found = text in page_source
        
        if text_found:
            # Success - take screenshot with success comment
            _attach_screenshot(f"Business Verification SUCCESS - Found: {text}")
            allure.attach(f"Verification text: '{text}'\nResult: FOUND\nStatus: SUCCESS", 
                         name="Business Verification Success", attachment_type=allure.attachment_type.TEXT)
        else:
            # Failure - take screenshot with error comment  
            _attach_screenshot(f"Business Verification FAILED - Not found: {text}")
            allure.attach(f"Verification text: '{text}'\nResult: NOT FOUND\nStatus: FAILED", 
                         name="Business Verification Failed", attachment_type=allure.attachment_type.TEXT)
            raise WebError(f"Business verification failed: Text '{text}' not found on page")
            
    except Exception as e:
        # Error during verification - capture screenshot
        error_msg = f"Business verification error for text '{text}': {e}"
        _attach_screenshot(f"Business Verification ERROR - {text}")
        allure.attach(error_msg, name="Business Verification Error", attachment_type=allure.attachment_type.TEXT)
        raise WebError(error_msg) from e


def _wait_for_page_to_load(timeout: int = 30):
    """
    Wait for page to load completely
    Equivalent to BrowserGlobal.iWaitForPageToLoad_d365()
    
    Args:
        timeout: Maximum time to wait in seconds
    """
    try:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        driver = _get_driver()
        wait = WebDriverWait(driver, timeout)
        
        # Wait for document ready state
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        
        # Additional wait for any dynamic content
        time.sleep(1)
        
        allure.attach(f"Page load completed within {timeout} seconds", 
                     name="Page Load Wait", attachment_type=allure.attachment_type.TEXT)
        
    except Exception as e:
        error_msg = f"Page load wait failed after {timeout} seconds: {e}"
        allure.attach(error_msg, name="Page Load Wait Error", attachment_type=allure.attachment_type.TEXT)
        # Don't raise exception, just log the warning
        print(f"Warning: {error_msg}")