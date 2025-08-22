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
        if not value:
            raise ValueError("Must be non-empty/ not NaN")
        return super().check(value)


class RectangularContaier(Validator):
    @classmethod
    def check(cls, value):
        _max_len = max(len(item) for item in value)
        if not all(len(item) == _max_len for item in value):
            raise ValueError("Expected a rectangular container")
        return super().check(value)


#
#
#


class TypedContainer(Typed):
    container_type = object

    @classmethod
    def check(cls, value):
        if not isinstance(value, cls.container_type):
            raise TypeError(f"Expected {cls.container_type.__name__}")
        _parent_check = super().check
        return cls.container_type(_parent_check(item) for item in value)  # type: ignore


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


class StringTuple(TypedContainer):
    expected_type = str
    container_type = tuple


#
#
#


class RectangularStringTuple(RectangularContaier, StringTuple, NonEmpty):
    pass
