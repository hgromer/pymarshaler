class PymarshallError(RuntimeError):
    pass


class UnknownFieldError(PymarshallError):
    pass


class UnsupportedClassError(PymarshallError):
    pass


class InvalidDelegateError(PymarshallError):
    pass


class MissingFieldsError(PymarshallError):
    pass
