import os
os.chdir('L:\python\ALMAFE-AmpPhasePlot')

from AmpPhaseDataLib.Constants import DataSource, Units, PlotEl, SpecLines
from AmpPhaseDataLib.LegacyImport import importTimeSeriesFETMSPhase
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

myPath = r'\\APROPOS\Workspace-L\data\FE100\Band2\phase_stability\2022-06-17'

# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
(_, _, filenames) = next(os.walk(myPath))
 
for name in filenames:
    (base, ext) = os.path.splitext(name)
    if ext.lower() == '.txt' and '__meas' not in base:
        print(name)
        
        notes = 'Band 2 phase stability'
        dataSource = 'FE100 Band 2 prototype cartridge'
        
        timePlotEls = { 
            PlotEl.TITLE : "Band 2 phase stability"
        }
        spectrumPlotEls = { 
            PlotEl.TITLE : "band 2 phase stability", 
            PlotEl.SPEC_LINE1 : SpecLines.FE_PHASE_STABILITY
        }
        
        measFile = base + 'meas' + ext
        tsId = importTimeSeriesFETMSPhase(myPath + '/' + name, myPath + '/' + measFile, notes = notes, systemName = 'NRAO FETMS')
        if tsId:
            tsa.setDataSource(tsId, DataSource.TEST_SYSTEM, dataSource)
            plt.plotTimeSeries(tsId, timePlotEls, outputName = myPath + "/" + str(tsId) + ".png", show = True)
            plt.plotPhaseStability([tsId], plotElements = spectrumPlotEls, outputName = myPath + "/" + str(tsId) + "-stability.png", show = True)    
