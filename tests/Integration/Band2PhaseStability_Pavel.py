import os
os.chdir('L:\python\ALMAFE-AmpPhasePlot')
import csv
import math
import statistics
import numpy as np

from AmpPhaseDataLib.Constants import DataKind, DataSource, PlotEl, SpecLines, Units
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
from Calculate.Common import getAveragesArray
tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

myPath = r'L:\Python\ALMAFE-AmpPhasePlot\SampleData-local\ESO_CCA2-98'
name = '220524-S2C3W98-Flo83.00-Frf95.00-stab-pol0-sb2.dat'
file = os.path.join(myPath, name)
 
(base, ext) = os.path.splitext(name)
print(name)
    
notes = 'Band 2 phase stability'
dataSource = 'ESO CCA2-03, WCA2-98'
    
timePlotEls = { 
    PlotEl.YRANGE_WINDOW : "-5.0, +5.0",
    PlotEl.XUNITS : (Units.MINUTES).value
}
allanPlotEls = { 
    PlotEl.SPEC_LINE1 : "0, 7, 500, 7",
    PlotEl.X_LINEAR : True,
    PlotEl.Y_LINEAR : True,
    PlotEl.XRANGE_PLOT : "10, 500",
    PlotEl.YRANGE_WINDOW : "0, 22"
}

with open(file, 'r') as f:

    timeArray = []
    realArray = []
    imagArray = []
    
    N = 0
    ts0 = None

    reader = csv.reader(f, delimiter=" ")
    for line in reader:
        if line[0] == "time":
            timeArray.append(float(line[1]))
        else:
            N += 1
            realArray.append(float(line[0]))
            imagArray.append(float(line[1]))

    # anayze timestamps - there are 20 readings per timestamp:
    tau = statistics.mean(np.diff(timeArray)) / 20
    
    # account for 20 readings after the last timestamp:
    duration = timeArray[-1] - timeArray[0] + (20 * tau)
    
    # compute S21:
    ampArray = []
    phiArray = []
    for real, imag in zip(realArray, imagArray):
        ampArray.append(math.sqrt(real * real + imag * imag))
        phiArray.append(math.atan(imag / real) * (180 / math.pi))

    # 1-second averaging:
    K = int(1 / tau)
    ampArray = getAveragesArray(ampArray, K)
    phiArray = getAveragesArray(phiArray, K)

    phi0 = phiArray[0]
    phiArray = [phi - phi0 for phi in phiArray]    
        
    print('T = {} s, duration = {} s'.format(tau, duration))
        
    tsId = tsa.insertTimeSeries(phiArray, tau0Seconds = K * tau, dataUnits = Units.DEG)
    
    if tsId:
        tsa.setDataSource(tsId, DataSource.TEST_SYSTEM, dataSource)
        tsa.setDataSource(tsId, DataSource.DATA_KIND, (DataKind.PHASE).value)
        tsa.setDataSource(tsId, DataSource.RF_GHZ, 95.0)
        plt.plotTimeSeries(tsId, timePlotEls, outputName = myPath + "/" + str(tsId) + ".png", show = True)
        plt.plotPhaseStability([tsId], plotElements = allanPlotEls, outputName = myPath + "/" + str(tsId) + "-stability.png", show = True)    
