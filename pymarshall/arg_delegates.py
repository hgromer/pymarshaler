import datetime
import inspect
import typing

import dateutil.parser as parser

from pymarshall.utils import is_user_defined


def _apply_typing(param_type, value: typing.Any) -> typing.Any:
    if value is None:
        return None
    elif is_user_defined(param_type):
        return param_type(**UserDefinedArgBuilderDelegate(param_type).resolve(value))
    elif isinstance(value, dict):
        return param_type(**value)
    elif issubclass(param_type, datetime.datetime):
        return parser.parse(value)
    else:
        return param_type(value)


class ArgBuilderDelegate:

    def resolve(self, data):
        raise NotImplementedError(f'{ArgBuilderDelegate.__name__} has no implementation of resolve')


class ListArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        self.cls = cls

    def resolve(self, data):
        inner_type = self.cls.__args__[0]
        return [_apply_typing(inner_type, x) for x in data]


class SetArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        self.cls = cls

    def resolve(self, data):
        inner_type = self.cls.__args__[0]
        return {_apply_typing(inner_type, x) for x in data}


class TupleArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        self.cls = cls

    def resolve(self, data):
        inner_type = self.cls.__args__[0]
        return (_apply_typing(inner_type, x) for x in data)


class DictArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        self.cls = cls

    def resolve(self, data: dict):
        key_type = self.cls.__args__[0]
        value_type = self.cls.__args__[1]
        return {
            _apply_typing(key_type, key): _apply_typing(value_type, value) for key, value in data.items()
        }


class BuiltinsArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        self.cls = cls

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
        self.cls = cls

    def resolve(self, data: dict):
        return UserDefinedArgBuilderDelegate._resolve(self.cls, data)

    @staticmethod
    def _resolve(cls, data: dict):
        args = {}
        unsatisfied = inspect.signature(cls.__init__).parameters
        for key, value in data.items():
            if key in unsatisfied:
                param_type = unsatisfied[key].annotation
                if is_user_defined(param_type):
                    result = UserDefinedArgBuilderDelegate._resolve(param_type, value)
                    args[key] = param_type(**result)
                else:
                    args[key] = ArgBuilderFactory.get_delegate(param_type).resolve(value)
        return args

    @staticmethod
    def _get_unfilled(all_args: dict, to_satisfy: dict):
        return {k: v for k, v in all_args.items() if k not in to_satisfy}


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

    _ignore_unknown_fields = False

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
    def set_ignore_unknown_fields(ignore: bool):
        ArgBuilderFactory._ignore_unknown_fields = ignore

    @staticmethod
    def is_ignore_unknown_fields():
        return ArgBuilderFactory._ignore_unknown_fields

    @staticmethod
    def is_registered(cls):
        return ArgBuilderFactory._registered_delegates.contains(cls)

    @staticmethod
    def register_delegate(cls, delegate: ArgBuilderDelegate):
        ArgBuilderFactory._registered_delegates.register(cls, delegate)

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
