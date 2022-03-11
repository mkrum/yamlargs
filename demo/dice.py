
import numpy as np
import yamlargs as ya

class Dice:

    def __init__(self, value, max_value=6):
        self.value = value
        if self.value > max_value:
            print("Bad value")

    def __str__(self):
        return f"Dice({self.value})"

    def __repr__(self):
        return self.__str__()

class DiceCup:
    def __init__(self, dice=Dice(1, max_value=10)):
        self.dice = dice


def sample(dice_cup, n=1):
    return np.random.choice(dice_cup.dice.value, size=n)

ya.make_lazy_constructor(Dice)
ya.make_lazy_constructor(DiceCup)
ya.make_lazy_function(sample)

if __name__ == "__main__":
    config = ya.load_config_and_parse_cli()
    cup = config["dice_cup"]()
    fn = config["fn"]()
    print(cup.dice)
    print(fn(cup))
