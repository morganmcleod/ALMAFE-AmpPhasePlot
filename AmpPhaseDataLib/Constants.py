'''
Constants used in these APIs:
When referring to metadata about a measurement or a plot, you must use these Enums or their str values.
Admittedly, a few other things are stashed here to avoid literals in the code.  
'''
from enum import Enum

#TODO: !!!***@*@**@*   the literals should be the same as the enums.   No reason to create a mapping here!s

class PlotKind(Enum):
    '''
    Known plot kinds and wildcards.
    For specifying what kind of plot this is or for finding a plot from a database.
    '''
    NONE = 0
    TIME_SERIES = 1
    AMP_STABILITY = 2
    PHASE_STABILITY = 3
    AMPLITUDE_SPECTRUM = 4  # ASD for linear volts, phase
    POWER_SPECTRUM = 5      # PSD for power, square-law detector volts
    ALL = 99

class EnumHelper(Enum):
    '''
    Add matching and conversion helpers to Enum.
    Used in sombunall classes below.
    '''
    @classmethod
    def exists(cls, value):
        '''
        True if the value str is a value in the Enum.
        :param cls:    derived from EnumHelper
        :param value:  str
        '''
        return value in cls.__members__
    
    @classmethod
    def fromStr(cls, value):
        '''
        Convert from str value to Enum value.  Doesn't catch exceptions.        
        :param cls:    derived from EnumHelper
        :param value:  str
        '''
        return cls(value)

class DataKind(EnumHelper):
    '''
    Known raw data series kinds.
    These refer to the underlying phenomena of the measurement system:
    The most peculiar case is POWER, normalll WATTS but could be a measured voltage from a square-law detector, 
      in which case the DataSource.UNITS would probably be Units.VOLTS or maybe Units.AMPLITUDE.
    '''
    AMPLITUDE   = "amplitude"   # unitless or unknown units. Treated as linear. 
    POWER       = "power"       # typically W or dBm but could be V of a square-law detector.
    PHASE       = "phase"       # linear degrees or radians.
    VOLTAGE     = "voltage"     # linear volts.

class DataStatus(EnumHelper):
    '''
    Data status flags for categorizing Time Series and Results    
    '''
    UNKNOWN     = 'unknown'     # setting any other tag will clear UNKNOWN
    ERROR       = 'error'       # an error occurred during the measurement
    TO_DELETE   = 'toDelete'    # setting TO_DELETE will clear TO_RETAIN
    TO_RETAIN   = 'toRetain'    # setting TO_RETAIN will clear TO_DELETE
    MEET_SPEC   = 'meetSpec'    # setting MEET_SPEC will clear FAIL_SPEC
    FAIL_SPEC   = 'failSpec'    # setting FAIL_SPEC will clear MEET_SPEC
    
class DataSource(EnumHelper):
    '''
    Data source flags for annotating Time Series and Results
    '''
    CONFIG_ID       = 'configId'    # of the device under test
    DATA_SOURCE     = 'dataSource'  # source data file on disk, if applicable.  Otherwise describe where this came from.
    DATA_KIND       = 'dataKind'    # of the primary data series. Values from DataKind enum.
    TEST_SYSTEM     = 'testSystem'  # name of measurement system or computer where the data was created.
    UNITS           = 'units'       # of the primary data series, like "dBm" or "deg".  Values from Units enum.
    T_UNITS         = 't_units'     # of the temperature data series, like "K".  Values from Units enum.
    LO_GHZ          = 'lo_GHz'      # the LO frequency in GHz
    RF_GHZ          = 'rf_GHz'      # if phase data, the RF in GHz
    TILT_ANGLE      = 'tiltAngle'   # tilt angle when measured
    SYSTEM          = 'system'      # like "FE-20, Band 6"
    SUBSYSTEM       = 'subsystem'   # like "pol0, USB"
    SERIALNUM       = 'serialNum'   # of a serialized part under test
    OPERATOR        = 'operator'    # name or initials
    NOTES           = 'notes'       # operator notes
    MEAS_SW_NAME    = 'measSwName'  # name of measurement software
    MEAS_SW_VERSION = 'measSwVer'   # version of measurement software

