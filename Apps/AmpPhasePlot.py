'''
AmpPhasePlot command-line tool to import measurement results, create and store plot results.
'''
import sys 
sys.path.append("L:\\python\\ALMAFE-AmpPhasePlot")
# print(sys.path)

from Utility.GitVersion import gitVersion, gitBranch
from AmpPhaseDataLib.TimeSeriesAPI import TimeSeriesAPI
from AmpPhasePlotLib.PlotAPI import PlotAPI
from AmpPhaseDataLib.LegacyImport import importTimeSeriesE4418B, importTimeSeriesFETMSAmp, importTimeSeriesFETMSPhase
from AmpPhaseDataLib.Constants import DataKind, DataSource, DataStatus, PlotEl, Units
from itertools import zip_longest
import argparse
import csv
import os

# module global instances of the two APIs:
tsAPI = TimeSeriesAPI()
plotAPI = PlotAPI()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action = 'store_true', help = 'show version info and exit')
    
    # arguments to control import/data load:
    group = parser.add_argument_group('Arguments to control data loading')
    # we can either load files, load existing Time Series by ID, or re-plot existing Results by ID:
    group2 = group.add_mutually_exclusive_group()
    group2.add_argument('-f', '--file', '--files', type = str, nargs = '+', help = 'Input file(s) containing the raw time series data')
    group2.add_argument('-i', '--time_series', type = int, nargs = '+', help = 'Time series ID(s) to load and plot')
    group2.add_argument('-r', '--result', '--results', type = int, nargs = '+', help = 'Result ID(s) to load and plot')
    # nested group of import type specifier:
    group2 = group.add_mutually_exclusive_group()
    group2.add_argument('-a', '--amplitude', action = 'store_true', help = 'Input file(s) are amplitude time series')
    group2.add_argument('-p', '--phase', action = 'store_true', help = 'Input file(s) are phase time series')
    group2.add_argument('-w', '--power', action = 'store_true', help = 'Input file(s) are power time series')
    group2.add_argument('-v', '--voltage', action = 'store_true', help = 'Input file(s) are voltage time series')
    group2.add_argument('--le', '--legacy_e4418b', dest = 'legacy_e4418b', action = 'store_true', help = "Input file(s) are from legacy 'HP E4418B Power Measurement.vi'")
    group2.add_argument('--la', '--legacy_fetms_amp', dest = 'legacy_fetms_amp', action = 'store_true', help = "Input file(s) are from legacy FETMS Amplitude Stabilty")
    group2.add_argument('--lp', '--legacy_fetms_phase', dest = 'legacy_fetms_phase', action = 'store_true', help = "Input file(s) are from legacy FETMS Phase Stabilty")
    # describing the data:
    group.add_argument('--tsc', '--timestamp_col', dest = 'timestamp_col', type = int, default = None, help = 'Time stamps column, default None')
    group.add_argument('--dc', '--data_col', dest = 'data_col', type = int, default = 0, help = 'Amplitude/phase data column, default 0')
    group.add_argument('--tc1', '--temp1_col', dest = 'temp1_col', type = int, default = None, help = 'Temperature sensor 1 column. default None')
    group.add_argument('--tc2', '--temp2_col', dest = 'temp2_col', type = int, default = None, help = 'Temperature sensor 2 column. default None')
    group.add_argument('--delim', type = str, default = '\t', help = 'Field delimiter, default <tab>')
    group.add_argument('--tau', '--tau0seconds', dest = 'tau0seconds', type = float, default = None, help = 'Integration time/sampling interval, default calculate from time stamps.')
    group.add_argument('--start_time', type = str, default = None, help = 'Time stamp when the measurement was started. Default first time stamp in file.')
    
    # optional arguments to specify DataSource attributes:
    group = parser.add_argument_group('Arguments to control data source tags')
    group.add_argument('-c', '--config_id', dest = 'config_id', type = str, default = None, help = 'Configuration ID of the item under test')
    group.add_argument('-d', '--data_source', dest = 'data_source', type = str, default = None, help = 'Data file name or description of data source')
    group.add_argument('--test_system', type = str, default = None, help = 'Test system where measured')
    group.add_argument('-u', '--units', dest = 'units', type = str, default = 'amplitude', choices=['W', 'mW', 'dBm', 'DEG', 'V', 'mV', 'amplitude'], help = "Units of the main data series")
    group.add_argument('--tu', '--temp_units', dest = 'temp_units', type = str, default = 'K', choices=['K', 'C'], help = "Units of the temperature column(s)")
    group.add_argument('--LO', '--lo', dest = 'lo', type = float, nargs = '+', default = [], help = 'LO frequenc(y|ies) in GHz')
    group.add_argument('--RF', '--rf', dest = 'rf', type = float, nargs = '+', default = [], help = 'RF frequenc(y|ies) in GHz')
    group.add_argument('--tilt_angle', type = float, default = None, help = 'Tilt angle when measured')
    group.add_argument('-y', '--system_name', type = str, default = None, help = "System which was measured. Example: 'FE-21 Band 6'")
    group.add_argument('-b', '--subsystem', type = str, default = None, help = "Subystem which was measured. Example: 'Pol0 USB'")
    group.add_argument('-o', '--operator', type = str, default = None, help = "Operator name or initials")
    group.add_argument('-n', '--notes', type = str, default = None, help = 'Notes to associate with the time series')
    group.add_argument('--sw', '--meas_sw_name', dest = 'meas_sw_name', type = str, default = None, help = "Measurement software identifier")
    group.add_argument('--swver', '--meas_sw_version', dest = 'meas_sw_version', type = str, default = None, help = "Measuremen softwaer version")

    # optional arguments to control plot creation and display:
    group = parser.add_argument_group('Arguments to control plot creation and storage')
    group.add_argument('--ot', '--ts_output_file', dest = 'ts_output_file', type = str, default = None, help = 'Output file name for time series plot.')
    group.add_argument('--of', '--fft_output_file', dest = 'fft_output_file', type = str, default = None, help = 'Output file name for FFT plot.')
    group.add_argument('--os', '--stability_output_file', dest = 'stability_output_file', type = str, default = None, help = 'Output file name for stability plot.')
    group.add_argument('--mt', '--make_ts_plot', dest = 'make_ts_plot', action = 'store_true', help = 'Make the time series plot. Forced True if --ts_output_file provided.')
    group.add_argument('--mf', '--make_fft_plot', dest = 'make_fft_plot', action = 'store_true', help = 'Make the FFT plot. Forced True if --fft_output_file provided.')
    group.add_argument('--ms', '--make_stability_plot', dest = 'make_stability_plot', action = 'store_true', help = 'Make the amp/phase stability plot. Forced True if --stability_output_file provided.')
    group.add_argument('-s', '--show', action = 'store_true', help = 'Show plots interactively. Default false')
    group.add_argument('--sr', '--store_result', dest = 'store_result', action = 'store_true', help = 'Store plots and traces to results database')
    
    # arguments to control plot appearance:
    group = parser.add_argument_group('Arguments to control plot appearance')
    group.add_argument('--title', '--titles', '-t', type = str, nargs = '+', default = [], help = 'Plot title(s)')
    
    # arguments specific to Time Series plots:
    group.add_argument('--ts_xunits', type = str, default = None, help = 'X axis units for time series plot. Default local time')
    group.add_argument('--ts_xlabel', type = str, default = None, help = 'X axis label for time series plot. Default based on ts_xunits')
    group.add_argument('--ts_yunits', type = str, default = None, help = 'Y axis units for time series plot. Default same as imported')
    group.add_argument('--ts_ylabel', type = str, default = None, help = 'Y axis label for time series plot. Default based on ts_yunits')
    group.add_argument('--ts_y2units', type = str, default = None, help = 'Y2 axis temperature units for time series plot. Default same as imported')
    group.add_argument('--ts_yslabel', type = str, default = None, help = 'Y2 axis label for time series plot. Default based on ts_y2units')

    # arguments specific to FFT plots:
    group.add_argument('--fft_xlabel', type = str, default = None, help = "X axis label for time series plot. Default 'Frequency [Hz]'")
    group.add_argument('--fft_yunits', type = str, default = None, help = 'Y axis units for time series plot. Default same as imported')
    group.add_argument('--fft_ylabel', type = str, default = None, help = 'Y axis label for time series plot. Default based on fft_yunits')
    # spec lines business:
    group2 = group.add_argument_group('Arguments to specify FFT plot spec lines')
    group2.add_argument('--fft_spec', type = str, default = None, help = "Show spec line or point on FFT plot. Format is 'x1, y1, x2, y2'.")
    group2.add_argument('--fft_rms_spec', type = str, default = None, help = "Evaluate compliance to an RMS spec.  Format is 'fMinHz, fMaxHz, RMSMax'")
    group2.add_argument('--fft_bias_lna_spec', action = 'store_true', help = 'Show spec line for the ALMA cartridge bias LNA: At 1 Hz, 800 nV/√Hz max')
    group2.add_argument('--fft_bias_lna_rms_spec', action = 'store_true', help = 'Evaluate compliance with the ALMA cartridge bias LNA spec: 0.1 to 800 Hz, 20 uV RMS max')
    
    # arguments specific to stability plots:
    group.add_argument('--stab_xunits', type = str, default = None, help = 'X axis units for stability plot. Default seconds')
    group.add_argument('--stab_xlabel', type = str, default = None, help = 'X axis label for stability plot. Default based on stab_xunits')
    group.add_argument('--stab_yunits', type = str, default = None, help = 'Y axis units for stability plot. Default depends on data source tags')
    group.add_argument('--stab_ylabel', type = str, default = None, help = 'Y axis label for stability plot. Default based on stab_yunits')
    # spec lines business:
    group2 = group.add_argument_group('Arguments to specify stability plot spec lines')
    group2.add_argument('--stab_spec1', type = str, default = None, help = "Show spec line or point on stability plot. Format is 'x1, y1, x2, y2'.")
    group2.add_argument('--stab_spec2', type = str, default = None, help = "Show second spec line or point on stability plot. Format is 'x1, y1, x2, y2'.")
    group2 = group.add_mutually_exclusive_group()
    group2.add_argument('--stab_fe_amp_spec', action = 'store_true', help = 'Show spec lines for ALMA FE amplitude stability.')
    group2.add_argument('--stab_lo_amp_spec', action = 'store_true', help = 'Show spec lines for ALMA FE LO amplitude stability.')
    group2.add_argument('--stab_cca_amp_spec', action = 'store_true', help = 'Show spec lines for ALMA FE CCA amplitude stability.')
    group2.add_argument('--stab_fe_phase_spec', action = 'store_true', help = 'Show spec lines for ALMA FE phase stability.')
    group2.add_argument('--stab_lo_phase_spec', action = 'store_true', help = 'Show spec lines for ALMA FE LO phase stability.')
    group2.add_argument('--stab_cca_phase_spec', action = 'store_true', help = 'Show spec lines for ALMA FE CCA phase stability.')
    group2.add_argument('--stab_fetms_amp_spec', action = 'store_true', help = 'Show spec lines for ALMA FETMS IF processor amplitude stability.')
    
    # parse arguments
    args = parser.parse_args()

    # print version string:
    if args.version:
        print("AmpPhasePlot: Analysis and plotting of amplitude and phase stability measurements")
        print("revision " + gitVersion() + " on branch '" + gitBranch() + "'")
        sys.exit(0)

    # handle some argument defaults:
    if args.ts_output_file:
        args.make_ts_plot = True
    if args.fft_output_file:
        args.make_fft_plot = True
    if args.stability_output_file:
        args.make_stability_plot = True
        
    # lists contain ids of what got done:
    timeSeriesIds = []
    plotsMade = []    

    # import file(s):
    if args.file:

        # check required data type is specified:
        if(args.amplitude or args.phase or args.voltage or args.legacy_e4418b or args.legacy_fetms_amp or args.legacy_fetms_phase):
            print('Error: Input data series kind is required: --amplitude, --phase, --power, --voltage, or one of the legacy types: --le, --la, --lp')
            sys.exit(1)

        # import and plot each file:        
        for file, lo, rf, title in zip_longest(args.file, args.lo, args.rf, args.title):
            tsId = importTimeSeries(file, lo, rf, args)
            if tsId:
                timeSeriesIds.append(tsId)
                success = makeSingleTracePlots(tsId, title, args)
                if success:
                    plotsMade.append(tsId)
        title = args.title[0] if args.title and len(args.title) else None
        plotsMade += makeMultiTracePlot(timeSeriesIds, title, args)
    
    # plot from Time Series already in the database:
    elif args.time_series:
        timeSeriesIds = args.time_series
        for tsId, title in zip_longest(timeSeriesIds, args.title):
            plotsMade += makeSingleTracePlots(tsId, title, args)
        title = args.title[0] if args.title and len(args.title) else None
        success = makeMultiTracePlot(timeSeriesIds, title, args)
        if success:
            plotsMade += timeSeriesIds

    # plot from existing results in the database:
    elif args.result:
        for resultId in args.result:
            success = plotFromResult(resultId, args)
            if success:
                plotsMade.append(resultId)
                
    if not (timeSeriesIds or plotsMade):
        # nothing was done, so display usage:
        parser.print_usage()
    else:
        print("{} tasks done.".format(len(timeSeriesIds) + len(plotsMade)))
    sys.exit(0)
        

