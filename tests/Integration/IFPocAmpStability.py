import os
os.chdir('L:\python\ALMAFE-AmpPhasePlot')

from AmpPhaseDataLib.Constants import DataSource, Units, PlotEl, SpecLines
from AmpPhaseDataLib.LegacyImport import importTimeSeriesE4418B
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

myPath = './SampleData-local/IFPROCV3/2022-05-06'

# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
(_, _, filenames) = next(os.walk(myPath))

notes = notes = 'bench test'
dataSource = "Andrew Smith bench"
tau0Seconds = 0.05
timePlotEls = { 
    PlotEl.TITLE : "IF Processor V3 Amplitude Stability"
}
spectrumPlotEls = { 
    PlotEl.TITLE : "IF Processor V3 Amplitude Stability", 
    PlotEl.SPEC_LINE1 : SpecLines.IFPROC_AMP_STABILITY1, 
    PlotEl.SPEC_LINE2 : SpecLines.IFPROC_AMP_STABILITY2
}
 
tsIds = []
for name in filenames:
    try:
        tsId = importTimeSeriesE4418B(myPath + "/" + name, notes, tau0Seconds = tau0Seconds, importUnits = Units.WATTS)
        tsa.setDataSource(tsId, DataSource.TEST_SYSTEM, dataSource)
        plt.plotTimeSeries(tsId, timePlotEls, outputName = myPath + "/" + str(tsId) + ".png", show = True)
        tsIds.append(tsId)
    except:
        pass
         
plt.plotAmplitudeStability(tsIds, plotElements = spectrumPlotEls, outputName = myPath + "/stability.png", show = True)    
