'''
PlotAPI for calling applications to generate plots.
'''
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhaseDataLib.Constants import Units, PlotEl, DataSource, SpecLines
from Calculate import AmplitudeStability, PhaseStability, PowerSpectrum
from Plot.Plotly import PlotTimeSeries, PlotStability, PlotPowerSpectrum
from datetime import datetime

class PlotAPI(object):
    '''
    PlotAPI for calling applications to generate plots.
    classdocs
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
        self.xResult = None
        self.yResult = None
        self.yError = None
        self.imageData = None
        self.plotterElementsFinal = None
        
    def plotTimeSeries(self, timeSeriesId, plotElements = {}, outputName = None, show = False):
        '''
        Create a TIME_SERIES plot
        The resulting image binary data (.png) is stored in self.imageData.
        The applied plotElements are stored in self.plotterElementsFinal.
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
        self.plotterElementsFinal = plotElements
        return True
    
    def plotPowerSpectrum(self, timeSeriesId, plotElements = {}, outputName = None, show = False):
        '''
        Create a POWER_SPECTRUM plot
        The resulting image binary data (.png) is stored in self.imageData.
        The applied plotElements are stored in self.plotterElementsFinal.
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
            plotElements[PlotEl.TITLE] = "Phase Stability"
        elif srcUnits == (Units.VOLTS).value:
            dataSeries = self.tsAPI.getDataSeries(requiredUnits = Units.VOLTS)
            plotElements[PlotEl.TITLE] = "Voltage Noise Density"
        else:
            dataSeries = self.tsAPI.getDataSeries(requiredUnits = Units.WATTS)
            plotElements[PlotEl.TITLE] = "Amplitude Stability"
        
        # make the plot:
        self.calc = PowerSpectrum.PowerSpectrum()
        self.plotter = PlotPowerSpectrum.PlotPowerSpectrum()
        
        if not self.calc.calculate(dataSeries, self.tsAPI.tau0Seconds):
            return False

        if not self.plotter.plot(timeSeriesId, self.calc.xResult, self.calc.yResult, plotElements, outputName, show):
            return False

        # get the results:
        self.imageData = self.plotter.imageData
        self.plotterElementsFinal = plotElements
        return True
    
    def plotAmplitudeStability(self, timeSeriesIds, plotElements = {}, outputName = None, show = False):
        '''
        Create an AMP_STABILITY plot
        The resulting image data is stored in self.imageData.
        The applied plotElements are stored in self.plotterElementsFinal.
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
        
        # is it a single time series plot?
        if isinstance(timeSeriesIds, int):
            timeSeriesId = timeSeriesIds
            plotElements[PlotEl.ERROR_BARS] = "1"
            self.plotter.startPlot(plotElements)
            if self.__plotAmplitudeStabilitySingle(timeSeriesId, plotElements):
                return self.plotter.finishPlot(self.tsAPI.startTime, plotElements, outputName, show)
            else:
                return False

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
            plotElements[PlotEl.TITLE] = "Amplitude Stability"
            return self.plotter.finishPlot(startTime, plotElements, outputName, show)
        else:
            return False

        # get the results:
        self.imageData = self.plotter.imageData
        self.plotterElementsFinal = plotElements
        return True
        
    def __plotAmplitudeStabilitySingle(self, timeSeriesId, plotElements):
        # get the TimeSeries data:
        if not self.tsAPI.retrieveTimeSeries(timeSeriesId):
            return False
        
        dataSeries = self.tsAPI.getDataSeries(requiredUnits = Units.WATTS)
        freqLOGHz = self.tsAPI.getDataSource(timeSeriesId, DataSource.LO_GHZ)
        if freqLOGHz:
            freqLOGHz = float(freqLOGHz)
                    
        # calculate Amplitude stability plot traces:
        xRangePlot = plotElements.get(PlotEl.XRANGE_PLOT, SpecLines.XRANGE_PLOT_AMP_STABILITY).split(', ')
        TMin = float(xRangePlot[0])
        TMax = float(xRangePlot[1])
        
        if not self.calc.calculate(dataSeries, self.tsAPI.tau0Seconds, TMin, TMax):
            return False
        
        # get the calculated trace:
        self.xResult = self.calc.xResult
        self.yResult = self.calc.yResult
        self.yError = self.calc.yError

        # add the trace:
        return self.plotter.addTrace(timeSeriesId, self.xResult, self.yResult, self.yError, plotElements)

    def plotPhaseStability(self, timeSeriesIds, plotElements = {}, outputName = None, show = False):
        '''
        Create an PHASE_STABILITY plot
        The resulting image data is stored in self.imageData.
        The applied plotElements are stored in self.plotterElementsFinal.
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
        
        # is it a single time series plot?
        if isinstance(timeSeriesIds, int):
            timeSeriesId = timeSeriesIds
            plotElements[PlotEl.ERROR_BARS] = "1"
            self.plotter.startPlot(plotElements)
            if self.__plotPhaseStabilitySingle(timeSeriesId, plotElements):
                return self.plotter.finishPlot(self.tsAPI.startTime, plotElements, outputName, show)
            else:
                return False

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
            plotElements[PlotEl.TITLE] = "Phase Stability"
            return self.plotter.finishPlot(startTime, plotElements, outputName, show)
        else:
            return False
        
        # get the results:
        self.imageData = self.plotter.imageData
        self.plotterElementsFinal = plotElements
        return True
    
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
        
        # get the calculated trace:
        self.xResult = self.calc.xResult
        self.yResult = self.calc.yResult
        self.yError = self.calc.yError

        # add the trace:
        return self.plotter.addTrace(timeSeriesId, self.xResult, self.yResult, self.yError, plotElements)
    