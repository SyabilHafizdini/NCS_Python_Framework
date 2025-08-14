#  Copyright (c) 2022 Infostretch Corporation
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  #
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

"""
Pattern-based step definitions for QAF framework
Provides BDD steps that use dynamic locator generation
"""

from qaf.automation.bdd2.step_registry import step
from qaf.automation.core.test_base import get_driver
from qaf.automation.step_def.common_steps import *
from qaf.automation.ui.util.pattern_locator import get_pattern_locator
from qaf.automation.ui.webdriver.qaf_web_element import QAFWebElement


# Input field operations using pattern locators
@step("enter {text} in {field_name} on {page}")
@step("type {text} in {field_name} on {page}")
def enter_text_in_field(text: str, field_name: str, page: str):
    """Enter text in input field using pattern locator"""
    locator = get_pattern_locator().input(page, field_name)
    element = QAFWebElement(get_driver(), locator)
    element.clear()
    element.send_keys(text)


@step("enter {text} in {field_name} with value {field_value} on {page}")
def enter_text_in_field_with_value(text: str, field_name: str, field_value: str, page: str):
    """Enter text in input field using pattern locator with field value"""
    locator = get_pattern_locator().input(page, field_name, field_value)
    element = QAFWebElement(get_driver(), locator)
    element.clear()
    element.send_keys(text)


# Button operations using pattern locators
@step("click {button_name} button on {page}")
@step("click {button_name} on {page}")
def click_button(button_name: str, page: str):
    """Click button using pattern locator"""
    locator = get_pattern_locator().button(page, button_name)
    element = QAFWebElement(get_driver(), locator)
    element.click()


@step("click {button_name} button with value {button_value} on {page}")
def click_button_with_value(button_name: str, button_value: str, page: str):
    """Click button using pattern locator with button value"""
    locator = get_pattern_locator().button(page, button_name, button_value)
    element = QAFWebElement(get_driver(), locator)
    element.click()


# Link operations using pattern locators
@step("click {link_name} link on {page}")
def click_link(link_name: str, page: str):
    """Click link using pattern locator"""
    locator = get_pattern_locator().link(page, link_name)
    element = QAFWebElement(get_driver(), locator)
    element.click()


@step("click {link_name} link with href {href_value} on {page}")
def click_link_with_href(link_name: str, href_value: str, page: str):
    """Click link using pattern locator with href value"""
    locator = get_pattern_locator().link(page, link_name, href_value)
    element = QAFWebElement(get_driver(), locator)
    element.click()


# Checkbox operations using pattern locators
@step("check {checkbox_name} checkbox on {page}")
def check_checkbox(checkbox_name: str, page: str):
    """Check checkbox using pattern locator"""
    locator = get_pattern_locator().checkbox(page, checkbox_name)
    element = QAFWebElement(get_driver(), locator)
    if not element.is_selected():
        element.click()


@step("uncheck {checkbox_name} checkbox on {page}")
def uncheck_checkbox(checkbox_name: str, page: str):
    """Uncheck checkbox using pattern locator"""
    locator = get_pattern_locator().checkbox(page, checkbox_name)
    element = QAFWebElement(get_driver(), locator)
    if element.is_selected():
        element.click()


@step("toggle {checkbox_name} checkbox on {page}")
def toggle_checkbox(checkbox_name: str, page: str):
    """Toggle checkbox using pattern locator"""
    locator = get_pattern_locator().checkbox(page, checkbox_name)
    element = QAFWebElement(get_driver(), locator)
    element.click()


# Radio button operations using pattern locators
@step("select {radio_name} radio button on {page}")
def select_radio_button(radio_name: str, page: str):
    """Select radio button using pattern locator"""
    locator = get_pattern_locator().radio(page, radio_name)
    element = QAFWebElement(get_driver(), locator)
    element.click()


@step("select {radio_name} radio button with value {radio_value} on {page}")
def select_radio_button_with_value(radio_name: str, radio_value: str, page: str):
    """Select radio button using pattern locator with specific value"""
    locator = get_pattern_locator().radio(page, radio_name, radio_value)
    element = QAFWebElement(get_driver(), locator)
    element.click()


# Select dropdown operations using pattern locators
@step("select {option_text} from {select_name} dropdown on {page}")
def select_from_dropdown(option_text: str, select_name: str, page: str):
    """Select option from dropdown using pattern locator"""
    from selenium.webdriver.support.ui import Select
    locator = get_pattern_locator().select(page, select_name)
    element = QAFWebElement(get_driver(), locator)
    select = Select(element)
    select.select_by_visible_text(option_text)


