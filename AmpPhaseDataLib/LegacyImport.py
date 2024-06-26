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
    api.setDataSource(timeSeriesId, DataSource.DATA_STATUS, DataStatus.UNKNOWN)
    return timeSeriesId

def importTimeSeriesFETMSAmp(file, measFile = None):
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
    yUnits = Units.WATTS
    
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
    timeSeriesId = api.insertTimeSeries(dataSeries, temperatures1, temperatures2, timeStamps, tau0Seconds, startTime, yUnits)
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
    if measNotes:
        api.setDataSource(timeSeriesId, DataSource.NOTES, measNotes)
    api.setDataSource(timeSeriesId, DataSource.DATA_STATUS, DataStatus.UNKNOWN)
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
    :return timeSeriesId if succesful, None otherwise. 
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
        return None
    
    except TypeError:
        print("Wrong file format '{0}'".format(file))
        print("Expecting <TS with milliseconds> <tilt deg> <phase deg> <amplitude dB> <locked?> <temperatures1 K> <temperatures2 K>")
        return None
    
    if len(dataSeries) < 2:
        print("Data file is too short '{0}'".format(file))
        return None
    
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
        return None
            
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
    api.setDataSource(timeSeriesId, DataSource.DATA_STATUS, DataStatus.UNKNOWN)
    return timeSeriesId


def importTimeSeriesNSI2000Phase(file, notes = None):
    '''
    Import phase stability data taken with NSI2000 stability plot
    
    Formatted comma-delimited:
    <amplitude dB>, <phase dB>, <time seconds>
    
    :param file:        str file to import
    :param notes:       str if provided will be assigned to the time series NOTES tag
    :return timeSeriesId if succesful, False otherwise. 
    '''
    if not os.path.exists(file):
        print("File not found '{0}'".format(file))
        return False
    
    dataSeries = []
    try:
        with open(file, 'r') as f:
            reader = csv.reader(f, delimiter=",")
            first = True
            sumSeconds = 0.0
            N = 0
            for line in reader:
                # skip header and comment lines:
                try:
                    amp = float(line[0])
                    phase = float(line[1])
                    seconds = float(line[2])
                except:
                    pass
                else:
                    if first:
                        prevSeconds = seconds
                        first = False
                    else:
                        sumSeconds += (seconds - prevSeconds)
                        prevSeconds = seconds
                        N += 1
                        dataSeries.append(phase)

    except OSError:
        print("Could not open file '{0}'".format(file))
        return False
    
    except TypeError:
        print("Wrong file format '{0}'".format(file))
        print("Expecting <amplitude dB>, <phase dB>, <time seconds>")
        return False
    
    if len(dataSeries) < 2:
        print("Data file is too short '{0}'".format(file))
        return False
    
    # calculate tau0Seconds seconds col in file:
    tau0Seconds = sumSeconds / N

    api = TimeSeriesAPI.TimeSeriesAPI()
    timeSeriesId = api.insertTimeSeries(dataSeries, tau0Seconds = tau0Seconds)
    if not timeSeriesId:
        print("insertTimeSeries failed")
        return False
            
    api.setDataSource(timeSeriesId, DataSource.DATA_SOURCE, file)
    api.setDataSource(timeSeriesId, DataSource.DATA_KIND, (DataKind.PHASE).value)
    api.setDataSource(timeSeriesId, DataSource.UNITS, (Units.DEG).value)
    api.setDataSource(timeSeriesId, DataSource.NOTES, notes)
        
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
    api.setDataSource(timeSeriesId, DataSource.DATA_STATUS, DataStatus.UNKNOWN)
    return timeSeriesId

