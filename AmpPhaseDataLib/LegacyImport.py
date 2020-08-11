'''
LegacyImport: methods to import legacy TimeSeries and Result data files
'''

from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhaseDataLib.Constants import DataKind, DataSource, DataStatus, Units
from Utility import ParseTimeStamp
from Utility.StripQuotes import stripQuotes
import configparser
import csv
import os

def importTimeSeriesE4418B(file, notes = None, tau0Seconds = None, importUnits = Units.WATTS):
    '''
    Import power meter measurements taken with the legacy 'HP E4418B Power Measurement.vi'
    
    Having the following format, tab-delimited:
    MM/DD/YY H/MM/SS AM    +NNN.NNE-09
    
    Amplitude may be in W, mW, or dBm
    Normally W and dBm can be distinguished automatically, 
      but the isdBm, isW, and ismW switches can be set to force the input format.    
    :param file: str file to import
    :param notes:       str if provided will be assigned to the time series NOTES tag
    :param tau0Seconds: float, if provided sets the integration time per sample
                        if None, determine integration time from the timestamps
    :param importUnits: units in the raw data file.  Supported values:  WATTS, MW, DBM
                        data will be converted to WATTS before insert. 
    :return timeSeriesId if succesful, False otherwise. 
    '''
    if not os.path.exists(file):
        print("File not found '{0}'".format(file))
        return False
    
    timeStamps = []
    dataSeries = []
    try:
        with open(file, 'r') as f:
            reader = csv.reader(f, delimiter="\t")
            for line in reader:
                timeStamps.append(line[0])
                dataSeries.append(float(line[1]))
        
    except OSError:
        print("Could not open file '{0}'".format(file))
        return False
    
    except TypeError:
        print("Wrong file format '{0}'".format(file))
        print("Expecting MM/DD/YY H/MM/SS AM<tab>+NNN.NNE-09")
        return False
    
    if len(dataSeries) < 2:
        print("Data file is too short '{0}'".format(file))
        return False
    
    # convert from mW to W:
    if importUnits == Units.MW:
        print("Importing mW")
        dataSeries = [y / 1000 for y in dataSeries]
    
    # convert from dBm to W:        
    elif importUnits == Units.DBM: 
        print("Importing dBm")
        dataSeries = [(10 ** (y / 10)) / 1000 for y in dataSeries]

    # no conversion:
    else:
        print("Importing Watts")
    
    # calculate tau0Seconds from timeStamps in file:
    if not tau0Seconds:
        parser = ParseTimeStamp.ParseTimeStamp()
        ts0 = parser.parseTimeStamp(timeStamps[0])
        tsN = parser.parseTimeStamp(timeStamps[-1])
        duration = (tsN - ts0).total_seconds()
        tau0Seconds = duration / (len(timeStamps) - 1)

    api = TimeSeriesAPI.TimeSeriesAPI()
    timeSeriesId = api.insertTimeSeries(dataSeries, tau0Seconds = tau0Seconds, startTime = timeStamps[0])
    if not timeSeriesId:
        print("insertTimeSeries failed")
        return False
    
    api.setDataSource(timeSeriesId, DataSource.DATA_SOURCE, file)
    api.setDataSource(timeSeriesId, DataSource.DATA_KIND, (DataKind.POWER).value)
    api.setDataSource(timeSeriesId, DataSource.UNITS, (Units.WATTS).value)
    api.setDataSource(timeSeriesId, DataSource.MEAS_SW_NAME, "HP E4418B Power Measurement.vi")
    api.setDataSource(timeSeriesId, DataSource.MEAS_SW_VERSION, "2009-03-13 changelist 6851")
    if notes:
        api.setDataSource(timeSeriesId, DataSource.NOTES, notes)
    api.setDataStatus(timeSeriesId, DataStatus.UNKNOWN)
    return timeSeriesId

