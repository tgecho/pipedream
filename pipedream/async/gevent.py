from __future__ import absolute_import

import gevent
from gevent.pool import Pool
from gevent.event import AsyncResult

from pipedream.async.base import BasePool


class GeventPool(BasePool):
    def __init__(self, *args, **kwargs):
        self.pool = Pool(*args, **kwargs)

    def get_future(self, func, *args, **kwargs):
        greenlet = self.pool.spawn(func, *args, **kwargs)
        async_result = AsyncResult()
        greenlet.link(async_result)
        return async_result.get
