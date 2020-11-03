import inspect
import json

import jsonpickle

from pymarshall.arg_delegates import ArgBuilderFactory


def unmarshall_str(cls, data: str):
    """
    Reconstruct an instance of type `cls` from a JSON formatted string
    :param ignore_unknown_fields:
    :param cls: The class type. Must be a user defined type
    :param data: The string JSON data
    :return: An instance of the class `cls`

    Example:

    >>> class Test:

        >>> def __init__(self, name: str):
            >>> self.name = name


    >>> data = "{'name': 'foo'}"
    >>> test_instance = unmarshall_str(Test,data)
    >>> print(test_instance.name)
    'foo'
    """
    return unmarshall(cls, json.loads(data))


def unmarshall(cls, data: dict):
    """
    Reconstruct an instance of type `cls` from JSON
    :param ignore_unknown_fields:
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
        return _unmarshall(cls, data)
    except ValueError:
        raise ValueError(f'Failed to pymarshall {data} to class {cls.__name__}')


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
    >>> data = pymarshall(test_instance)
    >>> print(data)
    '{name: foo}'
    """
    return jsonpickle.encode(obj, unpicklable=False, indent=indent)


def _unmarshall(cls, data: dict):
    init_params = inspect.signature(cls.__init__).parameters
    args = ArgBuilderFactory.get_delegate(cls).resolve(data)
    missing = _get_unsatisfied_args(args, init_params)
    if len(missing) > 0:
        unfilled = [key for key, param in missing.items() if param.default is inspect.Parameter.empty]
        if len(unfilled) > 0:
            raise ValueError(f'Missing required field(s): {", ".join(unfilled)}')
    result = cls(**args)
    if 'validate' in dir(cls):
        result.validate()
    return result


def _get_unsatisfied_args(current_args: dict, all_params: dict):
    return {k: v for (k, v) in all_params.items() if k not in current_args and k != 'self'}
