from functools import update_wrapper


def preserve_signature(wrapper, wrapped):
    wrapper = update_wrapper(wrapper, wrapped)
    wrapper._saved_co_varnames = func_kwargs(wrapped)
    return wrapper


def func_kwargs(func):
    return getattr(func, '_saved_co_varnames', func.__code__.co_varnames[:func.__code__.co_argcount])
