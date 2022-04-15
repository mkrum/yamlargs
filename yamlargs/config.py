from dataclasses import dataclass
from argparse import ArgumentParser
from typing import Dict, Any

import yaml

from yamlargs.lazy import LazyConstructor


@dataclass(frozen=True)
class YAMLConfig:
    """
    Config object.
    """

    data: Dict

    @classmethod
    def load(cls, path: str) -> "YAMLConfig":
        """
        Loads the config into a YAMLConfig object.

        This basically only exists to remind you to use yaml.UnsafeLoader.

        Parameters
        ----------
        path: str
            path to yaml config file

        Returns
        -------
        config: YAMLConfig
            Initialized config instance
        """
        data = yaml.load(open(path, "r"), yaml.UnsafeLoader)
        return cls(data)

    @classmethod
    def from_json(cls, data):
        yaml_data = _dict_to_yaml(data)
        data = yaml.load(yaml_data, yaml.UnsafeLoader)
        return cls(data)

    @classmethod
    def from_yaml(cls, yaml_str):
        data = yaml.load(yaml_str, yaml.UnsafeLoader)
        return cls(data)

    def access(self, access_str: str):
        return _dot_access(self.data, access_str)

    def set(self, access_str: str, new_value: Any):
        _dot_set(self.data, access_str, new_value)

    def keys(self):
        return _get_all_keys(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

    def to_json(self):
        """
        Converts the config into JSON data for logging purposes
        """
        new_data = {}
        for (k, v) in self.data.items():
            if isinstance(v, LazyConstructor):
                new_data[k] = v.as_dict()
            else:
                new_data[k] = v
        return new_data

    def to_yaml(self):
        """
        Converts the config into JSON data for logging purposes
        """
        yaml_data = ""
        json_data = self.to_json()
        return _dict_to_yaml(json_data)


def _dict_to_yaml(data, indent=""):
    """
    Helper function for recursively turning the json data into yaml strings.
    """
    yaml_data = ""
    for (k, v) in data.items():
        if isinstance(v, dict) and "lazyObject" in v.keys():
            name = v["lazyObject"]
            yaml_data += f"{indent}{k}: {name}\n"
            yaml_data += _dict_to_yaml(v["kwargs"], indent + " " * 4)
        else:
            yaml_data += f"{indent}{k}: {v}\n"
    return yaml_data


def _get_all_keys(config):
    keys = []
    for (k, v) in config.items():
        # isinstance(LazyConstructor, "keys") actually returns true, so we need
        # to double check that it is specifically not a LazyConstructor
        if hasattr(v, "keys") and v != LazyConstructor:
            subkeys = _get_all_keys(v)
            for sk in subkeys:
                keys.append(".".join([k, sk]))
        else:
            keys.append(k)

    return keys


def _dot_access(nested_dict, dot_key):
    keys = dot_key.split(".")
    d = nested_dict
    for k in keys:
        d = d[k]
    return d


def _dot_set(nested_dict, dot_key, value):
    keys = dot_key.split(".")
    d = nested_dict
    for k in keys[:-1]:
        d = d[k]
    d[keys[-1]] = value
    return d
