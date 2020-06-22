'''
Environment for behave.
Provides fixtures to set up and tear down the objects under test.
'''
from behave import fixture, use_fixture
from AmpPhaseDataLib import ResultAPI
from AmpPhaseDataLib import TimeSeriesAPI
from Utility import ParseTimeStamp
from AmpPhaseDataLib.Constants import DataStatus, DataSource, PlotElement

@fixture
def resultAPI(context, **kwargs):
    # -- SETUP-FIXTURE PART:
    context.API = ResultAPI.ResultAPI()
    context.resultTags = {}
    context.plotTags = {}
    yield context.API
    # -- CLEANUP-FIXTURE PART:
    for tag in context.resultTags:
        if DataStatus.exists(tag):
            context.API.clearResultDataStatus(context.resultId, DataStatus[tag])
        if DataSource.exists(tag):
            context.API.clearResultDataSource(context.resultId, DataSource[tag])
    for tag in context.plotTags:
        if PlotElement.exists(tag):
            context.API.clearPlotElement(context.plotId, PlotElement[tag])
    if context.resultId:
        context.API.deleteResult(context.resultId)

@fixture
def timeSeriesAPI(context, **kwargs):
    # -- SETUP-FIXTURE PART:
    context.API = TimeSeriesAPI.TimeSeriesAPI()
    assert(context.API.localDatabaseFile)
    context.tagsAdded = {}
    yield context.API
    # -- CLEANUP-FIXTURE PART:
    for tag in context.tagsAdded:
        if DataStatus.exists(tag):
            context.API.clearDataStatus(context.timeSeriesId, DataStatus[tag])
        if DataSource.exists(tag):
            context.API.clearDataSource(context.timeSeriesId, DataSource[tag])
    if context.timeSeriesId:
        context.API.deleteTimeSeries(context.timeSeriesId)

@fixture
def parseTimeStamp(context, **kwargs):
    # -- SETUP-FIXTURE PART:
    context.tsParser = ParseTimeStamp.ParseTimeStamp()
    yield context.tsParser
    # -- CLEANUP-FIXTURE PART:
    context.tsParser = None

def before_tag(context, tag):
    '''
    Select the fixture to use depending on tags in the .feature file.
    '''
    if tag == "fixture.resultAPI":
        use_fixture(resultAPI, context)
    elif tag == "fixture.timeSeriesAPI":
        use_fixture(timeSeriesAPI, context)
    elif tag == "fixture.parseTimeStamp":
        use_fixture(parseTimeStamp, context)

