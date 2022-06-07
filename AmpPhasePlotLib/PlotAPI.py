'''
PlotAPI for calling applications to generate plots.
'''
from AmpPhaseDataLib.TimeSeriesAPI import TimeSeriesAPI
from AmpPhaseDataLib.ResultAPI import ResultAPI
from AmpPhaseDataLib.Constants import DataKind, DataSource, DataStatus, PlotEl, PlotKind, SpecLines, Units
from Calculate import AmplitudeStability, PhaseStability, FFT
from Plot.Plotly import PlotTimeSeries, PlotStability, PlotSpectrum
from datetime import datetime

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
        
    def plotTimeSeries(self, timeSeriesId, plotElements = None, outputName = None, show = False):
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
        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}
        
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
    
    def plotSpectrum(self, timeSeriesId, plotElements = None, outputName = None, show = False, noiseFloorId = None):
        '''
        Create an AMP_SPECTRUM or POWER_SPECTRUM plot
        The resulting image binary data (.png) is stored in self.imageData.
        The applied plotElements are stored in self.plotElementsFinal.
        The resulting traces ([x], [y], [yError], name) are stored in self.traces 
        If any spec lines were provided, self.dataStatusFinal will be updated to MEET_SPEC or FAIL_SPEC.
        :param timeSeriesId: a timeSeriesId to retrieve and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: str filename to store the resulting .png file.
        :param show: if True, displays the plot using the default renderer.
        :param noiseFloorId: if provided, timeSeriesId to analyze subtract before plotting.
        :return True if succesful, False otherwise
        '''
        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}
        
        # clear anything kept from last plot:
        self.__reset()

        # get the TimeSeries data:
        timeSeries = self.tsAPI.retrieveTimeSeries(timeSeriesId)
        if not timeSeries:
            return False
        if not timeSeries.isValid():
            return False
        noiseFloor = self.tsAPI.retrieveTimeSeries(noiseFloorId)

        # Get the DataSource tags:
        srcKind = DataKind.fromStr(self.tsAPI.getDataSource(timeSeriesId, DataSource.DATA_KIND, (DataKind.AMPLITUDE).value))
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
        if noiseFloor:
            noiseFloor = noiseFloor.getDataSeries(requiredUnits)
    
        # set the plot title:
        if dfltTitle and not self.tsAPI.getDataSource(timeSeriesId, DataSource.DATA_SOURCE, False) \
                     and not plotElements.get(PlotEl.TITLE, False) and dfltTitle:
            plotElements[PlotEl.TITLE] = dfltTitle
        
        # make the plot:
        self.calc = FFT.FFT()
        self.plotter = PlotSpectrum.PlotSpectrum()

        if noiseFloor:
            if self.calc.calculate(noiseFloor, timeSeries.tau0Seconds):
                noiseFloor = self.calc.yResult
            else:
                noiseFloor = None
            
        if not self.calc.calculate(dataSeries, timeSeries.tau0Seconds):
            return False

        if noiseFloor:
            self.calc.yResult = [self.calc.yResult[x] - noiseFloor[x] for x in range(len(self.calc.yResult))]
            plotElements[PlotEl.PROCESS_NOTES] = "Subtracted noise floor {}".format(noiseFloorId)

        # check for a special RMS spec:
        rmsSpec = plotElements.get(PlotEl.RMS_SPEC, None)
        compliance = ""
        if rmsSpec:
            rmsSpec = rmsSpec.split(', ')
            bwLower = float(rmsSpec[0])
            bwUpper = float(rmsSpec[1])
            rmsSpec = float(rmsSpec[2])
            RMS = self.calc.RMSfromFFT(bwLower, bwUpper)
            if RMS <= rmsSpec:
                complies = "PASS"
                self.__updateDataStatusFinal(True)
            else:
                complies = "FAIL"
                self.__updateDataStatusFinal(False)
            
            compliance = "{0:.2e} {1} RMS in {2} to {3} Hz.  Max {4:.2e} : {5}".format(
                RMS, requiredUnits.value, bwLower, bwUpper, rmsSpec, complies)
            plotElements[PlotEl.SPEC_COMPLIANCE] = compliance
        
        # check whether to just display the RMS on the plot:
        elif plotElements.get(PlotEl.SHOW_RMS, False):
            RMS = self.calc.RMSfromFFT()
            if RMS < 1e-3:
                compliance = "RMS = {0:.2e}".format(RMS)
            else:
                compliance = "RMS = {0:.3}".format(RMS)
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

        if not self.plotter.plot(timeSeriesId, self.calc.xResult, self.calc.yResult, plotElements, outputName, show):
            return False

        # get the results:
        self.traces = self.plotter.traces
        self.imageData = self.plotter.imageData
        self.plotElementsFinal = plotElements
        return True
    
    def plotAmplitudeStability(self, timeSeriesIds, plotElements = None, outputName = None, show = False):
        '''
        Create an POWER_STABILITY, VOLT_STABILITY, or PHASE_STABILITY plot
        The resulting image data is stored in self.imageData.
        The applied plotElements are stored in self.plotElementsFinal.
        The resulting traces ([x], [y], [yError], name) are stored in self.traces 
        If any spec lines were provided, self.dataStatusFinal will be updated to MEET_SPEC or FAIL_SPEC.
        :param timeSeriesIds: a single int timeSeriesId or a list of Ids to retrieve and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: str filename to store the resulting .png file.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}

        # clear anything kept from last plot:
        self.__reset()
        self.calc = AmplitudeStability.AmplitudeStability()
        self.plotter = PlotStability.PlotStability()
        
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
        
        # use this to find the earliest start time if multiple traces:
        startTime = None
        
        # is it a single time series plot?
        if isinstance(timeSeriesIds, int):
            timeSeriesId = timeSeriesIds
            plotElements[PlotEl.ERROR_BARS] = "1"
            self.plotter.startPlot(plotElements)
            timeSeries = self.__plotAmplitudeStabilitySingle(timeSeriesId, plotElements)
            if not timeSeries:
                return False
            startTime = timeSeries.startTime

        # is it a list:
        elif isinstance(timeSeriesIds, list):
            # suppress error bars for ensemble plot
            plotElements[PlotEl.ERROR_BARS] = "0" if len(timeSeriesIds) > 1 else "1"
            startTime = datetime.now()
            self.plotter.startPlot(plotElements)
            for timeSeriesId in timeSeriesIds:
                timeSeries = self.__plotAmplitudeStabilitySingle(timeSeriesId, plotElements)
                if timeSeries:
                    if timeSeries.startTime < startTime:
                        startTime = timeSeries.startTime
                else:
                    return False
            # set a generic title:
            title = plotElements.get(PlotEl.TITLE, None)
            if not title:
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
        '''
        :param timeSeriesId:
        :param plotElements:
        :return the retrieved TimeSeries object if successful, else None
        '''
        # get the TimeSeries data:
        timeSeries = self.tsAPI.retrieveTimeSeries(timeSeriesId)
        if not timeSeries:
            return None
        
        # Get the DataSource tags:
        srcKind = self.tsAPI.getDataSource(timeSeriesId, DataSource.DATA_KIND, (DataKind.AMPLITUDE).value)
        currentUnits = timeSeries.dataUnits
        
        # Depending on srcKind, get the dataSeries in the proper units:
        if srcKind == (DataKind.VOLTAGE).value:
            dataSeries = timeSeries.getDataSeries(Units.VOLTS)
            normalize = False   # for pure voltage time series: don't normalize, calculate ADEV
            calcAdev = True     # this would be typical for a bias or power supply where absolute
                                # deviations from nominal are more of interest than relative level drifts.
        else: # for POWER and AMPLITUDE, use the source units, if any:
            dataSeries = timeSeries.getDataSeries(currentUnits)
            normalize = True    # for power or unknown amplitude time series, normalize and calculate AVAR.
            calcAdev = False    # units might still be VOLTS in the case of a crystal detector having 
                                # square-law output characteristic.

        if not dataSeries:
            return None

        freqLOGHz = self.tsAPI.getDataSource(timeSeriesId, DataSource.LO_GHZ)
        if freqLOGHz:
            freqLOGHz = float(freqLOGHz)
                    
        # calculate Amplitude stability plot traces:
        xRangePlot = plotElements.get(PlotEl.XRANGE_PLOT, SpecLines.XRANGE_PLOT_AMP_STABILITY).split(', ')
        TMin = float(xRangePlot[0])
        TMax = float(xRangePlot[1])
        
        if not self.calc.calculate(dataSeries, timeSeries.tau0Seconds, TMin, TMax, normalize, calcAdev):
            return None

        # check spec lines:
        for specLine in self.specLines:
            complies = self.calc.checkSpecLine(specLine[0], specLine[2], specLine[1], specLine[3])
            self.__updateDataStatusFinal(complies)

        # add the trace:
        if self.plotter.addTrace(timeSeriesId, self.calc.xResult, self.calc.yResult, self.calc.yError, plotElements):
            return timeSeries
        else:
            return None
        

    def plotPhaseStability(self, timeSeriesIds, plotElements = None, outputName = None, show = False):
        '''
        Create an PHASE_STABILITY plot
        The resulting image data is stored in self.imageData.
        The applied plotElements are stored in self.plotElementsFinal.
        The resulting traces ([x], [y], [yError], name) are stored in self.traces 
        If any spec lines were provided, self.dataStatusFinal will be updated to MEET_SPEC or FAIL_SPEC.
        :param timeSeriesIds: a single int timeSeriesId or a list of Ids to retrieve and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: str filename to store the resulting .png file.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}

        # clear anything kept from last plot:
        self.__reset()
        self.calc = PhaseStability.PhaseStability()
        self.plotter = PlotStability.PlotStability()

        # parse any spec lines:
        specLine = plotElements.get(PlotEl.SPEC_LINE1, None)
        if specLine:
            specLine = specLine.split(', ')
            self.specLines.append((float(specLine[0]), float(specLine[1]), float(specLine[2]), float(specLine[3])))

        # parse any spec lines:
        specLine = plotElements.get(PlotEl.SPEC_LINE2, None)
        if specLine:
            specLine = specLine.split(', ')
            self.specLines.append((specLine[0], specLine[1], specLine[2], specLine[3]))

        # use this to find the earliest start time if multiple traces:
        startTime = None

        # is it a single time series plot?
        if isinstance(timeSeriesIds, int):
            timeSeriesId = timeSeriesIds
            plotElements[PlotEl.ERROR_BARS] = "1"
            self.plotter.startPlot(plotElements)
            timeSeries = self.__plotPhaseStabilitySingle(timeSeriesId, plotElements)
            if not timeSeries:
                return False
            startTime = timeSeries.startTime

        # is it a list:
        elif isinstance(timeSeriesIds, list):
            # suppress error bars for ensemble plot
            plotElements[PlotEl.ERROR_BARS] = "0" if len(timeSeriesIds) > 1 else "1"
            startTime = datetime.now()
            self.plotter.startPlot(plotElements)
            for timeSeriesId in timeSeriesIds:
                timeSeries = self.__plotPhaseStabilitySingle(timeSeriesId, plotElements)
                if timeSeries:
                    if timeSeries.startTime < startTime:
                        startTime = timeSeries.startTime
                else:
                    return None
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
        '''
        :param timeSeriesId:
        :param plotElements:
        :return the retrieved TimeSeries object if successful, else None
        '''
        # get the TimeSeries data:
        timeSeries = self.tsAPI.retrieveTimeSeries(timeSeriesId)
        if not timeSeries:
            return None
        
        freqRFGHz = self.tsAPI.getDataSource(timeSeriesId, DataSource.RF_GHZ)
        if freqRFGHz:
            freqRFGHz = float(freqRFGHz)

        dataSeries = timeSeries.getDataSeries(Units.DEG)

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
        
        if not self.calc.calculate(dataSeries, timeSeries.tau0Seconds, TMin, TMax, freqRFGHz):
            return None

        # check spec lines:
        for specLine in self.specLines:
            complies = self.calc.checkSpecLine(specLine[0], specLine[2], specLine[1], specLine[3])
            self.__updateDataStatusFinal(complies)

        # add the trace:
        if self.plotter.addTrace(timeSeriesId, self.calc.xResult, self.calc.yResult, self.calc.yError, plotElements):
            return timeSeries
        else:
            return None
    
    def rePlot(self, plotId, plotElements = None, outputName = None, show = False):
        '''
        Make a plot from whatever data is in the Result database for plotId.
        Not supported for TIME_SERIES plots.       
        :param plotId: int to fetch and plot
        :param plotElements: dict of {PLotElement : str} to supplement or replace any defaults or loaded from database.
        :param outputName: Filename where to write the plot .PNG file, optional.
        :param show: if True, displays the plot using the default renderer.
        :return True if succesful, False otherwise
        '''
        # initialize default plotElements [https://docs.python.org/3/reference/compound_stmts.html#index-30]:
        if plotElements == None:
            plotElements = {}

        self.__reset()
        ra = ResultAPI()
        
        plot = ra.retrievePlot(plotId)
        if not plot:
            return False
        assert plot[0] == plotId
        kind = plot[1]

        if kind == PlotKind.POWER_SPECTRUM:
            self.plotter = PlotSpectrum.PlotSpectrum()
            if not self.plotter.rePlot(plotId, plotElements, outputName, show):
                return False
            
        elif kind == PlotKind.POWER_STABILITY or PlotKind.VOLT_STABILITY or kind == PlotKind.PHASE_STABILITY: 
            self.plotter = PlotStability.PlotStability()
            if not self.plotter.rePlot(plotId, plotElements, outputName, show):
                return False

        else:
            return False
        
        # get the results:
        self.imageData = self.plotter.imageData
        self.plotElementsFinal = plotElements
        return True

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
            self.dataStatusFinal = DataStatus.FAIL_SPEC

        # don't overwrite previous FAIL:
        elif self.dataStatusFinal != DataStatus.FAIL_SPEC:
            self.dataStatusFinal = DataStatus.MEET_SPEC
