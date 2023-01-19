# -*- coding: utf-8 -*-

"""
Format factory class
"""

from src.util import singleton

@singleton
class FormatFactory(object):
    def __init__(self):
        self.__formats = {}

    def __setitem__(self, key: str, value):
        self.__formats[key] = value

    def __getitem__(self, key: str):
        if key in self.__formats:
            return self.__formats[key]
        raise KeyError(f"format has no format method names '{key}'")

    def __contains__(self, key: str):
        return key in self.__formats


def format(name: str):
    def decorator(func):
        if name not in FormatFactory():
            FormatFactory()[name] = func

            def inner(value):
                if callable(func):
                    return func(value)
                raise ValueError(f"Format function '{func}' is not callable")

            return inner
        else:
            raise NameError(f"format name '{name}' already registered into format factory")
    return decorator


class FormatError(RuntimeError):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg
