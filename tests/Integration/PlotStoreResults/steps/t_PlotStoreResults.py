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
    context.dataColumm = 2
    context.temp1Column = 4
    context.temp2Column = 5
    context.delimiter = '\t'
    context.kind = "amplitude"
    context.units = "W"

@given('a phase time series data file on disk')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.dataFile = "SampleData/FETMS-Phase/B6Pe0RF215pol0_20200205-153444__.txt"
    context.tau0Seconds = 1.0
    context.tsColumn = 0
    context.dataColumm = 2
    context.temp1Column = 5
    context.temp2Column = 6
    context.delimiter = '\t'
    context.kind = "phase"
    context.units = "deg"

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
                    dataSeries.append(float(line[context.dataColumm]))
                    temperatures1.append(float(line[context.temp1Column]))
                    temperatures2.append(float(line[context.temp2Column]))
    except:
        print("Error reading file '{0}'".format(context.dataFile))
        assert_that(False)
    
    context.timeSeriesId = context.tAPI.insertTimeSeries(dataSeries, tau0Seconds = context.tau0Seconds, timeStamps = timeStamps)
    assert_that(context.timeSeriesId)
    
    context.tAPI.setDataSource(context.timeSeriesId, DataSource.DATA_SOURCE, context.dataFile)
    context.tAPI.setDataSource(context.timeSeriesId, DataSource.KIND, context.kind)
    context.tAPI.setDataSource(context.timeSeriesId, DataSource.UNITS, context.units)
    if hasattr(context, 'units'):
        context.tAPI.setDataSource(context.timeSeriesId, DataSource.UNITS, context.units)        
    
@when('the power spectrum plot is generated')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.pAPI.plotPowerSpectrum(context.timeSeriesId, plotElements = {}, show = context.show))
    context.plotKind = PlotKind.POWER_SPECTRUM
    context.imageData = context.pAPI.imageData

@when('the amplitude stability plot is generated')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    plotElements = {PlotEl.SPEC_LINE1 : SpecLines.FE_AMP_STABILITY1, 
                    PlotEl.SPEC_LINE2 : SpecLines.FE_AMP_STABILITY2}
    assert_that(context.pAPI.plotAmplitudeStability(context.timeSeriesId, plotElements, show = context.show))
    context.plotKind = PlotKind.AMP_STABILITY
    context.imageData = context.pAPI.imageData

@when('the phase stability plot is generated')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    plotElements = {PlotEl.SPEC_LINE1 : SpecLines.FE_PHASE_STABILITY}
    assert_that(context.pAPI.plotPhaseStability(context.timeSeriesId, plotElements, show = context.show))
    context.plotKind = PlotKind.PHASE_STABILITY
    context.imageData = context.pAPI.imageData

@when('the result is retrieved from the database')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.rAPI.retrieveResult(context.resultId))
    
##### THEN #####

@then('the plot header can be stored in a result')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.resultId = context.rAPI.createResult('t_PlotStoreResults')
    assert_that(context.resultId)
    context.plotId = context.rAPI.createPlot(context.resultId, context.plotKind)
    assert_that(context.plotId)

@then('the plot image can be stored in a result')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.imageData)
    context.plotImageId = context.rAPI.insertPlotImage(context.plotId, context.imageData, name = 't_PlotStoreResults:image', srcPath = context.dataFile)
    assert_that(context.plotImageId)
    
@then('the plot traces and attributes can be stored in the result')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.pAPI.traces)
    context.traces = context.pAPI.traces
    for trace in context.traces:
        assert_that(context.rAPI.createTrace(context.plotId, trace, trace[3]))
    context.plotElements = context.pAPI.plotElementsFinal
    assert_that(context.plotElements)
    context.rAPI.setAllPlotEl(context.plotId, context.plotElements)

@then('the plot image can be retrieved')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    imageData = context.rAPI.retrievePlotImage(context.plotImageId)
    assert_that(imageData is not None)

def compareLists(list1, list2):
    '''
    Compare list elements with some allowance for float representation error
    :param list1:
    :param list2:
    '''
    for x1, x2 in zip(list1, list2):
        assert_that(x1, close_to(x2, 0.00000001))

@then('the plot traces can be retrieved')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    traces = context.rAPI.retrieveTraces(context.plotId)
    assert_that(len(traces), equal_to(len(context.traces)))
    for stored, retrieved in zip(context.traces, traces):
        assert_that(retrieved[2], equal_to(stored[3])) #compare name
        xyData = retrieved[1]
        assert_that(len(xyData[0]), equal_to(len(stored[0])))  #compare x arrays
        compareLists(xyData[0], stored[0])

        assert_that(len(xyData[1]), equal_to(len(stored[1])))  #compare y arrays
        compareLists(xyData[1], stored[1])
        
        assert_that(len(xyData[2]), equal_to(len(stored[2])))  #compare yErrors
        compareLists(xyData[2], stored[2])
        
@then('the plot attributes can be retrieved')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    plotElements = context.rAPI.getAllPlotEl(context.plotId)
    assert_that(plotElements)
    assert_that(plotElements, equal_to(context.plotElements))
    
@then('the plot can be regenerated and the image matches')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    plotIds = context.rAPI.retrievePlotIds(context.resultId, context.plotKind)
    assert_that(len(plotIds), greater_than(0), "retrived Id")
    plotId = context.pAPI.rePlot(plotIds[0], plotElements = {}, show = context.show)
    assert_that(plotId, "got replot Id")
    assert_that(context.pAPI.imageData, "got imageData")
    assert_that(context.pAPI.imageData, equal_to, context.imageData)
    