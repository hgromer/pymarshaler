import dateutil.parser as parser

from pymarshaler.errors import UnknownFieldError
from pymarshaler.utils import get_init_params


def enum_delegate(cls, data, ignore_func):
    for v in cls.__members__.values():
        if v.value == data:
            return v
    raise UnknownFieldError(f'Invalid value {data} for enum {cls.__name__}')


def list_delegate(cls, data, func):
    inner_type = cls.__args__[0]
    return [func(inner_type, x) for x in data]


def set_delegate(cls, data, func):
    inner_type = cls.__args__[0]
    return {func(inner_type, x) for x in data}


def tuple_delegate(cls, data, func):
    inner_type = cls.__args__[0]
    return func(inner_type, data[0]), func(inner_type, data[1])


def dict_delegate(cls, data, func):
    key_type = cls.__args__[0]
    value_type = cls.__args__[1]
    return {
        func(key_type, key): func(value_type, value) for key, value in data.items()
    }


def builtin_delegate(cls, data, ignore_func):
    if data is None:
        return None
    else:
        return cls(data)


def datetime_delegate(cls_ignore, data, ignore_func=None):
    return parser.parse(data)


def user_defined_delegate(cls, data, func, ignore_unknown_fields: bool, walk_unknown_fields: bool):
    args = {}
    unsatisfied = get_init_params(cls)
    for key, value in data.items():
        if key in unsatisfied:
            param_type = unsatisfied[key]
            args[key] = func(param_type, value)
        elif not ignore_unknown_fields:
            raise UnknownFieldError(f'Found unknown field ({key}: {value}). '
                                    'If you would like to skip unknown fields '
                                    'create a Marshal object who can skip ignore_unknown_fields')
        elif walk_unknown_fields:
            if isinstance(value, dict):
                args.update(user_defined_delegate(cls, value, func, ignore_unknown_fields, walk_unknown_fields))
            elif isinstance(value, (list, set, tuple)):
                for x in value:
                    if isinstance(x, dict):
                        args.update(user_defined_delegate(cls, x, func, ignore_unknown_fields, walk_unknown_fields))
    return args
