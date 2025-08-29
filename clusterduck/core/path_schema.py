from dataclasses import dataclass, field
from typing import Optional
import os

@dataclass
class PathSchema:

    struct: Optional[str] = None                 # e.g. "molecule->method->distance"
    output_key: list[str] = field(default_factory=list)
    scratch_key: list[str] = field(default_factory=list)  # or Optional[list[str]] = None
    

    def struct_path(self, settings=None) -> str:
        if self.struct is None:
            if settings is None:
                raise ValueError("settings must be provided when struct is None")
            # names of variables that actually vary (sweep length > 1)
            struct_lis = [v.name for v in settings.variable.var if len(v.sweep) > 1]
        elif "->" in self.struct:
            struct_lis = [s.strip() for s in self.struct.split("->")]
        else:
            raise ValueError("Invalid input (must be 'var1->var2->var3' or None).")

        return os.path.join(*struct_lis) if struct_lis else ""
