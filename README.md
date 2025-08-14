# QAF Python Automation Framework

A comprehensive test automation framework built on Python 3.x for Web, Mobile Web, Mobile Hybrid apps, Mobile Native apps, and web services testing. The framework integrates with pytest, WebDriver, and Appium to provide BDD support using QAF BDD2.

## 🚀 Quick Start

### Prerequisites
- Python 3.6+ installed
- Chrome browser (for web testing)

### Installation
```bash
# 1. Create virtual environment
python -m venv venv_msvc
venv_msvc\Scripts\activate  # Windows
# source venv_msvc/bin/activate   # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt
```

### Run Your First Test
```bash
# Activate virtual environment
venv_msvc\Scripts\activate

# Run example test
venv_msvc/Scripts/python.exe -m behave tests/simple_demo.feature -f allure_behave.formatter:AllureFormatter -o reports/allure-results

# View test report
allure serve reports/allure-results
```

## 📁 Project Structure

```
NCS_Python_Framework/
├── 📁 config/                          # Configuration files
│   ├── behave.ini                       # Behave configuration
│   ├── pytest.ini                      # pytest configuration  
│   └── test-runner/                    # XML test runners (demo, smoke, regression)
│
├── 📁 docs/                            # Complete documentation
│   ├── getting-started/                # Installation, quick-start, first test
│   ├── user-guide/                     # Framework & automation library guides
│   ├── tutorials/                      # Pattern locators tutorial
│   ├── api/                           # API reference documentation
│   └── reference/                     # Configuration & troubleshooting
│
├── 📁 examples/                        # Example implementations
│   ├── pattern_locator_example.py     # Pattern locator examples
│   └── tests/                         # Example test files
│
├── 📁 qaf/                            # QAF Framework Core (245+ functions)
│   └── automation/                    # Core automation components
│       ├── ui/util/pattern_locator.py # Dynamic pattern locator system
│       └── step_def/                  # Common step definitions
│
├── 📁 reports/                        # Test reports and results
│   ├── allure-results/               # Allure test results
│   └── test-results/                 # Other test results
│
├── 📁 resources/                      # Test resources and configuration
│   ├── locators/                     # Pattern locator definitions
│   ├── test_data/                    # Test data files (CSV, Excel, JSON)
│   └── project_config.properties     # Main framework configuration
│
├── 📁 tests/                         # Main test directory
│   ├── automation_library/           # 245+ reusable automation functions
│   │   ├── BrowserGlobal.py          # Browser automation (182+ functions)
│   │   └── Web.py                    # Pattern-based web functions (63+ functions)
│   ├── steps/                        # BDD step definitions
│   ├── *.feature                    # BDD feature files
│   └── Examples/                     # Example test cases
│
├── 📄 CLAUDE.md                      # Framework usage instructions
├── 📄 requirements.txt               # Python dependencies
└── 📄 run_tests.py                   # Test execution script
```

## ✍️ Writing Tests

### Option 1: Using Automation Library (Recommended)
```python
from tests.automation_library import BrowserGlobal as BG
from tests.automation_library import Web

def test_login_with_automation_library():
    # Use 245+ pre-built functions
    BG.open_browser("https://www.saucedemo.com/v1/")
    BG.maximize_window()
    
    # Pattern-based element interaction
    Web.input_text_using_pattern("standard_user", "Username", "loginPage")
    Web.input_text_using_pattern("secret_sauce", "Password", "loginPage") 
    Web.click_button_using_pattern("Login", "loginPage")
    
    # Verification
    Web.verify_page_contains_text("Products")
    BG.close_browser()
```

### Option 2: BDD Style
```gherkin
Feature: Login Functionality
  Scenario: Valid User Login
    Given I open web browser with https://www.saucedemo.com/v1/ and maximise window
    When I input text using pattern value standard_user field Username
    And I input text using pattern value secret_sauce field Password  
    And I click button using pattern field Login
    Then I verify page contains text Products
```

### Option 3: Standard Selenium
```python
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class TestLogin:
    def setup_method(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        
    def teardown_method(self):
        self.driver.quit()
        
    @pytest.mark.smoke
    def test_login(self):
        self.driver.get("https://www.saucedemo.com/v1/")
        # Your test steps here
```

