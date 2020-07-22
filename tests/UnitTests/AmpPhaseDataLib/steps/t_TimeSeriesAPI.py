'''
Implement test cases for t_TimeSeriesAPI.feature
Validate TimeSeriesAPI
'''
from behave import given, when, then
from datetime import datetime
from AmpPhaseDataLib.Constants import DataSource, DataStatus, Units
from Utility import ParseTimeStamp
from hamcrest import assert_that, equal_to, close_to

##### GIVEN #####
        
@given('dataSeries list "{dataList}"')
def step_impl(context, dataList):
    """
    :param context: behave.runner.Context
    :param dataList: comma-separated list of float strings
    """
    # convert strings to lists: 
    context.dataSeries = dataList.strip('][').split(', ')

@given('timestamp list "{timeStampList}"')
def step_impl(context, timeStampList):
    """
    :param context: behave.runner.Context
    :param timeStampList: comma-separated list of datetime strings
    """
    # convert strings to lists: 
    context.timeStamps = timeStampList.strip('][').split(', ')

@given('a sequence of readings "{dataList}" and tau0 of "{floatString}"')
def step_impl(context, dataList, floatString):
    """
    :param context: behave.runner.Context
    :param dataList: comma-separated list of float strings
    :param floatString: a float as string
    """
    # convert string to list: 
    context.dataSeries = dataList.strip('][').split(', ')
    context.tau0Seconds = float(floatString)

@given('the units are "{units}"')
def step_impl(context, units):
    """
    :param context: behave.runner.Context
    :param units as string
    """
    context.units = units

##### WHEN #####

@when('the data is inserted')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.timeSeriesId = context.API.insertTimeSeries(dataSeries = context.dataSeries, timeStamps = context.timeStamps)
    if context.timeSeriesId and hasattr(context, 'units'):
        context.API.setDataSource(context.timeSeriesId, DataSource.UNITS, context.units)

@when('the measurement loop runs')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.now = datetime.now()    
    
    context.timeSeriesId = context.API.startTimeSeries(context.tau0Seconds)
    for item in context.dataSeries:
        context.API.insertTimeSeriesChunk(float(item))
    context.API.finishTimeSeries()
    if context.timeSeriesId and hasattr(context, 'units'):
        context.API.setDataSource(context.timeSeriesId, DataSource.UNITS, context.units)

@when('the time series is retrieved from the database')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    assert_that(context.API.retrieveTimeSeries(context.timeSeriesId))

@when('TimeSeries DataSource tag "{tagName}" is set with value "{tagValue}"')
def step_impl(context, tagName, tagValue):
    """
    :param context: behave.runner.Context
    :param tagName: str
    :param tagValue: str
    """
    context.tagsAdded[tagName] = tagValue
    context.API.setDataSource(context.timeSeriesId, DataSource[tagName], tagValue)

@when('we set the DataStatus "{tagName}"')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    dataStatus = DataStatus[tagName]
    context.tagsAdded[dataStatus.value] = True
    context.API.setDataStatus(context.timeSeriesId, dataStatus)

##### THEN #####
    
@then('startTime is "{timeStampString}"')
def step_impl(context, timeStampString):
    '''
    :param context: behave.runner.Context
    :param timeStampString: a datetime as string
    '''
    tsParser = ParseTimeStamp.ParseTimeStamp()
    timeStamp = tsParser.parseTimeStamp(timeStampString)
    assert_that(context.API.startTime, equal_to(timeStamp))
    
@then('tau0Seconds is "{floatString}"')
def step_impl(context, floatString):
    '''
    :param context: behave.runner.Context
    :param floatString: a float as string
    '''
    tau0Seconds = float(floatString)
    assert_that(context.API.tau0Seconds, equal_to(tau0Seconds))

@then('dataSeries is a list of "{intString}" elements')
def step_impl(context, intString):
    '''
    :param context: behave.runner.Context
    :param intString: an int as string
    '''
    dataLen = int(intString)
    assert_that(len(context.API.dataSeries), equal_to(dataLen))
    
@then('timeStamps is a list of "{intString}" elements')
def step_impl(context, intString):
    '''
    :param context: behave.runner.Context
    :param intString: an int as string
    '''
    dataLen = int(intString)
    assert_that(len(context.API.timeStamps), equal_to(dataLen))

