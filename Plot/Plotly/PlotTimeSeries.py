from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhaseDataLib.Constants import DataKind, DataSource, PlotEl, Units
from Calculate.Common import getMinMaxArray, getFirstItemArray
from Plot.Common import makeTitle, makeFooters
from Plot.Plotly.Common import addFooters, makePlotOutput
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

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
        
    def plot(self, timeSeriesId, plotElements = None, outputName = None, show = False, xResolution = 1000, unwrapPhase = False):
        '''
        Create a TIME_SERIES plot
        The resulting image data is stored in self.imageData
        :param timeSeriesId: to retrieve and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: Filename where to write the plot .PNG file, optional.
        :param show: if True, displays the plot using the default renderer.
        :param xResolution: reduce the number of data points actually rendered to this many, by boxcar max, min.
        :return True if succesful, False otherwise
        '''
        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}
                    
        # clear anything kept from last plot:
        self.__reset()

        # get the TimeSeries data:        
        timeSeries = self.timeSeriesAPI.retrieveTimeSeries(timeSeriesId)
        if not timeSeries:
            return False
        
        # unwrap
        if unwrapPhase:
            timeSeries.unwrapPhase(period = 360)

        # Get the DataSource tags:
        dataSources = self.timeSeriesAPI.getAllDataSource(timeSeriesId)
        dataKind = DataKind.fromStr(dataSources.get(DataSource.DATA_KIND, (DataKind.AMPLITUDE).value))
        currentUnits = timeSeries.dataUnits

        # Set up trace legends:
        legends = [dataSources.get(DataSource.SUBSYSTEM, dataKind.value)]
        if timeSeries.temperatures1:
            legend = plotElements.get(PlotEl.Y2_LEGEND1, 'Temperature sensor 1')
            legends.append(legend)
        if timeSeries.temperatures2:
            legend = plotElements.get(PlotEl.Y2_LEGEND2, 'Temperature sensor 2')
            legends.append(legend)
                    
        # Get the axis units:
        xUnits = plotElements.get(PlotEl.XUNITS, (Units.LOCALTIME).value)
        plotElements[PlotEl.XUNITS] = xUnits  # save it in case default was used
        
        yUnits = plotElements.get(PlotEl.YUNITS, None)
        if not yUnits:
            if dataKind == DataKind.VOLTAGE:
                yUnits = (Units.VOLTS).value                                
            elif dataKind == DataKind.PHASE:
                yUnits = (Units.DEG).value
            else: # for POWER and AMPLITUDE use the source units:
                yUnits = currentUnits.value
            plotElements[PlotEl.YUNITS] = yUnits
            
        y2Units = plotElements.get(PlotEl.Y2UNITS, None)
        if not y2Units:
            y2Units = dataSources.get(DataSource.T_UNITS, (Units.KELVIN).value)
            plotElements[PlotEl.Y2UNITS] = y2Units
        
        # get timestamps and data, possibly with unit conversions:        
        timeStamps = timeSeries.getTimeStamps(requiredUnits = xUnits)
        if not timeStamps:
            return False
        dataSeries = timeSeries.getDataSeries(yUnits)
        if not dataSeries:
            return False
        
        # reduce to approximately xResolution, to save plotting time:
        if xResolution:
            # get the number of groups to combine:
            K = len(dataSeries) // xResolution
            minArray, maxArray = getMinMaxArray(dataSeries, K)
            # interleave minArray, maxArray:
            dataSeries = [None]*(len(minArray)+len(maxArray))
            dataSeries[::2] = minArray
            dataSeries[1::2] = maxArray
            # reduce timestamps and temperatures by the same group size K.
            # because len(dataSeries) is now about 2 * xResoltion, repeat each element twice in the arrays: 
            timeStamps = np.repeat(getFirstItemArray(timeStamps, K), 2).tolist()
            if timeSeries.temperatures1:
                timeSeries.temperatures1 = np.repeat(getFirstItemArray(timeSeries.temperatures1, K), 2).tolist()
            if timeSeries.temperatures2:
                timeSeries.temperatures2 = np.repeat(getFirstItemArray(timeSeries.temperatures2, K), 2).tolist()

        # add the trace(s), compute temperature trace spans:
        y2min = None
        y2max = None
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x = timeStamps, y = dataSeries, mode = 'lines', name = legends[0]), secondary_y=False)
        
        if timeSeries.temperatures1:
            fig.add_trace(go.Scatter(x = timeStamps, y = timeSeries.temperatures1, mode = 'lines', name = legends[1]), secondary_y=True)
            y2min = min(timeSeries.temperatures1)
            y2max = max(timeSeries.temperatures1)
        if timeSeries.temperatures2:
            fig.add_trace(go.Scatter(x = timeStamps, y = timeSeries.temperatures2, mode = 'lines', name = legends[2]), secondary_y=True)
            if y2min:
                y2min = min(y2min, min(timeSeries.temperatures2))
                y2max = max(y2max, max(timeSeries.temperatures2))
        
        # force show legend even if only one trace:
        fig.update_layout(showlegend = True)
        
        # X axis label:
        xAxisLabel = plotElements.get(PlotEl.X_AXIS_LABEL, None)
        if not xAxisLabel:
            if xUnits == (Units.LOCALTIME).value:
                xAxisLabel = xUnits
            else:
                xAxisLabel = "time [" + xUnits + "]"  
        fig.update_xaxes(title_text = xAxisLabel)
        plotElements[PlotEl.X_AXIS_LABEL] = xAxisLabel

        # Y axis label:
        yAxisLabel = plotElements.get(PlotEl.Y_AXIS_LABEL, None)
        if not yAxisLabel:
            if yUnits == (Units.AMPLITUDE).value:
                yAxisLabel = yUnits
            else:
                yAxisLabel = dataKind.value
                if dataKind == DataKind.POWER and yUnits == (Units.VOLTS).value:
                    yAxisLabel += " [detector volts]"
                else:
                    yAxisLabel += " [" + yUnits + "]"
        tickformat = ".3f" if yUnits == (Units.DBM).value else ""
        fig.update_yaxes(title_text = yAxisLabel, tickformat=tickformat, secondary_y=False)
        plotElements[PlotEl.Y_AXIS_LABEL] = yAxisLabel

        # Y2 axis label:
        y2AxisLabel = plotElements.get(PlotEl.Y2_AXIS_LABEL, None)
        if not y2AxisLabel and timeSeries.temperatures1:
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

        # expand plot window:
        window = plotElements.get(PlotEl.XRANGE_WINDOW, None)
        if window:
            window = window.split(', ')
            fig.update_xaxes(range = [float(window[0]), window[1]])

        window = plotElements.get(PlotEl.YRANGE_WINDOW, None)
        if window:
            window = window.split(', ')
            fig.update_yaxes(range = [float(window[0]), window[1]])

        # Plot title:
        title = makeTitle([timeSeriesId], plotElements)
        if title:
            fig.update_layout(title_text = title)
        
        # Plot footers:        
        makeFooters([timeSeriesId], plotElements, self.timeSeriesAPI.getAllDataStatus(timeSeriesId), timeSeries.startTime)
        addFooters(fig, plotElements)
        
        # make and show plot:
        self.imageData = makePlotOutput(fig, plotElements, outputName, show)
        return True