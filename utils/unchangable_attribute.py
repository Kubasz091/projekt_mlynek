class CannotChange:
    def __init__(self, name=None):
        self._name = name

        self._values = {}
        self._set_once = {}

    def __set_name__(self, cls, name):
        self.name = name

    def __get__(self, instance, cls=None):
        if instance is None:  # when calling for example CannotChange._values
            return self

        return self._values.get(id(instance), None)

    def __set__(self, obj, value):
        obj_id = id(obj)
        if obj_id in self._set_once:
            raise ValueError(f"Cannot change {self._name} - already set")

        self._values[obj_id] = value
        self._set_once[obj_id] = True

    def __delete__(self, obj):
        raise Exception("Cannot delete")
