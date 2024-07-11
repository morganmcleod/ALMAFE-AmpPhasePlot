import os
os.chdir('L:\python\ALMAFE-AmpPhasePlot')

from AmpPhaseDataLib.Constants import DataSource, Units, PlotEl, SpecLines
from AmpPhaseDataLib.LegacyImport import importTimeSeriesE4418B, importTimeSeriesFETMSAmp
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

myPath = r'L:\Python\ALMAFE-AmpPhasePlot\SampleData-local\MTS1 GainCompression\AMC+PA'

# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
(_, _, filenames) = next(os.walk(myPath))
 
for name in filenames:
    (base, ext) = os.path.splitext(name)
    if ext.lower() == '.txt' and '__meas' not in base:

        dataSource = "Band6 test source F06-4"
        tau0Seconds = 0.05
        timePlotEls = { 
            PlotEl.TITLE : dataSource,
            PlotEl.XUNITS : (Units.MINUTES).value
        }
        spectrumPlotEls = { 
            PlotEl.TITLE : dataSource, 
            PlotEl.SPEC_LINE1 : SpecLines.WCA_AMP_STABILITY1,
            PlotEl.SPEC_LINE2 : SpecLines.WCA_AMP_STABILITY2
        }
        
        measFile = base + 'meas' + ext
        tsId = importTimeSeriesE4418B(myPath + "/" + name, tau0Seconds = tau0Seconds, importUnits = Units.WATTS)
        if tsId:
            tsa.setDataSource(tsId, DataSource.TEST_SYSTEM, dataSource)
            plt.plotTimeSeries(tsId, plotElements = timePlotEls, outputName = myPath + "/" + base + ".png", show = True)
            plt.plotAmplitudeStability([tsId], plotElements = spectrumPlotEls, outputName = myPath + "/" + base + "-stability.png", show = True)    
