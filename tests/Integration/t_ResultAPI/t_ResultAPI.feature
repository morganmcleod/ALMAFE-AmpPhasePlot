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
    Then the plot image can be stored in a result
    And the plot image can be retrieved by its plotId
    And the plot image can be retrieved by the resultId

    
