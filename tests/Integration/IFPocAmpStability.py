from AmpPhaseDataLib.Constants import DataSource, Units, PlotEl, SpecLines
from AmpPhaseDataLib.LegacyImport import importTimeSeriesE4418B
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhasePlotLib import PlotAPI
import os

tsa = TimeSeriesAPI.TimeSeriesAPI()
plt = PlotAPI.PlotAPI()

os.chdir('L:\python\ALMAFE-AmpPhasePlot')

ds0 = importTimeSeriesE4418B('./SampleData-local/IFPROCV3/2022-04-29/IFPv3-IF0.txt', notes = 'bench test', tau0Seconds = 0.05, importUnits = Units.WATTS)
ds1 = importTimeSeriesE4418B('./SampleData-local/IFPROCV3/2022-04-29/IFPv3-IF1.txt', notes = 'bench test', tau0Seconds = 0.05, importUnits = Units.WATTS)
ds2 = importTimeSeriesE4418B('./SampleData-local/IFPROCV3/2022-04-29/IFPv3-IF2.txt', notes = 'bench test', tau0Seconds = 0.05, importUnits = Units.WATTS)
ds3 = importTimeSeriesE4418B('./SampleData-local/IFPROCV3/2022-04-29/IFPv3-IF3.txt', notes = 'bench test', tau0Seconds = 0.05, importUnits = Units.WATTS)

tsa.setDataSource(ds0, DataSource.TEST_SYSTEM, "Andrew Smith bench")
tsa.setDataSource(ds1, DataSource.TEST_SYSTEM, "Andrew Smith bench")
tsa.setDataSource(ds2, DataSource.TEST_SYSTEM, "Andrew Smith bench")
tsa.setDataSource(ds3, DataSource.TEST_SYSTEM, "Andrew Smith bench")

tsa.setDataSource(ds0, DataSource.SUBSYSTEM, "IF0")
tsa.setDataSource(ds1, DataSource.SUBSYSTEM, "IF1")
tsa.setDataSource(ds2, DataSource.SUBSYSTEM, "IF2")
tsa.setDataSource(ds3, DataSource.SUBSYSTEM, "IF3")

plotEls = { PlotEl.TITLE : "IF Processor V3 Amplitude Stability", 
            PlotEl.SPEC_LINE1 : SpecLines.IFPROC_AMP_STABILITY1, 
            PlotEl.SPEC_LINE2 : SpecLines.IFPROC_AMP_STABILITY2
          } 

plt.plotAmplitudeStability([ds0,ds1], plotElements = plotEls, outputName = '.\\SampleData-local\\IFPROCV3\\2022-04-29\\StabilityIF0IF1.png', show = True)    
