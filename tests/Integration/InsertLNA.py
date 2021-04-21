from AmpPhaseDataLib.Constants import DataSource, Units, DataKind, PlotEl, SpecLines
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
import json
import time
import os

os.chdir('L:\python\ALMAFE-AmpPhasePlot')

def insert(howMany):
    tsAPI = TimeSeriesAPI.TimeSeriesAPI()
    
    with open('./SampleData-local/CBTS/lna.json', 'r') as f:
        lna = json.load(f) 
    
    start = time.time()
    for i in range(howMany):
        tsId = tsAPI.insertTimeSeries(lna['voltage'], tau0Seconds = lna['tau0Seconds'], startTime = lna['timestamp'])
        tsAPI.setDataSource(tsId, DataSource.UNITS, Units.VOLTS.value)
        tsAPI.setDataSource(tsId, DataSource.DATA_KIND, DataKind.VOLTAGE.value)
        print('.', end = '')
    end = time.time()
   
    print("last tsId:{} tAvg:{} sec".format(tsId, (end - start) / howMany))
    
def plot(tsId):
    pltAPI = PlotAPI.PlotAPI()
    pltAPI.plotSpectrum(tsId, show= True, plotElements={PlotEl.SPEC_LINE1: SpecLines.BIAS_LNA_VOLT_ASD_1HZ, 
                                                        PlotEl.RMS_SPEC: SpecLines.BIAS_LNA_VOLT_RMS})         