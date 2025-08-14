# SPF NGEN Production Test Case - CM009
# Customer Management Feature - User Profile Operations
# Production-ready test case following Java QAF structure

@CM009
@Regression
Feature: Customer Management - User Profile Operations (CM009)
  As a business user
  I want to manage customer profile information
  So that I can maintain accurate customer data

  Background:
    Given the SPF NGEN application is accessible in "UAT" environment
    And I have valid business user credentials

  @CM009
  @PRIORITY:CRITICAL
  @TestCaseId:CM009_001
  @TagGroup:CustomerManagement
  @Smoke
  Scenario: Create New Customer Profile
    Given I am logged in as a business user
    And I navigate to customer management page
    When I click the "Create Customer" button using pattern locator
    And I fill customer details:
      | Field           | Value                      |
      | Customer Name   | Test Customer Ltd          |
      | Email           | customer@testcompany.com   |
      | Phone           | +1-555-0123               |
      | Address         | 123 Business St           |
      | City            | Business City             |
      | State           | BC                        |
      | Postal Code     | 12345                     |
      | Customer Type   | Corporate                 |
    And I click the "Save Customer" button using pattern locator
    Then I should see success message "Customer created successfully"
    And the customer should appear in customer list
    And customer details should be saved correctly
    
  @CM009
  @PRIORITY:HIGH  
  @TestCaseId:CM009_002
  @TagGroup:CustomerManagement
  @Regression
  Scenario: Update Existing Customer Profile
    Given I am logged in as a business user
    And I navigate to customer management page
    And I have an existing customer "Test Customer Ltd"
    When I search for customer "Test Customer Ltd" using pattern locator
    And I click the "Edit" action for the customer
    And I update customer details:
      | Field         | Value                        |
      | Email         | updated@testcompany.com      |
      | Phone         | +1-555-0199                 |
      | Address       | 456 Updated Business Ave     |
    And I click the "Update Customer" button using pattern locator
    Then I should see success message "Customer updated successfully"
    And the updated information should be displayed
    And audit trail should record the changes

  @CM009
  @PRIORITY:MEDIUM
  @TestCaseId:CM009_003  
  @TagGroup:CustomerManagement
  @Validation
  Scenario: Customer Profile Field Validation
    Given I am logged in as a business user
    And I navigate to customer management page
    When I click the "Create Customer" button using pattern locator
    And I attempt to save without required fields
    Then I should see validation messages:
      | Field           | Message                     |
      | Customer Name   | Customer name is required   |
      | Email           | Email is required           |
      | Phone           | Phone number is required    |
    And the customer should not be created
    And I should remain on the create customer form

  @CM009
  @PRIORITY:HIGH
  @TestCaseId:CM009_004
  @TagGroup:CustomerManagement  
  @DataIntegrity
  Scenario: Duplicate Customer Prevention
    Given I am logged in as a business user
    And I navigate to customer management page
    And I have an existing customer with email "existing@company.com"
    When I attempt to create new customer with same email:
      | Field           | Value                      |
      | Customer Name   | Duplicate Test Customer    |
      | Email           | existing@company.com       |
      | Phone           | +1-555-9999               |
    And I click the "Save Customer" button using pattern locator
    Then I should see error message "Customer with this email already exists"
    And the duplicate customer should not be created
    And I should be prompted to update existing customer instead

  @CM009
  @PRIORITY:MEDIUM
  @TestCaseId:CM009_005
  @TagGroup:CustomerManagement
  @Search
  Scenario Outline: Customer Search and Filter Operations
    Given I am logged in as a business user
    And I navigate to customer management page
    And I have multiple customers in the system
    When I search for customers using "<search_criteria>" with value "<search_value>"
    And I apply filter "<filter_type>" with value "<filter_value>"
    Then I should see filtered results matching the criteria
    And the result count should be displayed
    And pagination should be available if needed
    
    Examples: {'dataFile':'test_data/customer_search_data.xlsx', 'sheetName':'SearchTests', 'filter':'TestCaseId=="CM009_005"'}

  @CM009
  @PRIORITY:LOW
  @TestCaseId:CM009_006
  @TagGroup:CustomerManagement
  @Export
  Scenario: Export Customer Data
    Given I am logged in as a business user
    And I navigate to customer management page
    And I have customers in the system
    When I select customers to export
    And I click the "Export" button using pattern locator
    And I choose export format "Excel"
    Then the customer data should be exported successfully
    And I should receive download confirmation
    And the exported file should contain correct customer information
    And the file should be in proper Excel format