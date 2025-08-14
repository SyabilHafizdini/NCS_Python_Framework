# Automation Library Demo - Comprehensive Function Showcase
# =========================================================
#
# This feature file demonstrates the complete automation library functionality
# including BrowserGlobal core functions and Web pattern-based interactions.
# 
# The demo covers:
# - Browser Management & Navigation
# - Element Interactions (Traditional + Pattern-based)
# - Text Input & Form Handling
# - Verification & Validation (Soft + Hard)
# - Wait Operations & Synchronization
# - Screenshot & Documentation
# - Data Management & Context
# - Advanced Pattern Locator Usage

@demo @automation-library @showcase
Feature: Automation Library Complete Demonstration
  As a QA Automation Engineer
  I want to demonstrate all automation library functions
  So that I can showcase the comprehensive testing capabilities

  Background:
    Given I set page name loginPage

  # ==========================================================================
  # BROWSER MANAGEMENT & BASIC INTERACTIONS DEMO
  # ==========================================================================
  
  @browser-management @demo-basic
  Scenario: Browser Management and Basic Interactions Demo
    # Browser initialization with different options
    When I take screenshot with comment Starting browser management demo
    
    # Open browser with maximized window (most common approach)
    Given I open web browser with https://www.saucedemo.com/v1/ and maximise window
    And I take screenshot with comment Browser opened and maximized
    
    # Basic element interactions using traditional locators
    When I fill standard_user into xpath=//input[@id='user-name']
    And I take screenshot with comment Username entered
    
    When I fill secret_sauce into xpath=//input[@id='password']
    And I take screenshot with comment Password entered
    
    When I click on xpath=//input[@id='login-button']
    And I take screenshot with comment Login button clicked
    
    # Wait for page transition
    When I wait for 2 seconds
    
    # Verification using traditional methods
    Then I verify xpath=//div[@class='inventory_list'] is present
    And I take screenshot with comment Login verification completed
    
    # Browser cleanup
    Then I close web browser

  # ==========================================================================
  # PATTERN LOCATOR SYSTEM DEMO
  # ==========================================================================
  
  @pattern-locators @demo-advanced @TestCaseId:PATTERN_001 @PRIORITY:HIGH
  Scenario: Pattern Locator System Comprehensive Demo
    # Initialize browser for pattern demo
    Given I open web browser with https://www.saucedemo.com/v1/ and take screenshot
    And I set page name loginPage
    And I take screenshot with comment Pattern locator demo starting
    
    # Pattern-based text input (uses dynamic locators)
    When I input text using pattern value standard_user field Username
    And I take screenshot with comment Username entered using pattern locator
    
    When I input text using pattern value secret_sauce field Password  
    And I take screenshot with comment Password entered using pattern locator
    
    # Pattern-based button clicking
    When I click button using pattern field Login
    And I take screenshot with comment Login clicked using pattern locator
    
    # Wait for navigation
    When I wait for 3 seconds
    
    # Change page context for dashboard
    When I set page name dashboardPage
    
    # Pattern-based verification on dashboard
    Then I verify element using pattern text field Products is present
    And I take screenshot with comment Dashboard verification using pattern locators
    
    # Verify page content using Web module
    Then I verify page contains text Products
    And I take screenshot with comment Page content verification completed
    
    Then I close web browser

  # ==========================================================================
  # MIXED APPROACH DEMO (Traditional + Pattern-based)
  # ==========================================================================
  
  @mixed-approach @demo-comprehensive @TestCaseId:MIXED_001 @PRIORITY:CRITICAL  
  Scenario: Mixed Traditional and Pattern-based Approach Demo
    # Start with traditional browser opening
    Given I open the web browser with https://www.saucedemo.com/v1/ maximise window and take screenshot
    
    # Set context for pattern locators
    And I set page name loginPage
    
    # Mix of traditional and pattern-based approaches
    When I clear and fill standard_user into xpath=//input[@id='user-name']
    And I take screenshot with comment Traditional clear and fill for username
    
    When I clear and fill using pattern value secret_sauce field Password
    And I take screenshot with comment Pattern-based clear and fill for password
    
    # Traditional click
    When I click on xpath=//input[@id='login-button']
    And I take screenshot with comment Traditional login click
    
    # Wait and verify using both approaches
    When I wait until element xpath=//div[@class='inventory_list'] is visible
    And I take screenshot with comment Traditional wait completed
    
    # Switch context and use pattern verification
    When I set page name dashboardPage
    Then I verify element using pattern text field Products is present
    
    # Traditional assertion (hard verification)
    Then I assert xpath=//span[text()='Products'] is present
    And I assert xpath=//span[text()='Products'] text is Products
    
    # Final screenshot and cleanup
    And I take screenshot with comment Mixed approach demo completed successfully
    Then I close web browser

  # ==========================================================================
  # ERROR HANDLING & EDGE CASES DEMO
  # ==========================================================================
  
  @error-handling @demo-edge-cases @TestCaseId:ERROR_001 @PRIORITY:MEDIUM
  Scenario: Error Handling and Edge Cases Demo
    Given I open web browser with https://www.saucedemo.com/v1/ and maximise window
    And I set page name loginPage
    And I take screenshot with comment Error handling demo starting
    
    # Demonstrate invalid login scenario
    When I input text using pattern value invalid_user field Username
    And I input text using pattern value wrong_password field Password
    And I click button using pattern field Login
    And I wait for 2 seconds
    
    # Verify error state (expecting to remain on login page)
    Then I verify xpath=//h3[@data-test='error'] is present
    And I take screenshot with comment Error message verified
    
    # Clear error and try valid login
    When I clear and fill standard_user into xpath=//input[@id='user-name']
    And I clear and fill using pattern value secret_sauce field Password
    And I click button using pattern field Login
    And I wait for 3 seconds
    
    # Verify successful navigation
    When I set page name dashboardPage
    Then I verify page contains text Products
    And I take screenshot with comment Recovery from error completed
    
    Then I close web browser

  # ==========================================================================
  # ADVANCED FEATURES DEMO
  # ==========================================================================
  
  @advanced-features @demo-complex @TestCaseId:ADVANCED_001 @PRIORITY:LOW
  Scenario: Advanced Automation Features Demo
    # Custom window size demonstration
    Given I open the web browser with https://www.saucedemo.com/v1/ and window size 1280 x 720
    And I take screenshot with comment Custom window size 1280x720
    
    And I set page name loginPage
    
    # Scrolling demonstration (scroll to element)
    When I scroll to element xpath=//input[@id='login-button']
    And I take screenshot with comment Scrolled to login button
    
    # Advanced text input with screenshots
    When I fill standard_user into xpath=//input[@id='user-name']
    And I take screenshot with comment Username filled with documentation
    
    When I input text using pattern value secret_sauce field Password
    And I take screenshot with comment Password filled using pattern
    
    # Click and immediate screenshot
    When I click button using pattern field Login
    And I take screenshot with comment Immediate post-click screenshot
    
    # Advanced wait with custom timing
    When I wait for 5 seconds
    
    # Context switching and verification
    When I set page name dashboardPage
    
    # Multiple verification approaches
    Then I verify page contains text Products
    And I verify element using pattern text field Products is present  
    And I assert xpath=//span[text()='Products'] text is Products
    
    # Final comprehensive screenshot
    And I take screenshot with comment Advanced features demo completed successfully
    
    Then I close web browser

  # ==========================================================================
  # COMPREHENSIVE WORKFLOW DEMO
  # ==========================================================================
  
  @comprehensive-workflow @demo-end-to-end @TestCaseId:WORKFLOW_001 @PRIORITY:CRITICAL
  Scenario: Complete E2E Workflow with All Library Functions
    # === PHASE 1: SETUP AND NAVIGATION ===
    Given I open web browser with https://www.saucedemo.com/v1/ and take screenshot
    And I set page name loginPage
    
    # === PHASE 2: LOGIN PROCESS ===
    When I input text using pattern value standard_user field Username
    And I input text using pattern value secret_sauce field Password
    And I take screenshot with comment Login credentials entered
    
    When I click button using pattern field Login
    And I wait until element xpath=//div[@class='inventory_list'] is visible
    
    # === PHASE 3: DASHBOARD VERIFICATION ===
    When I set page name dashboardPage
    Then I verify page contains text Products
    And I verify element using pattern text field Products is present
    And I take screenshot with comment Dashboard loaded successfully
    
    # === PHASE 4: PRODUCT INTERACTION ===
    When I scroll to element xpath=//div[@class='inventory_item'][1]
    And I take screenshot with comment First product in view
    
    When I click on xpath=//div[@class='inventory_item'][1]//button[contains(@id,'add-to-cart')]
    And I take screenshot with comment Product added to cart
    
    # === PHASE 5: CART VERIFICATION ===
    When I click on xpath=//a[@class='shopping_cart_link']
    And I wait for 2 seconds
    
    Then I verify xpath=//div[@class='cart_list'] is present
    And I take screenshot with comment Cart page verified
    
    # === PHASE 6: COMPREHENSIVE VALIDATION ===
    Then I assert xpath=//span[@class='title'] text is Your Cart
    And I verify page contains text Sauce Labs Backpack
    
    # === PHASE 7: FINAL DOCUMENTATION ===
    And I take screenshot with comment Complete E2E workflow finished successfully
    
    Then I close web browser

  # ==========================================================================
  # NEGATIVE TESTING DEMO
  # ==========================================================================
  
  @negative-testing @demo-validation @TestCaseId:NEGATIVE_001
  Scenario: Negative Testing and Validation Demo
    Given I open web browser with https://www.saucedemo.com/v1/ and maximise window
    And I set page name loginPage
    And I take screenshot with comment Negative testing demo starting
    
    # Test with empty credentials
    When I click button using pattern field Login
    And I wait for 1 seconds
    
    # Verify error handling
    Then I verify xpath=//h3[@data-test='error'] is present
    And I take screenshot with comment Empty credentials error verified
    
    # Test with invalid credentials
    When I input text using pattern value locked_out_user field Username
    And I input text using pattern value secret_sauce field Password
    And I click button using pattern field Login
    And I wait for 2 seconds
    
    # Verify locked out message
    Then I verify page contains text locked out
    And I take screenshot with comment Locked out user error verified
    
    # Clear and test valid credentials for recovery
    When I clear and fill standard_user into xpath=//input[@id='user-name']
    And I clear and fill using pattern value secret_sauce field Password
    And I click button using pattern field Login
    
    # Verify successful recovery
    When I wait until element xpath=//div[@class='inventory_list'] is visible
    When I set page name dashboardPage
    Then I verify element using pattern text field Products is present
    And I take screenshot with comment Recovery after negative tests successful
    
    Then I close web browser