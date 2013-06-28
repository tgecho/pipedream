import pytest
from pipedream import UnresolvableDependency, DuplicateFunction


def test_decorating_basic(dispatcher):
    @dispatcher.add
    def a():
        pass  # pragma: no cover
    assert dispatcher.find_resource('a')
    assert not dispatcher.find_resource('a').requirements


def test_decorating_implicit_requirements(dispatcher):
    @dispatcher.add
    def a(b):
        pass  # pragma: no cover
    assert dispatcher.find_resource('a').requirements == ('b',)
    assert a.__code__.co_varnames == ('b',)


def test_decorating_explicit_requirements(dispatcher):
    @dispatcher.add(requires=['b'])
    def a(**kwargs):
        pass  # pragma: no cover
    assert dispatcher.find_resource('a')
    assert list(dispatcher.find_resource('a').requirements) == ['b']


def test_decorating_attached_requirements(dispatcher):
    def a(**kwargs):
        pass  # pragma: no cover
    a.requires = ['b']
    dispatcher.add(a)
    assert dispatcher.find_resource('a')
    assert list(dispatcher.find_resource('a').requirements) == ['b']


def test_decorating_custom_name(dispatcher):
    @dispatcher.add('foo')
    def bar():
        pass  # pragma: no cover
    assert dispatcher.find_resource('foo')
    with pytest.raises(UnresolvableDependency):
        assert not dispatcher.find_resource('bar')

    @dispatcher.add(name='fro')
    def frum():
        pass  # pragma: no cover
    assert dispatcher.find_resource('fro')
    with pytest.raises(UnresolvableDependency):
        assert not dispatcher.find_resource('frum')


def test_decorating_duplicate(dispatcher):
    @dispatcher.add
    def a():
        pass  # pragma: no cover

    with pytest.raises(DuplicateFunction):
        @dispatcher.add
        def a():
            pass  # pragma: no cover


def test_wrapping_simple(dispatcher):
    @dispatcher.wrap
    def a(b):
        return '(a={0})'.format(b)

    @dispatcher.add
    def b():
        return 'b'

    assert a() == '(a=b)'


def test_wrapping_preresolved(dispatcher):
    @dispatcher.wrap
    def a(b):
        return '(a={0})'.format(b)

    @dispatcher.add
    def b():
        assert False, 'This should not be called'  # pragma: no cover
    assert a(b='b!') == '(a=b!)'


def test_wrapping_nothing_available(dispatcher):
    @dispatcher.wrap
    def a(b):
        return '(a={0})'.format(b)

    with pytest.raises(UnresolvableDependency):
        a()
    assert a(b='b!') == '(a=b!)'
