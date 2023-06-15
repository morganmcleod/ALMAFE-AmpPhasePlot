import os
from AmpPhaseDataLib.Constants import DataSource, PlotEl, SpecLines
from AmpPhaseDataLib.LegacyImport import importTimeSeriesFETMSAmp
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

myPath = r'L:\2023Band2\Amplitude Stability'
band = 2
serialNum = 'CCA2-14'
systemName = 'NA FETMS'
dataSource = "FE06"
title = f"Band {band} amplitude stability"
show = True        # set to True to show plots interactively in the browser

try:
    # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    (_, _, filenames) = next(os.walk(myPath))
except StopIteration:
    print(f"No files found path {myPath}")
    exit()

for name in filenames:
    (base, ext) = os.path.splitext(name)
    if ext.lower() == '.txt' and '__meas' not in base:
        print(name)
        
        timePlotEls = {
            PlotEl.TITLE : title
        }
        allanPlotEls = { 
            PlotEl.TITLE : title,
            PlotEl.SPEC_LINE1 : SpecLines.FE_AMP_STABILITY1, 
            PlotEl.SPEC_LINE2 : SpecLines.FE_AMP_STABILITY2
        }
        
        measFile = base + 'meas' + ext
        tsId = importTimeSeriesFETMSAmp(myPath + '/' + name, myPath + '/' + measFile)
        if tsId:
            tsa.setDataSource(tsId, DataSource.TEST_SYSTEM, systemName)
            tsa.setDataSource(tsId, DataSource.SYSTEM, dataSource)
            tsa.setDataSource(tsId, DataSource.SERIALNUM, serialNum)
            plt.plotTimeSeries(tsId, timePlotEls, outputName = myPath + "/" + base + ".png", show = show)
            plt.plotAmplitudeStability([tsId], plotElements = allanPlotEls, outputName = myPath + "/" + base + "stability.png", show = show)    
