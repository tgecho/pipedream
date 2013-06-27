from peak.util.proxies import LazyProxy


class FutureProxyException(Exception):
    pass


class BasePool(object):
    proxy_class = LazyProxy

    def __init__(self, *args, **kwargs):
        pass

    def do(self, func, *args, **kwargs):
        return LazyProxy(self.get_future(func, *args, **kwargs))

    def get_future(self, func, *args, **kwargs):
        return lambda: func(*args, **kwargs)
