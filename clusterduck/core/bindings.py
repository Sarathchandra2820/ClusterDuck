from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Optional


_SHELL_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class InputBinding:
    """Marker base class for ways a sweep value enters a workload."""


@dataclass(frozen=True)
class Argument(InputBinding):
    option: Optional[str] = None

    def __post_init__(self) -> None:
        if self.option is not None and (
            not self.option or "\x00" in self.option or "\n" in self.option or "\r" in self.option
        ):
            raise ValueError("argument option cannot be empty or contain control characters")

    def option_for(self, parameter_name: str) -> str:
        return self.option or "--" + parameter_name.replace("_", "-")


@dataclass(frozen=True)
class Environment(InputBinding):
    variable: str

    def __post_init__(self) -> None:
        if not _SHELL_NAME.fullmatch(self.variable):
            raise ValueError(f"invalid environment variable name: {self.variable}")


@dataclass(frozen=True)
class TemplateVariable(InputBinding):
    placeholder: Optional[str] = None

    def __post_init__(self) -> None:
        if self.placeholder is not None and not _SHELL_NAME.fullmatch(self.placeholder):
            raise ValueError(f"invalid template placeholder: {self.placeholder}")

    def placeholder_for(self, parameter_name: str) -> str:
        return self.placeholder or parameter_name


@dataclass(frozen=True)
class TemplateSpec:
    source: str
    destination: str
