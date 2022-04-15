import yaml
from yamlargs.config import YAMLConfig

from yamlargs import make_lazy_constructor, make_lazy_function


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


def fake_fn(x, n=10):
    return x + n


make_lazy_constructor(Dice)
make_lazy_function(Dice)

make_lazy_constructor(DiceCup)

make_lazy_function(fake_fn)


def test_load():
    config = YAMLConfig.load("test/example.yml")
    assert config["load"]["dice"]["value"] == 123
    assert config["fn"]["n"] == 100


def test_dot_access():
    config = YAMLConfig.load("test/example.yml")
    assert config.access("load.dice.value") == 123
    assert config.access("fn.n") == 100


def test_dot_set():
    config = YAMLConfig.load("test/example.yml")
    config.set("load.dice.value", 543)
    config.set("fn.n", 543)
    assert config.access("load.dice.value") == 543
    assert config.access("fn.n") == 543


def test_keys():
    config = YAMLConfig.load("test/example.yml")
    assert config.keys() == [
        "init.class",
        "init.value",
        "load.class",
        "load.dice.class",
        "load.dice.value",
        "fn.class",
        "fn.n",
    ]


def test_json():
    config = YAMLConfig.load("test/example.yml")
    data = config.to_json()
    assert data["init"] == {"lazyObject": "!Dice", "kwargs": {"value": 49}}
    assert config == YAMLConfig.from_json(config.to_json())


def test_yaml():
    config = YAMLConfig.load("test/example.yml")
    assert config == YAMLConfig.from_yaml(config.to_yaml())
