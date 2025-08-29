# from clusterduck.core.sweep import Sweep
# from clusterduck.core.var_t import Var_t, Config
from clusterduck.core.settings import Settings
from clusterduck.core.set_paths import Set_paths
from clusterduck.core.path_schema import PathSchema

from dataclasses import dataclass, field



@dataclass
class Job:

    settings : Settings = field(default_factory=Settings)
    set_paths : Set_paths = field(default_factory=Set_paths)
    path_schema : PathSchema = field(default_factory=PathSchema)














# j1.settings.job_name = "frag_test"
# j1.settings.time = "10:00:00"
# j1.settings.add_vars('molecule',["ethylene","benzene","pyrene"])
# j1.settings.add_vars('distance',(3,14,1))
# j1.settings.add_vars('method',["G0W0","evGW","TDDFT"])



# p1 = '/Users/sarath/Documents/Research/other_projects/clusterduck/'


# j1.set_paths.input_script = "input_script.py"
# j1.set_paths.output_dir = os.path.join(p1,'out_dir')
# j1.set_paths.scratch_dir = os.path.join(p1,'scratch')
# #j1.path_schema.struct = "molecule->method->distance"
# #j1.set_paths.make_dirs()

# path1 = j1.path_schema.struct_path(j1.settings)
# print(path1)

# j1_configs = j1.settings.configs()

# for c in j1_configs:
#     print(c.as_dict(),c.uid())

