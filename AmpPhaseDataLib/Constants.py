'''
Constants used in these APIs:
When referring to metadata about a measurement or a plot, you must use these Enums or their str values.
Admittedly, a few other things are stashed here to avoid literals in the code.  
'''
from enum import Enum

class PlotKind(Enum):
    '''
    Known plot kinds and wildcards.
    For specifying what kind of plot this is or for finding a plot from a database.
    '''
    NONE = 0
    TIME_SERIES = 1         # measurement units vs. time
    POWER_STABILITY = 2     # amplitude stability of power (W, V²)
    VOLT_STABILITY = 3      # voltage stability (V)
    PHASE_STABILITY = 4     # phase stability (deg, rad)
    AMP_SPECTRUM = 5        # ASD for linear volts, phase (V, deg, rad)
    POWER_SPECTRUM = 6      # PSD for power, square-law detector volts (W, V²)
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
    Known raw data series kinds and literals for display.
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
    UNKNOWN     = 'UNKNOWN'     # setting any other tag will clear UNKNOWN
    ERROR       = 'ERROR'       # an error occurred during the measurement
    TO_DELETE   = 'TO_DELETE'   # setting TO_DELETE will clear TO_RETAIN
    TO_RETAIN   = 'TO_RETAIN'   # setting TO_RETAIN will clear TO_DELETE
    MEET_SPEC   = 'MEET_SPEC'   # setting MEET_SPEC will clear FAIL_SPEC
    FAIL_SPEC   = 'FAIL_SPEC'   # setting FAIL_SPEC will clear MEET_SPEC
    
class DataSource(EnumHelper):
    '''
    Data source flags for annotating Time Series and Results
    '''
    CONFIG_ID       = 'CONFIG_ID'   # of the device under test
    DATA_SOURCE     = 'DATA_SOURCE' # source data file on disk, if applicable.  Otherwise describe where this came from.
    DATA_KIND       = 'DATA_KIND'   # of the primary data series. Values from DataKind enum.
    TEST_SYSTEM     = 'TEST_SYSTEM' # name of measurement system or computer where the data was created.
    UNITS           = 'UNITS'       # of the primary data series, like "dBm" or "deg".  Values from Units enum.
    T_UNITS         = 'T_UNITS'     # of the temperature data series, like "K".  Values from Units enum.
    LO_GHZ          = 'LO_GHZ'      # the LO frequency in GHz
    RF_GHZ          = 'RF_GHZ'      # if phase data, the RF in GHz
    TILT_ANGLE      = 'TILT_ANGLE'  # tilt angle when measured
    SYSTEM          = 'SYSTEM'      # like "FE-20, Band 6"
    SUBSYSTEM       = 'SUBSYSTEM'   # like "pol0, USB"
    SERIALNUM       = 'SERIALNUM'   # of a serialized part under test
    OPERATOR        = 'OPERATOR'    # name or initials
    NOTES           = 'NOTES'       # operator notes
    MEAS_SW_NAME    = 'MEAS_SW_NAME'    # name of measurement software
    MEAS_SW_VERSION = 'MEAS_SW_VERSION' # version of measurement software