def importTimeSeriesBand6CTS_experimental2(file, notes = None, dataKind = (DataKind.POWER).value):
    '''
    Import power meter or phase measurements extracted from the CTS database
    This is experimental and will likely not be used in the future CTS implementation
    Power measurements are imported as voltages, from the CTS square-law detector.
    Phase measurements are imported as degrees.
    
    Having the following format, tab-delimited:
    FreqCarrier <tab> Port <tab> TS <tab> time_sec <tab> Phase <tab> Amplitude <tab> Temp1 <tab> Temp2 <tab> Temp3 <tab> Temp4 <tab> Temp8 <tab> AmbientTemp

    :param file: str file to import
    :param notes:       str if provided will be assigned to the time series NOTES tag
    :return timeSeriesId if succesful, None otherwise. 
    '''
    if not os.path.exists(file):
        print("File not found '{0}'".format(file))
        return None
    
    startTime = None
    dataSeries = []
    temperatures = []
    tau0Seconds = None
    t0 = None
    rf = None
    try:
        with open(file, 'r') as f:
            reader = csv.reader(f)
            for line in reader:
                # skip header and comment lines:
                if line[0][0].isnumeric():
                    if not startTime:
                        parser = ParseTimeStamp.ParseTimeStamp()
                        startTime = parser.parseTimeStamp(line[2])
                        t0 = float(line[3])
                    elif not tau0Seconds:
                        tau0Seconds = float(line[3]) - t0
                    if not rf:
                        rf = float(line[0])
                    dataSeries.append(float(line[4]))
                    temperatures.append(float(line[11]))
        
    except OSError:
        print("Could not open file '{0}'".format(file))
        return None
    
    except TypeError:
        print("Wrong file format '{0}'".format(file))
        print("Expecting FreqCarrier <tab> Port <tab> TS <tab> time_sec <tab> Phase <tab> Amplitude <tab> Temp1 <tab> Temp2 <tab> Temp3 <tab> Temp4 <tab> Temp8 <tab> AmbientTemp")
        return None
    
    if len(dataSeries) < 2:
        print("Data file is too short '{0}'".format(file))
        return None
    
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
    timeSeriesId = api.insertTimeSeries(dataSeries, temperatures, startTime = startTime, tau0Seconds = tau0Seconds)
    if not timeSeriesId:
        print("insertTimeSeries failed")
        return None
    
    api.setDataSource(timeSeriesId, DataSource.DATA_SOURCE, file)
    api.setDataSource(timeSeriesId, DataSource.RF_GHZ, rf)
    api.setDataSource(timeSeriesId, DataSource.DATA_KIND, dataKind)
    api.setDataSource(timeSeriesId, DataSource.UNITS, units)
    api.setDataSource(timeSeriesId, DataSource.MEAS_SW_NAME, "Band 6 CTS")
    api.setDataSource(timeSeriesId, DataSource.MEAS_SW_VERSION, "6.3")
    if notes:
        api.setDataSource(timeSeriesId, DataSource.NOTES, notes)
    api.setDataSource(timeSeriesId, DataSource.DATA_STATUS, DataStatus.UNKNOWN)
    return timeSeriesId

def importTimeSeriesWCABench(file, notes = None, dataKind = (DataKind.POWER).value):
    '''
    Import power meter measurements from a CSV file from the OSF WCA test bench
    
    Having the following format:
    YYYY-MM-DD HH:MM:SS.mmm,power
    :param file: str file to import
    :param notes:       str if provided will be assigned to the time series NOTES tag
    :return timeSeriesId if succesful, False otherwise. 
    '''
    if not os.path.exists(file):
        print("File not found '{0}'".format(file))
        return False
    
    timeStamps = []
    dataSeries = []
    try:
        with open(file, 'r') as f:
            reader = csv.reader(f, delimiter=",")
            for line in reader:
                # skip header and comment lines:
                if line[0][0].isnumeric():
                    timeStamps.append(line[0])
                    dataSeries.append(float(line[1]))
        
    except OSError:
        print("Could not open file '{0}'".format(file))
        return False
    
    except TypeError:
        print("Wrong file format '{0}'".format(file))
        print("Expecting YYYY-MM-DD HH:MM:SS.mmm,power")
        return False
    
    if len(dataSeries) < 2:
        print("Data file is too short '{0}'".format(file))
        return False
    
    # import as POWER measurements:
    dataKind = DataKind.POWER
    units = Units.WATTS
    print("Importing power as W")
    
    api = TimeSeriesAPI.TimeSeriesAPI()
    timeSeriesId = api.insertTimeSeries(dataSeries, timeStamps = timeStamps, dataUnits = units)
    if not timeSeriesId:
        print("insertTimeSeries failed")
        return False
    
    api.setDataSource(timeSeriesId, DataSource.DATA_SOURCE, file)
    api.setDataSource(timeSeriesId, DataSource.DATA_KIND, dataKind.value)
    api.setDataSource(timeSeriesId, DataSource.UNITS, units.value)
    api.setDataSource(timeSeriesId, DataSource.MEAS_SW_NAME, "WCA test bench")
    if notes:
        api.setDataSource(timeSeriesId, DataSource.NOTES, notes)
    api.setDataSource(timeSeriesId, DataSource.DATA_STATUS, DataStatus.UNKNOWN)
    return timeSeriesId