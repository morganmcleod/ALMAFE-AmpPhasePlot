Feature: Validate ResultAPI

    @fixture.resultAPI
    Scenario: Create, retrieve, and delete a PlotResult
    Given the description "Just a Result"
    When the PlotResult is created
    Then the PlotResult can be retrieved and verified
    And the PlotResult can be deleted
    
    @fixture.resultAPI
    Scenario: Create, retrieve and delete an Image
    Given the description "Big Result"
    When the PlotResult is created
    And the Image is created
    Then the Image can be retrieved and verified
    And the Image can be deleted
    
    @fixture.resultAPI
    Scenario: Set, retrieve, and delete DataSource tags on a Result
    Given the description "Small Result"
    When the PlotResult is created
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

    