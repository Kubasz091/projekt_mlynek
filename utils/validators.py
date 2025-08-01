from typing import Any


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


class TypedList(Validator):
    expected_type = object
    container_type = list

    @classmethod
    def check(cls, value):
        if not isinstance(value, cls.container_type):
            raise TypeError(f"Expected {cls.container_type.__name__}")
        if not all(isinstance(item, cls.expected_type) for item in value):
            raise TypeError(f"All items must be {cls.expected_type.__name__}")
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


class StringList(TypedList):
    expected_type = str

class RectangularStringList(StringList, RectangularList, NonEmpty):
    pass



if __name__ == "__main__":
    class TestClass:
        txt = RectangularStringList()

        def __repr__(self) -> str:
            return '\n'.join(self.txt) + '\n' # type: ignore

    obj = TestClass()

    obj.txt = []

    print(obj)