def importTimeSeries(file, lo, rf, args):
    # check whether file can be accessed    
    if not os.path.exists(file):
        print("Error: Invalid file name. File '{}' does not exist.".format(file))
        return False
    
    systemName = args.system_name if args.system_name else None
    notes = args.notes if args.notes else None
    tau0Seconds = args.tau0seconds
    startTime = args.start_time
    importUnits = Units.fromStr(args.units)
    
    if args.legacy_e4418b:
        return importTimeSeriesE4418B(file, notes, tau0Seconds, importUnits)
    elif args.legacy_fetms_amp:
        return importTimeSeriesFETMSAmp(file, notes = notes, systemName = systemName)
    elif args.legacy_fetms_phase:
        return importTimeSeriesFETMSPhase(file, notes = notes, systemName = systemName)
    
    else:
        # create the header for the time series:
        tsId = tsAPI.startTimeSeries(tau0Seconds, startTime)

        if not tsId:
            print("Error creating Time Series Header for {}".format(file))
            return False
 
        # set the DataSource.DATA_KIND attribute:
        if args.phase:
            tsAPI.setDataSource(tsId, DataSource.DATA_KIND, (DataKind.PHASE).value)
            print("{}: Importing time series of phase".format(tsId))
        elif args.power:
            tsAPI.setDataSource(tsId, DataSource.DATA_KIND, (DataKind.POWER).value)
            print("{}: Importing time series of power".format(tsId))
        elif args.voltage:
            tsAPI.setDataSource(tsId, DataSource.DATA_KIND, (DataKind.VOLTAGE).value)
            print("{}: Importing time series of voltage".format(tsId))
        else:
            tsAPI.setDataSource(tsId, DataSource.DATA_KIND, (DataKind.AMPLITUDE).value)
            print("{}: Importing time series of amplitude".format(tsId))

        timeStamps = []
        dataSeries = []
        temperatures1 = []
        temperatures2 = []
        dataLen = 0
        CHUNK_SIZE = 1000   # max records to insert at a time

        # main read and insert loop.  Inserts up to CHUNK_SIZE records per datbase round-trip:
        try:
            with open(file, 'r', newline = '') as f:
                reader = csv.reader(f, delimiter = args.delim)
                reset = True
                for line in reader:
                    if reset:
                        timeStamps = []
                        dataSeries = []
                        temperatures1 = []
                        temperatures2 = []
                        dataLen = 0
                        reset = False
                    
                    # skip header and comment lines:
                    if line[0][0].isnumeric():
                        dataLen += 1
                        y = float(line[args.data_col])
                        # convert dBm to W:
                        if importUnits == Units.DBM:
                            y = (10 ** (y / 10)) / 1000
                        
                        dataSeries.append(y)
                        if args.timestamp_col is not None:
                            timeStamps.append(line[args.timestamp_col])
                        if args.temp1_col is not None:
                            temperatures1.append(float(line[args.temp1_col]))
                        if args.temp2_col is not None:
                            temperatures2.append(float(line[args.temp2_col]))
            
                    # write chunk?
                    if dataLen == CHUNK_SIZE:
                        tsAPI.insertTimeSeriesChunk(dataSeries, temperatures1, temperatures2, timeStamps)
                        # flush to force the database query to fire:
                        tsAPI.finishTimeSeries()
                        reset = True
    
                # write final partial chunk and finish:
                if dataLen:
                    tsAPI.insertTimeSeriesChunk(dataSeries, temperatures1, temperatures2, timeStamps)
                    tsAPI.finishTimeSeries()
            
        except OSError:
            print("Could not open file '{0}'".format(file))
            return False
        
        except TypeError:
            print("File format error '{0}'. One or more requested columns is not present.".format(file))
            return False
        
        if len(dataSeries) < 2:
            print("Data file is too short '{0}'".format(file))
            return False

    # set all the specified data source attributes:
    if args.config_id:
        tsAPI.setDataSource(tsId, DataSource.CONFIG_ID, args.config_id)
    if args.test_system:
        tsAPI.setDataSource(tsId, DataSource.TEST_SYSTEM, args.test_system)
    tsAPI.setDataSource(tsId, DataSource.UNITS, args.units)
    tsAPI.setDataSource(tsId, DataSource.T_UNITS, args.temp_units)
    if lo:
        tsAPI.setDataSource(tsId, DataSource.LO_GHZ, lo)
    if rf:
        tsAPI.setDataSource(tsId, DataSource.RF_GHZ, rf)
    if args.tilt_angle:
        tsAPI.setDataSource(tsId, DataSource.TILT_ANGLE, args.tilt_angle)
    if args.system_name:
        tsAPI.setDataSource(tsId, DataSource.SYSTEM, args.system_name)
    if args.subsystem:
        tsAPI.setDataSource(tsId, DataSource.SUBSYSTEM, args.subsystem)
    if notes:
        tsAPI.setDataSource(tsId, DataSource.NOTES, notes)
    if args.meas_sw_name:
        tsAPI.setDataSource(tsId, DataSource.MEAS_SW_NAME, args.meas_sw_name)
    if args.meas_sw_version:
        tsAPI.setDataSource(tsId, DataSource.MEAS_SW_VERSION, args.meas_sw_version)
    tsAPI.setDataSource(tsId, DataSource.DATA_SOURCE, file)
    
    # set the initial DataStatus tag:
    tsAPI.setDataStatus(tsId, DataStatus.UNKNOWN)
    return tsId
        
