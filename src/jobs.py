from sweep import Sweep
from var_t import Var_t, Config
from settings import Settings
from set_paths import Set_paths
from dataclasses import dataclass, field
import os


@dataclass
class Job:

    settings : Settings = field(default_factory=Settings)
    paths : Set_paths = field(default_factory=Set_paths)

    structure : list






j1 = Job()

j1.settings.job_name = "frag_test"
j1.settings.time = "10:00:00"
j1.settings.add_vars('molecule',["ethylene","benzene","pyrene"])
j1.settings.add_vars('distance',(3,14,1))
j1.settings.add_vars('method',["G0W0","evGW","TDDFT"])



p1 = '/Users/sarath/Documents/Research/other_projects/clusterduck/'


j1.paths.input_script = "input_script.py"
j1.paths.output_dir = os.path.join(p1,'out_dir')
j1.paths.scratch_dir = os.path.join(p1,'scratch')
j1.paths.structure = ['molecule','method','distance']
j1.paths.make_dirs()





# j1_configs = j1.settings.configs()

# for c in j1_configs:
#     print(c.as_dict(),c.uid())