@then('the units are "{units}"')
def step_impl(context, units):
    '''
    :param context: behave.runner.Context
    :param units: as string
    '''
    assert_that(context.API.getDataSource(context.timeSeriesId, DataSource.UNITS), equal_to(units))
    
@then('startTime is close to now')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    delta = max(context.API.startTime, context.now) - min(context.API.startTime, context.now)
    assert_that(delta.seconds, close_to(0, 0.05))

@then('the time series can be deleted from the database')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    context.API.deleteTimeSeries(context.timeSeriesId)
    
@then('the time series cannot be retrieved from the database')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    assert_that(not context.API.retrieveTimeSeries(context.timeSeriesId))
    
@then('the data has timeStamps starting now with steps of "{floatString}"')
def step_impl(context, floatString):
    """
    :param context: behave.runner.Context
    :param floatString: a float as string
    """
    tau0Seconds = float(floatString)
    delta = context.API.timeStamps[0] - context.now
    deltaSeconds = delta.seconds + (delta.microseconds / 1.0e6)
    assert_that(deltaSeconds, close_to(0.0, 0.05))
    firstTime = True
    for TS in context.API.timeStamps:
        if firstTime:
            TS0 = TS
            firstTime = False
        else:
            delta = TS - TS0
            deltaSeconds = delta.seconds + (delta.microseconds / 1.0e6)
            assert_that(deltaSeconds, equal_to(tau0Seconds))
            TS0 = TS
    
@then('we can retrieve DataSource tag "{tagName}" and the value matches')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    result = context.API.getDataSource(context.timeSeriesId, DataSource[tagName])
    assert_that(result, equal_to(context.tagsAdded[tagName]))
    
@then('we cannot retrieve DataSource tag "{tagName}"')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    result = context.API.getDataSource(context.timeSeriesId, DataSource[tagName])
    assert_that(not result)
    
@then('we can delete DataSource tag "{tagName}"')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    del context.tagsAdded[tagName]
    context.API.setDataSource(context.timeSeriesId, DataSource[tagName], None)

@then('we can set DataStatus "{tagName}"')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    dataStatus = DataStatus[tagName]
    context.tagsAdded[dataStatus.value] = True
    context.API.setDataStatus(context.timeSeriesId, dataStatus)
    
@then('we can read DataStatus "{tagName}" and the value matches')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    dataStatus = DataStatus[tagName]
    result = context.API.getDataStatus(context.timeSeriesId, dataStatus)
    expected = True if context.tagsAdded.get(dataStatus.value) else False
    assert_that(result, equal_to(expected))    

@then('we can clear DataStatus "{tagName}"')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    dataStatus = DataStatus[tagName]
    del context.tagsAdded[dataStatus.value]
    context.API.clearDataStatus(context.timeSeriesId, dataStatus)
    result = context.API.getDataStatus(context.timeSeriesId, dataStatus)
    assert_that(not result)

@then('the DataStatus "{tagName}" gets removed')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    dataStatus = DataStatus[tagName]
    result = context.API.getDataStatus(context.timeSeriesId, dataStatus)
    assert_that(not result)

@then('we can retrieve the timestamps as "{dataList}" in units "{units}"')
def step_impl(context, dataList, units):
    """
    :param context: behave.runner.Context
    :param dataList: comma-separated list of float strings
    :param units: units as a string
    """
    # convert string to list: 
    dataList = [float(i) for i in dataList.strip('][').split(', ')]
    units = Units.fromStr(units)
    result = context.API.getTimeStamps(units)
    assert_that(result, equal_to(dataList))

@then('we can retrieve the readings as "{dataList}" in units "{units}"')
def step_impl(context, dataList, units):
    """
    :param context: behave.runner.Context
    :param dataList: comma-separated list of float strings
    :param units: units as a string
    """
    # convert string to list: 
    dataList = [float(i) for i in dataList.strip('][').split(', ')]
    units = Units.fromStr(units)
    result = context.API.getDataSeries(units)
    for a, b in zip(result, dataList):
        assert_that(a, close_to(b, 0.00005))

