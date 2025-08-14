# SPF NGEN Demo Feature File
# Python QAF Framework - Demo Test Cases
# Follows Java QAF feature file structure with tags and annotations

@demo
Feature: SPF NGEN Application Demo Tests
  As a QA engineer
  I want to validate core SPF NGEN functionality
  So that I can ensure the application works as expected

  Background:
    Given the SPF NGEN application is accessible

  @demo
  @smoke
  @TestCaseId:DEMO_001
  @PRIORITY:CRITICAL
  @authentication
  Scenario: User Login with Valid Credentials
    Given I navigate to the SPF NGEN login page
    When I enter username "testuser" using pattern locator
    And I enter password "TestPass123!" using pattern locator  
    And I click the Login button using pattern locator
    Then I should be redirected to the dashboard
    And I should see welcome message on dashboard
    And I should see user navigation menu
    
  @demo
  @smoke
  @TestCaseId:DEMO_002
  @PRIORITY:CRITICAL
  @authentication
  @negative
  Scenario: User Login with Invalid Credentials
    Given I navigate to the SPF NGEN login page
    When I enter username "invalid_user" using pattern locator
    And I enter password "wrong_password" using pattern locator
    And I click the Login button using pattern locator
    Then I should remain on the login page
    And I should see error message "Invalid username or password"
    And the username field should be cleared
    
  @demo2
  @regression  
  @TestCaseId:DEMO_003
  @PRIORITY:HIGH
  @profile
  Scenario: User Profile Information Update
    Given I am logged in as a standard user
    And I navigate to user profile page
    When I update the following profile information:
      | Field      | Value                    |
      | First Name | Updated                  |
      | Last Name  | User                     |
      | Email      | updated.user@spfngen.com |
      | Phone      | 555-0199                 |
    And I click the Save button using pattern locator
    Then I should see success message "Profile updated successfully"
    And the profile information should be saved
    And I should see the updated information displayed

  @demo2
  @regression
  @TestCaseId:DEMO_004  
  @PRIORITY:MEDIUM
  @data_management
  Scenario: Search Functionality Validation
    Given I am logged in as a standard user
    And I navigate to data management page
    When I enter "test data" in the search field using pattern locator
    And I click the Search button using pattern locator
    Then I should see search results displayed
    And the results should contain "test data" 
    And I should see pagination controls if results exceed page limit
    
  @demo2
  @regression
  @TestCaseId:DEMO_005
  @PRIORITY:MEDIUM  
  @data_management
  @filter
  Scenario: Data Filter Operations
    Given I am logged in as a standard user
    And I navigate to data management page
    When I select "Active" from Status filter dropdown using pattern locator
    And I click the Apply Filter button using pattern locator
    Then I should see only active records in results
    And the filter selection should be highlighted
    And I should see filter clear option
    
  @demo
  @smoke
  @TestCaseId:DEMO_006
  @PRIORITY:HIGH
  @admin
  Scenario: Admin User Management Access
    Given I am logged in as an admin user
    When I navigate to user management page
    Then I should see user management interface
    And I should see Create User button
    And I should see user list with actions
    And I should see search and filter options
    
  @demo2
  @integration
  @TestCaseId:DEMO_007
  @PRIORITY:MEDIUM
  @workflow  
  Scenario: Complete User Workflow - Login to Logout
    Given I navigate to the SPF NGEN login page
    When I perform complete user workflow:
      | Action           | Details                    |
      | Login            | Valid credentials          |
      | Navigate Profile | Update personal information|
      | Navigate Data    | Search and filter data     |
      | Generate Report  | Export data to Excel       |
      | Logout           | Clean session termination |
    Then each workflow step should complete successfully
    And I should be returned to login page after logout

  # Data-Driven Test Example
  @demo2
  @regression
  @TestCaseId:DEMO_008
  @PRIORITY:MEDIUM
  @data_driven
  Scenario Outline: Multiple User Login Validation
    Given I navigate to the SPF NGEN login page
    When I enter username "<username>" using pattern locator
    And I enter password "<password>" using pattern locator
    And I click the Login button using pattern locator
    Then I should see "<expected_result>"
    
    Examples: {'dataFile':'test_data/login_test_data.xlsx', 'sheetName':'LoginTests', 'filter':'TestType=="demo"'}

  # Form Validation Test
  @demo
  @regression
  @TestCaseId:DEMO_009
  @PRIORITY:NORMAL
  @validation
  Scenario: Login Form Field Validation
    Given I navigate to the SPF NGEN login page
    When I click the Login button without entering credentials
    Then I should see validation message "Username is required" for username field
    And I should see validation message "Password is required" for password field
    And the login button should remain disabled
    
  # Accessibility Test  
  @demo2
  @accessibility
  @TestCaseId:DEMO_010
  @PRIORITY:LOW
  @a11y
  Scenario: Login Page Accessibility Validation
    Given I navigate to the SPF NGEN login page
    Then the username field should be accessible
    And the password field should be accessible  
    And the login button should be accessible
    And the page should have proper ARIA labels
    And the page should support keyboard navigation