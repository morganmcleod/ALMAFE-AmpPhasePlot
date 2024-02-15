"""
Allan deviation tools
=====================

**Author:** Anders Wallin (anders.e.e.wallin "at" gmail.com)
Extracted from https://github.com/aewallin/allantools
"""

import numpy as np

def adev(data, rate=1.0, data_type="phase", taus=None):
    """ Allan deviation.
        Classic - use only if required - relatively poor confidence.

    .. math::

        \\sigma^2_{ADEV}(\\tau) = { 1 \\over 2 \\tau^2 }
        \\langle ( {x}_{n+2} - 2x_{n+1} + x_{n} )^2 \\rangle
        = { 1 \\over 2 (N-2) \\tau^2 }
        \\sum_{n=1}^{N-2} ( {x}_{n+2} - 2x_{n+1} + x_{n} )^2

    where :math:`x_n` is the time-series of phase observations, spaced
    by the measurement interval :math:`\\tau`, and with length :math:`N`.

    Or alternatively calculated from a time-series of fractional frequency:

    .. math::

        \\sigma^{2}_{ADEV}(\\tau) =  { 1 \\over 2 }
        \\langle ( \\bar{y}_{n+1} - \\bar{y}_n )^2 \\rangle

    where :math:`\\bar{y}_n` is the time-series of fractional frequency
    at averaging time :math:`\\tau`


    Parameters
    ----------
    data: np.array
        Input data. Provide either phase or frequency (fractional,
        adimensional).
    rate: float
        The sampling rate for data, in Hz. Defaults to 1.0
    data_type: {'phase', 'freq'}
        Data type, i.e. phase or frequency. Defaults to "phase".
    taus: np.array
        Array of tau values, in seconds, for which to compute statistic.
        Optionally set taus=["all"|"octave"|"decade"] for automatic
        tau-list generation.

    Returns
    -------
    (taus2, ad, ade, ns): tuple
          Tuple of values
    taus2: np.array
        Tau values for which td computed
    ad: np.array
        Computed adev for each tau value
    ade: np.array
        adev errors
    ns: np.array
        Values of N used in each adev calculation

    References
    ----------
    * NIST [SP1065]_ eqn (6) and (7), pages 14 and 15.
    * [wikipedia_adev]_
    """
    phase = input_to_phase(data, rate, data_type)
    (phase, m, taus_used) = tau_generator(phase, rate, taus)

    ad = np.zeros_like(taus_used)
    ade = np.zeros_like(taus_used)
    adn = np.zeros_like(taus_used)

    for idx, mj in enumerate(m):  # loop through each tau value m(j)
        (ad[idx], ade[idx], adn[idx]) = calc_adev_phase(phase, rate, mj, mj)

    return remove_small_ns(taus_used, ad, ade, adn)

def calc_adev_phase(phase, rate, mj, stride):
    """  Main algorithm for adev() (stride=mj) and oadev() (stride=1)

    Parameters
    ----------
    phase: np.array
        Phase data in seconds.
    rate: float
        The sampling rate for phase or frequency, in Hz
    mj: int
        averaging factor, we evaluate at tau = m*tau0
    stride: int
        Size of stride

    Returns
    -------
    (dev, deverr, n): tuple
        Array of computed values.

    Notes
    -----
    stride = mj for nonoverlapping Allan deviation
    stride = 1 for overlapping Allan deviation

    References
    ----------
    * http://en.wikipedia.org/wiki/Allan_variance
    * http://www.leapsecond.com/tools/adev_lib.c
    * NIST [SP1065]_ eqn (7) and (11) page 16
    """
    mj = int(mj)
    stride = int(stride)
    d2 = phase[2 * mj::stride]
    d1 = phase[1 * mj::stride]
    d0 = phase[::stride]

    n = min(len(d0), len(d1), len(d2))

    if n == 0:
        RuntimeWarning("Data array length is too small: %i" % len(phase))
        n = 1

    v_arr = d2[:n] - 2 * d1[:n] + d0[:n]
    s = np.sum(v_arr * v_arr)

    dev = np.sqrt(s / (2.0*n)) / mj*rate
    deverr = dev / np.sqrt(n)

    return dev, deverr, n

def input_to_phase(data, rate, data_type):
    """ Take either phase or frequency as input and return phase
    """
    if data_type == "phase":
        return data
    elif data_type == "freq":
        return frequency2phase(data, rate)
    else:
        raise Exception("unknown data_type: " + data_type)
    
