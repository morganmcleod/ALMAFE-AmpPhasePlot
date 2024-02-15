from AmpPhaseDataLib.Constants import *
from AmpPhaseDataLib.TimeSeries import TimeSeries
from AmpPhasePlotLib.PlotAPI import PlotAPI
import numpy as np
from datetime import datetime
import os

def makeAmplitudeStabilitySamples():
    
    outputPath = './SampleData/t_AmplitudeStability'

    plotAPI = PlotAPI()

    now = datetime.now()
    
    duration = 1000  # seconds
    interval = 0.05 # seconds
    samples = int(duration / interval)

    dataSources = {
        DataSource.DATA_KIND: DataKind.VOLTAGE.value,
        DataSource.UNITS: Units.VOLTS.value
    }
    rng = np.random.default_rng()

    # unit gaussian distribution:    
    plotEls = {
        PlotEl.XRANGE_PLOT: "0.01, 100",
        PlotEl.TITLE: "normal distrubution stddev=1"
    }
    ts = TimeSeries(dataSeries = rng.standard_normal(samples).tolist(), tau0Seconds = interval, startTime = now, dataUnits = Units.VOLTS)
    plotAPI.plotAmplitudeStability(ts, dataSources = dataSources, plotElements = plotEls, outputName = os.path.join(outputPath, plotEls[PlotEl.TITLE] + '.png'))

    # gaussion std=5:
    plotEls[PlotEl.TITLE] = "normal distrubution stddev=5"
    ts = TimeSeries(dataSeries = rng.normal(size=samples, scale=5.0).tolist(), tau0Seconds = interval, startTime = now, dataUnits = Units.VOLTS)
    plotAPI.plotAmplitudeStability(ts, dataSources = dataSources, plotElements = plotEls, outputName = os.path.join(outputPath, plotEls[PlotEl.TITLE] + '.png'))



if __name__ == '__main__':
    makeAmplitudeStabilitySamples()
