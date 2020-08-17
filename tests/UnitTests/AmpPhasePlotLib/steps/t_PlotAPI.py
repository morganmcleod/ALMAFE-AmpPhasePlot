'''
Implement test cases for t_PlotAPI.feature
Validate PlotAPI
'''
from behave import given, when, then
from AmpPhaseDataLib.Constants import DataSource
from hamcrest import assert_that
from tempfile import NamedTemporaryFile
import csv
import os

##### GIVEN #####
        
@given('a time series data file on disk')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.dataFile = "SampleData/FETMS-Amp/B2Ae0LO74pol0LSB_20180410-084659__.txt"
    context.tsColumn = 0
    context.dataColumm = 2
    context.delimiter = '\t'
    context.kind = "AMPLITUDE"
    
@given('a phase time series data file on disk')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.dataFile = "SampleData/FETMS-Phase/B6Pe0RF215pol0_20200205-153444__.txt"
    context.tsColumn = 0
    context.dataColumm = 2
    context.delimiter = '\t'    
    context.kind = "PHASE"

@given('we want to show the plot')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.show = True
    
@given('we specify an output file')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    f = NamedTemporaryFile(suffix = '.png', delete = True)
    context.outputName = f.name
    f.close()
    assert_that(not os.path.isfile(context.outputName))
    
@given('we specify units "{units}"')
def step_impl(context, units):
    """
    :param context: behave.runner.Context
    :param units: as str
    """
    context.units = units
        
##### WHEN #####

@when('the time series data is inserted')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    timeStamps = []
    dataSeries = []
    try:
        with open(context.dataFile, 'r') as f:
            reader = csv.reader(f, delimiter=context.delimiter)
            for line in reader:
                # skip header and comment lines:
                if line[0][0].isnumeric():
                    timeStamps.append(line[context.tsColumn])
                    dataSeries.append(float(line[context.dataColumm]))

    except:
        print("Error reading file '{0}'".format(context.dataFile))
        assert_that(False)
    
    context.timeSeriesId = context.tAPI.insertTimeSeries(dataSeries, timeStamps = timeStamps)
    assert_that(context.timeSeriesId)
    
    context.tAPI.setDataSource(context.timeSeriesId, DataSource.DATA_SOURCE, context.dataFile)
    context.tAPI.setDataSource(context.timeSeriesId, DataSource.DATA_KIND, context.kind)
    if hasattr(context, 'units'):
        context.tAPI.setDataSource(context.timeSeriesId, DataSource.UNITS, context.units)

@when('the time series plot is generated')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.pAPI.plotTimeSeries(context.timeSeriesId, outputName = context.outputName, show = context.show))
    
@when('the power spectrum plot is generated')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.pAPI.plotSpectrum(context.timeSeriesId, outputName = context.outputName, show = context.show))

@when('the amplitude stability plot is generated')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.pAPI.plotAmplitudeStability(context.timeSeriesId, outputName = context.outputName, show = context.show))

@when('the phase stability plot is generated')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.pAPI.plotPhaseStability(context.timeSeriesId, outputName = context.outputName, show = context.show))
    
##### THEN #####

@then('the output file was created or updated')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(os.path.isfile(context.outputName))
    
@then('the image data can be retrieved')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.pAPI.imageData is not None)
