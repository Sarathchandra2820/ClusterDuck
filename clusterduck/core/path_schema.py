from dataclasses import dataclass
import os

@dataclass 
class PathSchema:
    
    variable = list = None
    struct : str = None  #Specify the folder structure that one wishes the outputs to be stored in 
    output_key : str = None # Optional : If the scratch is the temp then specify with files to be stored in output dir 
    scratch_key : str = None #Specify which files to be stored in scratch directory ; For ex plams_workdir* ... 

    def struct_path(self,settings=None) -> str: 

        if self.struct is None: 
            #struct_lis = settings.variable.export_names() 
            struct_lis = [v.name for v in settings.variable.var if len(v.sweep) > 1]
        elif "->" in self.struct:
            struct_lis = self.struct.split("->")

        else: 
            raise ValueError('Invalid input (must be var1->var2->var3 ..)') 

        struct_path = os.path.join(*struct_lis) 

        return struct_path