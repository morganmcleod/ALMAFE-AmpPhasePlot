import os
os.chdir('L:\python\ALMAFE-AmpPhasePlot')

from AmpPhaseDataLib.Constants import DataSource, Units, PlotEl, SpecLines
from AmpPhaseDataLib.LegacyImport import importTimeSeriesE4418B, importTimeSeriesFETMSAmp
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

myPath = r'\\cvfiler\ALMA-NA-FEIC\IF Processor\IFP v3 first unit tests\IF processor PAI 4-22\Amplitude stability\data6-23-22\ConnectedToB2'

# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
(_, _, filenames) = next(os.walk(myPath))
 
for name in filenames:
    (base, ext) = os.path.splitext(name)
    if ext.lower() == '.txt' and '__meas' not in base:

        dataSource = "IF Processor V3 SN01"
        tau0Seconds = 0.05
        timePlotEls = { 
            PlotEl.TITLE : "IF Processor V3 Amplitude Stability"
        }
        spectrumPlotEls = { 
            PlotEl.TITLE : "IF Processor V3 Amplitude Stability", 
            PlotEl.SPEC_LINE1 : SpecLines.IFPROC_AMP_STABILITY1, 
            PlotEl.SPEC_LINE2 : SpecLines.IFPROC_AMP_STABILITY2
        }
        
        measFile = base + 'meas' + ext
        #tsId = importTimeSeriesE4418B(myPath + "/" + name, notes, tau0Seconds = tau0Seconds, importUnits = Units.WATTS)
        tsId = importTimeSeriesFETMSAmp(myPath + '/' + name, myPath + '/' + measFile)
        if tsId:
            tsa.setDataSource(tsId, DataSource.TEST_SYSTEM, dataSource)
            plt.plotTimeSeries(tsId, timePlotEls, outputName = myPath + "/" + str(tsId) + ".png", show = True)
            plt.plotAmplitudeStability([tsId], plotElements = spectrumPlotEls, outputName = myPath + "/" + str(tsId) + "-stability.png", show = True)    
