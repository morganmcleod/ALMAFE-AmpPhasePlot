import os
os.chdir('L:\python\ALMAFE-AmpPhasePlot')

from AmpPhaseDataLib.Constants import DataSource, Units, PlotEl, SpecLines
from AmpPhaseDataLib.LegacyImport import importTimeSeriesFETMSAmp
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

myPath = r'\\cvfiler\cv-cdl-pub\Andrew Smith\if processor V3\V3 test results\IF processor PAI 4-22\Amplitude stability\data files\data 6-14-22'

# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
(_, _, filenames) = next(os.walk(myPath))

notes = 'integration test'
dataSource = "Band 2 prototype cartridge"
timePlotEls = { 
    PlotEl.TITLE : "IF Processor V3 Amplitude Stability"
}
spectrumPlotEls = { 
    PlotEl.TITLE : "IF Processor V3 Amplitude Stability", 
    PlotEl.SPEC_LINE1 : SpecLines.FE_AMP_STABILITY1, 
    PlotEl.SPEC_LINE2 : SpecLines.FE_AMP_STABILITY2
}
 
for name in filenames:
    (base, ext) = os.path.splitext(name)
    if ext.lower() == '.txt' and '__meas' not in base:
        measFile = base + 'meas' + ext
        tsId = importTimeSeriesFETMSAmp(myPath + '/' + name, myPath + '/' + measFile, notes = notes, systemName = 'NRAO Test Cryostat')
        tsa.setDataSource(tsId, DataSource.TEST_SYSTEM, dataSource)
        plt.plotTimeSeries(tsId, timePlotEls, outputName = myPath + "/" + str(tsId) + ".png", show = True)
        plt.plotAmplitudeStability([tsId], plotElements = spectrumPlotEls, outputName = myPath + "/" + str(tsId) + "-stability.png", show = True)    
