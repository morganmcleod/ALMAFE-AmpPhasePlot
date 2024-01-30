'''
Common functions used by plotting routines
'''
from AmpPhaseDataLib.Constants import PlotEl, DataSource

def makeTitle(timeSeriesIds, dataSources, plotElements):
    '''
    Make a title string from available items in dataSources, plotElements
    Also updates plotElements with the title string
    :param timeSeriesIds: list of int timeSeriesId
    :param plotElements: dict of {PlotEl : str}
    :return str title
    '''

    if not len(timeSeriesIds):
        return None

    title = plotElements.get(PlotEl.TITLE, "")
    
    if DataSource.SYSTEM in dataSources:
        title += ": " if title else ""
        title += dataSources[DataSource.SYSTEM]
    
    if len(timeSeriesIds) == 1:
        if DataSource.SUBSYSTEM in dataSources:
            title += ", " if title else ""
            title += dataSources[DataSource.SUBSYSTEM]
        if DataSource.LO_GHZ in dataSources:
            title += ", " if title else ""
            title += "LO={} GHz".format(dataSources[DataSource.LO_GHZ])
        if DataSource.RF_GHZ in dataSources:
            title += ", " if title else ""
            title += "RF={} GHz".format(dataSources[DataSource.RF_GHZ])
    
    serialNums = []
    for timeSeriesId in timeSeriesIds:            
        serialNum = dataSources.get(DataSource.SERIALNUM, None)
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

def makeFooters(timeSeriesIds, dataSources, plotElements, startTime):
    '''
    Make three footer strings from available items in dataSources, plotElements, allDataStatus
    Also updates plotElements with the footer strings
    :param timeSeriesIds: list of int timeSeriesId
    :param plotElements:  dict of {PlotEl : str}
    :param startTime: datetime from TimeSeries
    :return (footer1, footer2, footer3)
    '''
    if not len(timeSeriesIds):
        return None

    # Footer1 text:
    whenMeas = startTime.strftime('%a %Y-%m-%d %H:%M:%S')
    measSwname = dataSources.get(DataSource.MEAS_SW_NAME, "unknown")
    measSwVer = dataSources.get(DataSource.MEAS_SW_VERSION, "unknown")
    testSystem = dataSources.get(DataSource.TEST_SYSTEM, "unknown")
    
    configIds = set()
    for timeSeriesId in timeSeriesIds:
        configId = dataSources.get(DataSource.CONFIG_ID, None)
        if configId:
            configIds.add(str(configId))

    idStr = ",".join(map(str, timeSeriesIds))
    configStr = ",".join(configIds)
                                
    plural = 's' if len(timeSeriesIds) > 1 else ''
    
    footer1 = f"Config{plural}: {configStr if configStr else 'unknown'} | Key{plural}: {idStr} | Measured: {whenMeas}"
    plotElements[PlotEl.FOOTER1] = footer1

    # Footer2 text:
    footer2 = "Meas SW: {0} | Ver: {1} | TestSys: {2}".format(measSwname, measSwVer, testSystem)
    plotElements[PlotEl.FOOTER2] = footer2

    # Footer3 text:
    if len(timeSeriesIds) == 1:
        dataSource = dataSources.get(DataSource.DATA_SOURCE, "unknown")
        footer3 = "Source: " + dataSource
    else:
        footer3 = ""
    
    processNotes = plotElements.get(PlotEl.PROCESS_NOTES, None)
    if processNotes:
        if footer3:
            footer3 += " | "
        footer3 += processNotes
    
    wrap = 120
    if len(footer3) > wrap:
        plotElements[PlotEl.FOOTER3] = footer3[:wrap]
        plotElements[PlotEl.FOOTER4] = footer3[wrap:]
    else:
        plotElements[PlotEl.FOOTER3] = footer3
        
    return (footer1, footer2, footer3)
