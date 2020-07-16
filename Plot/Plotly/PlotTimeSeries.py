from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhaseDataLib.Constants import PlotEl, DataSource, Units
from Plot.Common import makeTitle, makeFooters
from Plot.Plotly.Common import addFooters, makePlotOutput
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class PlotTimeSeries(object):
    '''
    Plot TimeSeries using Plotly
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
        
    def plot(self, timeSeriesId, plotElements = {}, outputName = None, show = False):
        '''
        Create a TIME_SERIES plot
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

        xUnits = plotElements.get(PlotEl.XUNITS, (Units.LOCALTIME).value)
        plotElements[PlotEl.XUNITS] = xUnits  # save it in case default was used
        
        yUnits = plotElements.get(PlotEl.YUNITS, None)
        if not yUnits:
            if kind == "phase":
                yUnits = dataSources.get(DataSource.UNITS, (Units.DEG).value)
            else:
                yUnits = dataSources.get(DataSource.UNITS, (Units.WATTS).value)
            plotElements[PlotEl.YUNITS] = yUnits
        
        y2Units = plotElements.get(PlotEl.Y2UNITS, None)
        if not y2Units:
            y2Units = dataSources.get(DataSource.T_UNITS, (Units.KELVIN).value)
            plotElements[PlotEl.Y2UNITS] = y2Units
                    
        # get timestamps and data, possibly with unit conversions:
        timeStamps = ts.getTimeStamps(requiredUnits = Units.fromStr(xUnits))
        dataSeries = ts.getDataSeries(requiredUnits = Units.fromStr(yUnits))

        # Legend for trace:        
        legend = dataSources.get(DataSource.SUBSYSTEM, kind)

        # add the trace(s), compute temperature trace spans:
        y2min = None
        y2max = None
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x = timeStamps, y = dataSeries, mode = 'lines', name = legend), secondary_y=False)
        if ts.temperatures1:
            fig.add_trace(go.Scatter(x = timeStamps, y = ts.temperatures1, mode = 'lines', name = 'Sensor 1'), secondary_y=True)
            y2min = min(ts.temperatures1)
            y2max = min(ts.temperatures1)
        if ts.temperatures2:
            fig.add_trace(go.Scatter(x = timeStamps, y = ts.temperatures2, mode = 'lines', name = 'Sensor 2'), secondary_y=True)
            if y2min:
                y2min = min(y2min, min(ts.temperatures2))
                y2max = max(y2max, max(ts.temperatures2))
            
        # X axis label:
        xAxisLabel = plotElements.get(PlotEl.X_AXIS_LABEL, None)
        if not xAxisLabel:
            if xUnits == (Units.LOCALTIME).value:
                xAxisLabel = xUnits
            elif xUnits == (Units.SECONDS).value or xUnits == (Units.MINUTES).value:
                xAxisLabel = "time [" + xUnits + "]"  
        fig.update_xaxes(title_text = xAxisLabel)
        plotElements[PlotEl.X_AXIS_LABEL] = xAxisLabel

        # Y axis label:
        yAxisLabel = plotElements.get(PlotEl.Y_AXIS_LABEL, None)
        if not yAxisLabel:
            yAxisLabel = kind if kind else "amplitude"
            yAxisLabel += " [" + yUnits + "]"
        tickformat = ".3f" if yUnits == (Units.DBM).value else ""
        fig.update_yaxes(title_text = yAxisLabel, tickformat=tickformat, secondary_y=False)
        plotElements[PlotEl.Y_AXIS_LABEL] = yAxisLabel
            
        # Y2 axis label:
        y2AxisLabel = plotElements.get(PlotEl.Y2_AXIS_LABEL, None)
        if not y2AxisLabel and (ts.temperatures1 or ts.temperatures2):
            y2AxisLabel = "temperature [" + y2Units + "]"
        if y2AxisLabel:
            fig.update_yaxes(title_text = y2AxisLabel, showgrid=False, ticks="outside", secondary_y=True)
            plotElements[PlotEl.Y2_AXIS_LABEL] = y2AxisLabel

        # adjust Y2 axis range to be at least 4 degrees:
        if y2min:
            y2span = y2max - y2min
            if y2span < 4:
                y2center = y2min - (y2span / 2)
                fig.update_yaxes(range=[y2center - 1, y2center + 3], secondary_y=True)
            
        # Plot title:
        title = makeTitle([timeSeriesId], plotElements)
        fig.update_layout(title_text = title)
        
        # Plot footers:
        footer1, footer2, footer3 = makeFooters([timeSeriesId], plotElements, ts.getAllDataStatus(timeSeriesId), ts.startTime)
        addFooters(fig, footer1, footer2, footer3)
        
        # make and show plot:
        makePlotOutput(fig, plotElements, outputName, show)
        return True