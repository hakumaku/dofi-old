"""
Read spec from yaml files, and convert it to python objects.
"""
from pathlib import Path

from pydantic import TypeAdapter

import yaml

from dofi.extra.types import Package


class Spec:
    def __init__(self, packages: list[Package]):
        self.packages = packages

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ({len(self)})>"

    def __len__(self) -> int:
        return len(self.packages)

    @staticmethod
    def from_yaml(path: Path) -> "Spec":
        with open(path, "r") as fp:
            try:
                contents = yaml.safe_load(fp)
            except yaml.YAMLError as exc:
                print(exc)

        repositories = contents["packages"]

        adapter = TypeAdapter(list[Package])
        objects = adapter.validate_python(repositories)

        return Spec(objects)
