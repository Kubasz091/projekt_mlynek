class Validator:
    def __init__(self, name=None):
        self.name = name

    def __set_name__(self, cls, name):
        self.name = name

    @classmethod
    def check(cls, value):
        return value

    def __set__(self, instance, value):
        instance.__dict__[self.name] = self.check(value)


#
#
#


class Typed(Validator):
    expected_type = object

    @classmethod
    def check(cls, value):
        if isinstance(cls.expected_type, tuple):
            if not isinstance(value, cls.expected_type):
                type_names = " or ".join(t.__name__ for t in cls.expected_type)
                raise TypeError(f"Expected {type_names}, got {type(value).__name__}")
        else:
            if not isinstance(value, cls.expected_type):
                raise TypeError(
                    f"Expected {cls.expected_type.__name__}, got {type(value).__name__}"
                )
        return super().check(value)


class NonEmpty(Validator):
    @classmethod
    def check(cls, value):
        if len(value) == 0:
            raise ValueError("Must be non-empty")
        return super().check(value)


class RectangularList(Validator):
    @classmethod
    def check(cls, value):
        if not all(len(item) == max(len(row) for row in value) for item in value):
            raise ValueError("Expected a rectangular list")
        return super().check(value)


class FixedLengthContainer(Validator):
    expected_length = 0

    @classmethod
    def check(cls, value):
        if len(value) != cls.expected_length:
            raise ValueError(f"Expected container of length {cls.expected_length}")
        return super().check(value)


class PositiveContainer(Validator):
    @classmethod
    def check(cls, value):
        if not all(item >= 0 for item in value):
            raise ValueError("All items must be non-negative")
        return super().check(value)


class TypedContainer(Validator):
    expected_type = object
    container_type = object

    @classmethod
    def check(cls, value):
        if not isinstance(value, cls.container_type):
            raise TypeError(f"Expected {cls.container_type.__name__}")
        if isinstance(cls.expected_type, tuple):
            if not all(isinstance(item, cls.expected_type) for item in value):  # type: ignore
                type_names = " or ".join(t.__name__ for t in cls.expected_type)
                raise TypeError(f"All items must be {type_names}")
        else:
            if not all(isinstance(item, cls.expected_type) for item in value):  # type: ignore
                raise TypeError(f"All items must be {cls.expected_type.__name__}")
        return super().check(value)


#
#
#
class PositiveInt(Typed):
    expected_type = int

    @classmethod
    def check(cls, value):
        if value < 0:
            raise ValueError("Value must be non-negative")
        return super().check(value)


#
#
#


class TypedList(TypedContainer):
    container_type = list


class TypedTuple(TypedContainer):
    container_type = tuple


class StringList(TypedList):
    expected_type = str


class IntTuple(TypedTuple):
    expected_type = int


#
#
#
#
#


class TerminalPosition(IntTuple, PositiveContainer, FixedLengthContainer):
    expected_length = 2

    @classmethod
    def check(cls, value):
        try:
            return super().check(value)
        except TypeError as e:
            try:
                return super().check(tuple(value))
            except TypeError:
                raise TypeError(
                    f"Expected a tuple of two integers, got {type(value).__name__}"
                ) from e


class RectangularStringList(StringList, RectangularList, NonEmpty):
    pass
