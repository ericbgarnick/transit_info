import os
import pathlib

import typing

import yaml


class Config:
    def __init__(self):
        self._flask_env = os.getenv("FLASK_ENV")
        if not self._flask_env:
            raise RuntimeError("No FLASK_ENV value set!")

        self._config_file = pathlib.Path(
            pathlib.Path(__name__).absolute().parent,
            f"config_{self._flask_env}.yaml",
        )

        self._config = yaml.load(open(self._config_file, "r"), yaml.Loader)
        if not self._config:
            raise RuntimeError(f"No config loaded from {self._config_file}")

    @property
    def config(self) -> typing.Dict:
        return self._config

    @property
    def flask_env(self) -> str:
        return self._flask_env
