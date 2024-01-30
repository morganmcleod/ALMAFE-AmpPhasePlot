'''
PlotAPI for calling applications to generate plots.
'''
from AmpPhaseDataLib.TimeSeriesAPI import TimeSeriesAPI
from AmpPhaseDataLib.TimeSeries import TimeSeries
from AmpPhaseDataLib.Constants import DataKind, DataSource, DataStatus, PlotEl, SpecLines, Units
from Calculate.AmplitudeStability import AmplitudeStability
from Calculate.PhaseStability import PhaseStability
from Calculate.FFT import FFT
from Plot.Plotly.PlotTimeSeries import PlotTimeSeries
from Plot.Plotly.PlotStability import PlotStability
from Plot.Plotly.PlotSpectrum import PlotSpectrum
from datetime import datetime
import configparser
from typing import Dict, List, Optional, Union

class PlotAPI(object):
    '''
    PlotAPI for calling applications to generate plots.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.tsAPI = TimeSeriesAPI()
        self.__reset()

    def __reset(self):
        '''
        Reset members to just-constructed state
        '''
        self.calc = None
        self.plotter = None
        self.specLines = []
        self.traces = []
        self.imageData = None
        self.plotElementsFinal = None
        self.dataStatusFinal = DataStatus.UNKNOWN

    def plotTimeSeries(self, 
            timeSeries: Union[TimeSeries, int], 
            dataSources: Dict[DataSource, str] = None,
            plotElements: Dict[PlotEl, str] = None, 
            outputName: str = None, 
            show: bool = False,
            unwrapPhase = False) -> bool:
        '''
        Create a TIME_SERIES plot
        The resulting image binary data (.png) is stored in self.imageData.
        The applied plotElements are stored in self.plotElementsFinal.
        Unlike the other methods in this class, self.traces is not updated by this method. (It would be the same as the raw data, and huge.)
        :param timeSeries: the TimeSeries to plot *or* its ID to load via TimeSeriesAPI.
        :param plotElements: to supplement or replace any defaults or loaded via TimeSeriesAPI
        :param outputName: str filename to store the resulting .png file.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # get the TimeSeries data:
        timeSeries = self.__getTimeSeries(timeSeries)
        if not timeSeries:
            return False
        
        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}

        # load dataSources:
        if not dataSources and timeSeries.tsId > 0:
            dataSources = self.tsAPI.getAllDataSources(timeSeries.tsId)
        else:
            dataSources = {}
                    
        # clear anything kept from last plot:
        self.__reset()

        # make the plot:
        self.plotter = PlotTimeSeries()
        if not self.plotter.plot(timeSeriesId, dataSources, plotElements, outputName, show, unwrapPhase = unwrapPhase):
            return False
        
        # get the results:
        self.imageData = self.plotter.imageData
        self.plotElementsFinal = plotElements
        return True
    
    def plotSpectrum(self, 
            timeSeries: Union[TimeSeries, int], 
            dataSources: Dict[DataSource, str] = None,
            plotElements: Dict[PlotEl, str] = None, 
            outputName: str = None, 
            show: bool = False) -> bool:
        '''
        Create an AMP_SPECTRUM or POWER_SPECTRUM plot
        The resulting image binary data (.png) is stored in self.imageData.
        The applied plotElements are stored in self.plotElementsFinal.
        The resulting traces ([x], [y], [yError], name) are stored in self.traces 
        If any spec lines were provided, self.dataStatusFinal will be updated to MEET_SPEC or FAIL_SPEC.
        :param timeSeries: the TimeSeries to plot *or* its ID to load via TimeSeriesAPI.
        :param plotElements: to supplement or replace any defaults or loaded via TimeSeriesAPI
        :param outputName: str filename to store the resulting .png file.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # get the TimeSeries data:
        timeSeries = self.__getTimeSeries(timeSeries)
        if not timeSeries:
            return False

        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}

        # load dataSources:
        if not dataSources and timeSeries.tsId > 0:
            dataSources = self.tsAPI.getAllDataSources(timeSeries.tsId)
        else:
            dataSources = {}

        # read FFT_RMS configuration:
        config = configparser.ConfigParser()
        config.read("AmpPhaseDataLib.ini")
        try:
            ignoreHarmonicsOf = int(config['FFT_RMS']['ignoreHarmonicsOf'])
        except:
            ignoreHarmonicsOf = 0
        try:
            ignoreHarmonicsWindow = float(config['FFT_RMS']['ignoreHarmonicsWindow'])
        except:
            ignoreHarmonicsWindow = 3.0
        
        # clear anything kept from last plot:
        self.__reset()

        # Get the DataSource tags:
        srcKind = DataKind.fromStr(dataSources.get(DataSource.DATA_KIND, (DataKind.AMPLITUDE).value))
        currentUnits = timeSeries.dataUnits
        
        # Get the time series and set the default title:
        if srcKind == DataKind.POWER:
            dfltTitle = "Power Spectral Density"
            requiredUnits = currentUnits    # could be W or V
        elif srcKind == DataKind.PHASE:
            dfltTitle = "Phase Spectral Density"
            requiredUnits = Units.DEG
        elif srcKind == DataKind.VOLTAGE:
            dfltTitle = "Voltage Spectral Density"
            requiredUnits = Units.VOLTS
        else:
            dfltTitle = "Amplitude Spectral Density"
            requiredUnits = currentUnits

        dataSeries = timeSeries.getDataSeries(requiredUnits)  
    
        # set the plot title.  Priority is: PlotEl.TITLE, DATA_SOURCE, dfltTitle
        dataSource = dataSources.get(DataSource.DATA_SOURCE, False)                     
        if dfltTitle and not dataSource and not plotElements.get(PlotEl.TITLE, False):
            plotElements[PlotEl.TITLE] = dfltTitle
        
        # make the plot:
        self.calc = FFT()
        self.plotter = PlotSpectrum()
            
        if not self.calc.calculate(dataSeries, timeSeries.tau0Seconds):
            print("Invalid dataSeries or sampling interval for FFT.")
            return False

        # calculate highlight points:
        x2Array = []
        y2Array = []
        if ignoreHarmonicsOf:
            for x, y in zip(self.calc.xResult, self.calc.yResult):
                if self.calc.isHarmonic(x, ignoreHarmonicsOf, ignoreHarmonicsWindow):
                    x2Array.append(x)
                    y2Array.append(y)

        # check for a special RMS spec:
        rmsSpec = plotElements.get(PlotEl.RMS_SPEC, None)
        compliance = ""
        if rmsSpec:
            rmsSpec = rmsSpec.split(', ')
            bwLower = float(rmsSpec[0])
            bwUpper = float(rmsSpec[1])
            rmsSpec = float(rmsSpec[2])
            RMS = self.calc.RMSfromFFT(bwLower, bwUpper, 
                                       ignoreHarmonicsOf = ignoreHarmonicsOf, 
                                       ignoreHarmonicsWindow = ignoreHarmonicsWindow)
            if RMS <= rmsSpec:
                complies = "PASS"
                self.__updateDataStatusFinal(True)
            else:
                complies = "FAIL"
                self.__updateDataStatusFinal(False)
            
            compliance = "{0:.2e} {1} RMS in {2} to {3} Hz".format(RMS, requiredUnits.value, bwLower, bwUpper)
            if ignoreHarmonicsOf:
                compliance += " (ignoring harmonics of {} Hz)".format(ignoreHarmonicsOf)
            compliance += "  Max {0:.2e} : {1}".format(rmsSpec, complies)
            plotElements[PlotEl.SPEC_COMPLIANCE] = compliance
        
        # check whether to just display the RMS on the plot:
        elif plotElements.get(PlotEl.SHOW_RMS, False):
            RMS = self.calc.RMSfromFFT(ignoreHarmonicsOf = ignoreHarmonicsOf, 
                                       ignoreHarmonicsWindow = ignoreHarmonicsWindow)
            if RMS < 1e-3:
                compliance = "RMS = {0:.2e}".format(RMS)
            else:
                compliance = "RMS = {0:.3}".format(RMS)
            if ignoreHarmonicsOf:
                compliance += " (ignoring harmonics of {} Hz)".format(ignoreHarmonicsOf)
            plotElements[PlotEl.SPEC_COMPLIANCE] = compliance
            
        # check whether there is a spec line to compare to the FFT:
        fftSpec = plotElements.get(PlotEl.SPEC_LINE1, None)
        if fftSpec:
            fftSpec = fftSpec.split(', ')
            bwLower = float(fftSpec[0])
            bwUpper = float(fftSpec[1])
            specLimit = float(fftSpec[2])  # for now assuming that y2==y1
            # compare to spec line:
            if self.calc.checkFFTSpec(bwLower, bwUpper, specLimit):
                self.__updateDataStatusFinal(True)
            else:
                self.__updateDataStatusFinal(True)

        if not self.plotter.plot(timeSeriesId, self.calc.xResult, self.calc.yResult, x2Array, y2Array, 
                                 plotElements = plotElements, outputName = outputName, show = show):
            return False

        # get the results:
        self.traces = self.plotter.traces
        self.imageData = self.plotter.imageData
        self.plotElementsFinal = plotElements
        return True
    
    def plotAmplitudeStability(self, 
                timeSeries: Union[TimeSeries, int, List[Union[TimeSeries, int]]],
                dataSources: Dict[DataSource, str] = None,
                plotElements: Dict[PlotEl, str] = None, 
                outputName: str = None, 
                show: bool = False) -> bool:
        '''
        Create an POWER_STABILITY, VOLT_STABILITY, or PHASE_STABILITY plot
        The resulting image data is stored in self.imageData.
        The applied plotElements are stored in self.plotElementsFinal.
        The resulting traces ([x], [y], [yError], name) are stored in self.traces 
        If any spec lines were provided, self.dataStatusFinal will be updated to MEET_SPEC or FAIL_SPEC.
        :param timeSeries: either a single TimeSeries or ID to load, or a list of TimeSeries or IDs.
        :param plotElements: dict of {PLotEl : str} to supplement or replace any defaults or loaded from database.
        :param outputName: str filename to store the resulting .png file.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # get the TimeSeries data:
        timeSeriesList = self.__getTimeSeriesList(timeSeries)
        if not timeSeriesList:
            return False
    
        # load dataSources:
        if dataSources is None:
            if timeSeries.tsId > 0:
                dataSources = self.tsAPI.getAllDataSources(timeSeries.tsId)
            else:
                dataSources = {}
    
        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}

        # clear anything kept from last plot:
        self.__reset()
        self.calc = AmplitudeStability()
        self.plotter = PlotStability()
        
        # parse spec line 1:
        specLine = plotElements.get(PlotEl.SPEC_LINE1, None)
        if specLine:
            specLine = specLine.split(', ')
            self.specLines.append((float(specLine[0]), float(specLine[1]), float(specLine[2]), float(specLine[3])))

        # parse spec line 2:
        specLine = plotElements.get(PlotEl.SPEC_LINE2, None)
        if specLine:
            specLine = specLine.split(', ')
            self.specLines.append((float(specLine[0]), float(specLine[1]), float(specLine[2]), float(specLine[3])))
        
        # suppress error bars for ensemble plot
        plotElements[PlotEl.ERROR_BARS] = "0" if len(timeSeries) > 1 else "1"
        startTime = datetime.now()
        self.plotter.startPlot(plotElements)
        for timeSeries in timeSeriesList:
            if timeSeries.startTime < startTime:
                startTime = timeSeries.startTime
            self.__plotAmplitudeStabilitySingle(timeSeries, dataSources, plotElements)

        # set a generic title:
        title = plotElements.get(PlotEl.TITLE, None)
        if not title:
            plotElements[PlotEl.TITLE] = "Amplitude Stability"

        # get the results:
        if self.plotter.finishPlot(startTime, dataSources, plotElements, outputName, show):
            self.traces = self.plotter.traces
            self.imageData = self.plotter.imageData
            self.plotElementsFinal = plotElements
            return True
        else:
            return False
        
    def __plotAmplitudeStabilitySingle(self, 
            timeSeries: TimeSeries,
            dataSources: Dict[DataSource, str],
            plotElements: Dict[PlotEl, str] = None) -> bool:
        '''
        :param timeSeries:
        :param plotElements:
        :return True/False
        '''
        freqLOGHz = self.tsAPI.getDataSource(timeSeries.tsId, DataSource.LO_GHZ)
        if freqLOGHz:
            freqLOGHz = float(freqLOGHz)
                    
        # calculate Amplitude stability plot traces:
        xRangePlot = plotElements.get(PlotEl.XRANGE_PLOT, SpecLines.XRANGE_PLOT_AMP_STABILITY).split(', ')
        TMin = float(xRangePlot[0])
        TMax = float(xRangePlot[1])
        
        # Get the DataSource tags:
        srcKind = dataSources.get(DataSource.DATA_KIND, DataKind.AMPLITUDE.value)
        currentUnits = timeSeries.dataUnits
        
        # Depending on srcKind, get the dataSeries in the proper units:
        if srcKind == (DataKind.VOLTAGE).value:
            dataSeries = timeSeries.getDataSeries(Units.VOLTS)
            normalize = False   # for pure voltage time series: don't normalize, calculate ADEV
            calcAdev = True     # this would be typical for a bias or power supply where absolute
                                # deviations from nominal are more of interest than relative level drifts.
        elif srcKind == (DataKind.GAIN).value:
            # for IFP gain stability normalized ADEV
            dataSeries = timeSeries.getDataSeries(currentUnits)
            normalize = True
            calcAdev = True 
        else:
            # for POWER and AMPLITUDE, use the source units, if any:
            dataSeries = timeSeries.getDataSeries(currentUnits)
            normalize = True    # for power or unknown amplitude time series, normalize and calculate AVAR.
            calcAdev = False    # units might still be VOLTS in the case of a crystal detector having 
                                # square-law output characteristic.

        if not dataSeries:
            return False

        if not self.calc or not isinstance(self.calc, AmplitudeStability):
            self.calc = AmplitudeStability()        
        if not self.calc.calculate(dataSeries, timeSeries.tau0Seconds, TMin, TMax, normalize, calcAdev):
            return False

        # check spec lines:
        for specLine in self.specLines:
            complies = self.calc.checkSpecLine(specLine[0], specLine[2], specLine[1], specLine[3])
            self.__updateDataStatusFinal(complies)

        # add the trace:
        if self.plotter.addTrace(timeSeries, dataSources, self.calc.xResult, self.calc.yResult, self.calc.yError, plotElements):
            return timeSeries
        else:
            return False
    
    def getCalcTrace(self):
        return {
            'x': self.calc.xResult,
            'y': self.calc.yResult,
            'yError': self.calc.yError
        }
    
    def plotPhaseStability(self, 
            timeSeries: Union[TimeSeries, int, List[Union[TimeSeries, int]]],
            dataSources: Dict[DataSource, str] = None,
            plotElements: Dict[PlotEl, str] = None, 
            yUnits = Units.DEG, 
            outputName: str = None, 
            show: bool = False) -> bool:
        '''
        Create a PHASE_STABILITY plot
        The resulting image data is stored in self.imageData.
        The applied plotElements are stored in self.plotElementsFinal.
        The resulting traces ([x], [y], [yError], name) are stored in self.traces 
        If any spec lines were provided, self.dataStatusFinal will be updated to MEET_SPEC or FAIL_SPEC.
        :param timeSeries: either a single TimeSeries or ID to load, or a list of TimeSeries or IDs.
        :param plotElements: dict of {PLotEl : str} to supplement or replace any defaults or loaded from database.
        :param yUnits:
        :param outputName: str filename to store the resulting .png file.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        timeSeriesList = self.__getTimeSeriesList(timeSeries)
        if not timeSeriesList:
            return False
        
        # load dataSources:
        if not dataSources and timeSeries.tsId > 0:
            dataSources = self.tsAPI.getAllDataSources(timeSeries.tsId)
        else:
            dataSources = {}
        
        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}

        # clear anything kept from last plot:
        self.__reset()
        self.calc = PhaseStability()
        self.plotter = PlotStability()

        # parse any spec lines:
        specLine = plotElements.get(PlotEl.SPEC_LINE1, None)
        if specLine:
            specLine = specLine.split(', ')
            self.specLines.append((float(specLine[0]), float(specLine[1]), float(specLine[2]), float(specLine[3])))

        # parse any spec lines:
        specLine = plotElements.get(PlotEl.SPEC_LINE2, None)
        if specLine:
            specLine = specLine.split(', ')
            self.specLines.append((float(specLine[0]), float(specLine[1]), float(specLine[2]), float(specLine[3])))

        # suppress error bars for ensemble plot
        plotElements[PlotEl.ERROR_BARS] = "0" if len(timeSeries) > 1 else "1"
        startTime = datetime.now()
        self.plotter.startPlot(plotElements)
        for timeSeries in timeSeriesList:
            if timeSeries.startTime < startTime:
                startTime = timeSeries.startTime
            self.__plotPhaseStabilitySingle(timeSeries, dataSources, lotElements, yUnits)

        # set a generic title:
        if not plotElements.get(PlotEl.TITLE, None):
            plotElements[PlotEl.TITLE] = "Phase Stability"
        
        # get the results:
        if self.plotter.finishPlot(startTime, plotElements, outputName, show):
            self.traces = self.plotter.traces
            self.imageData = self.plotter.imageData
            self.plotElementsFinal = plotElements
            return True
        else:
            return False
    
    def __plotPhaseStabilitySingle(self, 
            timeSeries: TimeSeries,
            dataSources: Dict[DataSource, str] = None,
            plotElements: Dict[PlotEl, str] = None) -> bool:
        '''
        :param timeSeries:
        :param plotElements:
        :param yUnits:
        :return the retrieved TimeSeries object if successful, else None
        '''
        # get the raw data:
        dataSeries = timeSeries.getDataSeries(yUnits)
        
        # If we have freqRFGHz then can plot in FS instead of DEG:        
        freqRFGHz = dataSources.get(DataSource.RF_GHZ, None)
        if freqRFGHz:
            freqRFGHz = float(freqRFGHz)
            if freqRFGHz > 0:
                yUnits = Units.FS

        # set YUNITS on the first trace:
        if not plotElements.get(PlotEl.YUNITS, None):
            plotElements[PlotEl.YUNITS] = yUnits.value
        
        # calculate Amplitude stability plot traces:
        xRangePlot = plotElements.get(PlotEl.XRANGE_PLOT, SpecLines.XRANGE_PLOT_PHASE_STABILITY).split(', ')
        TMin = float(xRangePlot[0])
        TMax = float(xRangePlot[1])
        
        if not self.calc.calculate(dataSeries, timeSeries.tau0Seconds, TMin, TMax, freqRFGHz):
            return None

        # check spec lines:
        for specLine in self.specLines:
            complies = self.calc.checkSpecLine(specLine[0], specLine[2], specLine[1], specLine[3])
            self.__updateDataStatusFinal(complies)

        # add the trace:
        if self.plotter.addTrace(timeSeries.tsId, self.calc.xResult, self.calc.yResult, self.calc.yError, plotElements):
            return timeSeries
        else:
            return None
    
    def __getTimeSeries(self, timeSeries: Union[TimeSeries, int]) -> Optional[TimeSeries]:
        if isinstance(timeSeries, int):
            return self.tsAPI.retrieveTimeSeries(timeSeries)
        else:
            assert(isinstance(timeSeries, TimeSeries))
            return timeSeries
    
    def __getTimeSeriesList(self, timeSeries: Union[TimeSeries, int, List[Union[TimeSeries, int]]]) -> List[TimeSeries]:
        if isinstance(timeSeries, int): 
            return [self.tsAPI.retrieveTimeSeries(timeSeries)]
        elif isinstance(timeSeries, TimeSeries):
            return [timeSeries]
        else:
            assert(isinstance(timeSeries, list))
            result = []
            for item in timeSeries:
                if isinstance(item, int):
                    result.append(self.tsAPI.retrieveTimeSeries(item))
                else:
                    assert(isinstance(item, TimeSeries))
                    result.append(item)
            return result
                
    def __updateDataStatusFinal(self, passFail):
        '''
        Private helper to update self.dataStatusFinal.  Allowed transitions:
        UNKNOWN -> PASS
        UNKNOWN -> FAIL
        PASS -> FAIL
        :param passFail: True if PASS, False if FAIL
        '''
        # can always FAIL:
        if not passFail:
            self.dataStatusFinal = DataStatus.REJECTED

        # don't overwrite previous FAIL:
        elif self.dataStatusFinal != DataStatus.REJECTED:
            self.dataStatusFinal = DataStatus.ACCEPTED
