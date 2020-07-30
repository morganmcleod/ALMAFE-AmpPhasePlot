'''
Environment for behave.
Provides fixtures to set up and tear down the objects under test.
'''
from behave import fixture, use_fixture
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
import os

@fixture
def plotAPI(context, **kwargs):
    # -- SETUP-FIXTURE PART:
    context.tAPI = TimeSeriesAPI.TimeSeriesAPI()
    context.pAPI = PlotAPI.PlotAPI()
    context.show = False
    yield context.pAPI
    # -- CLEANUP-FIXTURE PART:
    if context.timeSeriesId:
        context.tAPI.deleteTimeSeries(context.timeSeriesId)
    if hasattr(context, 'outputName'):
        if context.outputName and os.path.isfile(context.outputName):
            os.remove(context.outputName)
        del context.outputName

def before_tag(context, tag):
    '''
    Select the fixture to use depending on tags in the .feature file.
    '''
    if tag == "fixture.plotAPI":
        use_fixture(plotAPI, context)
