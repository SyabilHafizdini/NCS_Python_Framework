# Template BDD feature file
# Copy this file and modify for your test needs

@web @your-app-tag
Feature: Your Feature Name
  As a user
  I want to perform some action
  So that I can achieve some goal

  Background:
    Given I navigate to the application

  @smoke @positive
  Scenario: Positive test case scenario
    Given I am on the login page
    When I enter valid credentials
    And I click the login button
    Then I should see the dashboard
    And I should see welcome message

  @smoke @negative  
  Scenario: Negative test case scenario
    Given I am on the login page
    When I enter invalid credentials
    And I click the login button
    Then I should see an error message
    And I should remain on the login page

  @regression
  Scenario Outline: Data-driven test scenario
    Given I am on the login page
    When I enter username '<username>' and password '<password>'
    And I click the login button
    Then I should see '<expected_result>'

    Examples:
      | username     | password      | expected_result |
      | valid_user   | valid_pass    | dashboard       |
      | invalid_user | invalid_pass  | error_message   |
      | empty_user   |               | validation_error|

  @accessibility
  Scenario: Accessibility test scenario
    Given I am on the login page
    Then the username field should be accessible
    And the password field should be accessible
    And the login button should be accessible