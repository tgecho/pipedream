from collections import namedtuple

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from pipedream.exceptions import UnresolvableDependency, CircularDependency, ResourceError, DuplicateFunction
from pipedream.utils import func_kwargs, preserve_signature


Resource = namedtuple('Resource', ['function', 'requirements'])


class Dispatcher(object):
    def __init__(self, async_pool=None):
        self._sub_dispatchers = []
        self._resources = {}
        self._error_handlers = []
        self.async_pool = async_pool

    def wrap(self, *args, **kwargs):
        """
        Use as a decorator to add a function to this dispatcher and ensure any
        calls are handled by this dispatcher. Accepts the same arguments as
        Dispatcher.add.

        @dispatcher.wrap
        def my_func(var):
            return var
        """
        func = self.add(*args, **kwargs)

        def wrapper(**f_kwargs):
            return self.call(func.__name__, **f_kwargs)
        return preserve_signature(wrapper, func)

    def add(self, func=None, **kwargs):
        """
        Use as a decorator to add a function to this dispatcher.

        @dispatcher.add
        def my_func(var):
            return var

        Requirements can be manually specified if desired. Can be handy to help
        avoid naming clashes or if something has messed with the signature of
        the function. The function will be called with arguments in the same
        order as the list passed in through requires.

        @dispatcher.add(requires=['long_named_var'])
        def my_func(var):
            return var
        """
        if func is None or not callable(func):
            kwargs.setdefault('name', func)
            def decorater(func):
                self.add_resource(func, **kwargs)
                return func
            return decorater
        else:
            self.add_resource(func, **kwargs)
            return func

    def add_resource(self, func, name=None, requires=None):
        requirements = requires or getattr(func, 'requires', None) or func_kwargs(func)
        assert isinstance(requirements, (list, tuple))
        name = name or func.__name__
        if name in self._resources:
            raise DuplicateFunction(name)
        self._resources[name] = Resource(func, requirements)
        return name

    def add_sub_dispatcher(self, resource):
        """
        Add the contents of a Dispatcher to the list of subdispatchers.
        """
        self._sub_dispatchers.append(resource)

    def find_resource(self, name, tried=None):
        """
        Find a named resource among available dispatchers.
        """
        tried = tried or []
        tried.append(self)
        try:
            return self._resources[name]
        except KeyError:
            available = list(self._resources.keys())
            for dispatcher in (d for d in self._sub_dispatchers if d not in tried):
                try:
                    return dispatcher.find_resource(name, tried=tried)
                except UnresolvableDependency as ex:
                    available.extend(ex.available)
            raise UnresolvableDependency(name, available=available)

    def resolve_dependency_graph(self, name, resolved=None, _unresolved=None):
        """
        Given a name and a list of already resolved resources, return an ordered
        list of resources to call.
        """
        if resolved is None:
            resolved = OrderedDict()
        elif not isinstance(resolved, OrderedDict):
            resolved = OrderedDict(resolved)

        _unresolved = _unresolved or []
        if name in resolved:
            return resolved
        _unresolved.append(name)
        result = self.find_resource(name)
        for dep in result.requirements:
            if dep not in resolved:
                if dep in _unresolved:
                    raise CircularDependency('{0} > {1}'.format(name, dep))
                self.resolve_dependency_graph(dep, resolved, _unresolved)
        resolved[name] = result
        _unresolved.remove(name)
        return resolved

    def call(self, name, **kwargs):
        """
        Call a resource by name, automatically resolving any needed dependencies along the way.
        """
        graph = self.resolve_dependency_graph(name, resolved=kwargs)
        return self.call_funcs(graph, kwargs)[name]

    def call_funcs(self, graph, kwargs):
        for dep in graph:
            if dep in kwargs:
                continue
            item = graph[dep]

            call_args = (kwargs[kw] for kw in item.requirements)

            kwargs[dep] = self.call_func(item.function, call_args)

        return kwargs

    def call_func(self, func, call_args):
        if self.async_pool:
            return self.async_pool.do(self.handle_errors, func, *call_args)
        else:
            return self.handle_errors(func, *call_args)

    def handle_errors(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            for handler in self._error_handlers:
                result = handler(ex)
                if not isinstance(result, Exception):
                    return result
            raise

    def error_handler(self, func):
        self._error_handlers.append(func)
