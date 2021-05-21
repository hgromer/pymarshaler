import datetime
import inspect

import typing


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


def is_builtin(cls) -> bool:
    try:
        return cls.__module__ == 'builtins'
    except AttributeError:
        return False


def get_init_params(cls) -> dict:
    params = typing.get_type_hints(cls)
    if params and len(params) > 0:
        return params
    params = inspect.signature(cls.__init__).parameters
    return {k: v.annotation for k, v in params.items()}

