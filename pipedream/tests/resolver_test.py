import pytest
from pipedream import Dispatcher, CircularDependency, UnresolvableDependency
from pipedream.dispatcher import OrderedDict


def add_many(dispatcher, funcs):
    for name, reqs in funcs.items():
        func = lambda **k: name + str(k)
        func.__name__ = name
        dispatcher.add(func, requires=reqs)


def test_resolving_simple(dispatcher):
    funcs = {
        'a': ['b'],
        'b': []
    }
    add_many(dispatcher, funcs)
    assert list(dispatcher.resolve_dependency_graph('a').keys()) == ['b', 'a']
    assert list(dispatcher.resolve_dependency_graph('b').keys()) == ['b']


def test_resolving_multi(dispatcher):
    funcs = {
        'a': ['b', 'c'],
        'b': ['c', 'd'],
        'c': ['d'],
        'd': []
    }
    add_many(dispatcher, funcs)
    assert list(dispatcher.resolve_dependency_graph('a').keys()) == ['d', 'c', 'b', 'a']
    assert list(dispatcher.resolve_dependency_graph('b').keys()) == ['d', 'c', 'b']
    assert list(dispatcher.resolve_dependency_graph('c').keys()) == ['d', 'c']
    assert list(dispatcher.resolve_dependency_graph('d').keys()) == ['d']


def test_resolving_preresolved(dispatcher):
    funcs = {
        'a': ['b', 'd'],
        'b': ['c', 'e'],
        'c': ['d', 'e'],
        'd': [],
        'e': []
    }
    add_many(dispatcher, funcs)
    assert list(dispatcher.resolve_dependency_graph('a', resolved={'b': 'b'}).keys()) == ['b', 'd', 'a']
    assert list(dispatcher.resolve_dependency_graph('a', resolved={'c': 'c'}).keys()) == ['c', 'e', 'b', 'd', 'a']
    assert list(dispatcher.resolve_dependency_graph('a', resolved=OrderedDict((('b', 'b'), ('d', 'd')))).keys()) == ['b', 'd', 'a']
    assert list(dispatcher.resolve_dependency_graph('b', resolved={'b': 'b'}).keys()) == ['b']
    assert list(dispatcher.resolve_dependency_graph('b', resolved={'c': 'c'}).keys()) == ['c', 'e', 'b']


def test_resolving_circular(dispatcher):
    funcs = {
        'a': ['b'],
        'b': ['a'],
    }
    add_many(dispatcher, funcs)
    with pytest.raises(CircularDependency):
        dispatcher.resolve_dependency_graph('a')


def test_resolving_unresolvable(dispatcher):
    funcs = {
        'a': ['b']
    }
    add_many(dispatcher, funcs)
    with pytest.raises(UnresolvableDependency):
        dispatcher.resolve_dependency_graph('a')


def test_deep_resolving():
    one = Dispatcher()
    two = Dispatcher()
    three = Dispatcher()
    one.add_sub_dispatcher(two)
    two.add_sub_dispatcher(three)

    @three.add
    def a():
        return 'a'  # pragma: no cover

    one.find_resource('a')

    with pytest.raises(UnresolvableDependency) as ex:
        one.find_resource('b')
    assert 'a' in ex.value.available


def test_circular_dispatchers():
    one = Dispatcher()
    two = Dispatcher()
    three = Dispatcher()
    one.add_sub_dispatcher(two)
    two.add_sub_dispatcher(three)
    three.add_sub_dispatcher(one)

    with pytest.raises(UnresolvableDependency):
        one.find_resource('a')
