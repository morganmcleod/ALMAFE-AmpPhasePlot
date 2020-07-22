Feature: Integrate Plots with Result storage
# test generating plots from time series 
#   storing and retrieving from Results
#   re-plotting from data in Results
    
    @fixture.plotStoreResults
    Scenario: Test ploting a time series and storing the result
    Given a time series data file on disk
    When the time series plot is generated
    Then the plot image can be stored in a result
    And the plot traces and attributes can be stored in the result
    And the plot image can be retrieved
    And the plot traces can be retrieved
    And the plot attributes can be retrieved
    
    @fixture.plotStoreResults
    Scenario: Test ploting a time series and storing the result
    Given a time series data file on disk
    When the time series plot is generated
    Then the plot image can be stored in a result
    And the plot traces and attributes can be stored in the result
    When the result is retrieved from the database
    Then the plot can be regenerated
    And the plot image matches

