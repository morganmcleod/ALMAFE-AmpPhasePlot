'''
Implement test cases for t_AmpPhaseDataLib.feature
Validate AmpPhaseDataLib API
'''
from behave import given, when, then 
from AmpPhaseDataLib import AmpPhaseDataLib, ParseTimeStamp
from hamcrest import assert_that, equal_to, close_to
from builtins import int
from datetime import datetime
   
@given('the configuration filename')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    #nothing to do
    
@when('the object is created')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    context.libObj = AmpPhaseDataLib.AmpPhaseDataLib()
    
@then('the database filename is stored')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    assert_that(context.libObj.localDatabaseFile)
        
@given('dataSeries list "{dataList}" and timestamp list "{timeStampList}"')
def step_impl(context, dataList, timeStampList):
    """
    :param context: behave.runner.Context
    :param dataList: comma-separated list of float strings
    :param timeStampList: comma-separated list of datetime strings
    """
    # convert strings to lists: 
    context.dataSeries = dataList.strip('][').split(', ')
    context.timeStamps = timeStampList.strip('][').split(', ')

@when('the data is inserted')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.libObj = AmpPhaseDataLib.AmpPhaseDataLib()
    context.dataSeriesId = context.libObj.insertTimeSeries(dataSeries = context.dataSeries, timeStamps = context.timeStamps)
    
@then('startTime is "{timeStampString}"')
def step_impl(context, timeStampString):
    '''
    :param context: behave.runner.Context
    :param timeStampString: a datetime as string
    '''
    tsParser = ParseTimeStamp.ParseTimeStamp()
    timeStamp = tsParser.parseTimeStamp(timeStampString)
    assert_that(context.libObj.startTime, equal_to(timeStamp))
    
@then('tau0Seconds is "{floatString}"')
def step_impl(context, floatString):
    '''
    :param context: behave.runner.Context
    :param floatString: a float as string
    '''
    tau0Seconds = float(floatString)
    assert_that(context.libObj.tau0Seconds, equal_to(tau0Seconds))

@then('dataSeries is a list of "{intString}" elements')
def step_impl(context, intString):
    '''
    :param context: behave.runner.Context
    :param intString: an int as string
    '''
    dataLen = int(intString)
    assert_that(len(context.libObj.dataSeries), equal_to(dataLen))
    
@then('timeStamps is a list of "{intString}" elements')
def step_impl(context, intString):
    '''
    :param context: behave.runner.Context
    :param intString: an int as string
    '''
    dataLen = int(intString)
    assert_that(len(context.libObj.timeStamps), equal_to(dataLen))

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
    
@when('the measurement loop runs using description "{description}"')
def step_impl(context, description):
    """
    :param context: behave.runner.Context
    :param description: string
    """
    context.description = description
    context.now = datetime.now()    
    
    context.libObj = AmpPhaseDataLib.AmpPhaseDataLib()
    context.dataSeriesId = context.libObj.startTimeSeries(context.tau0Seconds, description=description)
    for item in context.dataSeries:
        context.libObj.insertTimeSeriesChunk(float(item))
    context.libObj.finishTimeSeries()
    
@then('startTime is close to now')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    delta = max(context.libObj.startTime, context.now) - min(context.libObj.startTime, context.now)
    assert_that(delta.seconds, close_to(0, 0.05))
    
@then('the time series can be retrieved from the database')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    assert_that(context.libObj.retrieveTimeSeries(context.dataSeriesId))
    
@then('the description matches')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    assert_that(context.libObj.description, equal_to(context.description))
    
@then('the data has timeStamps starting now with steps of "{floatString}"')
def step_impl(context, floatString):
    """
    :param context: behave.runner.Context
    :param floatString: a float as string
    """
    tau0Seconds = float(floatString)
    delta = context.libObj.timeStamps[0] - context.now
    deltaSeconds = delta.seconds + (delta.microseconds / 1.0e6)
    assert_that(deltaSeconds, close_to(0.0, 0.05))
    firstTime = True
    for TS in context.libObj.timeStamps:
        if firstTime:
            TS0 = TS
            firstTime = False
        else:
            delta = TS - TS0
            deltaSeconds = delta.seconds + (delta.microseconds / 1.0e6)
            assert_that(deltaSeconds, equal_to(tau0Seconds))
            TS0 = TS

@then('we can add tag "{tagName}" with value "{tagValue}"')
def step_impl(context, tagName, tagValue):
    """
    :param context: behave.runner.Context
    :param tagName: str
    :param tagValue: str
    """
    if not hasattr(context, 'tagsAdded'):
        context.tagsAdded = {}
    context.tagsAdded[tagName] = tagValue
    context.libObj.setTimeSeriesTags(context.dataSeriesId, {tagName: tagValue})

@then('we can add tag "{tagName}" with value ""')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    if not hasattr(context, 'tagsAdded'):
        context.tagsAdded = {}
    context.tagsAdded[tagName] = ""
    context.libObj.setTimeSeriesTags(context.dataSeriesId, {tagName: ""})
    
@then('we can retrieve tag "{tagName}" and the value matches')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    if not hasattr(context, 'tagsAdded'):
        context.tagsAdded = {}
    tagValue = context.libObj.getTimeSeriesTags(context.dataSeriesId, [tagName])[tagName]
    assert_that(tagValue, equal_to(context.tagsAdded[tagName]))
    
@then('we cannot retrieve tag "{tagName}"')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    tagValue = context.libObj.getTimeSeriesTags(context.dataSeriesId, [tagName])[tagName]
    assert_that(tagValue, equal_to(None))
    
@then('we can delete tag "{tagName}"')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    if not hasattr(context, 'tagsAdded'):
        context.tagsAdded = {} 
    del context.tagsAdded[tagName]
    context.libObj.setTimeSeriesTags(context.dataSeriesId, {tagName: None})