def makeSingleTracePlots(tsId, title, args):
    made = []
    show = True if args.show else False

    if args.make_ts_plot:
        print("{}: Making time series plot".format(tsId))
        plotElements = {}
        if title:
            plotElements[PlotEl.TITLE] = title
        if args.ts_xunits:
            plotElements[PlotEl.XUNITS] = args.ts_xunits
        if args.ts_xlabel:
            plotElements[PlotEl.X_AXIS_LABEL] = args.ts_xlabel
        if args.ts_yunits:
            plotElements[PlotEl.YUNITS] = args.ts_yunits
        if args.ts_ylabel:
            plotElements[PlotEl.Y_AXIS_LABEL] = args.ts_ylabel
        if args.ts_y2units:
            plotElements[PlotEl.Y2UNITS] = args.ts_y2units
        if args.ts_yslabel:
            plotElements[PlotEl.Y2_AXIS_LABEL] = args.ts_yslabel  
        made.append(plotAPI.plotTimeSeries(tsId, plotElements, args.ts_output_file, show))

    if args.make_fft_plot:
        print("{}: Making FFT plot".format(tsId))
        plotElements = {}
        if title:
            plotElements[PlotEl.TITLE] = title
        if args.fft_xlabel:
            plotElements[PlotEl.X_AXIS_LABEL] = args.fft_xlabel
        if args.fft_yunits:
            plotElements[PlotEl.YUNITS] = args.fft_yunits
        if args.fft_ylabel:
            plotElements[PlotEl.Y_AXIS_LABEL] = args.fft_ylabel
        made.append(plotAPI.plotSpectrum(tsId, plotElements, args.fft_output_file, show))
    return made

