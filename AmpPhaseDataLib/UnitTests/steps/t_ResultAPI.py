'''
Implement test cases for t_TimeSeriesAPI.feature
Validate TimeSeriesAPI
'''
from behave import given, when, then 
from AmpPhaseDataLib.Constants import PlotKind, DataStatus, DataSource, PlotEl
from hamcrest import assert_that, equal_to

@given('the description "{description}"')
def step_impl(context, description):
    '''
    :param context: behave.runner.Context
    '''
    context.description = description
    
@when('the Result is created') 
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    context.resultId = context.API.createResult(context.description)
    assert_that(context.resultId)
    
@then('the Result can be retrieved and verified')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    result = context.API.retrieveResult(context.resultId)
    assert_that(result[0], equal_to(context.resultId))
    assert_that(result[1], equal_to(context.description))
    
@then('the Result can be deleted')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    context.API.deleteResult(context.resultId)
    result = context.API.retrieveResult(context.resultId)
    assert_that(result, equal_to(None))
    result = context.API.retrieveResult(context.resultId)
    assert_that(not result)

@when('the Plot, Traces, and Image are created') 
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    context.plotKind = PlotKind.TIME_SERIES
    context.plotId = context.API.createPlot(context.resultId, context.plotKind)
    assert_that(context.plotId)
    context.xyData = ([0, 1, 2, 3], [2.1, 2.2, 1.9, 2.0], [0, 0, 0, 0])
    context.xyData2 = ([0, 1, 2, 3], [5.1, 5.2, 5.9, 5.0], [0, 0, 0, 0]) 
    context.traceName = "time series"
    context.traceName2 = "temperature"
    context.traceId = context.API.createTrace(context.plotId, context.xyData, context.traceName)
    assert_that(context.traceId)
    context.traceId2 = context.API.createTrace(context.plotId, context.xyData2, context.traceName2)
    assert_that(context.traceId2)
    context.imagePath = "AmpPhaseDataLib/UnitTests/steps/Cone of dining (Paris) June 2020.jpg"
    context.imageName = "time image"
    context.plotImageId = context.API.insertPlotImageFromFile(context.plotId, context.imagePath, context.imageName)
    assert_that(context.plotImageId)
    
@then('the Plot can be retrieved and verified')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    plot = context.API.retrievePlot(context.plotId)
    assert_that(plot[0], equal_to(context.plotId))
    assert_that(plot[1], equal_to(context.plotKind))

@then('the Traces can be retrieved and verified')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    trace = context.API.retrieveTrace(context.traceId)
    assert_that(trace[0], equal_to(context.traceId))
    assert_that(trace[1], equal_to(context.xyData))
    assert_that(trace[2], equal_to(context.traceName))
    assert_that(trace[3], equal_to(context.traceName))
    trace = context.API.retrieveTrace(context.traceId2)
    assert_that(trace[0], equal_to(context.traceId2))
    assert_that(trace[1], equal_to(context.xyData2))
    assert_that(trace[2], equal_to(context.traceName2))
    assert_that(trace[3], equal_to(context.traceName2))
     
@then('the Image can be retrieved and verified')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    image = context.API.retrievePlotImage(context.plotImageId)
    assert_that(image[0], equal_to(context.plotId))
    assert_that(image[1], equal_to(context.plotImageId))
    assert_that(image[2], equal_to(context.imageName))
    assert_that(image[3], equal_to(context.imagePath))
    
    with open(context.imagePath, 'rb') as file:
        imageData = file.read()
    assert_that(image[4], equal_to(imageData))
    
@then('the Traces can be deleted')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    context.API.deleteTrace(context.traceId)
    result = context.API.retrieveTrace(context.traceId)
    assert_that(result, equal_to(None))
    context.API.deleteTrace(context.traceId2)
    result = context.API.retrieveTrace(context.traceId2)
    assert_that(result, equal_to(None))
        
@then('the Image can be deleted')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    context.API.deletePlotImage(context.plotImageId)
    result = context.API.retrievePlotImage(context.plotImageId)
    assert_that(result, equal_to(None))

@then('the Plot can be deleted')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    context.API.deletePlot(context.plotId)
    result = context.API.retrievePlot(context.plotId)
    assert_that(result, equal_to(None))

@when('DataStatus tag "{tagName}" is set')
def step_impl(context, tagName):
    '''
    :param context: behave.runner.Context
    '''
    dataStatus = DataStatus[tagName]
    context.resultTags[dataStatus.value] = True
    context.API.setResultDataStatus(context.resultId, dataStatus)

@then('DataStatus tag "{tagName}" can be retrieved and the value matches')
def step_impl(context, tagName):
    '''
    :param context: behave.runner.Context
    '''
    dataStatus = DataStatus[tagName]
    result = context.API.getResultDataStatus(context.resultId, dataStatus)
    assert_that(result, equal_to(True))    

@then('DataStatus tag "{tagName}" can be removed')
def step_impl(context, tagName):
    '''
    :param context: behave.runner.Context
    '''
    dataStatus = DataStatus[tagName]
    del context.resultTags[dataStatus.value] 
    context.API.clearResultDataStatus(context.resultId, dataStatus)
    result = context.API.getResultDataStatus(context.resultId, dataStatus)
    assert_that(result, equal_to(False))    
    
@when('Result DataSource tag "{tagName}" is set with value "{tagValue}"')
def step_impl(context, tagName, tagValue):
    """
    :param context: behave.runner.Context
    :param tagName: str
    :param tagValue: str
    """
    dataSource = DataSource[tagName]
    context.resultTags[dataSource.value] = tagValue
    context.API.setResultDataSource(context.resultId, dataSource, tagValue)
    
@then('we can retrieve Result DataSource tag "{tagName}" and the value matches')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    dataSource = DataSource[tagName]
    result = context.API.getResultDataSource(context.resultId, dataSource)
    retrieved = context.resultTags[dataSource.value]
    assert_that(result, equal_to(retrieved))
    
@then('we can delete Result DataSource tag "{tagName}"')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    dataSource = DataSource[tagName]
    del context.resultTags[dataSource.value]
    context.API.clearResultDataSource(context.resultId, dataSource)
    result = context.API.getResultDataSource(context.resultId, dataSource)
    assert_that(not result)
    
@when('the Result and Plot are created')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    context.resultId = context.API.createResult(context.description)
    assert_that(context.resultId)
    context.plotKind = PlotKind.TIME_SERIES
    context.plotId = context.API.createPlot(context.resultId, context.plotKind)
    assert_that(context.plotId)

@then('we can add plot element "{element}" with value "{value}"')
def step_impl(context, element, value):
    '''
    :param context: behave.runner.Context
    '''
    plotElement = PlotEl[element]
    context.plotTags[plotElement.value] = value
    context.API.setPlotEl(context.plotId, plotElement, value)

@then('we can retrieve plot element "{element}" and the value matches')
def step_impl(context, element):
    '''
    :param context: behave.runner.Context
    '''
    plotElement = PlotEl[element]
    expected = context.plotTags.get(plotElement.value, None)
    result = context.API.getPlotEl(context.plotId, plotElement)
    assert_that(result, equal_to(expected))

@then('we can delete plot element "{element}"')
def step_impl(context, element):
    '''
    :param context: behave.runner.Context
    '''
    plotElement = PlotEl[element]
    del context.plotTags[plotElement.value]
    context.API.clearPlotEl(context.plotId, plotElement)
    result = context.API.getPlotEl(context.plotId, plotElement)
    assert_that(result, equal_to(None))
    