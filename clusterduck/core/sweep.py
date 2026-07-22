from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from math import prod
from typing import Iterator, List

from clusterduck.core.var_t import Config, Var_t


@dataclass
class Sweep:
    var: List[Var_t] = field(default_factory=list)

    def add(self, variable: Var_t) -> None:
        if any(existing.name == variable.name for existing in self.var):
            raise ValueError(f"duplicate sweep parameter: {variable.name}")
        self.var.append(variable)

    @property
    def task_count(self) -> int:
        return prod(len(variable.sweep) for variable in self.var) if self.var else 1

    def iter_configs(self) -> Iterator[Config]:
        names = [variable.name for variable in self.var]
        grids = [variable.sweep for variable in self.var]
        for combination in product(*grids):
            yield Config(tuple(zip(names, combination)))

    def generate(self) -> List[Config]:
        """Compatibility helper. Prefer iter_configs() for large sweeps."""
        return list(self.iter_configs())

    def export_names(self) -> List[str]:
        return [variable.name for variable in self.var]
