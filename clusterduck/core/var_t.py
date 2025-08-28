from dataclasses import dataclass
import hashlib




# class Var_t():
#     def __init__(self,name,sweep=None):
#         if name is None:
#             self.name = ""
#         elif isinstance(name, str):
#             self.name = name
#         if isinstance(sweep, list):
#             self.sweep = sweep
#         if isinstance(sweep, int) or isinstance(sweep, float):
#             self.sweep = [sweep]
#         if isinstance(sweep, (tuple)) and len(sweep) == 3:
#             start, end, step = sweep
#             self.sweep = [round(start + i * step, 10) for i in range(int((end - start) / step) + 1)]

#     def __repr__(self):
#         return f"Var_t({self.name},{self.sweep})"

@dataclass
class Var_t:
    name: str 
    sweep: object

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise TypeError("name must be a string")
        if isinstance(self.sweep, list):
            pass
        elif isinstance(self.sweep, int) or isinstance(self.sweep, float):
            self.sweep = [self.sweep]
        elif isinstance(self.sweep, tuple):
            if len(self.sweep) == 3:
                start, end, step = tuple(self.sweep)
                self.sweep = [round(start + i * step, 10) for i in range(int((end - start) / step) + 1)]
            else:
                raise ValueError("If sweep is a tuple, it must be of the form (start, end, step)")
        else:
            raise TypeError("sweep must be a list, int, float, or a tuple of (start, end, step)")

@dataclass(frozen=True)
class Config:
    kv: tuple  # sorted (name, value) pairs

    def as_dict(self): return dict(self.kv)
    def uid(self):
        m = hashlib.md5(repr(self.kv).encode()); return m.hexdigest()[:8]
    

    

          
# class Jobs():
#     def __init__(self, var_type=None):
       
#         if var_type is None:
#             self.var_type = []

#     def add(self,var_type):
#         if isinstance(var_type, Var_t):
#             self.var_type.append(var_type)
#         else:
#             raise TypeError("var_type must be an instance of Var_t")
        
#     def generate_configs(self):
#         sweeps = [v.sweep for v in self.var_type]
#         return list(itertools.product(*sweeps))
    
#     def export_vartype(self):
#         return [v.name for v in self.var_type]
    

    # def __str__(self):
    #     configs = self.generate_configs()
    #     return "\n".join(str(c) for c in configs)
    




    # def write_scripts(self):
    #     names = self.jobs.export_vartype()
    #     for i, cfg in enumerate(self.jobs.generate_configs()):
    #         path = os.path.join(self.outdir, f"job_{i}.sh")
    #         args = " ".join(f"--{k} {v}" for k,v in zip(names, cfg))
    #         with open(path,"w") as f:
    #             f.write("#!/bin/bash\n")
    #             f.write(f"python run_cluster.py {args}\n")



# Example usage
# if __name__ == "__main__":
#     v1 = Var_t("ent_par",(3,10,1))
#     print(list[v1])
    # j = Jobs()
    # # j.add(Var_t([1, 2]))
    # # j.add(Var_t(["sym_in_out","sym_out_in"]))
    # # j.add(Var_t((10, 30, 10)))   # expands to [10, 20, 30]
    # # j.add(Var_t(5))              # single value

    # j.add(Var_t('ent_params',["random","symmetric"]))
    # j.add(Var_t('ent_struct',["sym_in_out","sym_out_in","forward","backward"]))
    # j.add(Var_t('lr',0.01))
    # j.add(Var_t('nr_ent',[4,5,6,7]))
    # j.add(Var_t('layer',(10, 30, 10)))   # expands to [10, 20, 30]
    
    # #mj.write_json()
    
    # print("Var types:")
    # print(j.export_vartype())