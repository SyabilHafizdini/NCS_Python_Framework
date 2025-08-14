# QAF Python Framework - Project Structure

This document outlines the clean, organized structure of the QAF Python Automation Framework.

## Directory Structure

```
NCS_Python_Framework/
├── 📁 config/                          # Configuration files
│   ├── behave.ini                       # Behave configuration
│   ├── pytest.ini                      # pytest configuration  
│   ├── setup.cfg                       # Setup configuration
│   ├── conftest.py                     # pytest fixtures and configuration
│   └── test-runner/                    # XML test runners
│       ├── demo.xml
│       ├── regression.xml
│       └── smoke.xml
│
├── 📁 docs/                            # Documentation (industry standard)
│   ├── README.md                       # Documentation index
│   ├── getting-started/                # Getting started guides
│   │   ├── installation.md
│   │   ├── quick-start.md
│   │   └── first-test.md
│   ├── user-guide/                     # User guides
│   │   ├── framework-guide.md
│   │   └── automation-library.md
│   ├── tutorials/                      # Step-by-step tutorials
│   │   └── pattern-locators.md
│   ├── api/                           # API reference
│   │   └── browser-global.md
│   └── reference/                     # Reference materials
│       ├── configuration.md
│       └── troubleshooting.md
│
├── 📁 examples/                        # Example implementations
│   ├── pattern_locator_example.py     # Pattern locator examples
│   ├── tests/                         # Example test files
│   │   ├── example_login.py           # Example pytest test
│   │   └── example_bdd.feature        # Example BDD test
│   └── configs/                       # Example configurations
│
├── 📁 qaf/                            # QAF Framework Core
│   ├── automation/                    # Core automation components
│   │   ├── bdd2/                     # BDD implementation
│   │   ├── core/                     # Core framework
│   │   ├── integration/              # Integration components
│   │   ├── keys/                     # Application properties
│   │   ├── report/                   # Reporting utilities
│   │   ├── step_def/                 # Common step definitions
│   │   ├── ui/                       # UI automation
│   │   │   ├── util/                 # Pattern locators & utilities
│   │   │   └── webdriver/            # WebDriver extensions
│   │   ├── util/                     # General utilities
│   │   └── ws/                       # Web service testing
│   ├── behave/                       # Behave integration
│   └── pytest/                       # pytest integration
│
├── 📁 reports/                        # Test reports and results
│   ├── allure-results/               # Allure test results
│   └── test-results/                 # Other test results
│
├── 📁 resources/                      # Test resources and configuration
│   ├── locators/                     # Element locators
│   │   ├── loc_pattern.properties    # Pattern locator definitions
│   │   └── saucedemo.properties      # Application-specific locators
│   ├── test_data/                    # Test data files
│   │   ├── customer_search_data.csv
│   │   ├── login_test_data.csv
│   │   ├── login_test_data.xlsx
│   │   ├── role_permissions_data.csv
│   │   └── environment_config/       # Environment-specific config
│   │       ├── DEV/
│   │       └── UAT/
│   └── project_config.properties     # Main framework configuration
│
├── 📁 tests/                         # Main test directory
│   ├── automation_library/           # Reusable automation functions
│   │   ├── BrowserGlobal.py          # Browser automation functions (182+)
│   │   └── Web.py                    # Pattern-based web functions (63+)
│   ├── steps/                        # BDD step definitions
│   │   ├── automation_library_steps.py  # Steps using automation library
│   │   └── spf_ngen_steps.py        # Application-specific steps
│   ├── Examples/                     # Example test cases
│   │   ├── CM009.feature
│   │   └── CM014.feature
│   ├── *.feature                    # BDD feature files
│   ├── environment.py               # Test environment setup
│   └── __init__.py
│
├── 📁 venv_msvc/                     # Virtual environment (local)
│
├── 📄 CLAUDE.md                      # Claude AI instructions
├── 📄 LICENSE                        # License file
├── 📄 README.md                      # Main project README
├── 📄 requirements.txt               # Python dependencies
├── 📄 run_tests.py                   # Test execution script
└── 📄 setup.py                       # Package setup file
```

## Key Directories Explained

### 📁 `config/`
Contains all configuration files for different test runners and tools:
- **behave.ini**: BDD test configuration
- **pytest.ini**: pytest configuration and markers
- **test-runner/**: XML configuration files for different test suites

### 📁 `docs/`
Industry-standard documentation structure:
- **getting-started/**: New user onboarding
- **user-guide/**: Comprehensive usage guides
- **tutorials/**: Step-by-step learning materials
- **api/**: API reference documentation
- **reference/**: Configuration and troubleshooting

### 📁 `tests/`
Main testing directory with clear organization:
- **automation_library/**: 245+ reusable automation functions
- **steps/**: BDD step definitions
- **Examples/**: Example test implementations
- **\*.feature**: BDD feature files

### 📁 `qaf/`
Core framework implementation:
- **automation/ui/**: UI testing components including pattern locators
- **automation/bdd2/**: BDD framework implementation
- **automation/step_def/**: Common step definitions
- **behave/** & **pytest/**: Test runner integrations

### 📁 `resources/`
Test resources and configuration:
- **locators/**: Pattern locator definitions
- **test_data/**: Test data in various formats
- **project_config.properties**: Main framework settings

### 📁 `reports/`
Centralized location for all test reports and results

## Benefits of This Structure

1. **Clear Separation**: Each directory has a specific purpose
2. **Industry Standards**: Follows common Python project conventions
3. **Logical Grouping**: Related files are grouped together
4. **Scalable**: Easy to add new components without confusion
5. **Maintainable**: Clear structure makes maintenance easier

## Configuration Files

All configuration files are centralized in the `config/` directory:
- Test runner configurations
- Framework settings
- pytest and behave configurations

## Documentation

Complete documentation is available in the `docs/` directory following industry standards with clear user journey organization.

## Test Organization

Tests are organized in the `tests/` directory with:
- Reusable automation library
- BDD step definitions
- Feature files
- Example implementations

This structure provides a professional, maintainable framework suitable for enterprise use.