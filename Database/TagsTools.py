'''
Functions to help use DataStatus, DataSource, and PlotEl tags in a consistent way 
'''

from AmpPhaseDataLib.Constants import DataStatus

def applyDataStatusRules(dataStatus):
    '''
    Apply rules for mutually exclusive DataStatus tags
    :param dataStatus: DataStatus enum from Constants.py
    :return dict of { tag str : value } where some values are None to remove those tags 
    '''
    if not isinstance(dataStatus, DataStatus):
        raise ValueError('Use DataStatus enum from Constants.py')

    tags = {dataStatus.value : "1"}
    # setting any other tag will clear UNKNOWN        
    if dataStatus is not DataStatus.UNKNOWN:
        tags[DataStatus.UNKNOWN.value] = None
        
    # setting TO_DELETE will clear TO_RETAIN:
    if dataStatus is DataStatus.TO_DELETE:
        tags[DataStatus.TO_RETAIN.value] = None
        
    # setting TO_RETAIN will clear TO_DELETE:
    elif dataStatus is DataStatus.TO_RETAIN:
        tags[DataStatus.TO_DELETE.value] = None
    
    # setting MEET_SPEC will clear FAIL_SPEC        
    elif dataStatus is DataStatus.MEET_SPEC:
        tags[DataStatus.FAIL_SPEC.value] = None
    
    # setting FAIL_SPEC will clear MEET_SPEC
    elif dataStatus is DataStatus.FAIL_SPEC:
        tags[DataStatus.MEET_SPEC.value] = None
    return tags

def getDataStatusString(tags):
    '''
    Given a collection of DataStatus tags generate a summary string for display
    :param tags: dict of {DataStatus : value} 
    :return str
    '''
    if int(tags.get(DataStatus.UNKNOWN, '0')):
        return DataStatus.UNKNOWN.value
    result = ''
    
    if int(tags.get(DataStatus.MEET_SPEC, False)):
        result += DataStatus.MEET_SPEC.value
    elif int(tags.get(DataStatus.FAIL_SPEC, False)):
        result += DataStatus.FAIL_SPEC.value
    
    if result:
        result += ", "
    
    if int(tags.get(DataStatus.TO_RETAIN, False)):
        result += DataStatus.TO_RETAIN.value
    elif int(tags.get(DataStatus.TO_DELETE, False)):
        result += DataStatus.TO_DELETE.value
    
    if not result:
        result = DataStatus.UNKNOWN.value
    return result
    