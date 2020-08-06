from AmpPhaseDataLib import TimeSeriesAPI, ResultAPI
from AmpPhaseDataLib.Constants import *
from Plot.Common import makeTitle, makeFooters
from Plot.Plotly.Common import addComplianceString, addFooters, addSpecLines, makePlotOutput
import plotly.graph_objects as go

class PlotPowerSpectrum(object):
    '''
    Plot power spectral density using Plotly
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.timeSeriesAPI = None
        self.resultAPI = None
        self.__reset()
        
    def __reset(self):
        '''
        Reset members to just-constructed state
        '''
        self.imageData = None
        self.traces = []
        
    def plot(self, timeSeriesId, xArray, yArray, plotElements = {}, outputName = None, show = False):
        '''
        Create a POWER_SPECTRUM plot from timeSeries.
        The resulting image data is stored in self.imageData.
        The resulting traces ([x], [y], [yError], name) are stored in self.traces 
        :param timeSeriesId: to retrieve and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: Filename where to write the plot .PNG file, optional.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # clear anything kept from last plot:
        self.__reset()
    
        # get the TimeSeries data:
        if not self.timeSeriesAPI:
            self.timeSeriesAPI = TimeSeriesAPI.TimeSeriesAPI()
        ts = self.timeSeriesAPI
        if not ts.retrieveTimeSeries(timeSeriesId):
            return False

        # Get the DataSource tags:
        dataSources = ts.getAllDataSource(timeSeriesId)
        dataKind = dataSources.get(DataSource.DATA_KIND, (DataKind.AMPLITUDE).value)
        
        # set the X axis units:
        xUnits = (Units.HZ).value
        plotElements[PlotEl.XUNITS] = xUnits

        # set the Y axis units:
        yUnits = dataSources.get(DataSource.UNITS, None)
        if not yUnits:
            if dataKind == (DataKind.VOLTAGE).value:
                yUnits = (Units.VOLTS).value
            elif dataKind == (DataKind.PHASE).value:
                yUnits = (Units.DEG).value
            elif dataKind == (DataKind.POWER).value:
                yUnits = (Units.WATTS).value
            else:
                yUnits = (Units.AMPLITUDE).value
        plotElements[PlotEl.YUNITS] = yUnits
        
        # set the trace legend:
        if dataKind == (DataKind.POWER).value:
            legend = "PSD({0})".format(yUnits)            
        else:
            legend = "ASD({0})".format(yUnits)

        # set the Y axis label:
        plotElements[PlotEl.Y_AXIS_LABEL] = (Units.PER_ROOT_HZ).value.format(yUnits)
        
        # save the trace:
        self.traces = [(xArray, yArray, [], legend)] 
        
        # Plot title:
        title = makeTitle([timeSeriesId], plotElements)
        plotElements[PlotEl.TITLE] = title
        
        # Make plot footer strings:
        footer1, footer2, footer3 = makeFooters([timeSeriesId], plotElements, ts.getAllDataStatus(timeSeriesId), ts.startTime)
        plotElements[PlotEl.FOOTER1] = footer1
        plotElements[PlotEl.FOOTER2] = footer2
        plotElements[PlotEl.FOOTER3] = footer3
        
        # Generate the plot:
        return self.__plot(plotElements, outputName, show)

    def rePlot(self, plotId, plotElements = {}, outputName = None, show = False):
        '''
        Recreate a POWER_SPECTRUM plot from traces and plotElements stored in the Result database.
        The resulting image data is stored in self.imageData.
        :param plotId: to retrieve and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: Filename where to write the plot .PNG file, optional.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # clear anything kept from last plot:
        self.__reset()

        if not self.resultAPI:
            self.resultAPI = ResultAPI.ResultAPI()
        ra = self.resultAPI

        # get the Plot header:
        plotHeader = ra.retrievePlot(plotId)
        if not plotHeader:
            return False
        
        # check retrieved plotId:
        assert(plotHeader[0] == plotId)
        
        # check retrived PlotKind:
        plotKind = plotHeader[1] 
        if not (plotKind == PlotKind.AMPLITUDE_SPECTRUM or plotKind == PlotKind.POWER_SPECTRUM): 
            return False

        # get the stored plotElements and merge in any overrides:
        plotElementsStored = ra.getAllPlotEl(plotId)
        plotElements = {**plotElementsStored, **plotElements}
        
        # get the axis units:
        xUnits = plotElements.get(PlotEl.XUNITS, (Units.HZ).value)
        plotElements[PlotEl.XUNITS] = xUnits
        yUnits = plotElements.get(PlotEl.YUNITS, (Units.AMPLITUDE).value)
        plotElements[PlotEl.YUNITS] = yUnits
        
        # Get the trace data
        traces = ra.retrieveTraces(plotId)
        if not traces:
            return False
        trace = traces[0]
        xyData = trace[1]
        legend = trace[3]        
        self.traces = [(xyData[0], xyData[1], xyData[2], legend)]
        
        # Generate the plot:
        return self.__plot(plotElements, outputName, show)
        
    def __plot(self, plotElements, outputName = None, show = False):
        '''
        implementation helper shared by plot() and rePlot()
        Uses the contents of self.traces [([x], [y], [yError], name)] 
        and the provided plotElements to produce the output plot.
        :param plotElements: dict of {PLotElement : str}
        :param outputName: optional filename where to write the plot .PNG file
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        
        # get the axis units:
        xUnits = plotElements[PlotEl.XUNITS]
        yUnits = plotElements[PlotEl.YUNITS]
        
        # Get the trace data
        trace = self.traces[0]
        legend = trace[3]
        
        # add the trace:
        fig = go.Figure()
        lines = dict(color='blue', width=1)
        fig.add_trace(go.Scatter(x = trace[0], y = trace[1], mode = 'lines', line = lines, name = legend))

        # add spec lines:
        addSpecLines(fig, plotElements)
        
        # X axis label:
        xAxisLabel = plotElements.get(PlotEl.X_AXIS_LABEL, None)
        if not xAxisLabel:
            xAxisLabel = "frequency [" + xUnits + "]"  
            plotElements[PlotEl.X_AXIS_LABEL] = xAxisLabel
        fig.update_xaxes(title_text = xAxisLabel)

        # Y axis label:
        yAxisLabel = plotElements.get(PlotEl.Y_AXIS_LABEL, None)
        if not yAxisLabel:
            yAxisLabel = yUnits
            plotElements[PlotEl.Y_AXIS_LABEL] = yAxisLabel
        fig.update_yaxes(title_text = yAxisLabel)

        # default to log-log plot, but allow overrides:
        xaxis_type = "linear" if plotElements.get(PlotEl.X_LINEAR, False) else "log"
        yaxis_type = "linear" if plotElements.get(PlotEl.Y_LINEAR, False) else "log"
        
        # scientific notation on Y:
        fig.update_layout(xaxis_type = xaxis_type, yaxis_type = yaxis_type, showlegend = True, 
                          yaxis = dict(showexponent = 'all', exponentformat = 'e'))
        
        # Compliance string:
        compliance = plotElements.get(PlotEl.SPEC_COMPLIANCE, None)
        if compliance:
            addComplianceString(fig, compliance) 
        
        # Plot title:
        title = plotElements.get(PlotEl.TITLE, "")
        fig.update_layout(title_text = title)
        
        # Plot footers:
        footer1 = plotElements.get(PlotEl.FOOTER1, "")
        footer2 = plotElements.get(PlotEl.FOOTER2, "")
        footer3 = plotElements.get(PlotEl.FOOTER3, "")
        addFooters(fig, footer1, footer2, footer3)
        
        # make and show plot:
        self.imageData = makePlotOutput(fig, plotElements, outputName, show)
        return True
        