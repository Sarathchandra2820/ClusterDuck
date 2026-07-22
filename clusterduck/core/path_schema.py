from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import List, Optional


@dataclass
class PathSchema:
    struct: Optional[str] = None
    output_key: List[str] = field(default_factory=list)
    scratch_key: List[str] = field(default_factory=list)

    def names(self, settings) -> List[str]:
        available = {variable.name for variable in settings.variable.var}
        if self.struct is None:
            return [
                variable.name
                for variable in settings.variable.var
                if len(variable.sweep) > 1
            ]
        names = [part.strip() for part in self.struct.split("->")]
        if not names or any(not name for name in names):
            raise ValueError("path schema must look like 'var1->var2->var3'")
        unknown = [name for name in names if name not in available]
        if unknown:
            raise ValueError(f"unknown parameters in path schema: {', '.join(unknown)}")
        return names

    def struct_path(self, settings=None) -> str:
        if settings is None:
            raise ValueError("settings must be provided")
        return os.path.join(*self.names(settings)) if self.names(settings) else ""

    def value_template(self, settings) -> str:
        return "/".join("{" + name + "}" for name in self.names(settings))
