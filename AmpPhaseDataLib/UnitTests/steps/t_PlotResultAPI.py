'''
Implement test cases for t_PlotResultAPI.feature
Validate PlotResultAPI
'''
from behave import given, when, then 
from AmpPhaseDataLib.Constants import PlotKind, DataStatus, DataSource, PlotEl
from hamcrest import assert_that, equal_to

@given('the description "{description}"')
def step_impl(context, description):
    '''
    :param context: behave.runner.Context
    '''
    context.description = description
    
@when('the PlotResult is created') 
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    context.plotResultId = context.API.create(context.description)
    assert_that(context.plotResultId)
    
@then('the PlotResult can be retrieved and verified')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    result = context.API.retrieve(context.plotResultId)
    assert_that(result[0], equal_to(context.plotResultId))
    assert_that(result[1], equal_to(context.description))
    
@then('the PlotResult can be deleted')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    context.API.delete(context.plotResultId)
    result = context.API.retrieve(context.plotResultId)
    assert_that(result, equal_to(None))
    result = context.API.retrieve(context.plotResultId)
    assert_that(not result)

@when('the Image is created') 
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    context.plotKind = PlotKind.TIME_SERIES
    context.imagePath = "AmpPhaseDataLib/UnitTests/steps/Cone of dining (Paris) June 2020.jpg"
    context.imageName = "cone of dining!"
    context.plotImageId = context.API.insertPlotImageFromFile(context.plotResultId, context.imagePath, context.imageName, context.plotKind)
    assert_that(context.plotImageId)
    
@then('the Plot can be retrieved and verified')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    image = context.API.retrievePlotImage(context.plotResultId)
    assert_that(image[0], equal_to(context.plotResultId))
    assert_that(image[3], equal_to(context.plotKind))
     
@then('the Image can be retrieved and verified')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    image = context.API.retrievePlotImage(context.plotImageId)
    assert_that(image[0], equal_to(context.plotResultId))
    assert_that(image[1], equal_to(context.plotImageId))
    assert_that(image[2], equal_to(context.imageName))
    assert_that(image[3], equal_to(context.plotKind))
    assert_that(image[4], equal_to(context.imagePath))
    
    with open(context.imagePath, 'rb') as file:
        imageData = file.read()
    assert_that(image[5], equal_to(imageData))
          
@then('the Image can be deleted')
def step_impl(context):
    '''
    :param context: behave.runner.Context
    '''
    context.API.deletePlotImage(context.plotImageId)
    result = context.API.retrievePlotImage(context.plotImageId)
    assert_that(result, equal_to(None))

@when('DataStatus tag "{tagName}" is set')
def step_impl(context, tagName):
    '''
    :param context: behave.runner.Context
    '''
    dataStatus = DataStatus[tagName]
    context.resultTags[dataStatus.value] = True
    context.API.setDataStatus(context.plotResultId, dataStatus)

@then('DataStatus tag "{tagName}" can be retrieved and the value matches')
def step_impl(context, tagName):
    '''
    :param context: behave.runner.Context
    '''
    dataStatus = DataStatus[tagName]
    result = context.API.getDataStatus(context.plotResultId, dataStatus)
    assert_that(result, equal_to(True))    

@then('DataStatus tag "{tagName}" can be removed')
def step_impl(context, tagName):
    '''
    :param context: behave.runner.Context
    '''
    dataStatus = DataStatus[tagName]
    del context.resultTags[dataStatus.value] 
    context.API.clearDataStatus(context.plotResultId, dataStatus)
    result = context.API.getDataStatus(context.plotResultId, dataStatus)
    assert_that(result, equal_to(False))    
    
@when('Result DataSource tag "{tagName}" is set with value "{tagValue}"')
def step_impl(context, tagName, tagValue):
    """
    :param context: behave.runner.Context
    :param tagName: str
    :param tagValue: str
    """
    dataSource = DataSource[tagName]
    context.resultTags[dataSource.value] = tagValue
    context.API.setDataSource(context.plotResultId, dataSource, tagValue)
    
@then('we can retrieve Result DataSource tag "{tagName}" and the value matches')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    dataSource = DataSource[tagName]
    result = context.API.getDataSource(context.plotResultId, dataSource)
    retrieved = context.resultTags[dataSource.value]
    assert_that(result, equal_to(retrieved))
    
@then('we can delete Result DataSource tag "{tagName}"')
def step_impl(context, tagName):
    """
    :param context: behave.runner.Context
    :param tagName: str
    """
    dataSource = DataSource[tagName]
    del context.resultTags[dataSource.value]
    context.API.clearDataSource(context.plotResultId, dataSource)
    result = context.API.getDataSource(context.plotResultId, dataSource)
    assert_that(not result)
    