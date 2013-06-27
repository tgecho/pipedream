import pytest
from pipedream import Dispatcher, CircularDependency, UnresolvableDependency


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
    assert dispatcher.resolve_dependency_graph('a').keys() == ['b', 'a']
    assert dispatcher.resolve_dependency_graph('b').keys() == ['b']


def test_resolving_multi(dispatcher):
    funcs = {
        'a': ['b', 'c'],
        'b': ['c', 'd'],
        'c': ['d'],
        'd': []
    }
    add_many(dispatcher, funcs)
    assert dispatcher.resolve_dependency_graph('a').keys() == ['d', 'c', 'b', 'a']
    assert dispatcher.resolve_dependency_graph('b').keys() == ['d', 'c', 'b']
    assert dispatcher.resolve_dependency_graph('c').keys() == ['d', 'c']
    assert dispatcher.resolve_dependency_graph('d').keys() == ['d']


def test_resolving_preresolved(dispatcher):
    funcs = {
        'a': ['b', 'd'],
        'b': ['c', 'e'],
        'c': ['d', 'e'],
        'd': [],
        'e': []
    }
    add_many(dispatcher, funcs)
    assert dispatcher.resolve_dependency_graph('a', resolved={'b': 'b'}).keys() == ['b', 'd', 'a']
    assert dispatcher.resolve_dependency_graph('a', resolved={'c': 'c'}).keys() == ['c', 'e', 'b', 'd', 'a']
    assert dispatcher.resolve_dependency_graph('a', resolved={'b': 'b', 'd': 'd'}).keys() == ['b', 'd', 'a']
    assert dispatcher.resolve_dependency_graph('b', resolved={'b': 'b'}).keys() == ['b']
    assert dispatcher.resolve_dependency_graph('b', resolved={'c': 'c'}).keys() == ['c', 'e', 'b']


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


def test_calling_basic(dispatcher):
    @dispatcher.add
    def a(b):
        return '(a={})'.format(b)

    @dispatcher.add
    def b():
        return 'b'

    assert dispatcher.call('a') == '(a=b)'
    assert dispatcher.call('b') == 'b'
    assert dispatcher.call('a', b='b!') == '(a=b!)'


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
    assert 'a' in ex.value.tried


def test_circular_dispatchers():
    one = Dispatcher()
    two = Dispatcher()
    three = Dispatcher()
    one.add_sub_dispatcher(two)
    two.add_sub_dispatcher(three)
    three.add_sub_dispatcher(one)

    with pytest.raises(RuntimeError):
        one.find_resource('a')
