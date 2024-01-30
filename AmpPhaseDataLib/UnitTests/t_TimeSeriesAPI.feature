Feature: Validate TimeSeriesAPI

    @fixture.timeSeriesAPI
    Scenario: Insert a time series having timestamps
    Given dataSeries list "2.1, 2.2, 2.3" 
    And timestamp list "2020:05:21 12:00:00.000, 2020:05:21 12:00:00.050, 2020:05:21 12:00:00.100"
    And the units are "mW"
    When the data is inserted 
    # check everything again after retrieval:
    When the time series is retrieved from the database
    Then startTime is "2020:05:21 12:00:00.000"
    And tau0Seconds is "0.05"
    And dataSeries is a list of "3" elements
    And timeStamps is a list of "3" elements
    And the units are "mW"
    
    @fixture.timeSeriesAPI
    Scenario: Insert a time series in real-time mode
    Given a sequence of readings "4.02, 4.04, 4.03, 4.10, 3.99, 4.03" and tau0 of "0.05"
    When the measurement loop runs
    Then startTime is close to now
    And tau0Seconds is "0.05"
    And dataSeries is a list of "6" elements
    # check everything again after retrieval:
    When the time series is retrieved from the database
    Then startTime is close to now
    And tau0Seconds is "0.05"
    And dataSeries is a list of "6" elements
    And timeStamps is a list of "6" elements
    And the data has timeStamps starting now with steps of "0.05"

    @fixture.timeSeriesAPI
    Scenario: Insert a time series, delete it, and verify it has been deleted
    Given dataSeries list "6.0, 6.1, 5.9" 
    And timestamp list "2020:05:28 14:15:00, 2020:05:28 14:15:01, 2020:05:28 14:15:02"
    When the data is inserted 
    And the time series is retrieved from the database
    Then the time series can be deleted from the database
    And the time series cannot be retrieved from the database

    @fixture.timeSeriesAPI
    Scenario: Insert a time series and add, remove, update DataSource tags
    Given dataSeries list "6.0, 6.1, 5.9" 
    And timestamp list "2020:05:28 14:15:00, 2020:05:28 14:15:01, 2020:05:28 14:15:02"
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
    # check everything again after retrieval:
    When the time series is retrieved from the database
    Then we can retrieve DataSource tag "CONFIG_ID" and the value matches
    And we can retrieve DataSource tag "DATA_SOURCE" and the value matches
    And we can retrieve DataSource tag "SUBSYSTEM" and the value matches
    And we can retrieve DataSource tag "MEAS_SW_VERSION" and the value matches
    Then we can retrieve DataSource tag "SUBSYSTEM" and the value matches
    
    @fixture.timeSeriesAPI
    Scenario: Insert time series in Watts and retrieve in different units
    Given a sequence of readings "0.001, 0.002, 0.003, 0.004, 0.005, 0.006" and tau0 of "6.0"
    And the units are "W"
    When the measurement loop runs
    And the time series is retrieved from the database
    Then the units are "W"
    And we can retrieve the timestamps as "0, 6, 12, 18, 24, 30" in units "seconds"
    And we can retrieve the timestamps as "0, 0.1, 0.2, 0.3, 0.4, 0.5" in units "minutes"
    And we can retrieve the readings as "1, 2, 3, 4, 5, 6" in units "mW"
    And we can retrieve the readings as "0, 3.0103, 4.7712, 6.0206, 6.9897, 7.7815" in units "dBm"
    
    @fixture.timeSeriesAPI
    Scenario: Insert time series in Volts and retrieve in different units
    Given a sequence of readings "0.001, 0.002, 0.003, 0.004, 0.005, 0.006" and tau0 of "6.0"
    And the units are "V"
    When the measurement loop runs
    And the time series is retrieved from the database
    Then the units are "V"
    And we can retrieve the readings as "1, 2, 3, 4, 5, 6" in units "mV"
