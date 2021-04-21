Feature: Validate PlotAPI
    
    @fixture.plotAPI
    Scenario: Test plotting a time series to disk file and in-memory
    Given a time series data file on disk
    And we want to show the plot
    And we specify an output file
    When the time series data is inserted
    And the time series plot is generated
    Then the output file was created or updated
    And the image data can be retrieved
    
    @fixture.plotAPI
    Scenario: Test plotting a power spectrum
    Given a time series data file on disk
    And we want to show the plot
    And we specify units "W"
    When the time series data is inserted
    And the power spectrum plot is generated
    Then the image data can be retrieved
    
    @fixture.plotAPI
    Scenario: Test plotting amplitude stability
    Given a time series data file on disk
    And we want to show the plot
    And we specify units "W"
    When the time series data is inserted
    And the amplitude stability plot is generated
    Then the image data can be retrieved

    @fixture.plotAPI
    Scenario: Test plotting phase stability
    Given a phase time series data file on disk
    And we want to show the plot
    And we specify units "deg"
    When the time series data is inserted
    And the phase stability plot is generated
    Then the image data can be retrieved
