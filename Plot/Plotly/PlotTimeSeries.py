from AmpPhaseDataLib import TimeSeriesAPI, ResultAPI
from AmpPhaseDataLib.Constants import PlotKind, PlotEl, DataSource, Units
from Plot.Common import makeTitle, makeFooters
from Plot.Plotly.Common import addFooters, makePlotOutput
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

class PlotTimeSeries(object):
    '''
    Plot TimeSeries using Plotly
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.timeSeriesAPI = TimeSeriesAPI.TimeSeriesAPI()
        self.resultAPI = ResultAPI.ResultAPI()
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
        kind = dataSources.get(DataSource.KIND, "amplitude")
        legends = [dataSources.get(DataSource.SUBSYSTEM, kind)]
        if ts.temperatures1:
            legends.append('Sensor1')
        if ts.temperatures2:
            legends.append('Sensor2')
                    
        # get timestamps and data, possibly with unit conversions:
        xUnits, yUnits, y2Units = self.__getUnits(dataSources, plotElements)
        timeStamps = ts.getTimeStamps(requiredUnits = Units.fromStr(xUnits))
        dataSeries = ts.getDataSeries(requiredUnits = Units.fromStr(yUnits))
            
        # Plot title:
        makeTitle([timeSeriesId], plotElements)
        
        # Make footers:
        makeFooters([timeSeriesId], plotElements, ts.getAllDataStatus(timeSeriesId), ts.startTime)

        # make the plot:
        return self.__plot(timeStamps, dataSeries, ts.temperatures1, ts.temperatures2, legends, dataSources, plotElements, outputName, show)


    def rePlot(self, plotId, plotElements = {}, outputName = None, show = False):
        '''
        Recreate a TIME_SERIES plot from whatever data is in the Result database for plotId
        The resulting image data is stored in self.imageData.
        :param plotId: to retrieve and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: Filename where to write the plot .PNG file, optional.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # clear anything kept from last plot:
        self.__reset()

        ra = self.resultAPI
        
        plot = ra.retrievePlot(plotId)
        if not plot:
            return False
        assert plot[0] == plotId
        assert plot[1] == PlotKind.TIME_SERIES
        
        # Get the DataSource tags:
        dataSources = ra.getAllDataSource(plotId)
        
        # Get the stored plotElements:
        plotElStored = ra.getAllPlotEl(plotId)
        if plotElStored:
            # Merge in the overrides:
            plotElements = {**plotElStored, **plotElements}
        
        #retrieve the trace data:
        traces = ra.retrieveTraces(plotId)
        if not traces:
            return False
        
        #get timeStamps from the first trace, X values:
        xUnits, yUnits, y2Units = self.__getUnits(dataSources, plotElements)
        if xUnits == (Units.LOCALTIME).value:
            # convert from float to LOCALTIME
            timeStamps = [datetime.fromtimestamp(point[0]) for point in traces[0].xyData]
        else:
            timeStamps = [point[0] for point in traces[0].xyData]
        
        #get dataSeries and legend:
        dataSeries = [point[1] for point in traces[0].xyData]
        legends = [traces[0].legend]
        
        #get temperatures1 from second trace:
        temperatures1 = None
        if len(traces) > 1:
            temperatures1 = [point[1] for point in traces[1].xyData]
            legends.append([traces[1].legend])

        #get temperatures2 from third trace:
        temperatures2 = None
        if len(traces) > 2:
            temperatures2 = [point[1] for point in traces[2].xyData]
            legends.append([traces[2].legend])

        return self.__plot(timeStamps, dataSeries, temperatures1, temperatures2, legends, dataSources, plotElements, outputName, show)
    
    def __getUnits(self, dataSources, plotElements):
        '''
        Common implementation used by plot() and replot() to determine axis units
        :param dataSources:   dict of {DataSource : str)
        :param plotElements:  dict of {PLotElement : str}
        :return strings (xUnits, yUnits, y2Units)
        '''
        kind = dataSources.get(DataSource.KIND, "amplitude")

        # Get the axis units:
        xUnits = plotElements.get(PlotEl.XUNITS, (Units.LOCALTIME).value)
        plotElements[PlotEl.XUNITS] = xUnits  # save it in case default was used
        
        yUnits = plotElements.get(PlotEl.YUNITS, None)
        if not yUnits:
            if kind == "phase":
                yUnits = dataSources.get(DataSource.UNITS, (Units.DEG).value)
            elif kind == "voltage":
                yUnits = dataSources.get(DataSource.UNITS, (Units.VOLTS).value)
            else:
                yUnits = dataSources.get(DataSource.UNITS, (Units.WATTS).value)
            plotElements[PlotEl.YUNITS] = yUnits
            
        y2Units = plotElements.get(PlotEl.Y2UNITS, None)
        if not y2Units:
            y2Units = dataSources.get(DataSource.T_UNITS, (Units.KELVIN).value)
            plotElements[PlotEl.Y2UNITS] = y2Units
        return (xUnits, yUnits, y2Units)
    
    def __plot(self, timeStamps, dataSeries, temperatures1, temperatures2, legends, dataSources, plotElements, outputName = None, show = False):
        '''
        Common implementation used by plot() and replot()
        The resulting image data is stored in self.imageData.
        :param timeStamps:    X-axis data points
        :param dataSeries:    main Y-axis data points
        :param temperatures1: optional secondary Y data
        :param temperatures2: optional secondary Y data
        :param legends:       list of strings like ['amplitude', 'sensor1', 'sensor2']
        :param dataSources:   dict of {DataSource : str)
        :param plotElements:  dict of {PLotElement : str}
        :param outputName:    filename where to write the plot .PNG file, optional.
        :param show:          if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        
        # Get the DataSource tags:
        kind = dataSources.get(DataSource.KIND, "amplitude")
        
        # add the trace(s), compute temperature trace spans:
        y2min = None
        y2max = None
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x = timeStamps, y = dataSeries, mode = 'lines', name = legends[0]), secondary_y=False)
        
        if temperatures1:
            fig.add_trace(go.Scatter(x = timeStamps, y = temperatures1, mode = 'lines', name = legends[1]), secondary_y=True)
            y2min = min(temperatures1)
            y2max = max(temperatures1)
        if temperatures2:
            fig.add_trace(go.Scatter(x = timeStamps, y = temperatures2, mode = 'lines', name = legends[2]), secondary_y=True)
            if y2min:
                y2min = min(y2min, min(temperatures2))
                y2max = max(y2max, max(temperatures2))
        
        xUnits = plotElements.get(PlotEl.XUNITS)
        yUnits = plotElements.get(PlotEl.YUNITS)
        y2Units = plotElements.get(PlotEl.Y2UNITS)
        
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
        if not y2AxisLabel and temperatures1:
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
        title = plotElements.get(PlotEl.TITLE, kind)
        if title:
            fig.update_layout(title_text = title)
        
        # Plot footers:        
        footer1 = plotElements.get(PlotEl.FOOTER1, None)
        footer2 = plotElements.get(PlotEl.FOOTER2, None)
        footer3 = plotElements.get(PlotEl.FOOTER3, None)
        addFooters(fig, footer1, footer2, footer3)
        
        # make and show plot:
        self.imageData = makePlotOutput(fig, plotElements, outputName, show)
        return True