def tau_generator(data, rate, taus=None, v=False, even=False, maximum_m=-1):
    """ pre-processing of the tau-list given by the user (Helper function)

    Does sanity checks, sorts data, removes duplicates and invalid values.
    Generates a tau-list based on keywords 'all', 'decade', 'octave'.
    Uses 'octave' by default if no taus= argument is given.

    Parameters
    ----------
    data: np.array
        data array
    rate: float
        Sample rate of data in Hz. Time interval between measurements
        is 1/rate seconds.
    taus: np.array
        Array of tau values for which to compute measurement.
        Alternatively one of the keywords: "all", "octave", "decade".
        Defaults to "octave" if omitted.
        
        +----------+--------------------------------+
        | keyword  |   averaging-factors            |
        +==========+================================+
        | "all"    |  1, 2, 3, 4, ..., len(data)    |
        +----------+--------------------------------+
        | "octave" |  1, 2, 4, 8, 16, 32, ...       |
        +----------+--------------------------------+
        | "decade" |  1, 2, 4, 10, 20, 40, 100, ... |
        +----------+--------------------------------+
        | "log10"  |  approx. 10 points per decade  |
        +----------+--------------------------------+
    v: bool
        verbose output if True
    even: bool
        require even m, where tau=m*tau0, for Theo1 statistic
    maximum_m: int
        limit m, where tau=m*tau0, to this value.
        used by mtotdev() and htotdev() to limit maximum tau.

    Returns
    -------
    (data, m, taus): tuple
        List of computed values
    data: np.array
        Data
    m: np.array
        Tau in units of data points
    taus: np.array
        Cleaned up list of tau values
    """

    if rate == 0:
        raise RuntimeError("Warning! rate==0")

    if taus is None:  # empty or no tau-list supplied
        taus = "octave"  # default to octave
    elif isinstance(taus, list) and taus == []:  # empty list
        taus = "octave"

    # numpy array or non-empty list detected first
    if isinstance(taus, np.ndarray) or isinstance(taus, list) and len(taus):
        pass
    elif taus == "all":  # was 'is'
        taus = (1.0/rate)*np.linspace(1.0, len(data), len(data))
    elif taus == "octave":
        maxn = np.floor(np.log2(len(data)))
        taus = (1.0/rate)*np.logspace(0, int(maxn), int(maxn+1), base=2.0)
    elif taus == "log10":
        maxn = np.log10(len(data))
        taus = (1.0/rate)*np.logspace(0, maxn, int(10*maxn), base=10.0)
        if v:
            print("tau_generator: maxn %.1f"%maxn)
            print("tau_generator: taus="%taus)
    elif taus == "decade":  # 1, 2, 4, 10, 20, 40, spacing similar to Stable32
        maxn = np.floor(np.log10(len(data)))
        taus = []
        for k in range(int(maxn+1)):
            taus.append(1.0*(1.0/rate)*pow(10.0, k))
            taus.append(2.0*(1.0/rate)*pow(10.0, k))
            taus.append(4.0*(1.0/rate)*pow(10.0, k))

    data, taus = np.array(data), np.array(taus)
    rate = float(rate)
    m = []  # integer averaging factor. tau = m*tau0

    if maximum_m == -1:  # if no limit given
        maximum_m = len(data)

    m = np.round(taus * rate)
    taus_valid1 = m < len(data)
    taus_valid2 = m > 0
    taus_valid3 = m <= maximum_m
    taus_valid = taus_valid1 & taus_valid2 & taus_valid3
    m = m[taus_valid]
    m = m[m != 0]       # m is tau in units of datapoints
    m = np.unique(m)    # remove duplicates and sort

    if v:
        print("tau_generator: ", m)

    if len(m) == 0:
        print("Warning: sanity-check on tau failed!")
        print("   len(data)=", len(data), " rate=", rate, "taus= ", taus)

    taus2 = m / float(rate)

    if even:  # used by Theo1
        m_even_mask = ((m % 2) == 0)
        m = m[m_even_mask]
        taus2 = taus2[m_even_mask]

    return data, m, taus2



def remove_small_ns(taus, devs, deverrs, ns):
    """ Remove results with small number of samples.
    
    If n is small (==1), reject the result

    Parameters
    ----------
    taus: array
        List of tau values for which deviation were computed
    devs: array
        List of deviations
    deverrs: array or list of arrays
        List of estimated errors (possibly a list containing two arrays :
        upper and lower values)
    ns: array
        Number of samples for each point

    Returns
    -------
    (taus, devs, deverrs, ns): tuple
        Identical to input, except that values with low ns have been removed.

    """
    ns_big_enough = ns > 1

    o_taus = taus[ns_big_enough]
    o_devs = devs[ns_big_enough]
    o_ns = ns[ns_big_enough]
    if isinstance(deverrs, list):
        assert len(deverrs) < 3
        o_deverrs = [deverrs[0][ns_big_enough], deverrs[1][ns_big_enough]]
    else:
        o_deverrs = deverrs[ns_big_enough]
    if len(o_devs) == 0:
        print("remove_small_ns() nothing remains!?")
        raise UserWarning

    return o_taus, o_devs, o_deverrs, o_ns

def frequency2phase(freqdata, rate):
    """ integrate fractional frequency data and output phase data

    Parameters
    ----------
    freqdata: np.array
        Data array of fractional frequency measurements (nondimensional)
    rate: float
        The sampling rate for phase or frequency, in Hz

    Returns
    -------
    phasedata: np.array
        Time integral of fractional frequency data, i.e. phase (time) data
        in units of seconds.
        For phase in units of radians, see phase2radians()
    """
    dt = 1.0 / float(rate)
    # Protect against NaN values in input array (issue #60)
    # Reintroduces data trimming as in commit 503cb82
    freqdata = trim_data(freqdata)
    # Erik Benkler (PTB): Subtract mean value before cumsum in order to
    # avoid precision issues when we have small frequency fluctuations on
    # a large average frequency
    freqdata = freqdata - np.nanmean(freqdata)
    phasedata = np.cumsum(freqdata) * dt
    phasedata = np.insert(phasedata, 0, 0)  # FIXME: why do we do this?
    # so that phase starts at zero and len(phase)=len(freq)+1 ??
    return phasedata


def trim_data(x):
    """Trim leading and trailing NaNs from dataset
    
    This is done by browsing the array from each end and store the index of the
    first non-NaN in each case, the return the appropriate slice of the array
    """
    # Find indices for first and last valid data
    first = 0
    while np.isnan(x[first]):
        first += 1
    last = len(x)
    while np.isnan(x[last - 1]):
        last -= 1
    return x[first:last]