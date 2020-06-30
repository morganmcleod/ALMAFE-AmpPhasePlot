'''
'''
from AmpPhaseDataLib import TimeSeriesAPI
import plotly.graph_objects as go

class PlotApi(object):
    '''
    classdocs
    '''

    def __init__(self, timeSeriesAPI = None):
        '''
        Constructor
        '''
        self.timeSeriesAPI = timeSeriesAPI if timeSeriesAPI else TimeSeriesAPI.TimeSeriesAPI()
        
    def plotTimeSeries(self, timeSeriesId):
        ts = self.timeSeriesAPI
        if not ts.retrieveTimeSeries(timeSeriesId):
            return None
    
        fig = go.Figure(go.Scatter(x = ts.timeStamps, y = ts.dataSeries, mode = 'lines'))
        fig.show()
    