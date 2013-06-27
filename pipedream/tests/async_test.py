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


def handle_breakage(func):
    try:
        func()
    except ZeroDivisionError, exc:
        return exc


def test_exception_handling(pool):
    result = pool.do(handle_breakage, break_things)
    assert isinstance(result, ZeroDivisionError)


def one_func():
    return 1


def two_func(a):
    return a + 1


def test_interplay(combination):
    # Ensure that each async backend can handle recieving a future from any other type of backend.
    one, two = combination
    one_future = one.do(one_func)
    two_future = two.do(two_func, one_future)
    assert two_future == 2
