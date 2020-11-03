import datetime
import inspect
import typing

import dateutil.parser as parser

from pymarshall.utils import is_user_defined


def _apply_typing(param_type, value: typing.Any) -> typing.Any:
    delegate = ArgBuilderFactory.get_delegate(param_type)
    result = delegate.resolve(value)
    if is_user_defined(param_type):
        return param_type(**result)
    return result


class ArgBuilderDelegate:

    def __init__(self, cls):
        self.cls = cls

    def resolve(self, data):
        raise NotImplementedError(f'{ArgBuilderDelegate.__name__} has no implementation of resolve')


class ListArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        super().__init__(cls)

    def resolve(self, data: typing.List):
        inner_type = self.cls.__args__[0]
        return [_apply_typing(inner_type, x) for x in data]


class SetArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        super().__init__(cls)

    def resolve(self, data: typing.Set):
        inner_type = self.cls.__args__[0]
        return {_apply_typing(inner_type, x) for x in data}


class TupleArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        super().__init__(cls)

    def resolve(self, data: typing.Tuple):
        inner_type = self.cls.__args__[0]
        return (_apply_typing(inner_type, x) for x in data)


class DictArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        super().__init__(cls)

    def resolve(self, data: dict):
        key_type = self.cls.__args__[0]
        value_type = self.cls.__args__[1]
        return {
            _apply_typing(key_type, key): _apply_typing(value_type, value) for key, value in data.items()
        }


class BuiltinsArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        super().__init__(cls)

    def resolve(self, data):
        if data is None:
            return None
        elif isinstance(data, dict):
            return self.cls(**data)
        elif issubclass(self.cls, datetime.datetime):
            return parser.parse(data)
        else:
            return self.cls(data)


class UserDefinedArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        super().__init__(cls)

    def resolve(self, data: dict):
        return UserDefinedArgBuilderDelegate._resolve(self.cls, data)

    @staticmethod
    def _resolve(cls, data: dict):
        args = {}
        unsatisfied = inspect.signature(cls.__init__).parameters
        for key, value in data.items():
            if key in unsatisfied:
                param_type = unsatisfied[key].annotation
                args[key] = _apply_typing(param_type, value)
        return args


class _RegisteredDelegates:

    def __init__(self):
        self.registered_delegates = {}

    def register(self, cls, delegate: ArgBuilderDelegate):
        self.registered_delegates[cls.__name__] = delegate

    def get(self, cls):
        return self.registered_delegates[cls.__name__]

    def contains(self, cls):
        try:
            return cls.__name__ in self.registered_delegates
        except AttributeError:
            return False


class ArgBuilderFactory:

    _registered_delegates = _RegisteredDelegates()

    _default_arg_builder_delegates = {
        typing.List._name: lambda x: ListArgBuilderDelegate(x),
        typing.Set._name: lambda x: SetArgBuilderDelegate(x),
        typing.Tuple._name: lambda x: TupleArgBuilderDelegate(x),
        typing.Dict._name: lambda x: DictArgBuilderDelegate(x),
        "PythonBuiltin": lambda x: BuiltinsArgBuilderDelegate(x),
        "UserDefined": lambda x: UserDefinedArgBuilderDelegate(x)
    }

    @staticmethod
    def is_registered(cls):
        return ArgBuilderFactory._registered_delegates.contains(cls)

    @staticmethod
    def register_delegate(cls, delegate_cls):
        ArgBuilderFactory._registered_delegates.register(cls, delegate_cls(cls))

    @staticmethod
    def get_delegate(cls) -> ArgBuilderDelegate:
        if ArgBuilderFactory._registered_delegates.contains(cls):
            return ArgBuilderFactory._registered_delegates.get(cls)
        elif is_user_defined(cls):
            return ArgBuilderFactory._default_arg_builder_delegates['UserDefined'](cls)
        elif '_name' in cls.__dict__:
            return ArgBuilderFactory._safe_get(cls._name)(cls)
        else:
            return ArgBuilderFactory._default_arg_builder_delegates['PythonBuiltin'](cls)

    @staticmethod
    def _safe_get(name):
        if name not in ArgBuilderFactory._default_arg_builder_delegates:
            raise ValueError(f'Unsupported class type {name}')
        return ArgBuilderFactory._default_arg_builder_delegates[name]
