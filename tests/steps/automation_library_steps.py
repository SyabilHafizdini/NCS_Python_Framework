"""
Automation Library Steps - Reusable BDD Step Definitions
========================================================

This module provides comprehensive BDD step definitions for the automation library.
All functions are now located within the tests/ directory structure for proper linking.
"""

from behave import given, when, then, step
import allure

# Import automation library from tests directory
try:
    from tests.automation_library import BrowserGlobal as BG
    from tests.automation_library import Web
    LIBRARY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Automation library not available: {e}")
    LIBRARY_AVAILABLE = False


def _ensure_library_available():
    """Ensure automation library is available"""
    if not LIBRARY_AVAILABLE:
        raise Exception("Automation library is not available")


# =============================================================================
# BROWSER MANAGEMENT STEPS
# =============================================================================

@given('I open web browser with URL {string}')
@when('I open web browser with URL {string}')
def step_open_browser(context, string):
    """I open web browser with URL {string}"""
    _ensure_library_available()
    with allure.step(f"Open web browser with URL: {string}"):
        BG.open_browser(string)


@given('I open web browser with {string} and maximise window')
@when('I open web browser with {string} and maximise window')
def step_open_browser_maximized(context, string):
    """I open web browser with {string} and maximise window"""
    _ensure_library_available()
    with allure.step(f"Open web browser maximized with URL: {string}"):
        BG.open_browser_maximized(string)


@given('I open web browser with {string} and take screenshot')
@when('I open web browser with {string} and take screenshot')
def step_open_browser_with_screenshot(context, string):
    """I open web browser with {string} and take screenshot"""
    _ensure_library_available()
    with allure.step(f"Open web browser with screenshot - URL: {string}"):
        BG.open_browser_with_screenshot(string)


@given('I open browser with {string} maximise window and take screenshot')
@when('I open browser with {string} maximise window and take screenshot')
def step_open_browser_maximized_with_screenshot(context, string):
    """I open browser with {string} maximise window and take screenshot"""
    _ensure_library_available()
    with allure.step(f"Open web browser maximized with screenshot - URL: {string}"):
        BG.open_browser_maximized_with_screenshot(string)


@when('I close web browser')
@then('I close web browser')
def step_close_browser(context):
    """I close web browser"""
    _ensure_library_available()
    with allure.step("Close web browser"):
        BG.close_browser()


# =============================================================================
# ELEMENT INTERACTION STEPS (Traditional)
# =============================================================================

@when('I click on locator {locator}')
def step_click_element(context, locator):
    """I click on {locator}"""
    _ensure_library_available()
    with allure.step(f"Click on element: {locator}"):
        BG.click_element(locator)


@when('I fill {value} into locator {locator}')
def step_fill_text(context, value, locator):
    """I fill {value} into {locator}"""
    _ensure_library_available()
    with allure.step(f"Fill '{value}' into {locator}"):
        BG.fill_text(locator, value)


@when('I clear and fill {value} into locator {locator}')
def step_clear_and_fill(context, value, locator):
    """I clear and fill {value} into {locator}"""
    _ensure_library_available()
    with allure.step(f"Clear and fill '{value}' into {locator}"):
        BG.clear_and_fill(locator, value)


# =============================================================================
# PATTERN-BASED INTERACTION STEPS (Web.py)
# =============================================================================

@when('I set page name {name}')
def step_set_page_name(context, name):
    """I set page name {name}"""
    _ensure_library_available()
    with allure.step(f"Set page name: {name}"):
        Web.set_page_name(name)


@when('I click button using pattern field {field}')
def step_click_button_pattern(context, field):
    """I click button using pattern field {field}"""
    _ensure_library_available()
    with allure.step(f"Click button using pattern - {field}"):
        Web.click_button_pattern(field)


@when('I click link using pattern field {field}')
def step_click_link_pattern(context, field):
    """I click link using pattern field {field}"""
    _ensure_library_available()
    with allure.step(f"Click link using pattern - {field}"):
        Web.click_link_pattern(field)