def importTimeSeriesFETMSAmp(file, measFile = None, notes = None, systemName = None):
    '''
    Import amplitude stability data taken with FETMS Automated Test application.
    
    Having a header row and the following format, tab-delimited:
    <TS with milliseconds> <tilt deg> <amplitude> <locked?> <temperatures1 K> <temperatures2 K> <milliseconds elapsed>
    
    The 'meas' file is INI format with the following items:
    [header]
    band = <int>
    pol = <0/1>
    sb = <1/2>        #these are used to make the DataSource.SUBSYSTEM tag
    TS = startTime
    LO = freqGhz      #to be included in TITLE
    powermeter_unit = <W/dBm>
    notes = <str>
    SWVersion = <str>
    
    :param file:        str file to import
    :param measFile:    str 'meas' metadata file to read. This will normally be auto-detected from 'file' name.
    :param notes:       str if provided will be assigned to the time series NOTES tag
                            else the notes from 'meas' file will be used, 
                            if no 'meas' file, the filename will be used. 
    :param systemName:  str if provided will be used as part of the title.  Example 'FE-21'  
    :return timeSeriesId if succesful, False otherwise. 
    '''
    
    if not os.path.exists(file):
        print("File not found '{0}'".format(file))
        return False
    
    timeStamps = []
    dataSeries = []
    temperatures1 = []
    temperatures2 = []
    try:
        with open(file, 'r') as f:
            reader = csv.reader(f, delimiter="\t")
            firstTime = True
            for line in reader:
                # skip header and comment lines:
                if line[0][0].isnumeric():
                    if firstTime:
                        ms0 = int(line[6])
                        firstTime = False
                    msN = int(line[6]) 
                    timeStamps.append(line[0])
                    dataSeries.append(float(line[2]))
                    temperatures1.append(float(line[4]))
                    temperatures2.append(float(line[5]))
        
    except OSError:
        print("Could not open file '{0}'".format(file))
        return False
    
    except TypeError:
        print("Wrong file format '{0}'".format(file))
        print("Expecting <TS with milliseconds> <tilt deg> <amplitude> <locked?> <temperatures1 K> <temperatures2 K> <milliseconds elapsed>")
        return False
    
    if len(dataSeries) < 2:
        print("Data file is too short '{0}'".format(file))
        return False
    
    if not measFile:
        root, ext = os.path.splitext(file)
        measFile = root + 'meas' + ext
    
    # calculate tau0Seconds from millisecond column in file:
    tau0Seconds = (msN - ms0) / (len(timeStamps) - 1) / 1000
    
    band = None
    startTime = None
    LO = None
    pol = None
    sb = None
    measNotes = None
    SWVersion = None
    yUnits = (Units.WATTS).value
    
    if os.path.exists(measFile):
        config = configparser.ConfigParser()
        try:
            config.read(measFile)
        except:
            pass
        else:
            header = config['header']
            if header:
                band = header.get('band', None)
                startTime = header.get('TS', None)
                if startTime:
                    startTime = stripQuotes(startTime)
                LO = header.get('LO', None)
                if LO:
                    LO = float(stripQuotes(LO))
                yUnits = header.get('powermeter_unit', (Units.WATTS).value)
                if yUnits:
                    yUnits = stripQuotes(yUnits)
                yUnits = Units.fromStr(yUnits)
                pol = header.get('pol', None)
                sb = header.get('sb', None)
                if sb:
                    sb = int(sb)
                    if sb == 1:
                        sb = "USB"
                    elif sb == 2:
                        sb = "LSB"
                    else:
                        sb = None
                measNotes = header.get('notes', None)
                if measNotes:
                    measNotes = stripQuotes(measNotes)                
                SWVersion = header.get('SWVersion', None)
                if SWVersion:
                    SWVersion = stripQuotes(SWVersion)                
    
    # convert from dBm to W:        
    if yUnits == Units.DBM:
        print("Importing dBm")
        dataSeries = [(10 ** (y / 10)) / 1000 for y in dataSeries]

    # make system string:
    system = ""
    if systemName:
        system += systemName
    if band:
        if len(system):
            system += ", "
        system += "Band " + band

    # make subsystem string:
    subsystem = ""
    if pol:
        subsystem += "Pol " + pol
    if sb:
        if len(subsystem):
            subsystem += ", "
        subsystem += sb
              
    # fix startTime:
    if not startTime:
        startTime = timeStamps[0]
          
    api = TimeSeriesAPI.TimeSeriesAPI()
    timeSeriesId = api.insertTimeSeries(dataSeries, temperatures1, temperatures2, timeStamps, tau0Seconds, startTime)
    if not timeSeriesId:
        print("insertTimeSeries failed")
        return False
            
    api.setDataSource(timeSeriesId, DataSource.DATA_SOURCE, file)
    api.setDataSource(timeSeriesId, DataSource.DATA_KIND, (DataKind.POWER).value)
    api.setDataSource(timeSeriesId, DataSource.UNITS, (Units.WATTS).value)
    if LO:
        api.setDataSource(timeSeriesId, DataSource.LO_GHZ, str(LO))
    if len(system):
        api.setDataSource(timeSeriesId, DataSource.SYSTEM, system)
    if len(subsystem):
        api.setDataSource(timeSeriesId, DataSource.SUBSYSTEM, subsystem)
    api.setDataSource(timeSeriesId, DataSource.MEAS_SW_NAME, "FETMS Automated Test")
    if SWVersion:
        api.setDataSource(timeSeriesId, DataSource.MEAS_SW_VERSION, SWVersion)
    if notes:
        api.setDataSource(timeSeriesId, DataSource.NOTES, notes)
    elif measNotes:
        api.setDataSource(timeSeriesId, DataSource.NOTES, measNotes)
    api.setDataStatus(timeSeriesId, DataStatus.UNKNOWN)
    return timeSeriesId

