import sys
from traceback import format_tb
from peak.util.proxies import LazyProxy
from pipedream.utils import preserve_signature


class FutureProxyException(Exception):
    pass


class PickleableException(FutureProxyException):
    pass


def exception_catcher(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception, exc:
        # We need to accomplish two things here: save the traceback for printing
        # later and ensure the raised exception can be pickled to avoid
        # multiprocessing hanging due to http://bugs.python.org/issue1692335.
        raise PickleableException((exc.__class__, exc.args, format_tb(sys.exc_traceback)))


class BasePool(object):
    proxy_class = LazyProxy

    def __init__(self, *args, **kwargs):
        pass

    def do(self, func, *args, **kwargs):
        future = self.get_future(func, *args, **kwargs)
        return LazyProxy(lambda: self.try_except(future))

    def get_future(self, func, *args, **kwargs):
        return lambda: exception_catcher(func, *args, **kwargs)

    def try_except(self, future):
        try:
            return future()
        except Exception, exc:
            self.unwrap_exception(exc)

    def unwrap_exception(self, exc):
        (exc_class, exc_args, exc_tb) = exc.args[0]
        for line in exc_tb:
            print(line)
        new_exc = exc_class(*exc_args)
        new_exc.tb = exc_tb
        raise new_exc


class ConcurrentFuture(BasePool):
    def get_future(self, func, *args, **kwargs):
        future = self.pool.submit(exception_catcher, func, *args, **kwargs)
        return future.result
