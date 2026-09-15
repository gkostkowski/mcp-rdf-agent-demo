Feature: Retrieve overdue library loans
  Scenario: Central Library has an overdue loan
    Given Central Library has Alice's overdue COPY-001 loan
    When an administrator requests Central Library overdue loans
    Then the overdue result includes Alice Adams and COPY-001

  Scenario: West Library has no overdue loans
    Given West Library has no overdue loans
    When an administrator requests West Library overdue loans
    Then the overdue result has no items
