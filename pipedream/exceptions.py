class PipedreamException(Exception):
    pass


class DuplicateFunction(PipedreamException):
    pass


class CircularDependency(PipedreamException):
    pass


class CircularDispatcherDependency(PipedreamException):
    pass


class UnresolvableDependency(PipedreamException):
    def __init__(self, name, available):
        self.available = available
        super(UnresolvableDependency, self).__init__("Can't find '{0}' in {1}".format(name, available))


class ResourceError(PipedreamException):
    pass


class IncompleteCall(PipedreamException):
    pass
