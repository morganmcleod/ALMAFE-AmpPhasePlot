'''
Plot.Plotly.Common:  functions used in more than one plot
'''
from AmpPhaseDataLib.Constants import PlotEl

def addFooters(fig, footer1, footer2, footer3):
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

def makePlotOutput(fig, plotElements, outputName = None, show = False):
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
        
