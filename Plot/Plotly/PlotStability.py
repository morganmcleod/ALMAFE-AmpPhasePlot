from AmpPhaseDataLib.TimeSeries import TimeSeries
from AmpPhaseDataLib.Constants import DataKind, DataSource, PlotEl, PlotKind, Units
from Plot.Common import makeTitle, makeFooters
from Plot.Plotly.Common import addFooters, addSpecLines, makePlotOutput
import plotly.graph_objects as go
from math import log10, floor, ceil
from numpy import logspace
from sys import float_info
from typing import Dict, List

class PlotStability(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__reset()        
        
    def __reset(self):
        '''
        Reset members to just-constructed state
        '''
        self.imageData = None
        self.traces = []
        self.plotKind = None
        self.timeSeriesIds = []
        self.minXY = [float_info.max, float_info.max]
        self.maxXY = [float_info.min, float_info.min]

    def startPlot(self, plotElements = None):
        '''
        Start a new STABILITY plot.
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :return None; updates plotElements
        '''
        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}

        # clear anything kept from last plot:
        self.__reset()
        
        # Default xUnits to seconds if not specified:
        xUnits = plotElements.get(PlotEl.XUNITS, None)
        if not xUnits:        
            plotElements[PlotEl.XUNITS] = (Units.SECONDS).value
        
    def addTrace(self, 
            timeSeries,
            dataSources: Dict[DataSource, str],
            xArray: List[float], 
            yArray: List[float], 
            yError: List[float], 
            plotElements: Dict[PlotEl, str] = None) -> bool:
        '''
        Add a trace to a STABILITY plot in-progress.
        The resulting traces ([x], [y], [yError], name) are stored in self.traces 
        :param timeSeries: the raw data to plot
        :param dataSources: data source attributes of the timeSeries
        :param xArray: datetimes or float seconds
        :param yArray: float amplitudes or phases
        :param yError: float +- error bar on yArray
        :param plotElements: dict of {PLotEl : str} to supplement or replace any defaults or loaded from database.
        :return True/False;  Updates plotElements
        '''
        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}
            
        # Determine yUnits:
        yUnits = plotElements.get(PlotEl.YUNITS, None)
        if not yUnits:
            yUnits = dataSources.get(DataSource.UNITS, None)
            plotElements[PlotEl.YUNITS] = yUnits
        
        # If we still don't know, guess based on DataSource.DATA_KIND:
        dataKind = dataSources.get(DataSource.DATA_KIND, (DataKind.AMPLITUDE).value)
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

        # update self.plotKind:
        if not self.plotKind:
            if dataKind == (DataKind.PHASE).value:
                self.plotKind = PlotKind.PHASE_STABILITY
            elif dataKind == (DataKind.VOLTAGE).value:
                self.plotKind = PlotKind.VOLT_STABILITY
            else:
                self.plotKind = PlotKind.POWER_STABILITY
        
        # Legend for trace:        
        name = ""
        subSystem = dataSources.get(DataSource.SUBSYSTEM, None)
        if subSystem:
            name += subSystem

        LO = dataSources.get(DataSource.LO_GHZ, None)
        if LO:
            if name:
                name += "_"
            name += "LO " + LO + " GHz"

        RF = dataSources.get(DataSource.RF_GHZ, None)
        if RF:
            if name:
                name += "_"
            name += "RF " + RF + " GHz"
        
        if not name:
            if self.plotKind == PlotKind.PHASE_STABILITY or self.plotKind == PlotKind.VOLT_STABILITY or dataSources.get(DataSource.DATA_KIND, None) == DataKind.GAIN.value:
                name = "ADEV({0})".format(yUnits)
            else:
                name = "AVAR({0})".format(yUnits)

        # append to self.traces:
        trace = (xArray, yArray, yError if yError else [], name)
        self.traces.append(trace)
        
        # update overall dimensions:
        self.minXY[0] = min(self.minXY[0], min(xArray))
        self.minXY[1] = min(self.minXY[1], min(yArray))
        self.maxXY[0] = max(self.maxXY[0], max(xArray))
        self.maxXY[1] = max(self.maxXY[1], max(yArray))
        
        # Save the timeSeriesId:
        self.timeSeriesIds.append(timeSeries.tsId)
        return True
    
    def finishPlot(self, startTime, dataSources, plotElements = None, outputName = None, show = False):
        '''
        Make plot title, axes labels, and footers;  Render the plot.
        Updates self.imageData with the finished plot
        :param startTime:  Of the measurement(s)
        :param outputName: Filename where to write the plot .PNG file, optional.
        :param show: If true, display in the default renderer.
        :return True/False; updates self.imageData and plotElements
        '''
        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}
            
        # update XY min/max from specline1:
        specLine = plotElements.get(PlotEl.SPEC_LINE1, None)
        if specLine:
            specLine = specLine.split(', ')
            x1 = float(specLine[0])
            y1 = float(specLine[1])
            x2 = float(specLine[2])
            y2 = float(specLine[3])
            # update overall dimensions:
            self.minXY[0] = min(self.minXY[0], min(x1, x2))
            self.minXY[1] = min(self.minXY[1], min(y1, y2))
            self.maxXY[0] = max(self.maxXY[0], max(x1, x2))
            self.maxXY[1] = max(self.maxXY[1], max(y1, y2))

        # update XY min/max from specline2:
        specLine = plotElements.get(PlotEl.SPEC_LINE2, None)
        if specLine:
            specLine = specLine.split(', ')
            x1 = float(specLine[0])
            y1 = float(specLine[1])
            x2 = float(specLine[2])
            y2 = float(specLine[3])
            # update overall dimensions:
            self.minXY[0] = min(self.minXY[0], min(x1, x2))
            self.minXY[1] = min(self.minXY[1], min(y1, y2))
            self.maxXY[0] = max(self.maxXY[0], max(x1, y2))
            self.maxXY[1] = max(self.maxXY[1], max(y1, y2))

        if not plotElements.get(PlotEl.X_LINEAR, False):
            # expand X range to nearest decade:
            decadeMin = log10(self.minXY[0])
            decadeMin = (decadeMin - 1) if decadeMin.is_integer() else decadeMin
            decadeMax = log10(self.maxXY[0])
            decadeMax = (decadeMax + 1) if decadeMax.is_integer() else decadeMax      
            fMin = floor(decadeMin)
            cMax = ceil(decadeMax)
            plotElements[PlotEl.XRANGE_WINDOW] = "{0}, {1}".format(fMin, cMax)

        if not plotElements.get(PlotEl.Y_LINEAR, False):
            # expand Y range to nearest decade:
            decadeMin = log10(self.minXY[1])
            decadeMin = (decadeMin - 1) if decadeMin.is_integer() else decadeMin
            decadeMax = log10(self.maxXY[1])
            decadeMax = (decadeMax + 1) if decadeMax.is_integer() else decadeMax        
            fMin = floor(decadeMin)
            cMax = ceil(decadeMax)
            plotElements[PlotEl.YRANGE_WINDOW] = "{0}, {1}".format(fMin, cMax)
        
        # Plot title:
        title = makeTitle(self.timeSeriesIds, dataSources, plotElements)
        plotElements[PlotEl.TITLE] = title
        
        # Plot footers:
        makeFooters(self.timeSeriesIds, dataSources, plotElements, startTime)
        
        # Generate the plot:
        return self.__plot(plotElements, outputName, show)    
    
    def __plot(self, plotElements, outputName = None, show = False):
        '''
        implementation helper
        Uses the contents of self.traces [([x], [y], [yError], name)] 
        and the provided plotElements to produce the output plot.
        :param plotElements: dict of {PLotElement : str}
        :param outputName: optional filename where to write the plot .PNG file
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''

        fig = go.Figure()
        
        # prepare for error bars:
        showErrorBars = int(plotElements.get(PlotEl.ERROR_BARS, "0"))

        # add the traces:
        for trace in self.traces:
            fig.add_trace(go.Scatter(x = trace[0], y = trace[1], mode = 'lines', name = trace[3]))
            
            # add error bars:
            if showErrorBars and trace[2]:
                # calculate the indexes of tau to use for error bars:
                space = logspace(0, log10(len(trace[0])), 11)
                errorBarsX = [trace[0][floor(x - 1)] for x in space]
                errorBarsY = [trace[1][floor(x - 1)] for x in space]
                errorBarsE = [trace[2][floor(x - 1)] for x in space]
            
                fig.add_trace(go.Scatter(x = errorBarsX, y = errorBarsY, mode = 'markers',  
                                         marker_symbol = 0, marker_color = 'black', marker_size = 1, showlegend = False,
                                         error_y = dict(type = 'data', array = errorBarsE, visible = True)))

        # add spec lines:
        addSpecLines(fig, plotElements)

        # X axis units and label:
        xUnits = plotElements[PlotEl.XUNITS]
        xAxisLabel = plotElements.get(PlotEl.X_AXIS_LABEL, None)
        if not xAxisLabel:
            if xUnits == (Units.SECONDS).value or xUnits == (Units.MINUTES).value:
                if self.plotKind == PlotKind.PHASE_STABILITY:
                    xAxisLabel = "time [" + xUnits + "]"
                else:
                    xAxisLabel = "integration time [" + xUnits + "]"
        fig.update_xaxes(title_text = xAxisLabel)
        plotElements[PlotEl.X_AXIS_LABEL] = xAxisLabel
        
        # Y axis units:
        if self.plotKind == PlotKind.PHASE_STABILITY:
            yUnits = plotElements.get(PlotEl.YUNITS, (Units.ADEV).value)
        else:
            yUnits = plotElements.get(PlotEl.YUNITS, (Units.AVAR).value)
        plotElements[PlotEl.YUNITS] = yUnits   # save it in case default was used

        # Y axis label:
        yAxisLabel = plotElements.get(PlotEl.Y_AXIS_LABEL, None)
        if not yAxisLabel:
            if self.plotKind == PlotKind.PHASE_STABILITY:
                yAxisLabel = "2-Pt ADEV: " + (Units.ADEV).value + " [" + yUnits + "]"                
            elif self.plotKind == PlotKind.VOLT_STABILITY:
                yAxisLabel = "ADEV: [" + yUnits + "]"
            else:
                yAxisLabel = "AVAR: " + (Units.AVAR).value
        fig.update_yaxes(title_text = yAxisLabel)
        plotElements[PlotEl.Y_AXIS_LABEL] = yAxisLabel

        # plot log in Y, configurable in X, scientific notation on Y:
        xaxis_type = "linear" if plotElements.get(PlotEl.X_LINEAR, False) else "log"
        yaxis_type = "linear" if plotElements.get(PlotEl.Y_LINEAR, False) else "log"
        
        fig.update_layout(xaxis_type=xaxis_type, yaxis_type=yaxis_type, showlegend=True, 
                          yaxis = dict(showexponent = 'all', exponentformat = 'e'))

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
        title = plotElements.get(PlotEl.TITLE, "")
        fig.update_layout(title_text = title)
        
        # Plot footers:
        addFooters(fig, plotElements)
        
        # Render:
        self.imageData = makePlotOutput(fig, plotElements, outputName, show)
        return True
        
