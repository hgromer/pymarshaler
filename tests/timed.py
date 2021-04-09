from functools import wraps

from timeit import default_timer as timer


def timed(function):
    """
    Log how long a function took
    :param function: Function to time
    :return: Result of the function
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        start = timer()
        result = function(*args, **kwargs)
        print("{} took {} ms".format(function.__name__, round(1000 * (timer() - start), 3)))
        return result
    return wrapper
