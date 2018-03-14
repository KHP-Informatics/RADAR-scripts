from functools import wraps

VERBOSITY = 0

def debug_wrapper(function):
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
