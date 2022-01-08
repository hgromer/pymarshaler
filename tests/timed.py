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
        total_time = 0
        result = None

        for _ in range(5):
            start = timer()
            result = function(*args, **kwargs)
            total_time += 1000 * (timer() - start)
        total_time = round(total_time / 5, 3)
        print(f"{function.__name__} took {total_time} ms after {5} attempts")
        return result
    return wrapper
