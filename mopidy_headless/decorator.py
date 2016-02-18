import time

def debounce(wait):
    """
    Wait before calling a function again, discarding any calls in between
    """
    def decorator(fn):
        def wrapped(*args, **kwargs):
            now = time.time()
            if wrapped.last is not None:
                delta = now - wrapped.last
                if delta < wait: return

            wrapped.last = now
            fn(*args, **kwargs)
        wrapped.last = None
        return wrapped
    return decorator