class PlotEl(EnumHelper):
    '''
    Plot elements to be used when rendering
    '''
    XUNITS          = 'XUNITS'          # of the primary x axis, like "seconds"
    YUNITS          = 'YUNITS'          # of the primary y axis, like "dBm"
    Y2UNITS         = 'Y2UNITS'         # of secondary y axis, like "K"
    ERROR_BARS      = 'ERROR_BARS'      # show error bars?  like "1" or "0"
    TITLE           = 'TITLE'           # plot title, overrides automatically generated
    X_AXIS_LABEL    = 'X_AXIS_LABEL'    # overrides automatically generated
    Y_AXIS_LABEL    = 'Y_AXIS_LABEL'    # overrides automatically generated
    Y2_AXIS_LABEL   = 'Y2_AXIS_LABEL'   # overrides automatically generated
    Y2_LEGEND1      = 'Y2_LEGEND1'      # override legend for first temperature sensor trace
    Y2_LEGEND2      = 'Y2_LEGEND2'      # override legend for second temperature sensor trace
    FFT_LEGEND2     = 'FFT_LEGEND2'     # legend for highlighted points in FFT plot
    FFT_COLOR2      = 'FFT_COLOR2'      # color for highlighted points in FFT plot
    XRANGE_PLOT     = 'XRANGE_PLOT'     # range of x values to plot, overriding auto defaults:
                                        #  value is 'float, float'. Use for TMin, TMax for stability plots
    XRANGE_WINDOW   = 'XRANGE_WINDOW'   # boundaries X-Y space to display.
    YRANGE_WINDOW   = 'YRANGE_WINDOW'   #  often needs to be larger than the data and spec lines so they are not at the edge.
    X_LINEAR        = 'X_LINEAR'        # force the X axis to be linear when it would normally be log
    Y_LINEAR        = 'Y_LINEAR'        # force the Y axis to be linear when it would normally be log
    SPEC_LINE1      = 'SPEC_LINE1'      # list of two points to draw a spec line. Value is 'x1, y1, x2, y2'.
    SPEC_LINE2      = 'SPEC_LINE2'      # list of two points to draw a second spec line. Value is 'x1, y1, x2, y2'.
    SPEC1_NAME      = 'SPEC1_NAME'      # label for SPEC_LINE1
    SPEC2_NAME      = 'SPEC2_NAME'      # label for SPEC_LINE2
    RMS_SPEC        = 'RMS_SPEC'        # for AMP_SPECTRUM plots, an RMS spec over a specified bandwidth, 
                                        #  like "0.1, 800, 20e-6".  See SpecLines.BIAS_LNA_VOLT_RMS below
    SPEC_COMPLIANCE = 'SPEC_COMPLIANCE' # string to add to plot indicating compliance
    SHOW_RMS        = 'SHOW_RMS'        # show the RMS of spectrum plots?  like "1" or "0"; default "0"
    FOOTER1         = 'FOOTER1'         # footer line 1
    FOOTER2         = 'FOOTER2'         # footer line 2 
    FOOTER3         = 'FOOTER3'         # footer line 3 
    FOOTER4         = 'FOOTER4'         # footer line 4 for overflow of DATASOURCE from line 3 
    IMG_WIDTH       = 'IMG_WIDTH'       # pixels width of output image
    IMG_HEIGHT      = 'IMG_HEIGHT'      # pixels height of output image
    PROCESS_NOTES   = 'PROCESS_NOTES'   # notes about data processing applied to the result (e.g. noise floor subtraction

class Units(EnumHelper):
    '''
    Units literals for display.
    '''
    WATTS       = 'W'           # watts
    MW          = 'mW'          # milliwatts
    VOLTS       = 'V'           # volts
    VOLTS_SQ    = 'V²'          # volts squared such as from a square-law detector
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
    PER_HZ      = '{0}/Hz'      # Power spectral density units

class SpecLines(object):
    '''
    Well-known ALMA spec lines.  Most are "x1, y1, x2, y2".  Exceptions being:
      RMS which is "f1, f2, RMS"
      XRANGE which is "x1, x2" and limits how far the plot extends, even if more data is available. 
    '''
    FE_AMP_STABILITY1 = "0.05, 5e-7, 100, 5e-7"     # Units = AVAR
    FE_AMP_STABILITY2 = "300, 4e-6, 300, 4e-6"      # Units = AVAR
    FE_PHASE_STABILITY = "20, 10, 300, 10"          # Units = FS
    IFPROC_AMP_STABILITY1 = "0.05, 1e-7, 100, 1e-7" # Units = AVAR
    IFPROC_AMP_STABILITY2 = "300, 1e-6, 300, 1e-6"  # Units = AVAR
    WCA_AMP_STABILITY1 = "0.05, 9e-8, 100, 9e-9"    # Units = AVAR
    WCA_AMP_STABILITY2 = "300, 1e-6, 300, 1e-6"     # Units = AVAR
    BAND6_AMP_STABILITY1 = "0.05, 4e-7, 100, 4e-7"  # Units = AVAR
    BAND6_AMP_STABILITY2 = "300, 3e-6, 300, 3e-6"   # Units = AVAR
    BAND6_PHASE_STABILITY1 = "10, 0.5, 300, 0.5"    # Units = DEG
    BAND6_PHASE_STABILITY2 = "10, 0.5, 300, 5"      # Band6 test limit. Units = DEG
    BIAS_SIS_VOLT_STABILITY = "0.1, 0.2e-6, 300, 0.2e-6" # Units = ADEV[V]
    BIAS_LNA_VOLT_ASD_1HZ = "1, 0.8e-6, 1, 0.8e-6"  # 800 nV/√Hz, max @ 1 Hz
    BIAS_LNA_VOLT_RMS = "0.1, 800, 20e-6"           # 0.1 to 800 Hz: 20 uV RMS max
    XRANGE_PLOT_AMP_STABILITY = "0.05, 375"         # Units = SECONDS, default XRANGE_PLOT for amp.
    XRANGE_PLOT_PHASE_STABILITY = "10, 300"         # Units = SECONDS, default XRANGE_PLOT for phase.
