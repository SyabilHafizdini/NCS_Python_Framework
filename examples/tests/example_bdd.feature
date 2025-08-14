Feature: Example BDD Test
  As a user
  I want to login to the application
  So that I can access the system

  Scenario: Successful login with valid credentials
    Given I navigate to the demo application
    When I enter username "standard_user" in the username field
    And I enter password "secret_sauce" in the password field
    And I click the login button
    Then I should see "Products" on the page
    And I should be on the inventory page