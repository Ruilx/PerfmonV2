# -*- coding: utf-8 -8-

"""
Common formats
@ Ruilx
"""

from src.formats.format import format, FormatError


@format("toInt")
def toInt(value):
    try:
        return int(value)
    except BaseException as e:
        raise FormatError(e) from e


@format("toIntOrNull")
def toIntOrNull(value):
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        return None


@format("toFloat")
def toFloat(value):
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        return float(0)


@format("toFloatOrNone")
def toFloatOrNone(value):
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        return None


@format("toFloat")
def toFloat(value):
    try:
        return float(value)
    except BaseException as e:
        raise FormatError(e) from e
