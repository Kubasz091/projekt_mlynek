from typing_extensions import Self


# after consideration I do not think it will be useful, but leaving it for now
class ObjectFactory:
    _instance = None
    _initialized = False

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        pass
