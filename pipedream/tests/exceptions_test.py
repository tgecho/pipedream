import pytest

from pipedream import Dispatcher


class FooBar(Exception):
    pass


def test_exceptions_without_handler(dispatcher):
    @dispatcher.add
    def a():
        1/0

    with pytest.raises(ZeroDivisionError):
        dispatcher.call('a')


def test_handled_exceptions(dispatcher):
    @dispatcher.error_handler
    def handle(error):
        return 'handled'

    @dispatcher.add()
    def a():
        1/0

    assert dispatcher.call('a') == 'handled'


def test_unhandled_exceptions(dispatcher):
    @dispatcher.error_handler
    def handler(error):
        return error

    @dispatcher.add()
    def a():
        1/0

    with pytest.raises(ZeroDivisionError):
        assert dispatcher.call('a')


def test_converted_exceptions(dispatcher):
    @dispatcher.error_handler
    def handler(error):
        raise FooBar()

    @dispatcher.add()
    def a():
        1/0

    with pytest.raises(FooBar):
        assert dispatcher.call('a')
