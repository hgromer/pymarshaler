import inspect
import json

import jsonpickle

from pymarshaler.arg_delegates import ArgBuilderFactory
from pymarshaler.errors import MissingFieldsError


def unmarshal_str(cls, data: str):
    """
    Reconstruct an instance of type `cls` from a JSON formatted string
    :param cls: The class type. Must be a user defined type
    :param data: The string JSON data
    :return: An instance of the class `cls`

    Example:

    >>> class Test:

        >>> def __init__(self, name: str):
            >>> self.name = name


    >>> data = "{'name': 'foo'}"
    >>> test_instance = unmarshal_str(Test,data)
    >>> print(test_instance.name)
    'foo'
    """
    return unmarshal(cls, json.loads(data))


def unmarshal(cls, data: dict):
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
    >>> test_instance = unmarshal(Test, data)
    >>> print(test_instance.name)
    'foo'
    """
    try:
        return _unmarshal(cls, data)
    except ValueError:
        raise ValueError(f'Failed to pymarshaler {data} to class {cls.__name__}')


def marshal(obj, indent=2) -> str:
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
    >>> data = pymarshaler(test_instance)
    >>> print(data)
    '{name: foo}'
    """
    return jsonpickle.encode(obj, unpicklable=False, indent=indent)


def _unmarshal(cls, data: dict):
    init_params = inspect.signature(cls.__init__).parameters
    args = ArgBuilderFactory.get_delegate(cls).resolve(data)
    missing = _get_unsatisfied_args(args, init_params)
    if len(missing) > 0:
        unfilled = [key for key, param in missing.items() if param.default is inspect.Parameter.empty]
        if len(unfilled) > 0:
            raise MissingFieldsError(f'Missing required field(s): {", ".join(unfilled)}')
    result = cls(**args)
    if 'validate' in dir(cls):
        result.validate()
    return result


def _get_unsatisfied_args(current_args: dict, all_params: dict):
    return {k: v for (k, v) in all_params.items() if k not in current_args and k != 'self'}
