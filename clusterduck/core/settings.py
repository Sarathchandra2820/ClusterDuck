from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional

from clusterduck.core.sweep import Sweep
from clusterduck.core.var_t import Var_t


_RESERVED_OPTIONS = {"array", "job-name"}
_SBATCH_KEY = re.compile(r"^[a-zA-Z][a-zA-Z0-9-]*$")


@dataclass
class Settings:
    concurrency: Optional[int] = None
    job_name: Optional[str] = None
    sbatch_opts: Dict[str, str] = field(default_factory=dict)
    module_load: List[str] = field(default_factory=list)
    export_opts: Dict[str, str] = field(default_factory=dict)
    variable: Sweep = field(default_factory=Sweep)

    def add(self, key: str, value: Any) -> None:
        normalized = key.strip().lstrip("-").replace("_", "-")
        if not _SBATCH_KEY.fullmatch(normalized):
            raise ValueError(f"invalid SBATCH option name: {key}")
        if normalized in _RESERVED_OPTIONS:
            raise ValueError(f"'{normalized}' is managed by ClusterDuck")
        self.sbatch_opts[normalized] = str(value)

    def add_export(self, key: str, value: Any) -> None:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ValueError(f"invalid environment variable name: {key}")
        self.export_opts[key] = str(value)

    def add_vars(self, name: str, sweep: Any) -> "Settings":
        self.variable.add(Var_t(name, sweep))
        return self

    def configs(self):
        return self.variable.generate()

    @property
    def task_count(self) -> int:
        return self.variable.task_count
