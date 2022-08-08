import os
import csv
from copy import copy
from datetime import datetime
os.chdir('L:\python\ALMAFE-AmpPhasePlot')
from AmpPhaseDataLib.TimeSeriesAPI import TimeSeriesAPI
from AmpPhasePlotLib.PlotAPI import PlotAPI
from AmpPhaseDataLib.Constants import DataKind, DataSource, DataStatus, Units, PlotEl, SpecLines
tsa = TimeSeriesAPI()
plt = PlotAPI()

def makePlots(title, legends, dataSeries, tau, myPath):
    tsIds = []
    for col in range(8):
        tsIds.append(tsa.insertTimeSeries(dataSeries[col], startTime = datetime.now(), tau0Seconds = tau))
        tsa.setDataSource(tsIds[col], DataSource.DATA_KIND, (DataKind.VOLTAGE).value)
        tsa.setDataSource(tsIds[col], DataSource.SYSTEM, title)
        tsa.setDataSource(tsIds[col], DataSource.SUBSYSTEM, legends[col])
        tsa.setDataSource(tsIds[col], DataSource.UNITS, (Units.VOLTS).value)
        timePlotEls = { 
            #PlotEl.XUNITS : (Units.SECONDS).value
        }
        outputName = os.path.join(myPath, '{}_timeseries{}.png'.format(title, col))
        plt.plotTimeSeries(tsIds[col], timePlotEls, outputName=outputName, show=True)
    outputName = os.path.join(myPath, '{}_stability.png'.format(title))
    plt.plotAmplitudeStability(tsIds, outputName=outputName, show=True)
    
myPath = r'L:\Python\ALMAFE-AmpPhasePlot\SampleData-local\BE-IFP'
name = 'IFPT - Allan_Std_Dev 166 20220616T171753.csv'
(base, ext) = os.path.splitext(name)
title = None
tau = None
valid = False
startRow = None

legends = ['LSB A', 'LSB B', 'LSB C', 'LSB D', 'USB A', 'USB B', 'USB C', 'USB D']
dataSeries = [[],[],[],[],[],[],[],[]]
with open(os.path.join(myPath, name)) as f:
    reader = csv.reader(f, delimiter=",")
    row = 0
    startRow = None                
    for line in reader:
        row += 1
        # skip header rows
        if row >= 14:
            plotNow = False
            if line[0][:2] == 'BB' or line[0][:2] == 'SB':
                if valid:
                    print('data starting at row {} tau={}'.format(startRow, tau))
                    startRow = None
                    makePlots(title, legends, dataSeries, tau, myPath)
                
                title = None
                tau = None
                valid = False
                dataSeries = [[],[],[],[],[],[],[],[]]
                startRow = None    
                
                title = line[0]
                print(row, title)
                if 't=1' in title or 't=01' in title or 'Time Data' in title:
                    tau = 1.0
                elif 't=0.05' in title:
                    tau = 0.05

            elif line[0] == 'END':
                if valid:
                    print('data starting at row {} tau={}'.format(startRow, tau))
                    makePlots(title, legends, dataSeries, tau, myPath)
            
            elif line[0][0].isnumeric():
                if not startRow:
                    startRow = row
                for col in range(8):
                    val = float(line[col])
                    if not valid and val !=0:
                        valid = True
                    dataSeries[col].append(val)
        