class PymarshalError(RuntimeError):
    pass


class UnknownFieldError(PymarshalError):
    pass


class UnsupportedClassError(PymarshalError):
    pass


class InvalidDelegateError(PymarshalError):
    pass


class MissingFieldsError(PymarshalError):
    pass
