import yaml

from yamlargs.lazy import LazyConstructor, make_lazy_constructor, make_lazy_function


class Dice:
    def __init__(self, value, max_value=6):
        self.value = value
        self.max_value = max_value
        if self.value > self.max_value:
            print("Bad value")

    def __str__(self):
        return f"Dice({self.value})"

    def __repr__(self):
        return self.__str__()


class DiceCup:
    def __init__(self, dice=Dice(1, max_value=10)):
        self.dice = dice


def test_kwargs():
    c = LazyConstructor(Dice, {"max_value": 10})
    assert c(0).max_value == 10

    c = LazyConstructor(Dice, {"max_value": -1})
    assert c(0).max_value == -1


def test_kwargs_overwrite():
    c = LazyConstructor(Dice, {"max_value": 30})
    c["max_value"] = -1

    assert c(1).max_value == -1


def test_args():
    c = LazyConstructor(Dice, {"value": 1})
    assert c().value == 1
    assert c(max_value=4).value == 1
    assert c(max_value=4).max_value == 4


def test_args_overwrite():
    c = LazyConstructor(Dice, {"value": 1})
    c["value"] = 5
    assert c().value == 5


def test_lazy_as_kwarg():
    lazy_dice = LazyConstructor(Dice, {"value": 123, "max_value": 1234})
    lazy_cup = LazyConstructor(DiceCup, {"dice": lazy_dice})

    cup = lazy_cup()
    assert cup.dice.value == 123
    assert cup.dice.max_value == 1234


def test_yaml_loading_no_args():
    make_lazy_constructor(Dice)
    data = yaml.load("load: !Dice", yaml.UnsafeLoader)
    assert data["load"](1).value == 1
    data = yaml.load("load: !DiceClass", yaml.UnsafeLoader)
    assert data["load"]() == Dice


def test_yaml_loading():
    make_lazy_constructor(Dice)
    data = yaml.load("load: !Dice\n value: 1", yaml.UnsafeLoader)
    assert data["load"]().value == 1
    data = yaml.load("load: !DiceClass", yaml.UnsafeLoader)
    assert data["load"]() == Dice


def test_yaml_loading_with_kwargs():
    make_lazy_constructor(Dice, {"max_value": 10})
    data = yaml.load("load: !Dice\n value: 1", yaml.UnsafeLoader)
    assert data["load"]().value == 1
    assert data["load"]().max_value == 10


def test_yaml_loading_lazy_recursive():
    make_lazy_constructor(Dice)
    make_lazy_constructor(DiceCup)
    data = yaml.load("load: !DiceCup\n dice: !Dice\n  value: 123", yaml.UnsafeLoader)
    assert data["load"]().dice.value == 123


def test_yaml_function_with_kwargs():
    def fn(x, b=1):
        return x**2 + b

    make_lazy_function(fn)
    data = yaml.load("my_fn: !fn\n b: 2", yaml.UnsafeLoader)
    myfn = data["my_fn"]()
    assert myfn(2) == 6


def test_yaml_function():
    def fn(x, b=1):
        return x**2 + b

    make_lazy_function(fn)
    data = yaml.load("my_fn: !fn", yaml.UnsafeLoader)
    myfn = data["my_fn"]()
    assert myfn(2) == 5


def test_yaml_function_recurse():
    def fn(x, b=1):
        return x**2 + b

    make_lazy_function(fn)
    data = yaml.load("cup: !DiceCup\n dice: !fn\n  b: 2", yaml.UnsafeLoader)
    cup = data["cup"]()
    assert cup.dice(2) == 6
