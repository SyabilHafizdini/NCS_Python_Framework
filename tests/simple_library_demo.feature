# Simple Automation Library Demo
# Using the same flow as tests/simple_demo.feature but with new automation library

@demo @simple
Feature: Simple Login Test using Automation Library
  As a QA engineer
  I want to test the login functionality using the automation library
  So that I can verify the reusable functions work correctly

  Background:
    Given I set page name loginPage

  @demo
  @smoke
  @TestCaseId:SIMPLE_001
  @PRIORITY:CRITICAL
  Scenario: Valid User Login using Automation Library
    Given I open web browser with https://www.saucedemo.com/v1/ and maximise window
    When I input text using pattern value standard_user field Username
    And I input text using pattern value secret_sauce field Password  
    And I click button using pattern field Login
    Then I verify page contains text Products
    And I verify element using pattern text field Products is present
    And I take screenshot with comment Login successful
    Then I close web browser

  @demo
  @smoke  
  @TestCaseId:SIMPLE_002
  @negative
  Scenario: Invalid User Login using Automation Library
    Given I open web browser with https://www.saucedemo.com/v1/ and maximise window
    When I input text using pattern value invalid_user field Username
    And I input text using pattern value wrong_password field Password
    And I click button using pattern field Login
    Then I verify page contains text Epic sadface
    And I take screenshot with comment Invalid login error shown
    Then I close web browser