@when('I input text using pattern value {value} field {field}')
def step_input_text_pattern(context, value, field):
    """I input text using pattern value {value} field {field}"""
    _ensure_library_available()
    with allure.step(f"Input text using pattern - '{value}' into {field}"):
        Web.input_text_pattern(value, field)


@when('I clear and fill using pattern value {value} field {field}')
def step_clear_and_fill_pattern(context, value, field):
    """I clear and fill using pattern value {value} field {field}"""
    _ensure_library_available()
    with allure.step(f"Clear and fill using pattern - '{value}' into {field}"):
        Web.clear_and_fill_pattern(value, field)


# =============================================================================
# VERIFICATION STEPS (Traditional)
# =============================================================================

@then('I verify locator {locator} is present')
def step_verify_element_present(context, locator):
    """I verify {locator} is present"""
    _ensure_library_available()
    with allure.step(f"Verify {locator} is present"):
        result = BG.verify_element_present(locator)
        assert result, f"Element not present: {locator}"


@then('I verify locator {locator} text is {text}')
def step_verify_element_text_is(context, locator, text):
    """I verify {locator} text is {text}"""
    _ensure_library_available()
    with allure.step(f"Verify {locator} text is '{text}'"):
        result = BG.verify_element_text_is(locator, text)
        assert result, f"Element text mismatch for {locator}"


@then('I assert locator {locator} is present')
def step_assert_element_present(context, locator):
    """I assert {locator} is present"""
    _ensure_library_available()
    with allure.step(f"Assert {locator} is present"):
        BG.assert_element_present(locator)


@then('I assert locator {locator} text is {text}')
def step_assert_element_text_is(context, locator, text):
    """I assert {locator} text is {text}"""
    _ensure_library_available()
    with allure.step(f"Assert {locator} text is '{text}'"):
        BG.assert_element_text_is(locator, text)


# =============================================================================
# VERIFICATION STEPS (Pattern-based)
# =============================================================================

@then('I verify page contains text {text}')
def step_verify_page_contains_text(context, text):
    """I verify page contains text {text}"""
    _ensure_library_available()
    with allure.step(f"Verify page contains text: {text}"):
        result = Web.verify_page_contains_text(text)
        assert result, f"Page does not contain text: {text}"


@then('I verify pattern-based element {element} field {field} is present')
def step_verify_element_present_pattern(context, element, field):
    """I verify element using pattern {element} field {field} is present"""
    _ensure_library_available()
    with allure.step(f"Verify element present using pattern - {element}: {field}"):
        result = Web.verify_element_present_pattern(element, field)
        assert result, f"Element not present: {element} - {field}"


# =============================================================================
# WAIT OPERATION STEPS
# =============================================================================

@when('I wait for {secs:d} seconds')
def step_wait_seconds(context, secs):
    """I wait for {secs} seconds"""
    _ensure_library_available()
    with allure.step(f"Wait {secs} seconds"):
        BG.wait_seconds(secs)


@when('I wait until locator {locator} is visible')
def step_wait_until_element_visible(context, locator):
    """I wait until element {locator} is visible"""
    _ensure_library_available()
    with allure.step(f"Wait until {locator} is visible"):
        BG.wait_until_element_visible(locator)


# =============================================================================
# SCREENSHOT & DOCUMENTATION STEPS
# =============================================================================

@when('I take screenshot')
def step_take_screenshot(context):
    """I take screenshot"""
    _ensure_library_available()
    with allure.step("Take screenshot"):
        BG.take_screenshot()


@when('I take screenshot with comment {comment}')
def step_take_screenshot_with_comment(context, comment):
    """I take screenshot with comment {comment}"""
    _ensure_library_available()
    with allure.step(f"Take screenshot with comment: {comment}"):
        BG.take_screenshot_with_comment(comment)


# =============================================================================
# SCROLLING & NAVIGATION STEPS
# =============================================================================

@when('I scroll to locator {locator}')
def step_scroll_to_element(context, locator):
    """I scroll to element {locator}"""
    _ensure_library_available()
    with allure.step(f"Scroll to element: {locator}"):
        BG.scroll_to_element(locator)