import logging
import os
from collections.abc import MutableMapping
from typing import Any, Iterator, Mapping
from typing import MutableMapping as TypeMutableMapping
from typing import Optional

import yaml

logger = logging.getLogger(__file__)

SYSTEM_CONFIGS_PATH = '/etc/grabar'
SETTINGS_DIR = os.path.join(
    os.path.realpath(os.path.dirname(__file__)),
    'configs'
)
SYSTEM_CONFIG_DIRECTORIES = (SYSTEM_CONFIGS_PATH, SETTINGS_DIR)


class Undefined:
    pass


class EnvironError(Exception):
    pass


class Environment(MutableMapping):
    def __init__(self):
        self._environ: TypeMutableMapping = os.environ
        self._has_been_read = set()

    def __getitem__(self, key: Any) -> Any:
        self._has_been_read.add(key)
        return self._environ.__getitem__(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        if key in self._has_been_read:
            raise EnvironError(
                f"Attempting to set environ['{key}'], "
                "but the value has already been read."
            )
        self._environ.__setitem__(key, value)

    def __delitem__(self, key: Any) -> None:
        if key in self._has_been_read:
            raise EnvironError(
                f"Attempting to delete environ['{key}'], "
                "but the value has already been read."
            )
        self._environ.__delitem__(key)

    def __iter__(self) -> Iterator:
        return iter(self._environ)

    def __len__(self) -> int:
        return len(self._environ)


environ = Environment()


class ConfigParser:
    def __init__(
        self,
        file_name: Optional[str] = None,
        env: Mapping[str, str] = environ
    ):
        self.environ = env
        self.configs_from_yaml = {}

        if file_name:
            self.configs_from_yaml = \
                ConfigParser.read_configs_from_yaml(file_name)

    def __call__(self, key: str, default: Any = Undefined) -> Any:
        if key in self.environ:
            return self.environ[key]

        if key in self.configs_from_yaml:
            return self.configs_from_yaml[key]

        if default is not Undefined:
            return default

        raise KeyError(f"Config '{key}' is missing, and has no default.")

    @staticmethod
    def _get_path_to_yaml(file_name):
        file_path = None

        for conf_path in SYSTEM_CONFIG_DIRECTORIES:
            path = os.path.join(conf_path, file_name)

            if os.path.exists(path):
                file_path = path
                break

        if file_path is None:
            raise OSError(f'Config with filename {file_name} is not found!')

        return file_path

    @classmethod
    def read_configs_from_yaml(cls, file_name: str) -> dict:
        file_path = cls._get_path_to_yaml(file_name)

        with open(file_path, 'r') as f:
            configs_from_yaml = yaml.safe_load(f)

            logger.info(f'YAML configs taken from {file_path}')

        return configs_from_yaml
