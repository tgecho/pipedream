import pytest
from pipedream import ResourceError


def test_calling_basic(dispatcher):
    @dispatcher.add
    def a(b):
        return '(a={0})'.format(b)

    @dispatcher.add
    def b():
        return 'b'

    assert dispatcher.call('a') == '(a=b)'
    assert dispatcher.call('b') == 'b'
    assert dispatcher.call('a', b='b!') == '(a=b!)'


def test_arguments_order(dispatcher):
    @dispatcher.add(requires=['b', 'c'])
    def a(c, b):
        return c + b

    assert dispatcher.call('a', b='b', c='c') == 'bc'
