import os
os.chdir('L:\python\ALMAFE-AmpPhasePlot')

from AmpPhaseDataLib.Constants import DataSource, PlotEl, SpecLines
from AmpPhaseDataLib.LegacyImport import importTimeSeriesWCABench
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

myPath = r'L:\Python\ALMAFE-AmpPhasePlot\SampleData-local\WCA9-SN02\2023-10-16'

show = True        # set to True to show plots interactively in the browser

# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
(_, _, filenames) = next(os.walk(myPath))
 
for name in filenames:
    (base, ext) = os.path.splitext(name)
    if ext.lower() == '.csv':
        print(name)
        
        timePlotEls = {
        }
        allanPlotEls = { 
            PlotEl.SPEC_LINE1 : SpecLines.WCA_AMP_STABILITY1, 
            PlotEl.SPEC_LINE2 : SpecLines.WCA_AMP_STABILITY2
        }
        
        measFile = base + 'meas' + ext
        tsId = importTimeSeriesWCABench(myPath + '/' + name, myPath + '/' + measFile)
        if tsId:
            pol = "Pol0" if "pol0" in name else "Pol1"
            tsa.setDataSource(tsId, DataSource.TEST_SYSTEM, "OSF FE Lab WCA test bench")
            tsa.setDataSource(tsId, DataSource.SYSTEM, f"WCA9-02 {pol}")
            plt.plotTimeSeries(tsId, timePlotEls, outputName = myPath + "/" + base + ".png", show = show)
            plt.plotAmplitudeStability([tsId], plotElements = allanPlotEls, outputName = myPath + "/" + base + "stability.png", show = show)    
