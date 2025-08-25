from dataclasses import dataclass, field
import os

@dataclass
class Set_paths():
    mode:str 
    input_script: str
    output_dir: str
    dependancies: list[str] = field(default_factory=list)
    scratch_dir: str 

    env_path: str = None

    def __post_init__(self):
        if self.mode=="automatic":
            self.scratch_dir = os.path.join(self.scratch_dir, self.output_dir)
            os.makedirs(self.scratch_dir, exist_ok=True)
            os.makedirs(self.output_dir, exist_ok=True)
            if self.env_path is None:
                self.env_path = os.path.join(os.getcwd(), 'env', 'bin', 'activate')


