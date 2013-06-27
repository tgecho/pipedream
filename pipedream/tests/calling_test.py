import pytest
from pipedream import ResourceError


def test_uncachable_scope(dispatcher):
    @dispatcher.add
    def a():
        return 'a'

    count = [0]

    @dispatcher.add(scope='a')
    def b():
        count[0] = count[0] + 1
        return count[0]

    with pytest.raises(ResourceError):
        dispatcher.call('b')


class Foo(object):
    pass


def test_persistant_scope(dispatcher):
    persistant = Foo()

    @dispatcher.add
    def a():
        return persistant

    count = [0]

    # This is an example of where the scope object is not part of the graph and
    # must be retrieved.
    @dispatcher.add(scope='a')
    def b():
        count[0] = count[0] + 1
        return count[0]

    assert dispatcher.call('b') == 1
    assert dispatcher.call('b') == 1

    # Here the scope object is alread in the graph.
    @dispatcher.add(scope='a')
    def c(a):
        count[0] = count[0] + 1
        return count[0]

    assert dispatcher.call('c') == 2
    assert dispatcher.call('c') == 2


def test_nonpersistant_scope(dispatcher):
    @dispatcher.add
    def a():
        return Foo()

    count = [0]

    @dispatcher.add(scope='a')
    def b():
        count[0] = count[0] + 1
        return count[0]

    assert dispatcher.call('b') == 1
    assert dispatcher.call('b') == 2


def test_arguments_order(dispatcher):
    @dispatcher.add(requires=['b', 'c'])
    def a(c, b):
        return c + b

    assert dispatcher.call('a', b='b', c='c') == 'bc'
