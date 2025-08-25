from dataclasses import dataclass, field
from var_t import Var_t
from sweep import Sweep

@dataclass
class Settings():

    time: str = "01:00:00"
    job_name: str = "test_job"
    mem: str = "4GB"
    partition: str = "tc"
    mail_type: str = "None"
    concurrency: int = 5
    variable : Sweep = field(default_factory=Sweep)

    # input_script : str
    # dependancies : list[str] = field(default_factory=list)
    # output_dir : str

    def add_vars(self,name,sweep):
        self.variable.add(Var_t(name,sweep))
        return self 
    
    
    
    def configs(self):
        return self.variable.generate()

# Example usage

settings = Settings()
settings.job_name = "frag_test"
settings.time = "10:00:00"
settings.add_vars('ent_params',["random","symmetric"])
settings.add_vars('ent_struct',["sym_in_out","sym_out_in","forward","backward"])
settings.add_vars('lr',[0.01,0.05])




configs = settings.configs()

print(settings.job_name)
for c in configs:
    print(c.as_dict(), c.uid())



    

# j = Jobs()
# j.add(Var_t('ent_params',["random","symmetric"]))
# j.add(Var_t('ent_struct',["sym_in_out","sym_out_in","forward","backward"]))
# j.add(Var_t('lr',[0.01,0.05]))

# settings = Settings()
# settings.time = "80:00:00"
# settings.var.add(Var_t('ent_params',["random","symmetric"]))
# settings.var.add(Var_t('ent_struct',["sym_in_out","sym_out_in","forward","backward"]))

# print(settings.var)