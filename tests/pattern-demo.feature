# SauceDemo Test

@demo
Feature: Simple Login Test Case for SauceDemo

  @demo
  @TestCaseId:DEMO_001
  Scenario: Simple Login Test Case for SauceDemo with Pattern
    Given Web: Open-Browser-And-Maximise Url:"https://www.saucedemo.com/v1"
    Then Web: Input-Text Value:"standard_user" Field:"user-name"
    Then Web: Input-Text Value:"secret_sauce" Field:"password"
    Then Web: Click-Element Pattern:"input" Field:"login-button"
    Then Web: Business verification: I verify "Logged in"