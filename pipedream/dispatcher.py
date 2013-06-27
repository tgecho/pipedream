from weakref import WeakKeyDictionary
from collections import OrderedDict, namedtuple

from pipedream.exceptions import UnresolvableDependency, CircularDependency, ResourceError, DuplicateFunction
from pipedream.utils import func_kwargs, preserve_signature


Resource = namedtuple('Resource', ['function', 'requirements', 'scope', 'error_handler'])


class Dispatcher(object):
    scope_cache = {}

    def __init__(self):
        self._sub_dispatchers = []
        self._resources = {}
        self._error_handlers = []

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
        if func is None:
            def decorater(func):
                self.add_resource(func, **kwargs)
                return func
            return decorater
        else:
            self.add_resource(func, **kwargs)
            return func

    def add_resource(self, func, requires=None, scope=None, error_handler=None):
        requirements = requires or getattr(func, 'requires', None) or func_kwargs(func)
        assert isinstance(requirements, (list, tuple))
        name = func.__name__
        if name in self._resources:
            raise DuplicateFunction(name)
        self._resources[name] = Resource(func, requirements, scope, error_handler)
        return name

    def add_sub_dispatcher(self, resource):
        """
        Add the contents of a Dispatcher to the list of subdispatchers.
        """
        self._sub_dispatchers.append(resource)

    def find_resource(self, name):
        """
        Find a named resource among available dispatchers.
        """
        try:
            return self._resources[name]
        except KeyError:
            tried = self._resources.keys()
            for dispatcher in self._sub_dispatchers:
                try:
                    return dispatcher.find_resource(name)
                except UnresolvableDependency, ex:
                    tried.extend(ex.tried)
            raise UnresolvableDependency(name, tried=tried)

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
                    raise CircularDependency('{} > {}'.format(name, dep))
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

            if item.scope:
                if item.scope not in kwargs:
                    missing = self.resolve_dependency_graph(item.scope, resolved=kwargs.keys())
                    self.call_funcs(missing, kwargs)

                cached = self.scope_cache_get(dep, kwargs[item.scope])
                if cached:
                    kwargs[dep] = cached
                    continue

            call_args = (kwargs[kw] for kw in item.requirements)

            kwargs[dep] = self.call_func(item, call_args)

            if item.scope:
                self.scope_cache_set(dep, kwargs[item.scope], kwargs[dep])

        return kwargs

    def call_func(self, func, call_kwargs):
        try:
            return func.function(*call_kwargs)
        except Exception, ex:
            for handler in [func.error_handler] + self._error_handlers:
                if handler:
                    result = handler(ex)
                    if not isinstance(result, Exception):
                        return result
            raise

    def error_handler(self, func):
        self._error_handlers.append(func)

    def scope_cache_get(self, name, scope):
        if name in self.scope_cache:
            return self.scope_cache[name].get(scope)
        return None

    def scope_cache_set(self, name, scope, value):
        try:
            self.scope_cache.setdefault(name, WeakKeyDictionary())[scope] = value
        except TypeError, ex:
            raise ResourceError('Can\'t cache "{}" based on "{}": {}'.format(name, scope, ex))