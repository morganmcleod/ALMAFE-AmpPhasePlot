Feature: Validate AmpPhaseDataLib API

    Scenario: Load the configuration file
    Given the configuration filename
    When the object is created
    Then the database filename is stored
  
    Scenario: Insert a time series having timestamps
    Given dataSeries list "2.1, 2.2, 2.3" and timestamp list "2020:05:21 12:00:00.000, 2020:05:21 12:00:00.050, 2020:05:21 12:00:00.100"
    When the data is inserted 
    Then startTime is "2020:05:21 12:00:00.000"
    And tau0Seconds is "0.05"
    And dataSeries is a list of "3" elements
    And timeStamps is a list of "3" elements
    
    Scenario: Insert a time series in real-time mode
    Given a sequence of readings "4.02, 4.04, 4.03, 4.10, 3.99, 4.03" and tau0 of "0.05"
    When the measurement loop runs using description "the measurement loop runs"
    Then startTime is close to now
    And tau0Seconds is "0.05"
    And dataSeries is a list of "6" elements
    And the time series can be retrieved from the database
    # check everything again after retrieval:
    And the description matches
    And startTime is close to now
    And tau0Seconds is "0.05"
    And dataSeries is a list of "6" elements
    And timeStamps is a list of "6" elements
    And the data has timeStamps starting now with steps of "0.05"

    Scenario: Insert a time series and add, remove, update tags
    Given dataSeries list "6.0, 6.1, 5.9" and timestamp list "2020:05:28 14:15:00, 2020:05:28 14:15:01, 2020:05:28 14:15:02"
    When the data is inserted
    Then we can add tag "configId" with value "23"
    And we can add tag "subsystem" with value "pol0"
    And we can add tag "operator" with value "MM"
    And we can add tag "errors" with value ""
    And we can retrieve tag "configId" and the value matches
    And we can retrieve tag "subsystem" and the value matches
    And we can retrieve tag "operator" and the value matches
    And we can retrieve tag "errors" and the value matches
    And we cannot retrieve tag "oops"
    And we can delete tag "operator"
    And we cannot retrieve tag "operator"

