'''
Environment for behave.
Provides fixtures to set up and tear down the objects under test.
'''
from behave import fixture, use_fixture
from AmpPhaseDataLib.TimeSeriesAPI import TimeSeriesAPI
from AmpPhaseDataLib.PlotResultAPI import PlotResultAPI
from Utility import ParseTimeStamp
from AmpPhaseDataLib.Constants import DataStatus, DataSource, PlotEl

@fixture
def resultAPI(context, **kwargs):
    # -- SETUP-FIXTURE PART:
    context.API = PlotResultAPI()
    context.resultTags = {}
    yield context.API
    # -- CLEANUP-FIXTURE PART:
    for tag in context.resultTags:
        if DataStatus.exists(tag):
            context.API.clearDataStatus(context.plotResultId, DataStatus[tag])
        if DataSource.exists(tag):
            context.API.clearDataSource(context.plotResultId, DataSource[tag])
    if context.plotResultId:
        context.API.delete(context.plotResultId)

@fixture
def timeSeriesAPI(context, **kwargs):
    # -- SETUP-FIXTURE PART:
    context.API = TimeSeriesAPI()
    assert(context.API.localDatabaseFile)
    context.tagsAdded = {}
    yield context.API
    # -- CLEANUP-FIXTURE PART:
    if context.timeSeriesId:
        for tag in context.tagsAdded:
            if DataStatus.exists(tag):
                context.API.clearDataStatus(context.timeSeriesId, DataStatus[tag])
            if DataSource.exists(tag):
                context.API.clearDataSource(context.timeSeriesId, DataSource[tag])
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