## 💻 Running Tests

```bash
# Always activate virtual environment first
venv_msvc\Scripts\activate.bat

# Run all tests with Allure reporting
python -m pytest tests/ -v --alluredir=reports/allure-results

# Run specific test file
python -m pytest tests/simple_library_demo.feature -v

# Run by markers
python -m pytest -m smoke tests/

# Run BDD tests
python -m behave tests/ -f allure_behave.formatter:AllureFormatter -o reports/allure-results

# View interactive report
allure serve reports/allure-results
```

## 🎯 Key Features

### 1. **245+ Reusable Functions**
Pre-built automation functions in `tests/automation_library/`:
- **BrowserGlobal.py**: 182+ browser automation functions
- **Web.py**: 63+ pattern-based web functions

### 2. **Dynamic Pattern Locators**
Smart element identification that generates XPath dynamically:
```python
# Instead of hardcoded locators, use patterns
Web.click_button_using_pattern("Login", "loginPage")
# Automatically generates multiple fallback XPath strategies
```

### 3. **Comprehensive Reporting**
- **Allure Reports**: Interactive dashboards with screenshots
- **Automatic Screenshots**: On every step and failure
- **Step-by-step Logging**: Detailed execution traces

### 4. **Multi-Format Support**
- **pytest**: Standard Python testing
- **BDD/Gherkin**: Business-readable scenarios  
- **XML Test Runners**: Organized test suites

## ⚙️ Configuration

Main configuration in `resources/project_config.properties`:

```properties
# Browser settings
driver.name=chromeDriver
selenium.wait.timeout=30

# Pattern locator system
loc.pattern.enabled=true
loc.pattern.code=loc.qaf

# Application settings  
env.baseurl=https://www.saucedemo.com/v1/

# Reporting
allure.results.directory=reports/allure-results
```

## 📚 Documentation

Complete documentation available in `docs/` directory:

- **[Getting Started](docs/getting-started/)**: Installation, quick start, first test
- **[User Guide](docs/user-guide/)**: Framework guide and automation library
- **[Tutorials](docs/tutorials/)**: Pattern locators deep dive
- **[API Reference](docs/api/)**: Complete function documentation
- **[Reference](docs/reference/)**: Configuration and troubleshooting

## 🐛 Troubleshooting

**Virtual environment issues:**
```bash
# Recreate environment
rm -rf venv_msvc
python -m venv venv_msvc
venv_msvc\Scripts\activate.bat
pip install -r requirements.txt
```

**Test failures:**
- Check `reports/allure-results` for detailed error information
- Verify application URLs are accessible  
- Review pattern locator configurations in `resources/locators/`

**More help:** See [Troubleshooting Guide](docs/reference/troubleshooting.md)

## 🎯 Best Practices

1. **Use the automation library** for consistent, maintainable tests
2. **Leverage pattern locators** instead of hardcoded selectors
3. **Always activate virtual environment** before running tests
4. **Use meaningful test names** and pytest markers
5. **Keep tests independent** - each should run standalone
6. **Follow BDD practices** for business-readable scenarios

## 📊 Example Output

When you run tests, you'll see rich reporting:

```
======= test session starts =======
tests/simple_library_demo.feature::Valid User Login using Automation Library PASSED [100%]

======= 1 passed in 15.23s =======

# Open interactive report
allure serve reports/allure-results
```

The Allure report provides:
- 📊 Interactive dashboards and trends
- 📷 Automatic screenshots at each step  
- 📋 Detailed execution logs
- 📈 Test statistics and history
- 🔍 Attachments and debugging info

## 🚀 Getting Started Quickly

1. **Read**: [Installation Guide](docs/getting-started/installation.md)
2. **Follow**: [Quick Start](docs/getting-started/quick-start.md)  
3. **Try**: [First Test Tutorial](docs/getting-started/first-test.md)
4. **Explore**: [Automation Library](docs/user-guide/automation-library.md)

---

**Happy Testing!** 🎉

*This framework provides enterprise-grade automation with 245+ pre-built functions, pattern locators, and comprehensive reporting.*