from AmpPhaseDataLib.TimeSeriesAPI import TimeSeriesAPI
from AmpPhaseDataLib.Constants import DataKind, DataSource, PlotEl, PlotKind, Units 
from Plot.Common import makeTitle, makeFooters
from Plot.Plotly.Common import addComplianceString, addFooters, addSpecLines, makePlotOutput
import plotly.graph_objects as go

class PlotSpectrum(object):
    '''
    Plot amplitude or power spectral density using Plotly
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
        
    def plot(self, timeSeriesId, xArray, yArray, x2Array = None, y2Array = None, 
             plotElements = None, outputName = None, show = False):
        '''
        Create a POWER_SPECTRUM plot from timeSeries.
        The resulting image data is stored in self.imageData.
        The resulting traces ([x], [y], [yError], name) are stored in self.traces 
        :param timeSeriesId: to retrieve and plot
        :param xArray: list of x coordinates to plot
        :param yArray: list of y coordinates to plot, corresponding 1:1 with xArray
        :param x2Array: list of x coordinates to plot for 2nd trace
        :param y2Array: list of y coordinates to plot for 2nd trace, corresponding 1:1 with x2Array
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: Filename where to write the plot .PNG file, optional.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}

        # clear anything kept from last plot:
        self.__reset()
    
        # get the TimeSeries data:        
        if not self.timeSeriesAPI:
            self.timeSeriesAPI = TimeSeriesAPI()

        timeSeries = self.timeSeriesAPI.retrieveTimeSeries(timeSeriesId)
        if not timeSeries:
            return False
        
        # Get the DataSource tags:
        dataSources = self.timeSeriesAPI.getAllDataSource(timeSeriesId)
        dataKind = DataKind.fromStr(dataSources.get(DataSource.DATA_KIND, (DataKind.AMPLITUDE).value))
        
        # set the X axis units:
        xUnits = (Units.HZ).value
        plotElements[PlotEl.XUNITS] = xUnits

        # set the Y axis units:
        if dataKind == DataKind.POWER:
            if timeSeries.dataUnits == Units.VOLTS:
                yUnits = (Units.VOLTS_SQ).value
            else:
                yUnits = timeSeries.dataUnits.value
        elif dataKind == DataKind.VOLTAGE:
            yUnits = (Units.VOLTS).value
        elif dataKind == DataKind.PHASE:
            yUnits = (Units.DEG).value
        else:
            yUnits = timeSeries.dataUnits.value
        plotElements[PlotEl.YUNITS] = yUnits
        
        # set the trace legend:
        legend = "Real FFT({0})".format(yUnits)

        # set the Y axis label:
        if yUnits == (Units.VOLTS_SQ).value:
            plotElements[PlotEl.Y_AXIS_LABEL] = (Units.PER_HZ).value.format(yUnits)
        else:
            plotElements[PlotEl.Y_AXIS_LABEL] = (Units.PER_ROOT_HZ).value.format(yUnits)
        
        # save the trace:
        self.traces = [(xArray, yArray, [], legend)] 
        
        # check for highlight points:
        if x2Array and y2Array:
            legend2 = plotElements.get(PlotEl.FFT_LEGEND2, '')
            self.traces.append((x2Array, y2Array, [], legend2))
        
        # Plot title:
        title = makeTitle([timeSeriesId], plotElements)
        plotElements[PlotEl.TITLE] = title
        
        # Make plot footer strings:
        footer1, footer2, footer3 = makeFooters([timeSeriesId], plotElements, 
                    self.timeSeriesAPI.getAllDataStatus(timeSeriesId), timeSeries.startTime)
        plotElements[PlotEl.FOOTER1] = footer1
        plotElements[PlotEl.FOOTER2] = footer2
        plotElements[PlotEl.FOOTER3] = footer3
        
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

        # add the highlight trace, if any:
        if len(self.traces) > 1:
            trace = self.traces[1]
            legend = trace[3]
            marker = dict(color = plotElements.get(PlotEl.FFT_COLOR2, 'red'), size = 3)
            fig.add_trace(go.Scatter(x = trace[0], y = trace[1], mode = 'markers', marker = marker, name = legend))

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
        
        # expand plot window:
        window = plotElements.get(PlotEl.XRANGE_WINDOW, None)
        if window:
            window = window.split(', ')
            window = [float(window[0]), float(window[1])]
            fig.update_xaxes(range = window)

        window = plotElements.get(PlotEl.YRANGE_WINDOW, None)
        if window:
            window = window.split(', ')
            window = [float(window[0]), float(window[1])]
            fig.update_yaxes(range = window)
            
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
        