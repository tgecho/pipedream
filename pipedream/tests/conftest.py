import pytest
from pipedream import Dispatcher


@pytest.fixture
def dispatcher(pool_or_none):
    return Dispatcher()


ASYNC_BACKENDS = (
    'pipedream.async.base.BasePool',
    'pipedream.async.gevent.GeventPool'
)


def import_backend(name):
    module, pool = name.rsplit('.', 1)
    return getattr(pytest.importorskip(module), pool)


@pytest.fixture(scope='session', params=ASYNC_BACKENDS)
def pool(request):
    return import_backend(request.param)(1)


@pytest.fixture(scope='session', params=ASYNC_BACKENDS + (None,))
def pool_or_none(request):
    # Simply allows us to try all of the pools but also allow no pool.
    if request.param:
        return import_backend(request.param)(1)
    else:
        return None


@pytest.fixture(params=[(a, b) for a in ASYNC_BACKENDS for b in ASYNC_BACKENDS])
def combination(request):
    return [import_backend(b)(1) for b in request.param]
