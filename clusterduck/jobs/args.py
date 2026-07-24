import argparse
import sys
from pathlib import Path
from typing import Any, Callable


class ArgParses:
    def __init__(self, argv=None) -> None:
        self.argv = list(sys.argv[1:] if argv is None else argv)
        self._arguments: list[str] = []

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)

        def read_argument(
            default=None,
            *,
            type=None,
            required=False,
            choices=None,
            nargs=None,
        ):
            if name not in self._arguments:
                self._arguments.append(name)

            inferred_type = type
            if inferred_type is None and default is not None:
                inferred_type = default.__class__
            if inferred_type is None:
                inferred_type = str

            parser = argparse.ArgumentParser(add_help=False)
            parser.add_argument(
                "--" + name.replace("_", "-"),
                dest=name,
                default=default,
                type=inferred_type,
                required=required,
                choices=choices,
                nargs=nargs,
            )

            namespace, _ = parser.parse_known_args(self.argv)
            return getattr(namespace, name)

        return read_argument

    def list_arguments(self) -> list[str]:
        return list(self._arguments)