class PlotEl(EnumHelper):
    '''
    Plot elements to be used when rendering
    '''
    XUNITS          = 'xUnits'      # of the primary x axis, like "seconds"
    YUNITS          = 'yUnits'      # of the primary y axis, like "dBm"
    Y2UNITS         = 'y2Units'     # of secondary y axis, like "K"
    ERROR_BARS      = 'errorBars'   # show error bars?  like "1" or "0"
    TITLE           = 'title'       # plot title, overrides automatically generated
    X_AXIS_LABEL    = 'xAxisLabel'  # overrides automatically generated
    Y_AXIS_LABEL    = 'yAxisLabel'  # overrides automatically generated
    Y2_AXIS_LABEL   = 'y2AxisLabel' # overrides automatically generated
    XRANGE_PLOT     = 'xRangePlot'  # range of x values to plot, overriding auto defaults:
                                    #  value is 'float, float'. Use for TMin, TMax for stability plots
    XRANGE_WINDOW   = 'xRangeWindow' # boundaries X-Y space to display.
    YRANGE_WINDOW   = 'yRangeWindow' #  often needs to be larger than the data and spec lines so they are not at the edge.
    X_LINEAR        = 'xLinear'     # force the X axis to be linear when it would normally be log
    Y_LINEAR        = 'yLinear'     # force the Y axis to be linear when it would normally be log
    SPEC_LINE1      = 'specLine1'   # list of two points to draw a spec line. Value is 'x1, y1, x2, y2'.
    SPEC_LINE2      = 'specLine2'   # list of two points to draw a second spec line. Value is 'x1, y1, x2, y2'.
    SPEC1_NAME      = 'spec1Name'   # label for SPEC_LINE1
    SPEC2_NAME      = 'spec2Name'   # label for SPEC_LINE2
    RMS_SPEC        = 'rmsSpec'     # for AMPLITUDE_SPECTRUM plots, an RMS spec over a specified bandwidth, 
                                    #  like "0.1, 800, 20e-6".  See SpecLines.BIAS_LNA_VOLT_RMS below
    SPEC_COMPLIANCE = 'specCompliance' # string to add to plot indicating compliance
    FOOTER1         = 'footer1'     # footer line 1
    FOOTER2         = 'footer2'     # footer line 2 
    FOOTER3         = 'footer3'     # footer line 3 
    IMG_WIDTH       = 'imgWidth'    # pixels width of output image
    IMG_HEIGHT      = 'imgHeight'   # pixels height of output image

class Units(EnumHelper):
    '''
    Units literals.
    '''
    WATTS       = 'W'           # watts
    MW          = 'mW'          # milliwatts
    VOLTS       = 'V'           # volts
    MV          = 'mV'          # millivolts
    DBM         = 'dBm'         # dBm
    DEG         = 'deg'         # degrees of phase
    SECONDS     = 'seconds'     # time as seconds
    MS          = 'ms'          # time as milliseconds
    FS          = 'fs'          # femtoseconds of phase
    MINUTES     = 'minutes'     # time as minutes
    LOCALTIME   = 'localtime'   # time as datetime
    HZ          = 'Hz'          # X axis of FFT
    AMPLITUDE   = 'amplitude'   # default Y axis units when unknown
    KELVIN      = 'K'           # temperature
    CELCIUS     = 'C'           # temperature
    AVAR        = u'σ²(T)'      # Allan variance definition. Actual units will be W or V etc.
    ADEV        = u'σ(2,t=10s,T)' # 2-pt Allan std dev. definition. Actual units will be DEG or FS.
    PER_ROOT_HZ = u'{0}/√Hz'    # Amplitude spectral density units. Replace {0} with actual units.

class SpecLines(object):
    '''
    Well-known ALMA spec lines.  Most are "x1, y1, x2, y2".  Exceptions being:
      RMS which is "x1, x2, RMS"
      XRANGE which is "x1, x2" and limits how far the plot extends, even if it could have been more. 
    '''
    FE_AMP_STABILITY1 = "0.05, 5e-7, 100, 5e-7"     # Units = AVAR
    FE_AMP_STABILITY2 = "300, 4e-6, 300, 4e-6"      # Units = AVAR
    FE_PHASE_STABILITY = "10, 10, 300, 10"          # Units = FS
    IFPROC_AMP_STABILITY1 = "0.05, 1e-7, 100, 1e-7" # Units = AVAR
    IFPROC_AMP_STABILITY2 = "300, 1e-6, 300, 1e-6"  # Units = AVAR
    WCA_AMP_STABILITY1 = "0.05, 9e-8, 100, 9e-9"    # Units = AVAR
    WCA_AMP_STABILITY2 = "300, 1e-6, 300, 1e-6"     # Units = AVAR
    BAND6_AMP_STABILITY1 = "0.05, 4e-7, 100, 4e-7"  # Units = AVAR
    BAND6_AMP_STABILITY2 = "300, 3e-6, 300, 3e-6"   # Units = AVAR
    BAND6_PHASE_STABILITY1 = "10, 0.5, 300, 0.5"    # Units = DEG
    BAND6_PHASE_STABILITY2 = "10, 0.5, 300, 5"      # Band6 test limit. Units = DEG
    BIAS_SIS_VOLT_STABILITY = "0.1, 0.2e-6, 300, 0.2e-6" # TODO: Since this is AVAR, may need to use sqrt(0.2e-6)
    BIAS_LNA_VOLT_ASD_1HZ = "1, 0.8e-6, 1, 0.8e-6"  # 800 nV/√Hz, max @ 1 Hz
    BIAS_LNA_VOLT_RMS = "0.1, 800, 20e-6"           # 0.1 to 800 Hz: 20 uV RMS max
    XRANGE_PLOT_AMP_STABILITY = "0.05, 375"         # Units = SECONDS, default XRANGE_PLOT for amp.
    XRANGE_PLOT_PHASE_STABILITY = "10, 300"         # Units = SECONDS, default XRANGE_PLOT for phase.
