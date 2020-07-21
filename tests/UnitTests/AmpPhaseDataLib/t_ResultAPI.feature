Feature: Validate ResultAPI

    @fixture.resultAPI
    Scenario: Create, retrieve, and delete a Result
    Given the description "Just a Result"
    When the Result is created
    Then the Result can be retrieved and verified
    And the Result can be deleted
    
    @fixture.resultAPI
    Scenario: Create, retrieve and delete Plots, Traces, and an Image
    Given the description "Big Result"
    When the Result is created
    And the Plot, Traces, and Image are created
    Then the Plot can be retrieved and verified
    And the Traces can be retrieved and verified
    And the Image can be retrieved and verified
    And the Traces can be deleted
    And the Image can be deleted
    And the Plot can be deleted
   
    @fixture.resultAPI
    Scenario: Set, update, retrieve, and delete DataStatus tags for a Result
    Given the description "Small Result"
    When the Result is created
    And  DataStatus tag "UNKNOWN" is set
    Then DataStatus tag "UNKNOWN" can be retrieved and the value matches
    And  DataStatus tag "UNKNOWN" can be removed
    When DataStatus tag "ERROR" is set
    Then DataStatus tag "ERROR" can be retrieved and the value matches
    And  DataStatus tag "ERROR" can be removed 
    When DataStatus tag "TO_DELETE" is set
    Then DataStatus tag "TO_DELETE" can be retrieved and the value matches
    And  DataStatus tag "TO_DELETE" can be removed
    When DataStatus tag "TO_RETAIN" is set
    Then DataStatus tag "TO_RETAIN" can be retrieved and the value matches
    And  DataStatus tag "TO_RETAIN" can be removed 
    When DataStatus tag "MEET_SPEC" is set
    Then DataStatus tag "MEET_SPEC" can be retrieved and the value matches
    And  DataStatus tag "MEET_SPEC" can be removed
    When DataStatus tag "FAIL_SPEC" is set
    Then DataStatus tag "FAIL_SPEC" can be retrieved and the value matches
    And  DataStatus tag "FAIL_SPEC" can be removed
    
    @fixture.resultAPI
    Scenario: Set, retrieve, and delete DataSource tags on a Result
    Given the description "Small Result"
    When the Result is created
    And Result DataSource tag "CONFIG_ID" is set with value "23"
    And Result DataSource tag "DATA_SOURCE" is set with value "pol0"
    And Result DataSource tag "SUBSYSTEM" is set with value "pol0"
    And Result DataSource tag "OPERATOR" is set with value "MM"
    And Result DataSource tag "MEAS_SW_VERSION" is set with value "123"
    Then we can retrieve Result DataSource tag "CONFIG_ID" and the value matches
    And we can retrieve Result DataSource tag "DATA_SOURCE" and the value matches
    And we can retrieve Result DataSource tag "SUBSYSTEM" and the value matches
    And we can retrieve Result DataSource tag "OPERATOR" and the value matches
    And we can retrieve Result DataSource tag "MEAS_SW_VERSION" and the value matches
    And we can delete Result DataSource tag "OPERATOR"
    When Result DataSource tag "SUBSYSTEM" is set with value "Pol1"
    Then we can retrieve Result DataSource tag "SUBSYSTEM" and the value matches
    
    @fixture.resultAPI
    Scenario: Create, update, delete plot elements
    Given the description "Plot Result"
    When the Result and Plot are created
    Then we can add plot element "X_AXIS_LABEL" with value "Seconds elapsed"
    And we can retrieve plot element "X_AXIS_LABEL" and the value matches
    And we can delete plot element "X_AXIS_LABEL"
    And we can add plot element "Y_AXIS_LABEL" with value "Amplitude (W)"
    And we can retrieve plot element "Y_AXIS_LABEL" and the value matches
    And we can delete plot element "Y_AXIS_LABEL"
    And we can add plot element "Y2_AXIS_LABEL" with value "Kelvin"
    And we can retrieve plot element "Y2_AXIS_LABEL" and the value matches
    And we can delete plot element "Y2_AXIS_LABEL"
    