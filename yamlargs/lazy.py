import sys
from dataclasses import dataclass
from typing import Any, Dict

import yaml


@dataclass(frozen=True)
class LazyConstructor:
    """
    An object that wraps a constructor in a lazy, configurable way.

    It turns the constructor into a dictionary like object that allows you to
    set and overwrite the default values like a dictionary, and then intialize
    kind of like a factory.

    LazyConstructor should be intialized with a class and a dictionary of key
    word arguemnts. It will then represent a lazy version of lambda *args:
    class(*args, **kwargs).

    If a LazyConstructor depends on a key word argument that is also a
    LazyConstructor, it will recursively intitialize it before intializing
    itself.

    >>> class Dice:
    ...       def __init__(self, value, max_value=6):
    ...               self.value = value
    ...               if self.value > max_value:
    ...                       print("Bad value")
    ...       def __str__(self):
    ...               return f"Dice({self.value})"
    ...       def __repr__(self):
    ...               return self.__str__()
    ...
    >>> c = LazyConstructor(Dice, {"max_value": 6})
    >>> c(1)
    Dice(1)
    >>> c(10)
    Bad value
    Dice(10)
    >>> c['max_value'] = 12
    >>> c(10)
    Dice(10)
    >>> print(c)
    {'class': <class '__main__.Dice'>, 'max_value': 12}
    >>> c = LazyConstructor(Dice, {"max_value": 6, "value": 1})
    >>> c()
    Dice(1)
    >>> c['value'] = 4
    >>> c()
    Dice(4)
    """

    _fn: Any
    _kwargs: Dict

    def __getitem__(self, key):
        if key == "class":
            return self._fn
        else:
            return self._kwargs.__getitem__(key)

    def __setitem__(self, key, value):
        if key == "class":
            self._fn = value
        else:
            self._kwargs.__setitem__(key, value)

    def __call__(self, *args, **kwargs):
        # If there are any LazyConstructors in the keyword arguments, intialize
        # them before intializing itself. Allows for a recursive chain of
        # intialization. Also copies over the specified kwargs.

        init_kwargs = {}
        for (k, v) in list(self._kwargs.items()) + list(kwargs.items()):
            if isinstance(v, LazyConstructor):
                init_kwargs[k] = v()
            else:
                init_kwargs[k] = v
        return self._fn(*args, **init_kwargs)

    def __repr__(self):
        d = {"class": self._fn}
        d.update(self._kwargs)
        return str(d)

    def __str__(self):
        return self.__repr__()

    def keys(self):
        """Fake keys to act like a dictionary"""
        return ["class"] + list(self._kwargs.keys())

    def values(self):
        """Fake values to act like a dictionary"""
        return [self._fn] + list(self._kwargs.values())

    def items(self):
        """Fake items to act like a dictionary"""
        keys = self.keys()
        return [(k, self.__getitem__(k)) for k in keys]

def _get_kwargs_from_node(loader, node):
    #TODO: This try except is a little weird. I feel like there should be a
    # way to check rather than the error
    try:
        kwargs = loader.construct_mapping(node)
    # No mapping specified, treat this an empty dict
    except yaml.constructor.ConstructorError:
        kwargs = {}
    return kwargs

def make_lazy_constructor(type_, default_kwargs=None):
    """
    Exposes to YAML a lazy constructor for the object, so it can be referenced
    in a config. Exposes both the ability to create the object itself, and it's
    class as a type.

    >>> make_lazy_constructor(Dice)
    >>> data = yaml.load("dice: !Dice", yaml.UnsafeLoader)
    >>> data["dice"]()
    Dice()
    >>> data = yaml.load("dice: !DiceClass", yaml.UnsafeLoader)
    >>> data["dice"]()
    Dice
    """

    name = type_.__name__

    def _constructor(loader, node):

        kwargs = _get_kwargs_from_node(loader, node)

        # Surely, there must be a better way to do this, right? I tried .update
        # but that was casuing weird issues.

        if default_kwargs is not None:
            for (k, v) in default_kwargs.items():
                if k not in kwargs.keys():
                    kwargs[k] = v


        return LazyConstructor(type_, kwargs)

    def _type_constructor(loader, node):
        return lambda: type_

    yaml.add_constructor("!" + name, _constructor)
    yaml.add_constructor("!" + name + "Class", _type_constructor)


def make_lazy_function(type_, default_kwargs=None):
    """
    Exposes to YAML a lazy function, so it can be referenced
    in a config.

    >>> def fn(x, b=1):
    ...     return x**2 + b
    >>> make_lazy_function(fn)
    >>> data = yaml.load("my_fn: !fn\n b: 2", yaml.UnsafeLoader)
    >>> myfn = data["my_fn"]()
    >>> myfn(2)
    6
    """

    name = type_.__name__

    def _constructor(loader, node):
        kwargs = _get_kwargs_from_node(loader, node)

        if default_kwargs is not None:
            for (k, v) in default_kwargs.items():
                if k not in kwargs.keys():
                    kwargs[k] = v

        return LazyConstructor(LazyConstructor, {"_fn": type_, "_kwargs": kwargs})

    yaml.add_constructor("!" + name, _constructor)