import pytest

class FooBar(Exception):
    pass


def test_default_exceptions(dispatcher):
    @dispatcher.add
    def a():
        1/0

    with pytest.raises(ZeroDivisionError):
        dispatcher.call('a')


def test_handled_exceptions(dispatcher):
    def handler(error):
        return 'handled'

    @dispatcher.add(error_handler=handler)
    def a():
        1/0

    assert dispatcher.call('a') == 'handled'


def test_dispatcher_handler(dispatcher):
    def handler(error):
        return 'handled'
    dispatcher.error_handler(handler)

    @dispatcher.add
    def a():
        1/0

    assert dispatcher.call('a') == 'handled'


def test_decorated_dispatcher_handler(dispatcher):
    @dispatcher.error_handler
    def handler(error):
        return 'handled'

    @dispatcher.add
    def a():
        1/0

    assert dispatcher.call('a') == 'handled'


def test_unhandled_exceptions(dispatcher):
    def handler(error):
        return error

    @dispatcher.add(error_handler=handler)
    def a():
        1/0

    with pytest.raises(ZeroDivisionError):
        assert dispatcher.call('a')


def test_converted_exceptions(dispatcher):
    def handler(error):
        raise FooBar()

    @dispatcher.add(error_handler=handler)
    def a():
        1/0

    with pytest.raises(FooBar):
        assert dispatcher.call('a')
