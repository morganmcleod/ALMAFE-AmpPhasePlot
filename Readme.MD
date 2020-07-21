# ALMAFE-AmpPhasePlot
Libraries for plotting and data management of Amplitude, Phase, and Voltage stability raw data and results.

These libraries are tailored to the system requirements of ALMA telescope Front End and its sub-assemblies but are intended to be flexible enough to use for other purposes.

Typically when measuring stability, a long Time Series is captured and stored in a local file or is inserted into a database.  Later when analysis is performed, more compact Result Files and Plots are produced.  The end state is typically that the Time Series files are never looked at again, but linger on disk of the measurement workstation or a database server forever.  Likewise, the discarded Result Files and Plots are never cleaned up.

The intent of these libraries is to produce full-featured plots plus manage the long-term storage or disposal of Time Series, Results, and Plots.

See FEND-40.09.03.00-0522-A-SPE for additional background.

## Installation / Deployment

Requires locally installed SQLite
On Windows, install SQLite and make sure it is on the PATH:
https://www.sqlite.org/download.html

Requires MySQL or compatible server for Results storage.
User account will need CREATE TABLE, CREATE, UPDATE, INSERT, DELETE privs.
Or alternately run once with CREATE TABLE privs and then restrict thereafter.
