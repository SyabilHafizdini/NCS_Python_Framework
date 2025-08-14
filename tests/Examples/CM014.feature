# SPF NGEN Production Test Case - CM014  
# System Administration - User Role Management
# Production-ready test case with comprehensive admin scenarios

@CM014
@Admin
Feature: System Administration - User Role Management (CM014)
  As a system administrator
  I want to manage user roles and permissions
  So that I can control system access appropriately

  Background:
    Given the SPF NGEN application is accessible in "UAT" environment
    And I have valid system administrator credentials

  @CM014
  @PRIORITY:CRITICAL
  @TestCaseId:CM014_001
  @TagGroup:UserManagement
  @Smoke
  Scenario: Create New User Account with Role Assignment
    Given I am logged in as system administrator
    And I navigate to user management page
    When I click the "Create User" button using pattern locator
    And I fill new user details:
      | Field           | Value                      |
      | Username        | newuser001                 |
      | Email           | newuser@spfngen.com        |
      | First Name      | New                        |
      | Last Name       | User                       |
      | Phone           | +1-555-0001               |
      | Department      | Operations                 |
      | Role            | Standard User              |
      | Status          | Active                     |
    And I set temporary password "TempPass123!"
    And I enable "Force Password Change" option
    And I click the "Create User" button using pattern locator
    Then I should see success message "User created successfully"
    And the user should appear in user list
    And user should have "Standard User" role assigned
    And password reset email should be sent

  @CM014
  @PRIORITY:HIGH
  @TestCaseId:CM014_002
  @TagGroup:UserManagement
  @RoleModification
  Scenario: Modify User Role and Permissions
    Given I am logged in as system administrator
    And I navigate to user management page
    And I have an existing user "testuser001"
    When I search for user "testuser001" using pattern locator
    And I click the "Edit User" action
    And I change user role from "Standard User" to "Business User"
    And I add additional permissions:
      | Permission          | Action |
      | Report Generation   | Grant  |
      | Data Export         | Grant  |
      | Approval Workflow   | Grant  |
    And I click the "Update User" button using pattern locator
    Then I should see success message "User permissions updated"
    And the user should have "Business User" role
    And the additional permissions should be active
    And audit log should record the role changes

  @CM014
  @PRIORITY:CRITICAL
  @TestCaseId:CM014_003
  @TagGroup:UserManagement
  @Security
  Scenario: User Account Deactivation and Reactivation
    Given I am logged in as system administrator
    And I navigate to user management page
    And I have an active user "testuser002"
    When I search for user "testuser002" using pattern locator
    And I click the "Deactivate User" action
    And I confirm deactivation with reason "User no longer with company"
    Then I should see success message "User deactivated successfully"
    And the user status should show "Inactive"
    And the user should not be able to login
    When I click the "Reactivate User" action
    And I confirm reactivation
    Then I should see success message "User reactivated successfully"
    And the user status should show "Active"
    And the user should be able to login again

  @CM014
  @PRIORITY:HIGH
  @TestCaseId:CM014_004
  @TagGroup:UserManagement
  @PasswordManagement
  Scenario: Admin Password Reset for User
    Given I am logged in as system administrator
    And I navigate to user management page
    And I have a user "testuser003" who needs password reset
    When I search for user "testuser003" using pattern locator
    And I click the "Reset Password" action
    And I generate new temporary password
    And I enable "Force Password Change on Next Login"
    And I click the "Reset Password" button using pattern locator
    Then I should see success message "Password reset successfully"
    And temporary password should be generated
    And password reset notification should be sent to user
    And user should be forced to change password on next login

  @CM014
  @PRIORITY:MEDIUM
  @TestCaseId:CM014_005
  @TagGroup:UserManagement
  @BulkOperations
  Scenario: Bulk User Operations
    Given I am logged in as system administrator
    And I navigate to user management page
    And I have multiple users in the system
    When I select multiple users using checkboxes
    And I choose bulk action "Role Update"
    And I select new role "Business User" for selected users
    And I click the "Apply Bulk Action" button using pattern locator
    Then I should see confirmation dialog with selected users count
    When I confirm the bulk operation
    Then I should see success message "Bulk operation completed successfully"
    And all selected users should have "Business User" role
    And bulk operation should be logged in audit trail

  @CM014
  @PRIORITY:HIGH
  @TestCaseId:CM014_006
  @TagGroup:UserManagement
  @RoleValidation
  Scenario Outline: Role-Based Access Control Validation
    Given I am logged in as system administrator
    And I navigate to user management page
    And I have a user with role "<user_role>"
    When I verify user permissions for "<user_role>"
    Then the user should have access to "<allowed_features>"
    And the user should NOT have access to "<restricted_features>"
    And permission validation should be enforced at UI level
    
    Examples: {'dataFile':'test_data/role_permissions_data.xlsx', 'sheetName':'RolePermissions', 'filter':'TestCaseId=="CM014_006"'}

  @CM014
  @PRIORITY:MEDIUM  
  @TestCaseId:CM014_007
  @TagGroup:UserManagement
  @AuditTrail
  Scenario: User Management Audit Trail Verification
    Given I am logged in as system administrator
    And I navigate to audit trail page
    When I filter audit logs by "User Management" activities
    And I select date range for today
    Then I should see all user management activities logged:
      | Activity          | Details                    |
      | User Created      | Username, Role, Timestamp  |
      | Role Modified     | Old Role, New Role, User   |
      | User Deactivated  | Username, Reason, Admin    |
      | Password Reset    | Username, Admin, Timestamp |
    And each log entry should have complete details
    And audit trail should be tamper-evident

  @CM014
  @PRIORITY:LOW
  @TestCaseId:CM014_008
  @TagGroup:UserManagement
  @Reporting
  Scenario: User Management Reports Generation
    Given I am logged in as system administrator
    And I navigate to reports page
    When I select report type "User Management Summary"
    And I set report parameters:
      | Parameter     | Value        |
      | Date Range    | Last 30 days |
      | User Status   | All          |
      | Role Filter   | All Roles    |
      | Department    | All          |
    And I click the "Generate Report" button using pattern locator
    Then the report should be generated successfully
    And report should contain user statistics
    And report should include role distribution
    And I should be able to export report to Excel/PDF

  @CM014
  @PRIORITY:HIGH
  @TestCaseId:CM014_009
  @TagGroup:UserManagement
  @Integration
  @SecurityCompliance
  Scenario: User Session Management and Security
    Given I am logged in as system administrator
    And I navigate to active sessions page
    When I view currently active user sessions
    Then I should see list of active sessions with details:
      | Detail          | Information                |
      | Username        | Logged in user             |
      | Login Time      | Session start timestamp    |
      | IP Address      | User connection IP         |
      | Browser         | User agent information     |
      | Last Activity   | Recent activity timestamp  |
    When I select a session to terminate
    And I click the "Terminate Session" button using pattern locator
    Then the selected session should be terminated
    And the user should be logged out immediately
    And session termination should be logged