import os
os.chdir('L:\python\ALMAFE-AmpPhasePlot')

from AmpPhaseDataLib.Constants import DataSource, PlotEl, SpecLines
from AmpPhaseDataLib.LegacyImport import importTimeSeriesFETMSAmp
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

myPath = r'\\cvfiler\ALMA-NA-FEIC\Band2_ESO_2022\amp_stability'

show = False        # set to True to show plots interactively in the browser

# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
(_, _, filenames) = next(os.walk(myPath))
 
for name in filenames:
    (base, ext) = os.path.splitext(name)
    if ext.lower() == '.txt' and '__meas' not in base:
        print(name)
        
        timePlotEls = {
        }
        allanPlotEls = { 
            PlotEl.SPEC_LINE1 : SpecLines.FE_AMP_STABILITY1, 
            PlotEl.SPEC_LINE2 : SpecLines.FE_AMP_STABILITY2
        }
        
        measFile = base + 'meas' + ext
        tsId = importTimeSeriesFETMSAmp(myPath + '/' + name, myPath + '/' + measFile)
        if tsId:
            tsa.setDataSource(tsId, DataSource.TEST_SYSTEM, "NRAO FETMS")
            tsa.setDataSource(tsId, DataSource.SYSTEM, "CCA2-03, WCA2-98")
            plt.plotTimeSeries(tsId, timePlotEls, outputName = myPath + "/" + base + ".png", show = show)
            plt.plotAmplitudeStability([tsId], plotElements = allanPlotEls, outputName = myPath + "/" + base + "stability.png", show = show)    
