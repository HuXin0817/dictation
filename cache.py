import threading
from functools import wraps


def cache(func):
    results = {}
    lock = threading.Lock()

    @wraps(func)
    def wrapper(*args):
        if args in results:
            return results[args]

        res = func(*args)
        with lock:
            results[args] = res
        return res

    return wrapper
