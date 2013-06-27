import pytest
from pipedream.async.base import BasePool
from pipedream.async.gevent import GeventPool

BACKENDS = (BasePool, GeventPool)


@pytest.fixture(scope='session', params=BACKENDS)
def pool(request):
    return request.param(1)


def do_stuff(one=1, two=2):
    return one + two


def test_call(pool):
    result = pool.do(do_stuff)
    assert result == 3


def test_call_with_args(pool):
    result = pool.do(do_stuff, 2, 3)
    assert result == 5


def test_call_with_kwargs(pool):
    result = pool.do(do_stuff, one=2, two=3)
    assert result == 5


def test_call_with_both(pool):
    result = pool.do(do_stuff, 2, two=3)
    assert result == 5


def break_things():
    return 1/0


def test_exception_handling(pool):
    result = pool.do(break_things)
    try:
        assert result
    except ZeroDivisionError, exc:
        pass

    assert isinstance(exc, ZeroDivisionError)
    assert any('break_things' in line for line in exc.tb), "Can't find currect traceback line."


@pytest.fixture(params=[(a, b) for a in BACKENDS for b in BACKENDS])
def combination(request):
    return request.param


@pytest.fixture
def one(combination):
    return combination[0](1)


@pytest.fixture
def two(combination):
    return combination[1](1)


def one_func():
    return 1


def two_func(a):
    return a + 1


def test_interplay(one, two):
    # Ensure that each async backend can handle recieving a future from any other type of backend.

    one_future = one.do(one_func)
    two_future = two.do(two_func, one_future)
    assert two_future == 2
