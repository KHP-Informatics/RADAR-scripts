from functools import wraps
import numpy as np

VERBOSITY = 0

AVRO_NUMPY_TYPES = {
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

def debug_wrapper(function):
    """ Wrapper that prints debug information when radar.common.VERBOSITY
    is set above 0.
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not VERBOSITY:
            return function(*args, **kwargs)
        print('^^^^^^^^^^ {} from {} ^^^^^^^^^^'.format(
            function.__name__, function.__module__))
        if VERBOSITY > 1:
            print('Args: ')
            for arg in args:
                print('Class: {} | Value: {}'.format(
                    arg.__class__, arg.__str__()))

            print('KWargs: ')
            for key, value in kwargs.items():
                print('{}: Class: {} | Value: {}'.format(key, value.__class__,
                                                       value.__str__()))
        print('____________________')
        result = function(*args, **kwargs)
        print('____________________')
        if VERBOSITY > 2:
            print('Result: ')
            print('Class: {} | Value: {}'.format(
                result.__class__, result.__str__()))
        print('vvvvvvvvvv {} from {} vvvvvvvvvv'.format(function.__name__,
                                                        function.__module__))
        return result
    return wrapper

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
