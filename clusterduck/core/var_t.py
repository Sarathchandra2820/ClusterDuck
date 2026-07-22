from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import hashlib
import re
from typing import Any, Iterable, List, Tuple


_SHELL_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _numeric_range(start: Any, end: Any, step: Any) -> List[Any]:
    """Expand an inclusive numeric range without accumulating float drift."""
    if step == 0:
        raise ValueError("sweep step cannot be zero")

    start_d = Decimal(str(start))
    end_d = Decimal(str(end))
    step_d = Decimal(str(step))
    if (end_d - start_d) * step_d < 0:
        raise ValueError("sweep step points away from the end value")

    values: List[Any] = []
    current = start_d
    compare = (lambda value: value <= end_d) if step_d > 0 else (lambda value: value >= end_d)
    all_integral = all(isinstance(value, int) and not isinstance(value, bool) for value in (start, end, step))
    while compare(current):
        values.append(int(current) if all_integral else float(current))
        current += step_d
    return values


@dataclass
class Var_t:
    """A named set of values used by a SLURM parameter sweep."""

    name: str
    sweep: Any

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _SHELL_NAME.fullmatch(self.name):
            raise ValueError(
                "parameter names must be valid shell identifiers "
                "(letters, numbers and underscores; cannot start with a number)"
            )

        values: Iterable[Any]
        if isinstance(self.sweep, range):
            values = list(self.sweep)
        elif isinstance(self.sweep, list):
            values = list(self.sweep)
        elif isinstance(self.sweep, tuple):
            if len(self.sweep) != 3:
                raise ValueError("a tuple sweep must be (start, end, step)")
            values = _numeric_range(*self.sweep)
        elif isinstance(self.sweep, (int, float, str)) and not isinstance(self.sweep, bool):
            values = [self.sweep]
        else:
            raise TypeError("sweep must be a scalar, list, range, or (start, end, step) tuple")

        self.sweep = list(values)
        if not self.sweep:
            raise ValueError(f"sweep '{self.name}' must contain at least one value")
        if any(value is None for value in self.sweep):
            raise ValueError(f"sweep '{self.name}' cannot contain None")
        if any(
            isinstance(value, str) and any(character in value for character in ("\x00", "\n", "\r"))
            for value in self.sweep
        ):
            raise ValueError(f"sweep '{self.name}' cannot contain NUL or newline characters")


@dataclass(frozen=True)
class Config:
    kv: Tuple[Tuple[str, Any], ...]

    def as_dict(self) -> dict:
        return dict(self.kv)

    def uid(self) -> str:
        digest = hashlib.sha256(repr(self.kv).encode("utf-8"))
        return digest.hexdigest()[:12]
