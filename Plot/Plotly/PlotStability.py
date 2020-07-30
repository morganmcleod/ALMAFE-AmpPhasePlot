from AmpPhaseDataLib import TimeSeriesAPI, ResultAPI
from AmpPhaseDataLib.Constants import PlotKind, PlotEl, DataSource, Units
from Plot.Common import makeTitle, makeFooters
from Plot.Plotly.Common import addFooters, makePlotOutput
import plotly.graph_objects as go
from math import log10, floor, ceil
from numpy import logspace
from sys import float_info

class PlotStability(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.tsAPI = None
        self.resultAPI = None
        self.__reset()        
        
    def __reset(self):
        '''
        Reset members to just-constructed state
        '''
        self.imageData = None
        self.traces = []
        self.fig = None
        self.timeSeriesIds = []
        self.minXY = [float_info.max, float_info.max]
        self.maxXY = [float_info.min, float_info.min]

    def startPlot(self, plotElements = {}):
        '''
        Start a new STABILITY plot.
        :param startTime: when the measurement data was originally taken
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :return None; updates plotElements
        '''
        # clear anything kept from last plot:
        self.__reset()
        
        if not self.tsAPI:
            self.tsAPI = TimeSeriesAPI.TimeSeriesAPI()
        
        # Apply any allowed axes label overrides:
        xUnits = (Units.SECONDS).value
        plotElements[PlotEl.XUNITS] = xUnits   # save it, overriding what may have been there
        
    def addTrace(self, timeSeriesId, xArray, yArray, yError, plotElements = {}):
        '''
        Add a trace to a STABILITY plot in-progress.
        The resulting traces ([x], [y], [yError], name) are stored in self.traces 
        :param timeSeriesId: int, of the trace so we can get dataSource tags
        :param xArray: datetimes or float seconds
        :param yArray: float amplitudes or phases
        :param yError: float +- error bar on yArray
        :return True/False;  Updates plotElements
        '''
        # get the Plotly figure object:
        self.fig = self.fig if self.fig else go.Figure()
        
        # Get the DataSource tags from the TimeSeries:
        dataSources = self.tsAPI.getAllDataSource(timeSeriesId)
        if not dataSources:
            return False
        
        # Legend for trace:        
        name = ""
        subSystem = dataSources.get(DataSource.SUBSYSTEM, None)
        if subSystem:
            name += subSystem

        LO = dataSources.get(DataSource.LO_GHZ, None)
        if LO:
            if name:
                name += "_"
            name += "LO" + LO

        RF = dataSources.get(DataSource.RF_GHZ, None)
        if RF:
            if name:
                name += "_"
            name += "RF" + RF
        
        if not name:
            name = dataSources.get(DataSource.KIND, "amplitude")

        # add the trace:
        self.fig.add_trace(go.Scatter(x = xArray, y = yArray, mode = 'lines', name = name))
        
        # update overall dimensions:
        self.minXY[0] = min(self.minXY[0], min(xArray))
        self.minXY[1] = min(self.minXY[1], min(yArray))
        self.maxXY[0] = max(self.minXY[0], max(xArray))
        self.maxXY[1] = max(self.minXY[1], max(yArray))
        
        # add error bars:
        showErrorBars = int(plotElements.get(PlotEl.ERROR_BARS, "0"))
        if showErrorBars and yError is not None:
            errorBarsX = []
            errorBarsY = []
            errorBarsE = []
            # calculate the indexes of tau to use for error bars:
            space = logspace(0, log10(len(xArray)), 13)
            for x in space:
                k = floor(x - 1)
                errorBarsX.append(xArray[k])
                errorBarsY.append(yArray[k])
                errorBarsE.append(yError[k])
            
            self.fig.add_trace(go.Scatter(x = errorBarsX, 
                                          y = errorBarsY, 
                                          mode = 'markers', 
                                          marker_symbol = 0, marker_color = 'black', marker_size = 1,
                                          showlegend = False,
                                          error_y=dict(type='data', array=errorBarsE, visible=True)))
            
            # update overall dimensions (not accounting for errorBarsE but probably good enough):
            self.minXY[0] = min(self.minXY[0], min(errorBarsX))
            self.minXY[1] = min(self.minXY[1], min(errorBarsY))
            self.maxXY[0] = max(self.minXY[0], max(errorBarsX))
            self.maxXY[1] = max(self.minXY[1], max(errorBarsY))

        # append to traces:
        trace = (xArray, yArray, yError if yError else [], name)
        self.traces.append(trace)

        # Save the timeSeriesId:
        self.timeSeriesIds.append(timeSeriesId)
        return True
    
    def finishPlot(self, startTime, plotElements = {}, outputName = None, show = False):
        '''
        Make plot title, axes labels, and footers;  Render the plot.
        Updates self.imageData with the finished plot
        :param startTime:  Of the measurement(s)
        :param outputName: Filename where to write the plot .PNG file, optional.
        :param show: If true, display in the default renderer.
        :return True/False; updates self.imageData and plotElements
        '''
        # add spec lines/points
        specLines = dict(color='black', width=3)
        specMarks = dict(color='black', symbol='square', size=7)
        specLine = plotElements.get(PlotEl.SPEC_LINE1, None)
        if specLine:
            specLine = specLine.split(', ')
            x1 = float(specLine[0])
            y1 = float(specLine[1])
            x2 = float(specLine[2])
            y2 = float(specLine[3])

            self.fig.add_trace(go.Scatter(x = [x1, x2], y = [y1, y2], mode = 'lines', line = specLines, name = 'Specification'))

            # update overall dimensions:
            self.minXY[0] = min(self.minXY[0], min(x1, x2))
            self.minXY[1] = min(self.minXY[1], min(y1, y2))
            self.maxXY[0] = max(self.minXY[0], max(x1, x2))
            self.maxXY[1] = max(self.minXY[1], max(y1, y2))
        
        specLine = plotElements.get(PlotEl.SPEC_LINE2, None)
        if specLine:
            specLine = specLine.split(', ')
            x1 = float(specLine[0])
            y1 = float(specLine[1])
            x2 = float(specLine[2])
            y2 = float(specLine[3])

            name = "Spec {:.1e}".format(y1)
            if x1 == x2 and y1 == y2:
                self.fig.add_trace(go.Scatter(x = [x1, x2], y = [y1, y2], mode = 'markers', marker = specMarks, name = name))
            else:
                self.fig.add_trace(go.Scatter(x = [x1, x2], y = [y1, y2], mode = 'lines', line = specLines, name = name))

            # update overall dimensions:
            self.minXY[0] = min(self.minXY[0], min(x1, x2))
            self.minXY[1] = min(self.minXY[1], min(y1, y2))
            self.maxXY[0] = max(self.minXY[0], max(x1, y2))
            self.maxXY[1] = max(self.minXY[1], max(y1, y2))
        
        # X axis label:
        kind = self.tsAPI.getDataSource(self.timeSeriesIds[0], DataSource.KIND)
        xUnits = plotElements[PlotEl.XUNITS]
        xAxisLabel = plotElements.get(PlotEl.X_AXIS_LABEL, None)
        if not xAxisLabel:
            if xUnits == (Units.SECONDS).value or xUnits == (Units.MINUTES).value:
                if kind == "phase":
                    xAxisLabel = "time [" + xUnits + "]"
                else:
                    xAxisLabel = "integration time [" + xUnits + "]"
        self.fig.update_xaxes(title_text = xAxisLabel)
        plotElements[PlotEl.X_AXIS_LABEL] = xAxisLabel
        
        # Y axis label:
        if kind == "phase":
            yUnits = plotElements.get(PlotEl.YUNITS, (Units.ADEV).value)
        else:
            yUnits = plotElements.get(PlotEl.YUNITS, (Units.AVAR).value)
        plotElements[PlotEl.YUNITS] = yUnits   # save it in case default was used
        yAxisLabel = plotElements.get(PlotEl.Y_AXIS_LABEL, None)
        if not yAxisLabel:
            if kind == "phase":
                yAxisLabel = "2-pt ADEV " + (Units.ADEV).value + " [" + yUnits + "]"                
            else:
                yAxisLabel = "Allan variance" + " [" + yUnits + "]"
        self.fig.update_yaxes(title_text = yAxisLabel)
        plotElements[PlotEl.Y_AXIS_LABEL] = yAxisLabel
        
        # log-log plot, scientific notation on Y:
        self.fig.update_layout(xaxis_type="log", yaxis_type="log", showlegend=True, 
                               yaxis = dict(showexponent = 'all', exponentformat = 'e'))

        # expand x and y ranges to nearest decade:
        decadeMin = log10(self.minXY[0])
        decadeMin = (decadeMin - 1) if decadeMin.is_integer() else decadeMin
        decadeMax = log10(self.maxXY[0])
        decadeMax = (decadeMax + 1) if decadeMax.is_integer() else decadeMax      
        fMin = floor(decadeMin)
        cMax = ceil(decadeMax)
        self.fig.update_xaxes(range = [fMin, cMax])
        plotElements[PlotEl.XRANGE_WINDOW] = "{0}, {1}".format(fMin, cMax)

        decadeMin = log10(self.minXY[1])
        decadeMin = (decadeMin - 1) if decadeMin.is_integer() else decadeMin
        decadeMax = log10(self.maxXY[1])
        decadeMax = (decadeMax + 1) if decadeMax.is_integer() else decadeMax        
        fMin = floor(decadeMin)
        cMax = ceil(decadeMax)
        self.fig.update_yaxes(range = [fMin, cMax])
        plotElements[PlotEl.YRANGE_WINDOW] = "{0}, {1}".format(fMin, cMax)
        
        # Plot title:
        title = makeTitle(self.timeSeriesIds, plotElements)
        self.fig.update_layout(title_text = title)
        
        # Plot footers:
        footer1, footer2, footer3 = makeFooters(self.timeSeriesIds, plotElements, 
                                                self.tsAPI.getAllDataStatus(self.timeSeriesIds[0]), startTime)
        addFooters(self.fig, footer1, footer2, footer3)
        
        # Render:
        self.imageData = makePlotOutput(self.fig, plotElements, outputName, show)
        return True    

    def rePlot(self, plotId, plotElements = {}, outputName = None, show = False):
        '''
        Recreate a STABILITY plot from traces and plotElements stored in the Result database.
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
        if not (plot[1] == PlotKind.AMP_STABILITY or plot[1] == PlotKind.PHASE_STABILITY):
            return False
        
        # get the stored plotElements and merge in any overrides:
        plotElementsStored = ra.getAllPlotEl(plotId)
        plotElements = {**plotElementsStored, **plotElements}
        
        # get the axis units:
        xUnits = plotElements.get(PlotEl.XUNITS, None)
        yUnits = plotElements.get(PlotEl.YUNITS, None)
        if not xUnits or not yUnits:
            return False
        
        # Get the trace data
        traces = ra.retrieveTraces(plotId)
        if not traces:
            return False
    
        self.fig = go.Figure()
        
        # prepare for error bars:
        showErrorBars = int(plotElements.get(PlotEl.ERROR_BARS, "0"))

        # add the traces:
        for trace in traces:
            xyData = trace[1]
            legend = trace[3]
            self.fig.add_trace(go.Scatter(x = xyData[0], y = xyData[1], mode = 'lines', name = legend))
            
            # add error bars:
            if showErrorBars and xyData[2]:
                # calculate the indexes of tau to use for error bars:
                space = logspace(0, log10(len(xyData[0])), 13)
                errorBarsX = [xyData[0][floor(x - 1)] for x in space]
                errorBarsY = [xyData[1][floor(x - 1)] for x in space]
                errorBarsE = [xyData[2][floor(x - 1)] for x in space]
            
                self.fig.add_trace(go.Scatter(x = errorBarsX, 
                                              y = errorBarsY, 
                                              mode = 'markers', 
                                              marker_symbol = 0, marker_color = 'black', marker_size = 1,
                                              showlegend = False,
                                              error_y=dict(type='data', array=errorBarsE, visible=True)))
                
        # add spec lines/points
        specLines = dict(color='black', width=3)
        specMarks = dict(color='black', symbol='square', size=7)
        specLine = plotElements.get(PlotEl.SPEC_LINE1, None)
        if specLine:
            specLine = specLine.split(', ')
            x1 = float(specLine[0])
            y1 = float(specLine[1])
            x2 = float(specLine[2])
            y2 = float(specLine[3])

            self.fig.add_trace(go.Scatter(x = [x1, x2], y = [y1, y2], mode = 'lines', line = specLines, name = 'Specification'))

        specLine = plotElements.get(PlotEl.SPEC_LINE2, None)
        if specLine:
            specLine = specLine.split(', ')
            x1 = float(specLine[0])
            y1 = float(specLine[1])
            x2 = float(specLine[2])
            y2 = float(specLine[3])

            name = "Spec {:.1e}".format(y1)
            if x1 == x2 and y1 == y2:
                self.fig.add_trace(go.Scatter(x = [x1, x2], y = [y1, y2], mode = 'markers', marker = specMarks, name = name))
            else:
                self.fig.add_trace(go.Scatter(x = [x1, x2], y = [y1, y2], mode = 'lines', line = specLines, name = name))
        
        # X axis label:
        xAxisLabel = plotElements.get(PlotEl.X_AXIS_LABEL, "")
        self.fig.update_xaxes(title_text = xAxisLabel)
        
        # Y axis label:
        yAxisLabel = plotElements.get(PlotEl.Y_AXIS_LABEL, "")
        self.fig.update_yaxes(title_text = yAxisLabel)
        
        # log-log plot, scientific notation on Y:
        self.fig.update_layout(xaxis_type="log", yaxis_type="log", showlegend=True, 
                               yaxis = dict(showexponent = 'all', exponentformat = 'e'))
        
        # expand plot window:
        window = plotElements.get(PlotEl.XRANGE_WINDOW, None)
        if window:
            window = window.split(', ')
            self.fig.update_xaxes(range = [float(window[0]), window[1]])

        window = plotElements.get(PlotEl.YRANGE_WINDOW, None)
        if window:
            window = window.split(', ')
            self.fig.update_yaxes(range = [float(window[0]), window[1]])
        
        # Plot title:
        title = plotElements.get(PlotEl.TITLE, "")
        self.fig.update_layout(title_text = title)
        
        # Plot footers:
        footer1 = plotElements.get(PlotEl.FOOTER1, "")
        footer2 = plotElements.get(PlotEl.FOOTER2, "")
        footer3 = plotElements.get(PlotEl.FOOTER3, "")
        addFooters(self.fig, footer1, footer2, footer3)
        
        # Render:
        self.imageData = makePlotOutput(self.fig, plotElements, outputName, show)
        return True