from dataclasses import dataclass, field
import os

@dataclass
class Set_paths:
    
 
    input_script: str = None
    output_dir: str = None
    output_files: str = None
    scratch_dir: str = None

    dependancies: list[str] = field(default_factory=list)

    env_path: str = None

    def make_dirs(self):
        
        if self.scratch_dir != "$TMPDIR":
            os.makedirs(self.scratch_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def rm_dirs(self):
        if os.path.exists(self.scratch_dir):
            os.rmdir(self.scratch_dir)
        if os.path.exists(self.output_dir):
            os.rmdir(self.output_dir)
            



path = Set_paths()
path.input_script = os.path.join(os.getcwd(), 'run_experiment.sh')
path.output_dir = os.path.join(os.getcwd(), 'results')
path.scratch_dir = os.path.join(os.getcwd(), 'scratch')

path.make_dirs()
path.rm_dirs()

print(path.scratch_dir)