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
    assert a.func_code.co_varnames == ('b',)


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
        return '(a={})'.format(b)

    @dispatcher.add
    def b():
        return 'b'

    assert a() == '(a=b)'


def test_wrapping_preresolved(dispatcher):
    @dispatcher.wrap
    def a(b):
        return '(a={})'.format(b)

    @dispatcher.add
    def b():
        assert False, 'This should not be called'  # pragma: no cover
    assert a(b='b!') == '(a=b!)'


def test_wrapping_nothing_available(dispatcher):
    @dispatcher.wrap
    def a(b):
        return '(a={})'.format(b)

    with pytest.raises(UnresolvableDependency):
        a()
    assert a(b='b!') == '(a=b!)'