def importTimeSeriesFETMSPhase(file, measFile = None, notes = None, systemName = None):
    '''
    Import phase stability data taken with FETMS Automated Test application.
    
    Having a header row and the following format, tab-delimited:
    <TS with milliseconds> <tilt deg> <phase deg> <amplitude dB> <locked?> <temperatures1 K> <temperatures2 K>
    
    The 'meas' file is INI format with the following items:
    [header]
    band = <int>
    TS = startTime
    LO = freqGhz      
    RF = freqGhz      #to be included in TITLE
    pol = <0/1>
    sb = <1/2>        #these are used to make the DataSource.SUBSYSTEM tag
    tilt_angle = <float deg>
    meas_length_minutes <float>
    notes = <str>
    integration_time = <float ms>
    SWVersion = <str>
    
    :param file:        str file to import
    :param measFile:    str 'meas' metadata file to read. This will normally be auto-detected from 'file' name.
    :param notes:       str if provided will be assigned to the time series NOTES tag
                            else the notes from 'meas' file will be used. 
    :param systemName:  str if provided will be used as part of the title.  Example 'FE-21'  
    :return timeSeriesId if succesful, False otherwise. 
    '''
    if not os.path.exists(file):
        print("File not found '{0}'".format(file))
        return False
    
    timeStamps = []
    dataSeries = []
    temperatures1 = []
    temperatures2 = []
    try:
        with open(file, 'r') as f:
            reader = csv.reader(f, delimiter="\t")
            for line in reader:
                # skip header and comment lines:
                if line[0][0].isnumeric():
                    timeStamps.append(line[0])
                    dataSeries.append(float(line[2]))
                    temperatures1.append(float(line[5]))
                    temperatures2.append(float(line[6]))
    
    except OSError:
        print("Could not open file '{0}'".format(file))
        return False
    
    except TypeError:
        print("Wrong file format '{0}'".format(file))
        print("Expecting <TS with milliseconds> <tilt deg> <phase deg> <amplitude dB> <locked?> <temperatures1 K> <temperatures2 K>")
        return False
    
    if len(dataSeries) < 2:
        print("Data file is too short '{0}'".format(file))
        return False
    
    if not measFile:
        root, ext = os.path.splitext(file)
        measFile = root + 'meas' + ext
    
    band = None
    startTime = None
    LO = None      
    RF = None
    pol = None
    sb = None
    measNotes = None
    tau0Seconds = None
    SWVersion = None
    
    if os.path.exists(measFile):
        config = configparser.ConfigParser()
        try:
            config.read(measFile)
        except:
            pass
        else:
            header = config['header']
            if header:
                band = header.get('band', None)
                startTime = header.get('TS', None)
                if startTime:
                    startTime = stripQuotes(startTime)
                LO = header.get('LO', None)
                if LO:
                    LO = float(stripQuotes(LO))
                RF = header.get('RF', None)
                if RF:
                    RF = float(stripQuotes(RF))
                pol = header.get('pol', None)
                sb = header.get('sb', None)
                if sb:
                    sb = int(sb)
                    if sb == 1:
                        sb = "USB"
                    elif sb == 2:
                        sb = "LSB"
                    else:
                        sb = None
                measNotes = header.get('notes', None)
                if measNotes:
                    measNotes = stripQuotes(measNotes)                
                tau0Seconds = header.get('integration_time', None)
                if tau0Seconds:
                    tau0Seconds = float(stripQuotes(tau0Seconds)) / 1000 # convert ms to s
                SWVersion = header.get('SWVersion', None)
                if SWVersion:
                    SWVersion = stripQuotes(SWVersion)                
    
    # make system string:
    system = ""
    if systemName:
        system += systemName
    if band:
        if len(system):
            system += ", "
        system += "Band " + band

    # make subsystem string:
    subsystem = ""
    if pol:
        subsystem += "Pol " + pol
    if sb:
        if len(subsystem):
            subsystem += ", "
        subsystem += sb

    # calculate tau0Seconds from timeStamps in file:
    if not tau0Seconds:
        parser = ParseTimeStamp.ParseTimeStamp()
        ts0 = parser.parseTimeStamp(timeStamps[0])
        tsN = parser.parseTimeStamp(timeStamps[-1])
        duration = (tsN - ts0).total_seconds()
        tau0Seconds = duration / (len(timeStamps) - 1)

    # fix startTime:
    if not startTime:
        startTime = timeStamps[0]
        
    api = TimeSeriesAPI.TimeSeriesAPI()
    timeSeriesId = api.insertTimeSeries(dataSeries, temperatures1, temperatures2, timeStamps, tau0Seconds, startTime)
    if not timeSeriesId:
        print("insertTimeSeries failed")
        return False
            
    api.setDataSource(timeSeriesId, DataSource.DATA_SOURCE, file)
    api.setDataSource(timeSeriesId, DataSource.DATA_KIND, (DataKind.PHASE).value)
    api.setDataSource(timeSeriesId, DataSource.UNITS, (Units.DEG).value)
    if LO:
        api.setDataSource(timeSeriesId, DataSource.LO_GHZ, str(LO))
    if RF:
        api.setDataSource(timeSeriesId, DataSource.RF_GHZ, str(RF))
    if len(system):
        api.setDataSource(timeSeriesId, DataSource.SYSTEM, system)
    if len(subsystem):
        api.setDataSource(timeSeriesId, DataSource.SUBSYSTEM, subsystem)
    api.setDataSource(timeSeriesId, DataSource.MEAS_SW_NAME, "FETMS Automated Test")
    if SWVersion:
        api.setDataSource(timeSeriesId, DataSource.MEAS_SW_VERSION, SWVersion)
    if notes:
        api.setDataSource(timeSeriesId, DataSource.NOTES, notes)
    elif measNotes:
        api.setDataSource(timeSeriesId, DataSource.NOTES, measNotes)        
    api.setDataStatus(timeSeriesId, DataStatus.UNKNOWN)
    return timeSeriesId

