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
    dataSources = tsAPI.getAllDataSource(timeSeriesIds[0])
    
    if DataSource.SYSTEM in dataSources:
        title += ": " if title else ""
        title += dataSources[DataSource.SYSTEM]
    
    if len(timeSeriesIds) == 1:
        if DataSource.SUBSYSTEM in dataSources:
            title += ", " if title else ""
            title += dataSources[DataSource.SUBSYSTEM]
        if DataSource.LO_GHZ in dataSources:
            title += ", " if title else ""
            title += " LO={} GHz".format(dataSources[DataSource.LO_GHZ])
        if DataSource.RF_GHZ in dataSources:
            title += ", " if title else ""
            title += " RF={} GHz".format(dataSources[DataSource.RF_GHZ])
    
    serialNums = []
    for timeSeriesId in timeSeriesIds:            
        serialNum = tsAPI.getDataSource(timeSeriesId, DataSource.SERIALNUM)
        if serialNum:
            serialNums.append(serialNum)                
    if serialNums:
        # remove duplicates:
        serialNums = list(set(serialNums))
        serialString = ""
        for s in serialNums:
            serialString += ", " if serialString else ""
            serialString += s
        title += " SN: " + serialString

    if not title and DataSource.DATA_SOURCE in dataSources:
        title = dataSources[DataSource.DATA_SOURCE]

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
    
    processNotes = plotElements.get(PlotEl.PROCESS_NOTES, None)
    if processNotes:
        if footer3:
            footer3 += " | "
        footer3 += processNotes
    plotElements[PlotEl.FOOTER3] = footer3
    
    return (footer1, footer2, footer3)
