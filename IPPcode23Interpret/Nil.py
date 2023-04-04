# Custom type nil
# Nil class is used for storing nil value
class nilType(type):

    def __repr__(cls):
        return cls.__name__


class nil(metaclass=nilType):

    def __new__(cls, name):
        obj = object.__new__(cls)
        return obj

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, nil)

    def __ne__(self, other):
        return not isinstance(other, nil)

    def __repr__(self):
        return ""