# -*- coding: utf-8 -*-

class ExpectError(RuntimeError):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg


class Expect(object):
    ValidExpectEnum = ('int', 'intOrNull', 'real', 'realOrNull', 'string', 'stringOrNull', 'null')

    @staticmethod
    def expectInt(value, nullable: bool):
        if not isinstance(value, int):
            if nullable and value is None:
                return value
            try:
                value = int(value)
            except (ValueError, TypeError) as e:
                raise ExpectError(f"value expect type 'int'(int), but type '{type(value)}' found")
        return value

    @staticmethod
    def expectReal(value, nullable: bool):
        if not isinstance(value, float):
            if nullable and value is None:
                return value
            try:
                value = float(value)
            except (ValueError, TypeError) as e:
                raise ExpectError(f"value expect type 'real'(float), but type '{type(value)}' found")
        return value

    @staticmethod
    def expectString(value, nullable: bool):
        if not isinstance(value, str):
            if nullable and value is None:
                return
            try:
                value = str(value)
            except (ValueError, TypeError) as e:
                raise ExpectError(f"value expect type 'string'(str), but type '{type(value)}' found")
        return value

    @staticmethod
    def expectNull(value):
        if value is not None:
            if isinstance(value, str) and not value:
                return None
        else:
            raise ExpectError(f"value expect type 'null'(None) but type '{type(value)}' found")
        return value

    @staticmethod
    def expect(type: str, value):
        match type:
            case "int":
                return Expect.expectInt(value, nullable=False)
            case "intOrNull":
                return Expect.expectInt(value, nullable=True)
            case "real":
                return Expect.expectReal(value, nullable=False)
            case "realOrNull":
                return Expect.expectReal(value, nullable=True)
            case "string":
                return Expect.expectString(value, nullable=False)
            case "stringOrNull":
                return Expect.expectString(value, nullable=True)
            case "null":
                return Expect.expectNull(value)
            case default:
                raise KeyError(f"type must be one of {Expect.ValidExpectEnum!r}, but '{type}' found")
