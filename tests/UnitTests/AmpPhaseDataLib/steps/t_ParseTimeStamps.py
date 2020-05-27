'''
Implement test cases for t_ParseTimeStamps.feature
Validate AmpPhaseDataLib API
'''
from behave import given, when, then 
from AmpPhaseDataLib import ParseTimeStamp
from hamcrest import assert_that, equal_to, is_not, instance_of
from datetime import datetime

@given('dateTime string "{timeStampString}"')
def step_impl(context, timeStampString):
    """
    :param context: behave.runner.Context
    :param timeStampString: a valid dateTime string
    """
    context.timeStampString = timeStampString

@when('the test is run')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    context.tsParser = ParseTimeStamp.ParseTimeStamp()
    context.result = context.tsParser.parseTimeStamp(context.timeStampString)

@then('a valid datetime is returned')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.result, instance_of(datetime))

@then('a valid datetime will not be returned')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.result, is_not(instance_of(datetime)))
    
@then('the matching format string is stored')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.tsParser.lastTimeStampFormat, instance_of(str))

@then('no matching format string is stored')
def step_impl(context):
    """
    :param context: behave.runner.Context
    """
    assert_that(context.tsParser.lastTimeStampFormat, is_not(instance_of(str)))
    
@then('the milliseconds equals "{msString}"')
def step_impl(context, msString):
    """
    :param context: behave.runner.Context
    :param msString: integer number of milliseconds
    """
    ms = int(msString)
    assert_that(context.result.microsecond, equal_to(ms * 1000))
