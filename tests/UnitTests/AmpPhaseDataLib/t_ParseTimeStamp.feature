Feature: Validate parsing time stamps
    
    Scenario: Test parsing a valid timestamp in SQL format
    Given dateTime string "2020-05-20 14:30:02"
    When the test is run
    Then a valid datetime is returned
    And the matching format string is stored
    
    Scenario: Test parsing a valid timestamp with milliseconds
    Given dateTime string "2020-05-21 11:15:22.100"
    When the test is run
    Then a valid datetime is returned
    And the matching format string is stored
    And the milliseconds equals "100"
    
    Scenario: Test parsing a valid timestamp in 12 hour format
    Given dateTime string "2020-05-20 2:45:04 PM"
    When the test is run
    Then a valid datetime is returned
    And the matching format string is stored
  
    Scenario: Test parsing a valid timestamp in an unexpected format
    Given dateTime string "5/21/2020 9:45"
    When the test is run
    Then a valid datetime is returned
    And no matching format string is stored
 
    Scenario: Test parsing an invalid timestamp
    Given dateTime string "Moo 000"
    When the test is run
    Then a valid datetime will not be returned
    And no matching format string is stored