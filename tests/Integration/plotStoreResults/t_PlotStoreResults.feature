Feature: Integrate Plots with Result storage
# test generating plots from time series 
#   storing and retrieving from Results
#   re-plotting from data in Results
    
    @fixture.plotStoreResults
    Scenario: Make a plot then store and retrieve the result
    Given an amplitude time series data file on disk
#    And we want to show the plot
    When the time series data is inserted
    And the amplitude stability plot is generated
    Then the plot header can be stored in a result 
    And the plot image can be stored in a result
    And the plot traces and attributes can be stored in the result
    And the plot image can be retrieved
    And the plot traces can be retrieved
    And the plot attributes can be retrieved
    
    @fixture.plotStoreResults
    Scenario: Make an amplitude stability plot from a trace stored in a result
    Given an amplitude time series data file on disk
#    And we want to show the plot
    When the time series data is inserted
    And the amplitude stability plot is generated
    Then the plot header can be stored in a result 
    And the plot traces and attributes can be stored in the result
    When the result is retrieved from the database
    Then the plot can be regenerated and the image matches

    @fixture.plotStoreResults
    Scenario: Make an phase stability plot from a trace stored in a result
    Given a phase time series data file on disk
#    And we want to show the plot
    When the time series data is inserted
    And the phase stability plot is generated
    Then the plot header can be stored in a result 
    And the plot traces and attributes can be stored in the result
    When the result is retrieved from the database
    Then the plot can be regenerated and the image matches

    @fixture.plotStoreResults
    Scenario: Make a power spectrum plot from a trace stored in a result
    Given an amplitude time series data file on disk
#    And we want to show the plot
    When the time series data is inserted
    And the power spectrum plot is generated
    Then the plot header can be stored in a result 
    And the plot traces and attributes can be stored in the result
    When the result is retrieved from the database
    Then the plot can be regenerated and the image matches
    