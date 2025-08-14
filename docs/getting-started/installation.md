# Installation Guide

## Prerequisites

Before installing the QAF Python Automation Framework, ensure you have:

- Python 3.6 or higher
- pip package manager
- Git (for cloning the repository)

## System Requirements

### Supported Operating Systems
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+, CentOS 7+)

### Hardware Requirements
- Minimum 4GB RAM (8GB recommended)
- 2GB free disk space
- Internet connection for downloading dependencies

## Installation Methods

### Method 1: Direct Installation from PyPI

```bash
pip install qaf-python
```

### Method 2: Install from Source

1. Clone the repository:
```bash
git clone https://github.com/qmetry/qaf-python.git
cd qaf-python
```

2. Install in development mode:
```bash
pip install -e .
```

### Method 3: Using requirements.txt

1. Download or clone the framework
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Core Dependencies

The framework automatically installs these dependencies:

```
selenium~=4.9.1
Appium-Python-Client~=2.10.1
pytest~=7.3.1
behave~=1.2.6
requests~=2.31.0
webdriver-manager~=3.8.6
allure-pytest~=2.13.2
allure-behave~=2.13.2
```

## WebDriver Setup

The framework uses `webdriver-manager` for automatic driver management. No manual driver downloads required!

### Supported Browsers
- Chrome (default)
- Firefox
- Edge
- Safari

### Browser Configuration

Create a `project_config.properties` file:
```properties
# Browser settings
driver.name=chromeDriver
selenium.wait.timeout=30

# Remote execution (optional)
remote.server=localhost
remote.port=4444

# Application settings
env.baseurl=https://your-app-url.com
```

## Virtual Environment Setup (Recommended)

### Windows
```cmd
python -m venv qaf-env
qaf-env\Scripts\activate
pip install -r requirements.txt
```

### macOS/Linux
```bash
python3 -m venv qaf-env
source qaf-env/bin/activate
pip install -r requirements.txt
```

## Verification

Verify your installation by running:

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(selenium|pytest|behave|allure)"

# Run a simple test
python -c "from selenium import webdriver; print('QAF Python Framework installed successfully!')"
```

## IDE Configuration

### VS Code
Install recommended extensions:
- Python
- Cucumber (Gherkin) Full Support
- Test Explorer UI

### PyCharm
1. Configure Python interpreter to point to your virtual environment
2. Install Gherkin plugin
3. Set test runner to pytest

## Troubleshooting

### Common Issues

**ImportError: No module named 'selenium'**
```bash
pip install --upgrade selenium
```

**WebDriver not found**
- Framework handles this automatically via webdriver-manager
- Check internet connectivity if downloads fail

**Permission Issues**
```bash
# Windows
pip install --user -r requirements.txt

# macOS/Linux
sudo pip install -r requirements.txt
```

**Port conflicts for remote WebDriver**
```bash
# Check if port 4444 is in use
netstat -an | grep 4444
```

### Getting Help

If you encounter issues:
1. Check the [Troubleshooting Guide](../reference/troubleshooting.md)
2. Review [FAQ](../reference/faq.md)
3. Submit an issue on GitHub

## Next Steps

After successful installation:
1. Follow the [Quick Start Guide](quick-start.md)
2. Create your [First Test](first-test.md)
3. Explore [Basic Usage Examples](../examples/basic-usage.md)