def makeMultiTracePlot(timeSeriesIds, title, args):
    made = []
    show = True if args.show else False
    
    if args.make_stability_plot:
        print("Making stability plot with {} traces".format(len(timeSeriesIds)))
        plotElements = {}
        if title:
            plotElements[PlotEl.TITLE] = title
        if args.stab_xunits:
            plotElements[PlotEl.XUNITS] = args.stab_xunits
        if args.stab_xlabel:
            plotElements[PlotEl.X_AXIS_LABEL] = args.stab_xlabel
        if args.stab_yunits:
            plotElements[PlotEl.YUNITS] = args.stab_yunits
        if args.stab_ylabel:
            plotElements[PlotEl.Y_AXIS_LABEL] = args.stab_ylabel
        
        dataKind = DataKind.fromStr(tsAPI.getDataSource(timeSeriesIds[0], DataSource.DATA_KIND, (DataKind.AMPLITUDE).value))
        if dataKind == DataKind.PHASE:
            made.append(plotAPI.plotPhaseStability(timeSeriesIds, plotElements, args.stability_output_file, show))
        else:
            made.append(plotAPI.plotAmplitudeStability(timeSeriesIds, plotElements, args.stability_output_file, show))
    return made
    
def plotFromResult(resultId, args):
    made = []
    return made
        
if __name__ == '__main__':
    main()
