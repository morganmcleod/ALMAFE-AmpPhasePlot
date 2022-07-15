import os
os.chdir('L:\python\ALMAFE-AmpPhasePlot')

from AmpPhaseDataLib.Constants import DataSource, PlotEl, SpecLines
from AmpPhaseDataLib.LegacyImport import importTimeSeriesNSI2000Phase
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

myPath = r'C:\Users\mmcleod\Desktop\Transport\Band2\714'

filenames = ['90 GHz StabilityTest Jul 14, 2022 18.44.20.csv']

for name in filenames:
    (base, ext) = os.path.splitext(name)
    if ext.lower() == '.csv':
        print(name)
        
        notes = 'Band 2 phase stability'
        dataSource = 'FE-100 CCA2-3 WCA2-98'
        
        if '74' in name:
            rfGHz = 74.0
        elif '90' in name:
            rfGHz = 90.0
        else:
            rfGHz = None
        
        rfGHzStr = ' ' + str(rfGHz) + ' GHz' if rfGHz else ''
        
        timePlotEls = { 
            PlotEl.TITLE : notes + ': ' + dataSource + rfGHzStr
        }
        allanPlotEls = { 
            PlotEl.TITLE : notes + ': ' + dataSource + rfGHzStr, 
            PlotEl.SPEC_LINE1 : SpecLines.FE_PHASE_STABILITY
        }
        
        tsId = importTimeSeriesNSI2000Phase(myPath + '/' + name, notes = notes)
        if tsId:
            tsa.setDataSource(tsId, DataSource.TEST_SYSTEM, dataSource)
            if rfGHz:
                tsa.setDataSource(tsId, DataSource.RF_GHZ, rfGHz)
            plt.plotTimeSeries(tsId, timePlotEls, outputName = myPath + "/" + str(tsId) + ".png", show = True)
            plt.plotPhaseStability(tsId, allanPlotEls, outputName = myPath + "/" + str(tsId) + "-stability.png", show = True)    
