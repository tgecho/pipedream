import pytest
from pipedream import ResourceError


def test_arguments_order(dispatcher):
    @dispatcher.add(requires=['b', 'c'])
    def a(c, b):
        return c + b

    assert dispatcher.call('a', b='b', c='c') == 'bc'