@step("select option with value {option_value} from {select_name} dropdown on {page}")
def select_from_dropdown_by_value(option_value: str, select_name: str, page: str):
    """Select option from dropdown by value using pattern locator"""
    from selenium.webdriver.support.ui import Select
    locator = get_pattern_locator().select(page, select_name)
    element = QAFWebElement(get_driver(), locator)
    select = Select(element)
    select.select_by_value(option_value)


# Text verification using pattern locators
@step("verify {expected_text} text is present in {element_name} on {page}")
def verify_text_present(expected_text: str, element_name: str, page: str):
    """Verify text is present in element using pattern locator"""
    locator = get_pattern_locator().text(page, element_name)
    element = QAFWebElement(get_driver(), locator)
    actual_text = element.get_text()
    assert expected_text in actual_text, f"Expected text '{expected_text}' not found in '{actual_text}'"


@step("verify {expected_text} is displayed on {page}")
def verify_text_displayed(expected_text: str, page: str):
    """Verify text is displayed on page using pattern locator"""
    locator = get_pattern_locator().text(page, expected_text)
    element = QAFWebElement(get_driver(), locator)
    assert element.is_displayed(), f"Text '{expected_text}' is not displayed on page '{page}'"


# Element presence and visibility using pattern locators
@step("verify {element_name} {element_type} is present on {page}")
def verify_element_present(element_name: str, element_type: str, page: str):
    """Verify element is present using pattern locator"""
    pattern_locator = get_pattern_locator()
    
    # Get appropriate locator based on element type
    if element_type.lower() == 'input':
        locator = pattern_locator.input(page, element_name)
    elif element_type.lower() == 'button':
        locator = pattern_locator.button(page, element_name)
    elif element_type.lower() == 'link':
        locator = pattern_locator.link(page, element_name)
    elif element_type.lower() == 'checkbox':
        locator = pattern_locator.checkbox(page, element_name)
    elif element_type.lower() == 'select':
        locator = pattern_locator.select(page, element_name)
    else:
        locator = pattern_locator.element(page, element_name)
    
    element = QAFWebElement(get_driver(), locator)
    assert element.is_present(), f"{element_type} '{element_name}' is not present on page '{page}'"


@step("verify {element_name} {element_type} is visible on {page}")
def verify_element_visible(element_name: str, element_type: str, page: str):
    """Verify element is visible using pattern locator"""
    pattern_locator = get_pattern_locator()
    
    # Get appropriate locator based on element type
    if element_type.lower() == 'input':
        locator = pattern_locator.input(page, element_name)
    elif element_type.lower() == 'button':
        locator = pattern_locator.button(page, element_name)
    elif element_type.lower() == 'link':
        locator = pattern_locator.link(page, element_name)
    elif element_type.lower() == 'checkbox':
        locator = pattern_locator.checkbox(page, element_name)
    elif element_type.lower() == 'select':
        locator = pattern_locator.select(page, element_name)
    else:
        locator = pattern_locator.element(page, element_name)
    
    element = QAFWebElement(get_driver(), locator)
    assert element.is_displayed(), f"{element_type} '{element_name}' is not visible on page '{page}'"


# Wait operations using pattern locators
@step("wait for {element_name} {element_type} to be present on {page}")
def wait_for_element_present(element_name: str, element_type: str, page: str):
    """Wait for element to be present using pattern locator"""
    pattern_locator = get_pattern_locator()
    
    # Get appropriate locator based on element type
    if element_type.lower() == 'input':
        locator = pattern_locator.input(page, element_name)
    elif element_type.lower() == 'button':
        locator = pattern_locator.button(page, element_name)
    elif element_type.lower() == 'link':
        locator = pattern_locator.link(page, element_name)
    elif element_type.lower() == 'checkbox':
        locator = pattern_locator.checkbox(page, element_name)
    elif element_type.lower() == 'select':
        locator = pattern_locator.select(page, element_name)
    else:
        locator = pattern_locator.element(page, element_name)
    
    element = QAFWebElement(get_driver(), locator)
    element.wait_for_present()


@step("wait for {element_name} {element_type} to be visible on {page}")
def wait_for_element_visible(element_name: str, element_type: str, page: str):
    """Wait for element to be visible using pattern locator"""
    pattern_locator = get_pattern_locator()
    
    # Get appropriate locator based on element type
    if element_type.lower() == 'input':
        locator = pattern_locator.input(page, element_name)
    elif element_type.lower() == 'button':
        locator = pattern_locator.button(page, element_name)
    elif element_type.lower() == 'link':
        locator = pattern_locator.link(page, element_name)
    elif element_type.lower() == 'checkbox':
        locator = pattern_locator.checkbox(page, element_name)
    elif element_type.lower() == 'select':
        locator = pattern_locator.select(page, element_name)
    else:
        locator = pattern_locator.element(page, element_name)
    
    element = QAFWebElement(get_driver(), locator)
    element.wait_for_visible()