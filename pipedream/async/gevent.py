# from peak.util.proxies import get_callback
from __future__ import absolute_import

import gevent
from gevent.pool import Pool
from gevent.event import AsyncResult

from pipedream.async.base import ConcurrentFuture, exception_catcher


class GeventPool(ConcurrentFuture):
    async_types = ['net']

    def __init__(self, *args, **kwargs):
        self.pool = Pool(*args, **kwargs)

    def get_future(self, func, *args, **kwargs):
        greenlet = self.pool.spawn(exception_catcher, func, *args, **kwargs)
        async_result = AsyncResult()
        greenlet.link(async_result)
        return async_result.get
