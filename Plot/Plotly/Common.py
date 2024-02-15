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
    if specLine:
        specName = plotElements.get(PlotEl.SPEC1_NAME, "Specification")
        specLine = specLine.split(',')
        x1 = float(specLine[0])
        y1 = float(specLine[1])
        x2 = float(specLine[2])
        y2 = float(specLine[3])
        
        # show spec line 1 in black:
        specLines = dict(color='black', width=3)
        specMarks = dict(color='black', symbol='square', size=7)

        # use a square marker if both endpoints are the same:
        if x1 == x2 and y1 == y2:
            fig.add_trace(go.Scatter(x = [x1, x2], y = [y1, y2], mode = 'markers', marker = specMarks, name = specName))
        else:
            fig.add_trace(go.Scatter(x = [x1, x2], y = [y1, y2], mode = 'lines', line = specLines, name = specName))

    # add spec line 2, if defined:
    specLine = plotElements.get(PlotEl.SPEC_LINE2, None)
    if specLine:
        specName = plotElements.get(PlotEl.SPEC2_NAME, None)
        specLine = specLine.split(',')
        x1 = float(specLine[0])
        y1 = float(specLine[1])
        x2 = float(specLine[2])
        y2 = float(specLine[3])
        
        # name for spec line 2 defaults to value of y2:
        if not specName:
            specName = "Spec {:.1e}".format(y2)

        # show spec line 2 in brick red:
        specLines = dict(color='firebrick', width=3)
        specMarks = dict(color='firebrick', symbol='square', size=7)
        
        # use a square marker if both endpoints are the same:
        if x1 == x2 and y1 == y2:
            fig.add_trace(go.Scatter(x = [x1, x2], y = [y1, y2], mode = 'markers', marker = specMarks, name = specName))
        else:
            fig.add_trace(go.Scatter(x = [x1, x2], y = [y1, y2], mode = 'lines', line = specLines, name = specName))

def addFooters(fig, plotElements):
    '''
    Common Plotly implementation for adding footers
    :param fig: plotly.graph_objects.Figure
    :param plotElements dict having keys 'FOOTER1' 'FOOTER2' 'FOOTER3' optional 'FOOTER4'
    '''
    # make room at the bottom for footers:
    fig.update_layout(margin=dict(b=126))
    
    # add the footers:
    fig.update_layout(
        annotations=[
            dict(
                x=0,
                y=0,
                showarrow=False,
                text="",            # UGLY work-around a Plotly bug where it 
                xref="paper",       # sometimes doesn't show the first annotation
                yref="paper",
                xshift=-50,
                yshift=-75
            ),
            dict(
                x=0,
                y=0,
                showarrow=False,
                text=plotElements.get(PlotEl.FOOTER1, ''),
                xref="paper",
                yref="paper",
                xshift=-50,
                yshift=-80
            ),
            dict(
                x=0,
                y=0,
                showarrow=False,
                text=plotElements.get(PlotEl.FOOTER2, ''),
                xref="paper",
                yref="paper",
                xshift=-50,
                yshift=-95
            ),
            dict(
                x=0,
                y=0,
                showarrow=False,
                text=plotElements.get(PlotEl.FOOTER3, ''),
                xref="paper",
                yref="paper",
                xshift=-50,
                yshift=-110
            ),
            dict(
                x=0,
                y=0,
                showarrow=False,
                text=plotElements.get(PlotEl.FOOTER4, ''),
                xref="paper",
                yref="paper",
                xshift=-50,
                yshift=-125
            )
        ])
    
def addComplianceString(fig, compliance):
    fig.update_layout(
        annotations=[
            dict(
                x=0.5,
                y=1,
                showarrow=False,
                text=compliance,
                xref="paper",
                yref="paper",
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
