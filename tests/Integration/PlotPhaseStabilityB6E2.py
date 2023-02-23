import os
from AmpPhaseDataLib.Constants import DataSource, PlotEl, SpecLines, DataKind
from AmpPhaseDataLib.LegacyImport import importTimeSeriesBand6CTS_experimental2
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

myPath = r'L:\Python\ALMAFE-AmpPhasePlot\SampleData-local\Band6 CTS\CTS2-2023-02-17'
band = 6
systemName = 'CTS2'
title = f"Band {band} phase stability 231 GHz"

# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
(_, _, filenames) = next(os.walk(myPath))

for name in filenames:
    (base, ext) = os.path.splitext(name)
    if ext.lower() == '.csv':
        print(name)  

        timePlotEls = { 
            PlotEl.TITLE : title
        }
        spectrumPlotEls = { 
            PlotEl.TITLE : title, 
            PlotEl.SPEC_LINE1 : SpecLines.BAND6_PHASE_STABILITY1,
            PlotEl.SPEC_LINE2 : SpecLines.BAND6_PHASE_STABILITY2,
            PlotEl.SPEC2_NAME : "CTS relaxed spec"
        }
        
        tsId = importTimeSeriesBand6CTS_experimental2(myPath + "/" + name, dataKind = (DataKind.PHASE).value)
        if tsId:
            tsa.setDataSource(tsId, DataSource.TEST_SYSTEM, systemName)
            tsa.setDataSource(tsId, DataSource.RF_GHZ, None)    # we want to plot degrees, not fS
            plt.plotTimeSeries(tsId, timePlotEls, outputName = myPath + "/" + str(tsId) + ".png", show = True)
            plt.plotPhaseStability([tsId], plotElements = spectrumPlotEls, outputName = myPath + "/" + str(tsId) + "-stability.png", show = True)