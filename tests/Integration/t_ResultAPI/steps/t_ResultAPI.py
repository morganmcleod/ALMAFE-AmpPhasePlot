'''
test generating plots from time series 
  storing and retrieving from Results
  re-plotting from data in Results
'''
from behave import given, when, then
from AmpPhaseDataLib.Constants import PlotKind, DataSource, PlotEl, SpecLines
from hamcrest import assert_that, equal_to, close_to, greater_than
import csv

##### GIVEN #####

@given('an amplitude time series data file on disk')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.dataFile = "SampleData/FETMS-Amp/B2Ae0LO74pol0USB_20180410-081528__.txt"
    context.tau0Seconds = 0.05
    context.tsColumn = 0
    context.dataColumn = 2
    context.temp1Column = 4
    context.temp2Column = 5
    context.delimiter = '\t'
    context.kind = "amplitude"
    context.units = "W"

@given('we want to show the plot')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.show = True

##### WHEN #####
        
@when('the time series data is inserted')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    timeStamps = []
    dataSeries = []
    temperatures1 = []
    temperatures2 = []
    try:
        with open(context.dataFile, 'r') as f:
            reader = csv.reader(f, delimiter=context.delimiter)
            for line in reader:
                # skip header and comment lines:
                if line[0][0].isnumeric():
                    timeStamps.append(line[context.tsColumn])
                    dataSeries.append(float(line[context.dataColumn]))
                    temperatures1.append(float(line[context.temp1Column]))
                    temperatures2.append(float(line[context.temp2Column]))
    except:
        print("Error reading file '{0}'".format(context.dataFile))
        assert_that(False)
    
    context.timeSeriesId = context.tAPI.insertTimeSeries(dataSeries, tau0Seconds = context.tau0Seconds, timeStamps = timeStamps)
    assert_that(context.timeSeriesId)
    
    context.tAPI.setDataSource(context.timeSeriesId, DataSource.DATA_SOURCE, context.dataFile)
    context.tAPI.setDataSource(context.timeSeriesId, DataSource.DATA_KIND, context.kind)
    context.tAPI.setDataSource(context.timeSeriesId, DataSource.UNITS, context.units)
    if hasattr(context, 'units'):
        context.tAPI.setDataSource(context.timeSeriesId, DataSource.UNITS, context.units)        

@when('the amplitude stability plot is generated')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    plotElements = {PlotEl.SPEC_LINE1 : SpecLines.FE_AMP_STABILITY1, 
                    PlotEl.SPEC_LINE2 : SpecLines.FE_AMP_STABILITY2}
    assert_that(context.pAPI.plotAmplitudeStability(context.timeSeriesId, plotElements, show = context.show))
    context.plotKind = PlotKind.POWER_STABILITY
    context.imageData = context.pAPI.imageData
    
##### THEN #####

@then('the plot image can be stored in a result')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.imageData)
    context.plotResultId = context.rAPI.create('t_PlotStoreResults:result')
    context.plotImageId = context.rAPI.insertPlotImage(
        context.plotResultId, context.imageData, 
        name = 't_PlotStoreResults:image', kind = context.plotKind, srcPath = context.dataFile)
    assert_that(context.plotResultId)
    assert_that(context.plotImageId)

@then('the plot image can be retrieved by its plotId')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    image = context.rAPI.retrievePlotImage(context.plotImageId)
    assert_that(image is not None)

@then('the plot image can be retrieved by the resultId')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    images = context.rAPI.retrievePlotImages(context.plotResultId)
    assert_that(images is not None)
    assert_that(len(images) == 1)
    assert_that(images[0] is not None)
