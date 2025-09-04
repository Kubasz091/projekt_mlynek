class CannotChange:
    def __init__(self, name=None):
        self._name = name
        # Unique per-descriptor attribute names to store data on the instance itself
        self._values_attr = f"__cc_values_{id(self)}"
        self._set_flag_attr = f"__cc_set_{id(self)}"

    def __set_name__(self, cls, name):
        self.name = name
        if self._name is None:
            self._name = name

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        return getattr(instance, self._values_attr, None)

    def __set__(self, obj, value):
        if getattr(obj, self._set_flag_attr, False):
            raise ValueError(f"Cannot change {self._name} - already set")
        setattr(obj, self._values_attr, value)
        setattr(obj, self._set_flag_attr, True)

    def __delete__(self, obj):
        raise Exception("Cannot delete")
