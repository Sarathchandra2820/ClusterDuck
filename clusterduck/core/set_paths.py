from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import List, Optional


@dataclass
class Set_paths:
    input_script: Optional[str] = None
    output_dir: Optional[str] = None
    output_files: Optional[str] = None
    scratch_dir: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    env_path: Optional[str] = None

    @property
    def dependancies(self) -> List[str]:
        """Backward-compatible alias for the old misspelling."""
        return self.dependencies

    @dependancies.setter
    def dependancies(self, value: List[str]) -> None:
        self.dependencies = list(value)

    def make_dirs(self) -> None:
        if self.scratch_dir and self.scratch_dir != "$TMPDIR":
            os.makedirs(self.scratch_dir, exist_ok=True)
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)

    def rm_dirs(self) -> None:
        if self.scratch_dir and self.scratch_dir != "$TMPDIR" and os.path.isdir(self.scratch_dir):
            os.rmdir(self.scratch_dir)
        if self.output_dir and os.path.isdir(self.output_dir):
            os.rmdir(self.output_dir)
