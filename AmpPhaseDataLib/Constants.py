'''
Constants used in the AmpPhaseDataLib API
'''
from enum import Enum

class PlotKind(Enum):
    '''
    Known plot kinds and wildcards
    '''
    NONE = 0
    TIME_SERIES = 1
    ALLAN_VAR = 2
    ALLAN_DEV = 3
    PWR_SPECTRUM = 4
    ALL = 99
    
class DataStatus(Enum):
    '''
    Data status flags for categorizing Time Series and Result
    '''
    UNKNOWN = 'unknown'
    ERROR = 'error'
    TO_DELETE = 'toDelete'
    TO_RETAIN = 'toRetain'
    MEET_SPEC = 'meetSpec'
    FAIL_SPEC = 'failSpec'
    @classmethod
    def exists(cls, value):
        return value in cls.__members__
    
class DataSource(Enum):
    '''
    Data source flags for annotating Time Series and Result
    '''
    CONFIG_ID = 'configId'
    DATA_SOURCE = 'dataSource'
    SUBSYSTEM = 'subsystem'
    OPERATOR = 'operator'
    MEAS_SW_VERSION = 'measSwVersion'
    @classmethod
    def exists(cls, value):
        return value in cls.__members__

class PlotElement(Enum):
    '''
    Superset of DataSource: plot elements to be used when rendering
    '''
    CONFIG_ID = 'configId'
    DATA_SOURCE = 'dataSource'
    SUBSYSTEM = 'subsystem'
    MEAS_SW_VERSION = 'measSwVersion'
    TITLE = 'title'
    X_AXIS_LABEL = 'xAxisLabel'
    Y_AXIS_LABEL = 'yAxisLabel'
    Y2_AXIS_LABEL = 'y2AxisLabel'
    @classmethod
    def exists(cls, value):
        return value in cls.__members__
