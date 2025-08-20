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

# Import QAF system (pattern locator temporarily disabled for new implementation)
try:
    from qaf.automation.core import get_bundle
    QAF_AVAILABLE = True
except ImportError:
    QAF_AVAILABLE = False

# Pattern locator temporarily disabled for new implementation
get_pattern_locator = None

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