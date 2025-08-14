# WebDriver Setup

This directory contains WebDriver executables for local browser automation.

## ChromeDriver Setup

1. **Check your Chrome version:**
   ```bash
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --version
   ```

2. **Download matching ChromeDriver:**
   - Visit: https://chromedriver.chromium.org/
   - Download the version that matches your Chrome browser
   - For Chrome 115+, use: https://googlechromelabs.github.io/chrome-for-testing/

3. **Extract and place:**
   - Extract `chromedriver.exe` to this `/drivers` directory
   - Ensure the file is named exactly `chromedriver.exe`

## Other Drivers (Optional)

### Firefox (GeckoDriver)
- Download from: https://github.com/mozilla/geckodriver/releases
- Place as `drivers/geckodriver.exe`

### Edge (EdgeDriver)  
- Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
- Place as `drivers/msedgedriver.exe`

## Directory Structure
```
drivers/
├── README.md
├── chromedriver.exe    # Required for Chrome tests
├── geckodriver.exe     # Optional for Firefox tests
└── msedgedriver.exe    # Optional for Edge tests
```

## Troubleshooting

### Version Mismatch
If you get "version mismatch" errors:
1. Check your browser version
2. Download the exact matching driver version
3. Replace the old driver file

### Permission Issues
If you get "permission denied" errors:
1. Ensure the executable has proper permissions
2. Run as administrator if needed
3. Check antivirus software isn't blocking the driver

### Path Issues
- Always use forward slashes or double backslashes in paths
- Ensure the driver filename matches exactly what's in the code