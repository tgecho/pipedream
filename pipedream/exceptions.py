class PipedreamException(Exception):
    pass


class DuplicateFunction(PipedreamException):
    pass


class CircularDependency(PipedreamException):
    pass


class CircularDispatcherDependency(PipedreamException):
    pass


class UnresolvableDependency(PipedreamException):
    def __init__(self, name, tried):
        self.tried = tried
        super(UnresolvableDependency, self).__init__("Can't find '{}' in {}".format(name, tried))


class ResourceError(PipedreamException):
    pass


class IncompleteCall(PipedreamException):
    pass
