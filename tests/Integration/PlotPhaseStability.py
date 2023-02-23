import os
from AmpPhaseDataLib.Constants import DataSource, PlotEl, SpecLines
from AmpPhaseDataLib.LegacyImport import importTimeSeriesFETMSPhase
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

myPath = r'L:\LV2021Requal\NA-FETMS\phase_stability\B2\morning'
band = 2
systemName = 'NA FETMS'
dataSource = "FE34 LV2021 validation"
title = f"Band {band} phase stability"

# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
(_, _, filenames) = next(os.walk(myPath))
 
for name in filenames:
    (base, ext) = os.path.splitext(name)
    if ext.lower() == '.txt' and '__meas' not in base:
        print(name)
        
        timePlotEls = { 
            PlotEl.TITLE : title
        }
        spectrumPlotEls = { 
            PlotEl.TITLE : title, 
            PlotEl.SPEC_LINE1 : SpecLines.FE_PHASE_STABILITY
        }
        
        measFile = base + 'meas' + ext
        tsId = importTimeSeriesFETMSPhase(myPath + '/' + name, myPath + '/' + measFile, systemName = systemName)
        if tsId:
            tsa.setDataSource(tsId, DataSource.TEST_SYSTEM, systemName)
            tsa.setDataSource(tsId, DataSource.SYSTEM, dataSource)
            plt.plotTimeSeries(tsId, timePlotEls, outputName = myPath + "/" + str(tsId) + ".png", show = True)
            try:
                plt.plotPhaseStability([tsId], plotElements = spectrumPlotEls, outputName = myPath + "/" + str(tsId) + "-stability.png", show = True)    
            except:
                pass
