'''
Plot.Plotly.Common:  functions used in more than one plot
'''
import plotly.graph_objects as go
from AmpPhaseDataLib.Constants import PlotEl

def addSpecLines(fig, plotElements):
    '''
    Common Plotly implemenation for adding spec lines 
    :param fig: plotly.graph_objects.Figure
    :param plotElements: dict of {PlotEl : str}
    '''
    # add spec line 1, if defined:
    specLine = plotElements.get(PlotEl.SPEC_LINE1, None)
    specName = plotElements.get(PlotEl.SPEC1_NAME, "Specification")
    if specLine:
        specLine = specLine.split(', ')
        x1 = float(specLine[0])
        y1 = float(specLine[1])
        x2 = float(specLine[2])
        y2 = float(specLine[3])
        specLines = dict(color='black', width=3)
        fig.add_trace(go.Scatter(x = [x1, x2], y = [y1, y2], mode = 'lines', line = specLines, name = specName))

    # add spec line 2, if defined:
    specLine = plotElements.get(PlotEl.SPEC_LINE2, None)
    specName = plotElements.get(PlotEl.SPEC2_NAME, None)
    if specLine:
        specLine = specLine.split(', ')
        x1 = float(specLine[0])
        y1 = float(specLine[1])
        x2 = float(specLine[2])
        y2 = float(specLine[3])
        
        # name for spec line 2 defaults to y2:
        if not specName:
            specName = "Spec {:.1e}".format(y2)

        specLines = dict(color='firebrick', width=3)
        specMarks = dict(color='firebrick', symbol='square', size=7)
        
        # use a square marker if both endpoints are the same:
        if x1 == x2 and y1 == y2:
            fig.add_trace(go.Scatter(x = [x1, x2], y = [y1, y2], mode = 'markers', marker = specMarks, name = specName))
        else:
            fig.add_trace(go.Scatter(x = [x1, x2], y = [y1, y2], mode = 'lines', line = specLines, name = specName))

def addFooters(fig, footer1, footer2, footer3):
    '''
    Common Plotly implementation for adding footers
    :param fig: plotly.graph_objects.Figure
    :param footer1: str
    :param footer2: str
    :param footer3: str
    '''
    # make room at the bottom for footers:
    fig.update_layout(margin=dict(b=110))
    
    # add the footers:
    fig.update_layout(
        annotations=[
            dict(
                x=0,
                y=0,
                showarrow=False,
                text=footer1,
                xref="paper",
                yref="paper",
                xshift=-50,
                yshift=-80
            ),
            dict(
                x=0,
                y=0,
                showarrow=False,
                text=footer2,
                xref="paper",
                yref="paper",
                xshift=-50,
                yshift=-95
            ),
            dict(
                x=0,
                y=0,
                showarrow=False,
                text=footer3,
                xref="paper",
                yref="paper",
                xshift=-50,
                yshift=-110
            )
        ])
    
def addComplianceString(fig, compliance):
    fig.update_layout(
        annotations=[
            dict(
                x=0,
                y=0,
                showarrow=False,
                text=compliance,
                xshift=0,
                yshift=0
            )
        ])

def makePlotOutput(fig, plotElements, outputName = None, show = False):
    '''
    Common Plotly implementation for producing plot output
    :param fig: plotly.graph_objects.Figure
    :param plotElements: dict of {PlotEl : str}
    :param outputName: optional filename where to write the plot .PNG file
    :param show: if True, displays the plot using the default renderer.
    :return binary imageData
    '''
    # show interactive:
    if show:
        fig.show()

    # make .png output:
    width = int(plotElements.get(PlotEl.IMG_WIDTH, "800"))
    plotElements[PlotEl.IMG_WIDTH] = str(width) 
    height = int(plotElements.get(PlotEl.IMG_HEIGHT, "500"))
    plotElements[PlotEl.IMG_HEIGHT] = str(height) 

    imageData = fig.to_image(format = "png", width = width, height = height)
    
    # save to file, if requested:
    if outputName:
        with open(outputName, 'wb') as file:
            file.write(imageData)
            
    return imageData
