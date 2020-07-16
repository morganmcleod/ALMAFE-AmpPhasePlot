Feature: Validate TimeSeriesAPI

    @fixture.timeSeriesAPI
    Scenario: Insert a time series having timestamps
    Given dataSeries list "2.1, 2.2, 2.3" and timestamp list "2020:05:21 12:00:00.000, 2020:05:21 12:00:00.050, 2020:05:21 12:00:00.100"
    When the data is inserted 
    Then startTime is "2020:05:21 12:00:00.000"
    And tau0Seconds is "0.05"
    And dataSeries is a list of "3" elements
    And timeStamps is a list of "3" elements
    
    @fixture.timeSeriesAPI
    Scenario: Insert a time series in real-time mode
    Given a sequence of readings "4.02, 4.04, 4.03, 4.10, 3.99, 4.03" and tau0 of "0.05"
    When the measurement loop runs using description "the measurement loop runs"
    Then startTime is close to now
    And tau0Seconds is "0.05"
    And dataSeries is a list of "6" elements
    # check everything again after retrieval:
    When the time series is retrieved from the database
    Then the description matches
    And startTime is close to now
    And tau0Seconds is "0.05"
    And dataSeries is a list of "6" elements
    And timeStamps is a list of "6" elements
    And the data has timeStamps starting now with steps of "0.05"

    @fixture.timeSeriesAPI
    Scenario: Insert a time series, delete it, and verify it has been deleted
    Given dataSeries list "6.0, 6.1, 5.9" and timestamp list "2020:05:28 14:15:00, 2020:05:28 14:15:01, 2020:05:28 14:15:02"
    When the data is inserted 
    And the time series is retrieved from the database
    Then the time series can be deleted from the database
    And the time series cannot be retrieved from the database

    @fixture.timeSeriesAPI
    Scenario: Insert a time series and add, remove, update DataSource tags
    Given dataSeries list "6.0, 6.1, 5.9" and timestamp list "2020:05:28 14:15:00, 2020:05:28 14:15:01, 2020:05:28 14:15:02"
    When the data is inserted
    And TimeSeries DataSource tag "CONFIG_ID" is set with value "23"
    And TimeSeries DataSource tag "DATA_SOURCE" is set with value "pol0"
    And TimeSeries DataSource tag "SUBSYSTEM" is set with value "pol0"
    And TimeSeries DataSource tag "OPERATOR" is set with value "MM"
    And TimeSeries DataSource tag "MEAS_SW_VERSION" is set with value "123"
    Then we can retrieve DataSource tag "CONFIG_ID" and the value matches
    And we can retrieve DataSource tag "DATA_SOURCE" and the value matches
    And we can retrieve DataSource tag "SUBSYSTEM" and the value matches
    And we can retrieve DataSource tag "OPERATOR" and the value matches
    And we can retrieve DataSource tag "MEAS_SW_VERSION" and the value matches
    And we can delete DataSource tag "OPERATOR"
    And we cannot retrieve DataSource tag "OPERATOR"
    When TimeSeries DataSource tag "SUBSYSTEM" is set with value "Pol1"
    Then we can retrieve DataSource tag "SUBSYSTEM" and the value matches

    @fixture.timeSeriesAPI
    Scenario: Insert a time series and add, remove DataStatus tags
    Given dataSeries list "6.0, 6.1, 5.9" and timestamp list "2020:05:28 14:15:00, 2020:05:28 14:15:01, 2020:05:28 14:15:02"
    When the data is inserted
    Then we can set DataStatus "UNKNOWN"
    And we can read DataStatus "UNKNOWN" and the value matches
    And we can clear DataStatus "UNKNOWN"
    And we can set DataStatus "MEET_SPEC"
    And we can read DataStatus "MEET_SPEC" and the value matches
    And we can clear DataStatus "MEET_SPEC"

    @fixture.timeSeriesAPI
    Scenario: Some DataStatus tags are mutually exclusive
    Given dataSeries list "6.0, 6.1, 5.9" and timestamp list "2020:05:28 14:15:00, 2020:05:28 14:15:01, 2020:05:28 14:15:02"
    When the data is inserted
    Then we can set DataStatus "UNKNOWN"
    And we can read DataStatus "UNKNOWN" and the value matches
    When we set the DataStatus "ERROR"
    Then the DataStatus "UNKNOWN" gets removed
    When we set the DataStatus "MEET_SPEC"
    And we set the DataStatus "FAIL_SPEC"
    Then the DataStatus "MEET_SPEC" gets removed
    When we set the DataStatus "TO_RETAIN"
    And we set the DataStatus "TO_DELETE"
    Then the DataStatus "TO_RETAIN" gets removed
        