import datetime
import inspect
import typing

import dateutil.parser as parser

from pymarshal.errors import UnknownFieldError, InvalidDelegateError
from pymarshal.utils import is_user_defined, is_builtin


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


class BuiltinArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self, cls):
        super().__init__(cls)

    def resolve(self, data):
        if data is None:
            return None
        else:
            return self.cls(data)


class DateTimeArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self):
        super().__init__(datetime.datetime)

    def resolve(self, data):
        return parser.parse(data)


class UserDefinedArgBuilderDelegate(ArgBuilderDelegate):

    def __init__(self, cls, ignore_unknown_fields: bool, walk_unknown_fields: bool):
        super().__init__(cls)
        self.ignore_unknown_fields = ignore_unknown_fields
        self.walk_unknown_fields = walk_unknown_fields

    def resolve(self, data: dict):
        return self._resolve(self.cls, data)

    def _resolve(self, cls, data: dict):
        args = {}
        unsatisfied = inspect.signature(cls.__init__).parameters
        for key, value in data.items():
            if key in unsatisfied:
                param_type = unsatisfied[key].annotation
                args[key] = _apply_typing(param_type, value)
            elif not self.ignore_unknown_fields:
                raise UnknownFieldError(f'Found unknown field ({key}: {value}). '
                                        'If you would like to skip unknown fields set '
                                        'ArgBuilderFactory.ignore_unknown_fields(True)')
            elif self.walk_unknown_fields:
                if isinstance(value, dict):
                    args.update(self._resolve(cls, value))
                elif isinstance(value, (list, set, tuple)):
                    for x in value:
                        if isinstance(x, dict):
                            args.update(self._resolve(cls, x))
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
    _walk_unknown_fields = False

    _ignore_unknown_fields = False

    _registered_delegates = _RegisteredDelegates()

    _default_arg_builder_delegates = {
        typing.List._name: lambda x: ListArgBuilderDelegate(x),
        typing.Set._name: lambda x: SetArgBuilderDelegate(x),
        typing.Tuple._name: lambda x: TupleArgBuilderDelegate(x),
        typing.Dict._name: lambda x: DictArgBuilderDelegate(x),
        "PythonBuiltin": lambda x: BuiltinArgBuilderDelegate(x),
        "UserDefined": lambda x: UserDefinedArgBuilderDelegate(
            x,
            ArgBuilderFactory._ignore_unknown_fields,
            ArgBuilderFactory._walk_unknown_fields
        ),
        "DateTime": lambda: DateTimeArgBuilderDelegate(),
    }

    @staticmethod
    def walk_unknown_fields(walk: bool):
        ArgBuilderFactory._walk_unknown_fields = walk
        if walk:
            ArgBuilderFactory._ignore_unknown_fields = walk

    @staticmethod
    def ignore_unknown_fields(ignore: bool):
        ArgBuilderFactory._ignore_unknown_fields = ignore
        if not ignore:
            ArgBuilderFactory._walk_unknown_fields = ignore

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
        elif issubclass(cls, datetime.datetime):
            return ArgBuilderFactory._default_arg_builder_delegates['DateTime']()
        elif is_builtin(cls):
            return ArgBuilderFactory._default_arg_builder_delegates['PythonBuiltin'](cls)
        else:
            raise InvalidDelegateError(f'No delegate for class {cls}')

    @staticmethod
    def _safe_get(name):
        if name not in ArgBuilderFactory._default_arg_builder_delegates:
            raise InvalidDelegateError(f'Unsupported class type {name}')
        return ArgBuilderFactory._default_arg_builder_delegates[name]
