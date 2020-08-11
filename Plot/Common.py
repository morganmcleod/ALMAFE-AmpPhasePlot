'''
Common functions used by plotting routines
'''
from AmpPhaseDataLib import TimeSeriesAPI
from AmpPhaseDataLib.Constants import PlotEl, DataSource
from Database.TagsTools import getDataStatusString

def makeTitle(timeSeriesIds, plotElements):
    '''
    Make a title string from available items in dataSources, plotElements
    Also updates plotElements with the title string
    :param timeSeriesIds: list of int timeSeriesId
    :param plotElements: dict of {PlotEl : str}
    :return str title
    '''

    if not len(timeSeriesIds):
        return None

    tsAPI = TimeSeriesAPI.TimeSeriesAPI()

    title = plotElements.get(PlotEl.TITLE, "")
    system = tsAPI.getDataSource(timeSeriesIds[0], DataSource.SYSTEM)
    if system:
        if title:
            title += ": "
        title += system
    
    if len(timeSeriesIds) == 1:
        if not title:
            dataSource = tsAPI.getDataSource(timeSeriesIds[0], DataSource.DATA_SOURCE)
            title = dataSource if dataSource else ""
        if not title:
            serialNum = tsAPI.getDataSource(timeSeriesIds[0], DataSource.SERIALNUM)
            title = serialNum if serialNum else ""
    else:
        serialNums = ""
        for timeSeriesId in timeSeriesIds:            
            serialNum = tsAPI.getDataSource(timeSeriesId, DataSource.SERIALNUM)
            if serialNum:
                if serialNums:
                    serialNums += ", "
                serialNums += serialNum
        if serialNums:
            title += " SN: " + serialNums

    plotElements[PlotEl.TITLE] = title
    return title

def makeFooters(timeSeriesIds, plotElements, allDataStatus, startTime):
    '''
    Make three footer strings from available items in dataSources, plotElements, allDataStatus
    Also updates plotElements with the footer strings
    :param timeSeriesIds: list of int timeSeriesId
    :param plotElements:  dict of {PlotEl : str}
    :param allDataStatus: dict of {DataStatus : str}
    :param startTime: datetime from TimeSeries
    :return (footer1, footer2, footer3)
    '''
    if not len(timeSeriesIds):
        return None

    tsAPI = TimeSeriesAPI.TimeSeriesAPI()

    # Footer1 text:
    whenMeas = startTime.strftime('%a %Y-%m-%d %H:%M:%S')
    measSwname = tsAPI.getDataSource(timeSeriesIds[0], DataSource.MEAS_SW_NAME, "unknown")
    measSwVer = tsAPI.getDataSource(timeSeriesIds[0], DataSource.MEAS_SW_VERSION, "unknown")
    testSystem = tsAPI.getDataSource(timeSeriesIds[0], DataSource.TEST_SYSTEM, "unknown")
    dataStatus = getDataStatusString(allDataStatus) 
    
    idStr = ""
    configStr = ""
    for timeSeriesId in timeSeriesIds:
        if idStr:
            idStr += ", "
        idStr += str(timeSeriesId)
        configId = tsAPI.getDataSource(timeSeriesId, DataSource.CONFIG_ID)
        if configId:
            if configStr:
                configStr += ", "
            configStr += configId
    
    plural = len(timeSeriesIds) > 1
    
    footer1 = "Config{}: {} | DataStatus: {} | Key{}: {} | Measured: {}".format(
        "s" if plural else "",
        configStr if configStr else "unknown", 
        dataStatus, 
        "s" if plural else "",
        idStr, 
        whenMeas)
    plotElements[PlotEl.FOOTER1] = footer1

    # Footer2 text:
    footer2 = "Meas SW: {0} | Ver: {1} | TestSys: {2}".format(measSwname, measSwVer, testSystem)
    plotElements[PlotEl.FOOTER2] = footer2

    # Footer3 text:
    if len(timeSeriesIds) == 1:
        dataSource = tsAPI.getDataSource(timeSeriesIds[0], DataSource.DATA_SOURCE, "unknown")
        footer3 = "Source: " + dataSource
    else:
        footer3 = ""
    plotElements[PlotEl.FOOTER3] = footer3
    
    return (footer1, footer2, footer3)
