'''
Environment for behave.
Provides fixtures to set up and tear down the objects under test.
'''
from behave import fixture, use_fixture
from AmpPhaseDataLib import TimeSeriesAPI, ResultAPI
from AmpPhasePlotLib import PlotAPI

@fixture
def plotStoreResults(context, **kwargs):
    # -- SETUP-FIXTURE PART:
    context.tAPI = TimeSeriesAPI.TimeSeriesAPI()
    context.rAPI = ResultAPI.ResultAPI()
    context.pAPI = PlotAPI.PlotAPI()
    context.show = False
    context.timeSeriesId = None
    context.resultId = None
    yield context.pAPI
    # -- CLEANUP-FIXTURE PART:
    if context.timeSeriesId:
        context.tAPI.deleteTimeSeries(context.timeSeriesId)
    if context.resultId:
        context.rAPI.deleteResult(context.resultId)
        
def before_tag(context, tag):
    '''
    Select the fixture to use depending on tags in the .feature file.
    '''
    if tag == "fixture.plotStoreResults":
        use_fixture(plotStoreResults, context)
