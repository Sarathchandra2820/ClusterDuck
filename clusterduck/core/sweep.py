from clusterduck.core.var_t import Var_t, Config
from dataclasses import dataclass, field
from itertools import product

@dataclass
class Sweep():
    var: list[Var_t] = field(default_factory=list)


    def add(self, var_t: Var_t):
        self.var.append(var_t)
    
    def generate(self) -> list[Config]:
        names = [v.name for v in self.var]
        grid = [v.sweep for v in self.var]
        configs=[]

        for combo in product(*grid):
            kv = tuple(sorted(zip(names, combo)))
            configs.append(Config(kv))
        return configs
    
    def export_names(self) -> list:
        var_names = [v.name for v in self.var]
        return var_names

    


# v1 = Var_t('ent_params',["random","symmetric"])
# v2 = Var_t('ent_struct',["sym_in_out","sym_out_in","forward","backward"])

# sw = Sweep([v1,v2])
# configs = sw.generate()

# for c in configs:
#     print(c.as_dict(), c.uid())

# print("Var names:", sw.export_names())