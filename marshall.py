import datetime
import inspect
import typing

import dateutil.parser as parser
import jsonpickle


def unmarshall(cls, data: dict):
    """
    Reconstruct an instance of type `cls` from JSON
    :param cls: The class type. Must be a user defined type
    :param data: The JSON data
    :return: An instance of the class `cls`

    Example:

    >>> class Test:

        >>> def __init__(self, name: str):
            >>> self.name = name


    >>> data = {'name': 'foo'}
    >>> test_instance = unmarshall(Test, data)
    >>> print(test_instance.name)
    'foo'
    """
    try:
        return __unmarshall(cls, data)
    except Exception as e:
        raise ValueError(f'Failed to marshall {data} to class {cls.__name__}')


def marshall(obj, indent=2) -> str:
    """
    Convert a class instance to a JSON formatted string
    :param obj: The object to convert
    :param indent: How to format the JSON. Defaults to an indent of 2
    :return: String JSON representation of the class instance

    Example:

    >>> class Test:

        >>> def __init__(self, name: str):
            >>> self.name = name


    >>> test_instance = Test('foo', indent=0)
    >>> data = marshall(test_instance)
    >>> print(data)
    '{name: foo}'
    """
    return jsonpickle.encode(obj, unpicklable=False, indent=indent)


def is_user_defined(cls, ignore=None) -> bool:
    """
    Returns whether the given class is user defined or not
    :param ignore: Any additional classes you'd like to ignore
    :param cls: The class type
    :return: True if the `cls` is defined by user, False otherwise

    Example:

    >>> class Test:
        >>> pass

    >>> print(is_user_defined(Test))
    True

    >>> print(is_user_defined(str))
    False

    >>> print(is_user_defined(Test, {Test}))
    False
    """
    if ignore is None:
        ignore = {}
    return cls is not None \
        and inspect.isclass(cls) \
        and cls is not datetime.datetime \
        and cls is not inspect.Parameter.empty \
        and cls.__module__ != 'builtins' \
        and cls not in ignore


def __unmarshall(cls, data: dict):
    init_params = inspect.signature(cls.__init__).parameters
    args = __get_args(cls, init_params, data)
    missing = __get_unsatisfied_args(args, init_params)
    if len(missing) > 0:
        unfilled = [key for key, param in missing.items() if param.default is inspect.Parameter.empty]
        if len(unfilled) > 0:
            raise ValueError(f'Missing required field(s): {", ".join(unfilled)}')
    result = cls(**args)
    if 'validate' in dir(cls):
        result.validate()
    return result


def __get_args(cls, unsatisfied_args, data: dict) -> dict:
    args = {}
    for key, value in __safe_get_items(cls, data):
        if key in unsatisfied_args:
            args[key] = __apply_python_typing(unsatisfied_args[key].annotation, value)
        elif isinstance(value, (list, tuple, set)):
            current_unsatisfied_args = __get_unsatisfied_args(args, unsatisfied_args)
            for x in value:
                args.update(__get_args(cls, current_unsatisfied_args, x))
        elif isinstance(value, dict):
            current_unsatisfied_args = __get_unsatisfied_args(args, unsatisfied_args)
            args.update(__get_args(cls, current_unsatisfied_args, value))
    return args


def __apply_python_typing(param_type, value: typing.Any) -> typing.Any:
    if isinstance(value, (list, set, tuple)):
        inner_param_type = param_type.__args__[0]
        if is_user_defined(inner_param_type):
            return [__unmarshall(inner_param_type, x) for x in value]
        else:
            return [__apply_python_typing(inner_param_type, x) for x in value]
    elif '_name' in param_type.__dict__ and param_type.__dict__['_name'] == 'Dict':
        key_param_type = param_type.__args__[0]
        value_param_type = param_type.__args__[1]
        return {__apply_python_typing(key_param_type, k): __apply_python_typing(value_param_type, v)
                for k, v in value.items()}
    elif is_user_defined(param_type):
        return __unmarshall(param_type, value)
    elif value is None:
        return None
    elif isinstance(value, dict):
        return param_type(**value)
    elif issubclass(param_type, datetime.datetime):
        return parser.parse(value)
    else:
        return param_type(value)


def __safe_get_items(cls, data: dict):
    try:
        return data.items()
    except AttributeError:
        raise ValueError(f'Attempted to unmarshall unsupported type {cls}')


def __get_unsatisfied_args(current_args: dict, all_params: dict):
    return {k: v for (k, v) in all_params.items() if k not in current_args and k != 'self'}