def importTimeSeriesBand6CTS_experimental(file, notes = None, dataKind = (DataKind.POWER).value):
    '''
    Import power meter or phase measurements extracted from a CTS spreadsheet.
    This is experimental and will likely not be used in the future CTS implementation
    Power measurements are imported as voltages, from the CTS square-law detector.
    Phase measurements are imported as degrees.
    
    Having the following format, tab-delimited:
    MM/DD/YY HH/MM/SS.mmm <tab> seconds <tab> power/phase <tab> tempK 
    :param file: str file to import
    :param notes:       str if provided will be assigned to the time series NOTES tag
    :return timeSeriesId if succesful, False otherwise. 
    '''
    if not os.path.exists(file):
        print("File not found '{0}'".format(file))
        return False
    
    timeStamps = []
    dataSeries = []
    temperatures = []
    try:
        with open(file, 'r') as f:
            reader = csv.reader(f, delimiter="\t")
            for line in reader:
                # skip header and comment lines:
                if line[0][0].isnumeric():
                    timeStamps.append(line[0])
                    dataSeries.append(float(line[2]))
                    temperatures.append(float(line[3]))
        
    except OSError:
        print("Could not open file '{0}'".format(file))
        return False
    
    except TypeError:
        print("Wrong file format '{0}'".format(file))
        print("Expecting MM/DD/YY HH/MM/SS.mmm <tab> seconds <tab> power/phase <tab> tempK")
        return False
    
    if len(dataSeries) < 2:
        print("Data file is too short '{0}'".format(file))
        return False
    
    # no conversion:
    if dataKind == (DataKind.PHASE).value:
        units = (Units.DEG).value
        print("Importing phase in degrees")
    else:
        # import as POWER measurements:
        dataKind = (DataKind.POWER).value
        units = (Units.VOLTS).value
        print("Importing power as voltage")
    
    api = TimeSeriesAPI.TimeSeriesAPI()
    timeSeriesId = api.insertTimeSeries(dataSeries, temperatures, timeStamps = timeStamps)
    if not timeSeriesId:
        print("insertTimeSeries failed")
        return False
    
    api.setDataSource(timeSeriesId, DataSource.DATA_SOURCE, file)
    api.setDataSource(timeSeriesId, DataSource.DATA_KIND, dataKind)
    api.setDataSource(timeSeriesId, DataSource.UNITS, units)
    api.setDataSource(timeSeriesId, DataSource.MEAS_SW_NAME, "Band 6 CTS")
    api.setDataSource(timeSeriesId, DataSource.MEAS_SW_VERSION, "6.3")
    if notes:
        api.setDataSource(timeSeriesId, DataSource.NOTES, notes)
    api.setDataStatus(timeSeriesId, DataStatus.UNKNOWN)
    return timeSeriesId
