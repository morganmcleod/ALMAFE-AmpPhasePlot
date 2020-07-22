from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhaseDataLib.Constants import PlotEl, DataSource, Units
from Plot.Common import makeTitle, makeFooters
from Plot.Plotly.Common import addFooters, makePlotOutput
import plotly.graph_objects as go
from math import log10, floor, ceil

class PlotPowerSpectrum(object):
    '''
    Plot power spectral density using Plotly
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.timeSeriesAPI = TimeSeriesAPI.TimeSeriesAPI()
        self.__reset()
        
    def __reset(self):
        '''
        Reset members to just-constructed state
        '''
        self.imageData = None
        
    def plot(self, timeSeriesId, xArray, yArray, plotElements = {}, outputName = None, show = False):
        '''
        Create a POWER_SPECTRUM plot
        The resulting image data is stored in self.imageData.
        :param timeSeriesId: to retrieve and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: Filename where to write the plot .PNG file, optional.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # clear anything kept from last plot:
        self.__reset()
    
        # get the TimeSeries data:        
        ts = self.timeSeriesAPI
        if not ts.retrieveTimeSeries(timeSeriesId):
            return False

        # Get the DataSource tags:
        dataSources = ts.getAllDataSource(timeSeriesId)
        
        # Get the desired axis units:
        kind = dataSources.get(DataSource.KIND, None)

        xUnits = (Units.HZ).value
        plotElements[PlotEl.XUNITS] = xUnits
        
        yUnits = (Units.AMPLITUDE).value
        plotElements[PlotEl.XUNITS] = xUnits
            
        # Legend for trace:        
        legend = dataSources.get(DataSource.SUBSYSTEM, kind)
        
        # add the trace:
        lines = dict(color='black', width=1)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x = xArray, y = yArray, mode = 'lines', line = lines, name = legend))
        
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
