import numpy as np
import tables

AVRO_NP_TYPES = {
    'null': None,
    'boolean': np.bool_,
    'int': np.int32,
    'long': np.int64,
    'float': np.float32,
    'double': np.float64,
    'bytes': np.bytes_,
    'string': np.object,
    'enum': np.object,
}

AVRO_HDF_TYPE = {
    'null': 1,
    'boolean': 1,
    'int': 1,
    'long': 1,
    'float': 1,
    'double': 1,
    'bytes': 1,
    'string': 1,
    'enum': 1,
}

NP_HDF_TYPES = {}

def _datetime_to_int(arr):
    return arr.astype('int64')

NP_HDF_CONVERSION = {
    '<M8[ns]': _datetime_to_int,
}


def col_names(obj):
    if isinstance(obj, np.ndarray):
        return list(obj.dtype.names)
    else:
        return list(obj.columns)

def iter_repeater(x):
    """ Returns a function that will yield an object a given number of times
    Parameters
    _________
    x: object
        The object to be yielded
    Returns
    _______
    repeat: function
        A function that yields 'x' a given number of times (set by the
        function's parameter 'times').
    """
    def repeat(times):
        """ Yields a set object a number of times
        Parameters
        _________
        times: int
            The number of times to yield the object
        Yields
        ______
        x: object
            An object defined at the functions creation time.
        See Also
        ________
        radar.common.iter_repeater
        """
        i = 0
        while i < times:
            i += 1
            yield x
    return repeat

def progress_bar(progress, total, prefix='Progress: ', suffix='', length=50):
    completed = int((progress/total)*length)
    bar = "{pre} |{comp}{empty}| {suff}".format(
        pre=prefix,
        comp='█' * completed,
        empty='-' * (length - completed),
        suff=suffix)
    print(bar, end='\r')
    if progress >= total:
        print('')

