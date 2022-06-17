import os
os.chdir('L:\python\ALMAFE-AmpPhasePlot')

from AmpPhaseDataLib.Constants import DataSource, Units, PlotEl, SpecLines
from AmpPhaseDataLib.LegacyImport import importTimeSeriesFETMSAmp
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

myPath = r'\\cvfiler\ALMA-NA-FEIC\IF Processor\IFP v3 first unit tests\IF processor PAI 4-22\Amplitude stability\data6-22-22'


# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
(_, _, filenames) = next(os.walk(myPath))
 
for name in filenames:
    (base, ext) = os.path.splitext(name)
    if ext.lower() == '.txt' and '__meas' not in base:
        print(name)
        
        notes = 'Band 2 amplitude stability'
        dataSource = 'FE100 Band 2 prototype'
        
        timePlotEls = { 
            PlotEl.TITLE : "Band 2 Amplitude stability time series"
        }
        spectrumPlotEls = { 
            PlotEl.TITLE : "Band 2 Amplitude stability", 
            PlotEl.SPEC_LINE1 : SpecLines.FE_AMP_STABILITY1, 
            PlotEl.SPEC_LINE2 : SpecLines.FE_AMP_STABILITY2
        }
        
        measFile = base + 'meas' + ext
        tsId = importTimeSeriesFETMSAmp(myPath + '/' + name, myPath + '/' + measFile, notes = notes, systemName = 'NRAO FETMS')
        if tsId:
            tsa.setDataSource(tsId, DataSource.TEST_SYSTEM, dataSource)
            plt.plotTimeSeries(tsId, timePlotEls, outputName = myPath + "/" + str(tsId) + ".png", show = True)
            plt.plotAmplitudeStability([tsId], plotElements = spectrumPlotEls, outputName = myPath + "/" + str(tsId) + "-stability.png", show = True)    
