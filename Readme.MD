# ALMAFE-AmpPhasePlot
Libraries for plotting and data management of Amplitude, Phase, and Voltage stability, both raw data and results.

[AmpPhaseDataLib](AmpPhaseDataLib/Readme.MD)  

[AmpPhasePlotLib](AmpPhasePlotLib/Readme.MD)

These libraries are tailored to the system requirements of the ALMA Front End and its sub-assemblies but are intended to be flexible enough to use for other purposes.

## Rationale:
Typically when measuring stability, a long Time Series is captured and stored in a local file or is inserted into a database.  Later when analysis is performed, more compact Results and Plots are produced. The end state is typically that the Time Series data are never looked at again, but linger on disk of the measurement workstation or a database server forever.  Likewise, the discarded Results and Plots are never cleaned up.

The intent of these libraries is to produce full-featured plots plus manage the long-term storage or disposal of Time Series, Results, and Plots.

See FEND-40.09.03.00-0522-A-SPE for additional background.

## Demo Jupyter Notebook

Copy [ALMAFE-AmpPhasePlot-demo.ipynb](https://www.dropbox.com/s/0gi4soxm0om50hy/ALMAFE-AmpPhasePlot-demo.ipynb?dl=0) to your user directory then launch Jupyter Notebook.
Open the notebook and fix up the working directory in the first frame to match your system. 

## Installation / Deployment

**Requires locally installed Orca**
But only if you need to make .PNG files on disk.

You may be able to work around this requirement by retrieving
each plot as binary data and writing the file yourself.
https://github.com/plotly/orca/releases

For some use cases, requires MySQL or compatible server for Results storage.
User account will need CREATE TABLE, CREATE, UPDATE, INSERT, DELETE privs.
Or alternately run once with CREATE TABLE privs and then restrict thereafter.

The file AmpPhaseDataLib.ini must be set up with the MySQL database credentials on your client.
