from AmpPhaseDataLib.TimeSeriesAPI import TimeSeriesAPI
from AmpPhaseDataLib.TimeSeries import TimeSeries
from AmpPhasePlotLib.PlotAPI import PlotAPI
from AmpPhaseDataLib.Constants import DataSource, DataKind, PlotEl, SpecLines, Units
from Calculate.Common import getAveragesArray
from Calculate.IFPT_ASD import AllanDev
from datetime import datetime
import csv
import os
inputFile = r'.\SampleData-local\BE-IFP\2024-04-30_with_warmup\BB Time Data.csv'
startTime = datetime.strptime("20240430T140000", "%Y%m%dT%H%M%S")

class BackEndIFProcessor():

    TITLE_SHORT = 'BB ASD<sub>g</sub>(2,T,τ) for T in range 0.05 to 1 sec.'
    TITLE_MEDIUM = 'BB ASD<sub>g</sub>(2,T,τ) for T in range 1 to 100 sec.'
    FILENAME_SHORT = 'BB ASD SHORT'
    FILENAME_MEDIUM = 'BB ASD MEDIUM'
    TAU_SHORT = 0.05
    TAU_MEDIUM = 1.0
    CONFIG_SHORT = (TAU_SHORT, TAU_SHORT, 0.05, 1.0)
    CONFIG_MEDIUM = (TAU_SHORT, TAU_MEDIUM, 1.0, 100.0)

    def __init__(self, fileName = None, startTime = datetime.now()):
        self.fileName = None
        self.tsAPI = TimeSeriesAPI()
        self.plotAPI = PlotAPI()
        if fileName:
            self.loadFile(fileName, startTime)            

    def loadFile(self, fileName, startTime = datetime.now()):
        self.fileName = fileName
        
        self.path, _ = os.path.split(fileName)

        self.outputNames = []

        self.dataSeries = [
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            []
        ]
        self.timeSeries = []
        self.timeSeriesMedium = []

        with open(fileName) as file:
            reader = csv.reader(file, delimiter = ',')
            for row in reader:
                try:
                    for i in range(8):
                        self.dataSeries[i].append(float(row[i]))                        
                except:
                    self.outputNames = [name.strip() for name in row]

        # scale from V to mW and divide by input power:
        for i in range(8):
            self.timeSeries.append(TimeSeries(
                dataSeries = self.dataSeries[i], 
                tau0Seconds = self.TAU_SHORT, 
                startTime = startTime, 
                dataUnits = Units.DELTA_GAIN)
            )
            # boxcar average:
            self.timeSeriesMedium.append(TimeSeries(
                dataSeries = getAveragesArray(self.dataSeries[i], self.TAU_MEDIUM // self.TAU_SHORT + 1), 
                tau0Seconds = self.TAU_MEDIUM, 
                startTime = startTime, 
                dataUnits = Units.DELTA_GAIN)
            )

        plotEls_SHORT = {
            PlotEl.SPEC_LINE1: SpecLines.IFP_GAIN_STABILITY_SHORT,
            PlotEl.XRANGE_PLOT: SpecLines.XRANGE_PLOT_IFP_GAIN_SHORT,            
            PlotEl.Y_AXIS_LABEL: Units.ADEV_IFP_05.value,
            PlotEl.Y_LINEAR: True,
            PlotEl.YUNITS: Units.DELTA_GAIN.value,
            PlotEl.XRANGE_WINDOW: "0.1,1",
            PlotEl.YRANGE_WINDOW: "8e-5,2.7e-4"
        }
        plotEls_MEDIUM = {
            PlotEl.SPEC_LINE1: SpecLines.IFP_GAIN_STABILITY_MEDIUM,
            PlotEl.XRANGE_PLOT: SpecLines.XRANGE_PLOT_IFP_GAIN_MEDIUM,
            PlotEl.Y_AXIS_LABEL: Units.ADEV_IFP_1.value,
            PlotEl.Y_LINEAR: True,
            PlotEl.YUNITS: Units.DELTA_GAIN.value,
            PlotEl.XRANGE_WINDOW: "1,100",
            PlotEl.YRANGE_WINDOW: "0.5e-5,6.5e-4"
        }
        dataSources = {
            DataSource.DATA_KIND: DataKind.GAIN.value,
            DataSource.UNITS: Units.DELTA_GAIN.value
        }

        for i in range(8):            
            outputName = f"{self.outputNames[i]}_{self.TITLE_SHORT}"
            fileName = f"{self.outputNames[i]}_{self.FILENAME_SHORT}"
            print(outputName)
            dataSources[DataSource.DATA_SOURCE] = outputName
            plotEls_SHORT[PlotEl.TITLE] = outputName
            self.plotAPI.plotAmplitudeStability(self.timeSeries[i], dataSources, plotEls_SHORT, outputName = os.path.join(self.path, fileName + ".png"))

            taus, adev, aderr = AllanDev(self.CONFIG_SHORT, self.timeSeries[i].dataSeries)
        
            outputName = f"{self.outputNames[i]}_{self.TITLE_MEDIUM}"
            fileName = f"{self.outputNames[i]}_{self.FILENAME_MEDIUM}"
            print(outputName)
            dataSources[DataSource.DATA_SOURCE] = outputName
            plotEls_MEDIUM[PlotEl.TITLE] = outputName
            self.plotAPI.plotAmplitudeStability(self.timeSeriesMedium[i], dataSources, plotEls_MEDIUM, outputName = os.path.join(self.path, fileName + ".png"))

            taus, adev, aderr = AllanDev(self.CONFIG_MEDIUM, self.timeSeries[i].dataSeries)
       
        print("done.")


obj = BackEndIFProcessor()
obj.loadFile(inputFile, startTime)
pass