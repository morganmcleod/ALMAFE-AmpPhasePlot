'''
test generating plots from time series via the AmpPhasePlot app command-line interface
'''
from behave import given, when, then
from hamcrest import assert_that, equal_to, close_to, greater_than
from Apps.AmpPhasePlot import main as AppPhasePlot_main
from tempfile import NamedTemporaryFile
import sys
import os

##### GIVEN #####

@given('an amplitude time series data file on disk')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.dataFile = "SampleData\\FETMS-Amp\\B2Ae0LO74pol0USB_20180410-081528__.txt"
    context.tau0Seconds = '0.05'
    context.tsColumn = '0'
    context.dataColumn = '2'
    context.temp1Column = '4'
    context.temp2Column = '5'
    context.delimiter = '\t'
    context.kind = "--power"
    context.units = "W"
    
@given('a phase time series data file on disk')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.dataFile = "SampleData\\FETMS-Phase\\B6Pe0RF215pol0_20200205-153444__.txt"
    context.tau0Seconds = '1.0'
    context.tsColumn = '0'
    context.dataColumn = '2'
    context.temp1Column = '5'
    context.temp2Column = '6'
    context.delimiter = '\t'
    context.kind = "--phase"
    context.units = "deg"
    
@given('we want to show the plots')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.show = True    

##### WHEN #####
    
@when('the data is loaded and the plots generated')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    f = NamedTemporaryFile(suffix = '.png', delete = True)
    context.ts_output_file = f.name
    f.close()
    assert_that(not os.path.isfile(context.ts_output_file))

    f = NamedTemporaryFile(suffix = '.png', delete = True)
    context.fft_output_file = f.name
    f.close()
    assert_that(not os.path.isfile(context.fft_output_file))
    
    f = NamedTemporaryFile(suffix = '.png', delete = True)
    context.stability_output_file = f.name
    f.close()
    assert_that(not os.path.isfile(context.stability_output_file))
    
    sys.argv[1:] = ['-f', context.dataFile, context.kind, '--tsc', context.tsColumn, 
                    '--dc', context.dataColumn, '--tc1', context.temp1Column,
                    '--tc2', context.temp2Column, '--delim', context.delimiter,
                    '-u', context.units, '--tau', context.tau0Seconds,
                    '--ts_output_file', context.ts_output_file,
                    '--fft_output_file', context.fft_output_file,
                    '--stability_output_file', context.stability_output_file,
                    '--stab_fe_amp_spec']
    
    if context.show:
        sys.argv.append('--show')
    
    AppPhasePlot_main()
    