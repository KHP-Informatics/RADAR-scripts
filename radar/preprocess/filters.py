#!/usr/bin/env python3
from scipy import signal

def butter_filter(arr, cutoff, freq, order=5, ftype='highpass'):
    """ butter_filter returns a butter filtered array.
    Parameters
    __________
    arr: list or numpy.array
        The timeseries array on which the filter is applied
    cutoff: scalar or len-2 sequence
        The critical frequencies for the Butterworth filter. The point at
        which the gain drops to 1/sqrt(2) of the passband. Must be length-2
        sequence for a bandpass filter giving [low, high]. Or else the scalar
        cutoff frequency for either a low-pass' or 'highpass' filter.
    freq: scalar
        The frequency of the input array
    ftype: {'highpass', 'lowpass', 'bandpass'}
        The filter type. Default is 'highpass'
    """
    nyq = 0.5 * freq
    b, a = signal.butter(order, cutoff/nyq, ftype)
    return signal.lfilter(b, a, arr)


