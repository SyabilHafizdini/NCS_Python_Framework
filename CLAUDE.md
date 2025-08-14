# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Framework Overview

This is the QAF-Python Automation Framework, a comprehensive test automation framework built on Python 3.x for Web, Mobile Web, Mobile Hybrid apps, Mobile Native apps, and web services testing. The framework integrates with pytest, WebDriver, and Appium to provide BDD support using QAF BDD2.

## Core Architecture

### Module Structure
- `qaf/automation/core/` - Core framework components including TestBase, configurations, and reporting
- `qaf/automation/ui/webdriver/` - WebDriver abstraction layer with enhanced element handling
- `qaf/automation/ui/util/` - UI utilities including dynamic pattern locator system
- `qaf/automation/bdd2/` - BDD implementation with step definitions and parsers
- `qaf/automation/step_def/` - Common step definitions for web and web service testing
- `qaf/automation/ws/` - Web service testing components with request/response handling
- `qaf/behave/` - Behave integration for BDD testing
- `qaf/pytest/` - Pytest plugin integration

### Key Components
- **Driver Management**: Automatic driver session creation/teardown via `driver_factory.py`
- **Test Base**: Central test execution context in `test_base.py` with command logging and checkpoints
- **Pattern Locator System**: Dynamic XPath generation using configurable patterns in `pattern_locator.py`
- **Locator Repository**: Element locator management system
- **Configuration Management**: Multi-format configuration support (ini, properties, etc.)
- **Data-Driven Testing**: CSV/JSON data provider integration

## Pattern-Based Dynamic Locator System

The framework includes a sophisticated pattern-based locator system that generates XPath locators dynamically at runtime:

### Core Pattern Components

#### 1. Pattern Configuration (`resources/locators/loc_pattern.properties`)
- Contains XPath patterns with placeholder variables like `${loc.auto.fieldName}`, `${loc.auto.fieldValue}`
- Patterns organized by element type: input, button, link, checkbox, select, etc.
- Multiple fallback locators per element type for robustness
- Example: `loc.qaf.pattern.button=xpath=//button[contains(text(),'${loc.auto.fieldName}')] | //button[@value='${loc.auto.fieldName}']`

#### 2. Pattern Processor (`qaf/automation/ui/util/pattern_locator.py`)
- **PatternLocator class**: Central component for dynamic locator generation
- Element-specific methods: `input()`, `button()`, `link()`, `checkbox()`, `select()`, etc.
- **Dynamic Generation Process:**
  1. Check for hardcoded locator first
  2. If none exists, generate using patterns
  3. Replace pattern placeholders with actual values
  4. Return single locator or JSON array for multiple fallbacks

#### 3. Pattern Configuration (`resources/project_config.properties`)
- `loc.pattern.code = loc.qaf` - defines pattern prefix
- `loc.pattern.enabled = true` - enables/disables pattern system
- Links pattern processor to pattern definitions

### Pattern Usage Examples

```python
from qaf.automation.ui.util.pattern_locator import get_pattern_locator

pattern_loc = get_pattern_locator()

# Generate locators for different element types
username_input = pattern_loc.input("loginPage", "Username")
login_button = pattern_loc.button("loginPage", "Login")
terms_checkbox = pattern_loc.checkbox("registrationPage", "Terms", "accept")
```

### Pattern-Based BDD Steps

Enhanced step definitions in `qaf/automation/step_def/pattern_steps.py`:

```gherkin
# Input operations
Given enter 'john.doe' in 'Username' on 'loginPage'
When type 'password123' in 'Password' with value 'login-pwd' on 'loginPage'

# Button operations  
Then click 'Submit' button on 'registrationPage'
And click 'Login' button with value 'login-btn' on 'loginPage'

# Element verification
Then verify 'Welcome' text is displayed on 'dashboardPage'
And verify 'Logout' button is present on 'dashboardPage'
```

## Development Commands

### Installation
```bash
pip install -r requirements.txt
# or install from source
pip install git+https://github.com/qmetry/qaf-python.git@master
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific feature files
pytest features/
pytest features/login.feature

# Run with metadata filters
pytest features -m web --metadata-filter "module == 'login'"

# Dry run mode
pytest features --dryrun
```

### Testing Pattern Locator System
```bash
# Test pattern locator functionality
python test_pattern_logic.py

# Run pattern locator examples
python examples/pattern_locator_example.py
```

### Test Development Approaches

#### BDD Style (Recommended)
Create `.feature` files in `features/` directory with Gherkin syntax and implement step definitions using `@step` decorator from `qaf.automation.bdd2`.

#### pytest Style
Use standard pytest with `@metadata` decorators for test organization and filtering.

## Configuration

### Key Properties
- `driver.name` - WebDriver to use (e.g., firefoxDriver, chromeRemoteDriver)
- `env.baseurl` - Base URL of application under test
- `selenium.wait.timeout` - Default wait timeout for framework operations
- `remote.server` / `remote.port` - Remote WebDriver server configuration
- `env.resources` - Resources directory path for locators and test data

### Environment Management
Framework supports environment-specific configuration through properties files and environment variables.

## Framework Features

- Multi-driver session support within same test
- Automatic wait/assert/verify functionality with built-in synchronization
- Command and element listeners for custom behavior
- Step retry capabilities with configurable thresholds
- Comprehensive reporting with screenshots and command logging
- Data-driven testing with external data files
- Metadata-based test filtering and organization

## Dependencies

Core dependencies managed in `requirements.txt`:
- selenium~=4.9.1
- Appium-Python-Client~=2.10.1
- pytest~=7.3.1
- behave~=1.2.6
- requests~=2.31.0

Framework requires Python 3.6+ and automatically handles WebDriver management through webdriver-manager.