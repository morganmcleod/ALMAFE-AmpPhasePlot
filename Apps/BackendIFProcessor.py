from AmpPhaseDataLib.TimeSeriesAPI import TimeSeriesAPI
from AmpPhaseDataLib.TimeSeries import TimeSeries
from AmpPhasePlotLib.PlotAPI import PlotAPI
from AmpPhaseDataLib.Constants import DataSource, DataKind, PlotEl, SpecLines, Units
from datetime import datetime
import csv
import os
inputFile = r'./sampleData-local/BE-IFP/IFPT - Allan_Std_Dev 999 20231214T151829.csv'
startTime = datetime.strptime("20231214T151829", "%Y%m%dT%H%M%S")

class BackEndIFProcessor():

    OUTPUTS_LIST = (
        'LSB A',
        'LSB B',
        'LSB C',
        'LSB D',
        'USB A',
        'USB B',
        'USB C',
        'USB D'
    )

    DATA_LIST = (
        'SB (T=1 t=0.05)',
        'SB (T=100 t=1)',
        'BB (T=1 t=0.05)',
        'BB (T=100 t=1)'       
    )

    def __init__(self, fileName = None, startTime = datetime.now()):
        self.fileName = None
        self.tsAPI = TimeSeriesAPI()
        self.plotAPI = PlotAPI()
        if fileName:
            self.loadFile(fileName, startTime)

    def loadFile(self, fileName, startTime = datetime.now()):
        self.fileName = fileName
        self.timeSeriesIds = {}
        
        self.path, _ = os.path.split(fileName)
            
        with open(fileName) as file:
            reader = csv.reader(file, delimiter = ',')
            currentOutput = None            
            for row in reader:
                if row[0] in (self.OUTPUTS_LIST):
                    if currentOutput is not None:
                        self.__finish(currentOutput)
                    currentOutput = row[0]
                    print(f"{currentOutput}...")
                    self.__start(currentOutput, startTime)
                else:
                    try:
                        self.timeSeries[self.DATA_LIST[0]].dataSeries.append(float(row[0]))
                        self.timeSeries[self.DATA_LIST[1]].dataSeries.append(float(row[1]))
                        self.timeSeries[self.DATA_LIST[2]].dataSeries.append(float(row[2]))
                        self.timeSeries[self.DATA_LIST[3]].dataSeries.append(float(row[3]))
                    except:
                        pass
            self.__finish(currentOutput)

    def __start(self, currentOutput, startTime):
        self.timeSeries = {}
        self.timeSeries[self.DATA_LIST[0]] = TimeSeries(tau0Seconds = 0.005, startTime = startTime)
        self.timeSeries[self.DATA_LIST[1]] = TimeSeries(tau0Seconds = 0.05, startTime = startTime)
        self.timeSeries[self.DATA_LIST[2]] = TimeSeries(tau0Seconds = 0.005, startTime = startTime)
        self.timeSeries[self.DATA_LIST[3]] = TimeSeries(tau0Seconds = 0.05, startTime = startTime)

    def __finish(self, currentOutput):
        plotEls_SHORT = {
            PlotEl.SPEC_LINE1: SpecLines.IFP_GAIN_STABILITY_SHORT,
            PlotEl.XRANGE_PLOT: SpecLines.XRANGE_PLOT_IFP_GAIN_SHORT,
            PlotEl.Y_AXIS_LABEL: u'σ(2,t=0.05s,T)'
        }
        plotEls_MEDIUM = {
            PlotEl.SPEC_LINE1: SpecLines.IFP_GAIN_STABILITY_MEDIUM,
            PlotEl.XRANGE_PLOT: SpecLines.XRANGE_PLOT_IFP_GAIN_MEDIUM,
            PlotEl.Y_AXIS_LABEL: u'σ(2,t=1s,T)'
        }
        dataSources = {
            DataSource.DATA_KIND: DataKind.GAIN.value,
            DataSource.UNITS: Units.MW.value
        }
        outputName = f"{currentOutput}_{self.DATA_LIST[0]}"
        dataSources[DataSource.DATA_SOURCE] = outputName
        plotEls_SHORT[PlotEl.TITLE] = outputName
        self.plotAPI.plotAmplitudeStability(self.timeSeries[self.DATA_LIST[0]], dataSources, plotEls_SHORT, outputName = os.path.join(self.path, outputName + ".png"))
        
        outputName = f"{currentOutput}_{self.DATA_LIST[1]}"
        dataSources[DataSource.DATA_SOURCE] = outputName
        plotEls_MEDIUM[PlotEl.TITLE] = outputName
        self.plotAPI.plotAmplitudeStability(self.timeSeries[self.DATA_LIST[1]], dataSources, plotEls_MEDIUM, outputName = os.path.join(self.path, outputName + ".png"))
        
        outputName = f"{currentOutput}_{self.DATA_LIST[2]}"
        dataSources[DataSource.DATA_SOURCE] = outputName
        plotEls_SHORT[PlotEl.TITLE] = outputName
        self.plotAPI.plotAmplitudeStability(self.timeSeries[self.DATA_LIST[2]], dataSources, plotEls_SHORT, outputName = os.path.join(self.path, outputName + ".png"))

        outputName = f"{currentOutput}_{self.DATA_LIST[3]}"
        dataSources[DataSource.DATA_SOURCE] = outputName
        plotEls_MEDIUM[PlotEl.TITLE] = outputName
        self.plotAPI.plotAmplitudeStability(self.timeSeries[self.DATA_LIST[3]], dataSources, plotEls_MEDIUM, outputName = os.path.join(self.path, outputName + ".png"))
        print("done.")


obj = BackEndIFProcessor()
obj.loadFile(inputFile, startTime)
pass