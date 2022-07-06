'''
Environment for behave.
Provides fixtures to set up and tear down the objects under test.
'''
from behave import fixture, use_fixture
from AmpPhaseDataLib.TimeSeriesAPI import TimeSeriesAPI
from AmpPhaseDataLib.PlotResultAPI import PlotResultAPI
from AmpPhasePlotLib.PlotAPI import PlotAPI

@fixture
def plotStoreResults(context, **kwargs):
    # -- SETUP-FIXTURE PART:
    context.tAPI = TimeSeriesAPI()
    context.rAPI = PlotResultAPI()
    context.pAPI = PlotAPI()
    context.show = False
    context.timeSeriesId = None
    context.resultId = None
    yield context.pAPI
    # -- CLEANUP-FIXTURE PART:
    if context.timeSeriesId:
        context.tAPI.deleteTimeSeries(context.timeSeriesId)
    if context.plotResultId:
        context.rAPI.delete(context.plotResultId)
        
def before_tag(context, tag):
    '''
    Select the fixture to use depending on tags in the .feature file.
    '''
    if tag == "fixture.plotStoreResults":
        use_fixture(plotStoreResults, context)
