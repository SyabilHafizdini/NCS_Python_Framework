# SPF NGEN Simple Demo Test
# Working demo test case to verify framework functionality

@demo
Feature: SPF NGEN Login Test
  As a QA engineer
  I want to test the login functionality
  So that I can verify the application works

  @demo
  @smoke
  @TestCaseId:DEMO_001
  @PRIORITY:CRITICAL
  Scenario: Valid User Login Syabil from Demo 3
    Given I navigate to the SPF NGEN login page
    When I enter username "standard_user" using pattern locator
    And I enter password "secret_sauce" using pattern locator  
    And I click the Login button using pattern locator
    Then I should be redirected to the dashboard
    And I should see welcome message on dashboard


  # @demo
  # @smoke
  # @TestCaseId:DEMO_002
  # @negative
  # Scenario: Invalid User Login Syabil
  #   Given I navigate to the SPF NGEN login page
  #   When I enter username "invalid_user" using pattern locator
  #   And I enter password "wrong_password" using pattern locator
  #   And I click the Login button using pattern locator
  #   Then I should remain on the login page