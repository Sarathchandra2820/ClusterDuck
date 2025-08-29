from dataclasses import dataclass, field
from clusterduck.core.var_t import Var_t
from clusterduck.core.sweep import Sweep

@dataclass
class Settings:
    
    sbatch_opts : dict =  field(default_factory=dict)
    module_load : list[str] = field(default_factory=list)
    export_opts : dict = field(default_factory=dict)
    # time: str = None
    # job_name: str = None
    # mem: str = None
    # partition: str = None
    # mail_type: str = "NONE" #by default
    # concurrency: int = None
    variable : Sweep = field(default_factory=Sweep)

    def add(self,key:str, value: str):
        self.sbatch_opts[key] = value
    
    def add_export(self,key:str, value : str):
        self.export_opts[key] = value

    # input_script : str
    # dependancies : list[str] = field(default_factory=list)
    # output_dir : str

    def add_vars(self,name,sweep):
        self.variable.add(Var_t(name,sweep))
        return self     
    
    def configs(self):
        return self.variable.generate()

# Example usage

# settings = Settings()
# settings.add('job-name',"default")
# settings.add('time','01:00:00')
# settings.add('concurrency','5')
# settings.add_vars('ent_params',["random","symmetric"])
# settings.add_vars('ent_struct',["sym_in_out","sym_out_in","forward","backward"])
# settings.add_vars('lr',[0.01,0.05])







# configs = settings.configs()

# print(settings.job_name)
# for c in configs:
#     print(c.as_dict(), c.uid())



    

# j = Jobs()
# j.add(Var_t('ent_params',["random","symmetric"]))
# j.add(Var_t('ent_struct',["sym_in_out","sym_out_in","forward","backward"]))
# j.add(Var_t('lr',[0.01,0.05]))

# settings = Settings()
# settings.time = "80:00:00"
# settings.var.add(Var_t('ent_params',["random","symmetric"]))
# settings.var.add(Var_t('ent_struct',["sym_in_out","sym_out_in","forward","backward"]))

# print(settings.var)