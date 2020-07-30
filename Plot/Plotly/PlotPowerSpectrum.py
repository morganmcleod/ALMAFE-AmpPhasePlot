from AmpPhaseDataLib import TimeSeriesAPI, ResultAPI
from AmpPhaseDataLib.Constants import PlotKind, PlotEl, DataSource, Units
from Plot.Common import makeTitle, makeFooters
from Plot.Plotly.Common import addFooters, makePlotOutput
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
        
        # set the axis units:
        xUnits = (Units.HZ).value
        plotElements[PlotEl.XUNITS] = xUnits
        
        yUnits = (Units.AMPLITUDE).value
        plotElements[PlotEl.YUNITS] = yUnits
            
        # Legend for trace:        
        kind = dataSources.get(DataSource.KIND, None)
        legend = dataSources.get(DataSource.SUBSYSTEM, kind)
        if not legend:
            legend = 'power spectrum'
        
        # add the trace:
        lines = dict(color='black', width=1)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x = xArray, y = yArray, mode = 'lines', line = lines, name = legend))
        self.traces = [(xArray, yArray, [], legend)] 
        
        # X axis label:
        xAxisLabel = plotElements.get(PlotEl.X_AXIS_LABEL, None)
        if not xAxisLabel:
            xAxisLabel = "frequency [" + xUnits + "]"  
        fig.update_xaxes(title_text = xAxisLabel)
        plotElements[PlotEl.X_AXIS_LABEL] = xAxisLabel

        # Y axis label:
        yAxisLabel = plotElements.get(PlotEl.Y_AXIS_LABEL, None)
        if not yAxisLabel:
            yAxisLabel = yUnits
        fig.update_yaxes(title_text = yAxisLabel)
        plotElements[PlotEl.Y_AXIS_LABEL] = yAxisLabel

        # log-log plot, scientific notation on Y:
        fig.update_layout(xaxis_type="log", yaxis_type="log", showlegend=True, 
                          yaxis = dict(showexponent = 'all', exponentformat = 'e'))
        
        # Plot title:
        title = makeTitle([timeSeriesId], plotElements)
        fig.update_layout(title_text = title)
        
        # Plot footers:
        footer1, footer2, footer3 = makeFooters([timeSeriesId], plotElements, ts.getAllDataStatus(timeSeriesId), ts.startTime)
        addFooters(fig, footer1, footer2, footer3)
        
        # make and show plot:
        self.imageData = makePlotOutput(fig, plotElements, outputName, show)
        return True

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
        plot = ra.retrievePlot(plotId)
        if not plot:
            return False
        if not plot[1] == PlotKind.POWER_SPECTRUM:
            return False

        # get the stored plotElements and merge in any overrides:
        plotElementsStored = ra.getAllPlotEl(plotId)
        plotElements = {**plotElementsStored, **plotElements}
        
        # set the axis units:
        xUnits = (Units.HZ).value
        plotElements[PlotEl.XUNITS] = xUnits
        
        yUnits = (Units.AMPLITUDE).value
        plotElements[PlotEl.YUNITS] = yUnits
        
        # Get the trace data
        traces = ra.retrieveTraces(plotId)
        if not traces:
            return False
        xyData = traces[0][1]
        legend = traces[0][3]
        
        # add the trace:
        lines = dict(color='black', width=1)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x = xyData[0], y = xyData[1], mode = 'lines', line = lines, name = legend))
        
        # X axis label:
        xAxisLabel = plotElements.get(PlotEl.X_AXIS_LABEL, None)
        if not xAxisLabel:
            xAxisLabel = "frequency [" + xUnits + "]"  
        fig.update_xaxes(title_text = xAxisLabel)
        plotElements[PlotEl.X_AXIS_LABEL] = xAxisLabel

        # Y axis label:
        yAxisLabel = plotElements.get(PlotEl.Y_AXIS_LABEL, None)
        if not yAxisLabel:
            yAxisLabel = yUnits
        fig.update_yaxes(title_text = yAxisLabel)
        plotElements[PlotEl.Y_AXIS_LABEL] = yAxisLabel

        # log-log plot, scientific notation on Y:
        fig.update_layout(xaxis_type="log", yaxis_type="log", showlegend=True, 
                          yaxis = dict(showexponent = 'all', exponentformat = 'e'))
        
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
        