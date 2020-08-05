'''
PlotAPI for calling applications to generate plots.
'''
from AmpPhaseDataLib import TimeSeriesAPI, ResultAPI
from AmpPhaseDataLib.Constants import PlotKind, Units, PlotEl, DataSource, SpecLines
from Calculate import AmplitudeStability, PhaseStability, PowerSpectrum
from Plot.Plotly import PlotTimeSeries, PlotStability, PlotPowerSpectrum
from datetime import datetime

class PlotAPI(object):
    '''
    PlotAPI for calling applications to generate plots.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__reset()
        self.tsAPI = TimeSeriesAPI.TimeSeriesAPI()

    def __reset(self):
        '''
        Reset members to just-constructed state
        '''
        self.calc = None
        self.plotter = None
        self.traces = []
        self.imageData = None
        self.plotElementsFinal = None
        
    def plotTimeSeries(self, timeSeriesId, plotElements = {}, outputName = None, show = False):
        '''
        Create a TIME_SERIES plot
        The resulting image binary data (.png) is stored in self.imageData.
        The applied plotElements are stored in self.plotElementsFinal.
        Unlike the other methods in this class, self.traces is not updated by this method. 
        (It would be the same as the raw data, and huge.)
        :param timeSeriesId: a timeSeriesId to retrieve and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: str filename to store the resulting .png file.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # clear anything kept from last plot:
        self.__reset()
        
        # make the plot:
        self.plotter = PlotTimeSeries.PlotTimeSeries()
        if not self.plotter.plot(timeSeriesId, plotElements, outputName, show):
            return False
        
        # get the results:
        self.imageData = self.plotter.imageData
        self.plotElementsFinal = plotElements
        return True
    
    def plotPowerSpectrum(self, timeSeriesId, plotElements = {}, outputName = None, show = False):
        '''
        Create an AMPLITUDE_SPECTRUM or POWER_SPECTRUM plot
        The resulting image binary data (.png) is stored in self.imageData.
        The applied plotElements are stored in self.plotElementsFinal.
        The resulting traces ([x], [y], [yError], name) are stored in self.traces 
        :param timeSeriesId: a timeSeriesId to retrieve and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: str filename to store the resulting .png file.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # clear anything kept from last plot:
        self.__reset()
        
        # get the TimeSeries data:
        if not self.tsAPI.retrieveTimeSeries(timeSeriesId):
            return False

        # Get the DataSource tags:
        srcUnits = self.tsAPI.getDataSource(timeSeriesId, DataSource.UNITS)

        # Get the timeseries in linear units:
        if srcUnits == (Units.DEG).value:
            dataSeries = self.tsAPI.getDataSeries(requiredUnits = Units.DEG)
            dfltTitle = "Phase Spectral Density"
        elif srcUnits == (Units.VOLTS).value:
            dataSeries = self.tsAPI.getDataSeries(requiredUnits = Units.VOLTS)
            dfltTitle = "Voltage Spectral Density"
        else:
            dataSeries = self.tsAPI.getDataSeries(requiredUnits = Units.WATTS)
            dfltTitle = "Power Spectral Density"
        
        # set the plot title:
        if not plotElements.get(PlotEl.TITLE, False):        
            plotElements[PlotEl.TITLE] = dfltTitle
        
        # make the plot:
        self.calc = PowerSpectrum.PowerSpectrum()
        self.plotter = PlotPowerSpectrum.PlotPowerSpectrum()
        
        if not self.calc.calculate(dataSeries, self.tsAPI.tau0Seconds):
            return False

        if not self.plotter.plot(timeSeriesId, self.calc.xResult, self.calc.yResult, plotElements, outputName, show):
            return False

        # get the results:
        self.traces = self.plotter.traces
        self.imageData = self.plotter.imageData
        self.plotElementsFinal = plotElements
        return True
    
    def plotAmplitudeStability(self, timeSeriesIds, plotElements = {}, outputName = None, show = False):
        '''
        Create an AMP_STABILITY plot
        The resulting image data is stored in self.imageData.
        The applied plotElements are stored in self.plotElementsFinal.
        The resulting traces ([x], [y], [yError], name) are stored in self.traces 
        :param timeSeriesIds: a single int timeSeriesId or a list of Ids to retrieve and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: str filename to store the resulting .png file.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''        
        # clear anything kept from last plot:
        self.__reset()
        self.calc = AmplitudeStability.AmplitudeStability()
        self.plotter = PlotStability.PlotStability()
        
        # use this to find the earliest start time if multiple traces:
        startTime = None
        
        # is it a single time series plot?
        if isinstance(timeSeriesIds, int):
            timeSeriesId = timeSeriesIds
            plotElements[PlotEl.ERROR_BARS] = "1"
            self.plotter.startPlot(plotElements)
            if not self.__plotAmplitudeStabilitySingle(timeSeriesId, plotElements):
                return False
            startTime = self.tsAPI.startTime

        # is it a list:
        elif isinstance(timeSeriesIds, list):
            # suppress error bars for ensemble plot
            plotElements[PlotEl.ERROR_BARS] = "0" if len(timeSeriesIds) > 1 else "1"
            startTime = datetime.now()
            self.plotter.startPlot(plotElements)
            for timeSeriesId in timeSeriesIds:
                if self.__plotAmplitudeStabilitySingle(timeSeriesId, plotElements):
                    if self.tsAPI.startTime < startTime:
                        startTime = self.tsAPI.startTime
                else:
                    return False
            # set a generic title:
            plotElements[PlotEl.TITLE] = "Amplitude Stability"

        # get the results:
        if self.plotter.finishPlot(startTime, plotElements, outputName, show):
            self.traces = self.plotter.traces
            self.imageData = self.plotter.imageData
            self.plotElementsFinal = plotElements
            return True
        else:
            return False
        
    def __plotAmplitudeStabilitySingle(self, timeSeriesId, plotElements):
        # get the TimeSeries data:
        if not self.tsAPI.retrieveTimeSeries(timeSeriesId):
            return False
        
        kind = self.tsAPI.getDataSource(timeSeriesId, DataSource.KIND)
        if not kind:
            kind = "amplitude"
        
        if kind == "voltage":
            dataSeries = self.tsAPI.getDataSeries(requiredUnits = Units.VOLTS)
        else:
            dataSeries = self.tsAPI.getDataSeries(requiredUnits = Units.WATTS)

        if not dataSeries:
            return False

        freqLOGHz = self.tsAPI.getDataSource(timeSeriesId, DataSource.LO_GHZ)
        if freqLOGHz:
            freqLOGHz = float(freqLOGHz)
                    
        # calculate Amplitude stability plot traces:
        xRangePlot = plotElements.get(PlotEl.XRANGE_PLOT, SpecLines.XRANGE_PLOT_AMP_STABILITY).split(', ')
        TMin = float(xRangePlot[0])
        TMax = float(xRangePlot[1])
        
        if not self.calc.calculate(dataSeries, self.tsAPI.tau0Seconds, TMin, TMax):
            return False

        # add the trace:
        return self.plotter.addTrace(timeSeriesId, self.calc.xResult, self.calc.yResult, self.calc.yError, plotElements)

    def plotPhaseStability(self, timeSeriesIds, plotElements = {}, outputName = None, show = False):
        '''
        Create an PHASE_STABILITY plot
        The resulting image data is stored in self.imageData.
        The applied plotElements are stored in self.plotElementsFinal.
        The resulting traces ([x], [y], [yError], name) are stored in self.traces 
        :param timeSeriesIds: a single int timeSeriesId or a list of Ids to retrieve and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: str filename to store the resulting .png file.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # clear anything kept from last plot:
        self.__reset()
        self.calc = PhaseStability.PhaseStability()
        self.plotter = PlotStability.PlotStability()

        # use this to find the earliest start time if multiple traces:
        startTime = None

        # is it a single time series plot?
        if isinstance(timeSeriesIds, int):
            timeSeriesId = timeSeriesIds
            plotElements[PlotEl.ERROR_BARS] = "1"
            self.plotter.startPlot(plotElements)
            if not self.__plotPhaseStabilitySingle(timeSeriesId, plotElements):
                return False
            startTime = self.tsAPI.startTime

        # is it a list:
        elif isinstance(timeSeriesIds, list):
            # suppress error bars for ensemble plot
            plotElements[PlotEl.ERROR_BARS] = "0" if len(timeSeriesIds) > 1 else "1"
            startTime = datetime.now()
            self.plotter.startPlot(plotElements)
            for timeSeriesId in timeSeriesIds:
                if self.__plotPhaseStabilitySingle(timeSeriesId, plotElements):
                    if self.tsAPI.startTime < startTime:
                        startTime = self.tsAPI.startTime
                else:
                    return False
            # set a generic title:
            plotElements[PlotEl.TITLE] = "Phase Stability"
        
        # get the results:
        if self.plotter.finishPlot(startTime, plotElements, outputName, show):
            self.traces = self.plotter.traces
            self.imageData = self.plotter.imageData
            self.plotElementsFinal = plotElements
            return True
        else:
            return False
    
    def __plotPhaseStabilitySingle(self, timeSeriesId, plotElements):
        # get the TimeSeries data:
        if not self.tsAPI.retrieveTimeSeries(timeSeriesId):
            return False
        
        dataSeries = self.tsAPI.getDataSeries(requiredUnits = Units.DEG)
        freqRFGHz = self.tsAPI.getDataSource(timeSeriesId, DataSource.RF_GHZ)
        if freqRFGHz:
            freqRFGHz = float(freqRFGHz)

        # set YUNITS on the first trace:
        if not plotElements.get(PlotEl.YUNITS, None):
            if freqRFGHz:
                plotElements[PlotEl.YUNITS] = (Units.FS).value
            else:
                plotElements[PlotEl.YUNITS] = (Units.DEG).value
        
        # calculate Amplitude stability plot traces:
        xRangePlot = plotElements.get(PlotEl.XRANGE_PLOT, SpecLines.XRANGE_PLOT_PHASE_STABILITY).split(', ')
        TMin = float(xRangePlot[0])
        TMax = float(xRangePlot[1])
        
        if not self.calc.calculate(dataSeries, self.tsAPI.tau0Seconds, TMin, TMax, freqRFGHz):
            return False

        # add the trace:
        return self.plotter.addTrace(timeSeriesId, self.calc.xResult, self.calc.yResult, self.calc.yError, plotElements)
    
    def rePlot(self, plotId, plotElements = {}, outputName = None, show = False):
        '''
        Make a plot from whatever data is in the Result database for plotId.
        Not supported for TIME_SERIES plots.       
        :param plotId: int to fetch and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: Filename where to write the plot .PNG file, optional.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        self.__reset()
        ra = ResultAPI.ResultAPI()
        
        plot = ra.retrievePlot(plotId)
        if not plot:
            return False
        assert plot[0] == plotId
        kind = plot[1]

        if kind == PlotKind.POWER_SPECTRUM:
            self.plotter = PlotPowerSpectrum.PlotPowerSpectrum()
            if not self.plotter.rePlot(plotId, plotElements, outputName, show):
                return False
            
        elif kind == PlotKind.AMP_STABILITY or kind == PlotKind.PHASE_STABILITY: 
            self.plotter = PlotStability.PlotStability()
            if not self.plotter.rePlot(plotId, plotElements, outputName, show):
                return False

        else:
            return False
        
        # get the results:
        self.imageData = self.plotter.imageData
        self.plotElementsFinal = plotElements
        return True
