from clusterduck.jobs.jobs import Job
from clusterduck.utils.radix_helper import generate_radix_block
import os

class SlurmWrite:

    jobs: Job

    def header_write(self) -> str:
        """Generic SLURM header builder from job settings."""
        opts = self.jobs.settings.sbatch_opts
        header = ["#!/bin/bash",
                  f"#SBATCH --array={0}-{self.jobs.settings.concurrency}%{len(self.jobs.settings.configs())}"]

        for key, val in opts.items():
            header.append(f"#SBATCH --{key}={val}")

        # Load modules or other cluster-specific defaults
        for elem in self.jobs.settings.module_load:
            header.append(f"module load {elem}")

        for key,val in self.jobs.settings.export_opts.items():
            header.append(f'export {key}="{val}"')

        return "\n".join(header)
    

    def write_slurm_vars(self):

        """
        Write bash array definitions from ClusterDuck's var_t objects.
        settings.variable is assumed to be a Sweep containing Var_t's.
        """
        lines=[]
        for var in self.jobs.settings.variable.var:  # or however you access them
            name = var.name
            sweep = var.sweep
            if all(isinstance(x, (int, float)) for x in sweep):
                sweep_str = " ".join(map(str, sweep))
            else:
                sweep_str = " ".join(f'"{x}"' for x in sweep)  # quote strings
            lines+=[f'declare -a {name}_vals=({sweep_str})']
        return "\n".join(lines)
        
   

    def radix_logic(self):
        schema = self.jobs.path_schema.struct_path(self.jobs.settings)
        schema = schema.split('/')
        lines = []
        lines.append(generate_radix_block(schema))
     

        return "\n".join(lines) 
    
    def scratch_copying(self):


        path_input = self.jobs.set_paths.input_script
        path_scratch = self.jobs.set_paths.scratch_dir

        path_dependancies = self.jobs.set_paths.dependancies  #files we want to copy to the scratch

        lines=[

            f'cp -rfv {path_input} {path_scratch}',
            f'cp -rfv {" ".join(path_dependancies)} {path_scratch}'
        
        ]



        return '\n'.join(lines)
        
    def output_logic_write(self):
        line=[]
        if self.jobs.set_paths.scratch_dir=="$TMPDIR":
            store_scratch = False
        else:
            store_scratch = True
        output_path = os.path.join(self.jobs.set_paths.output_dir,self.jobs.path_schema.struct_path(self.jobs.settings))
        if store_scratch:
            scratch_path = os.path.join(self.jobs.set_paths.scratch_dir,self.jobs.path_schema.struct_path(self.jobs.settings))
        else:
            scratch_path = None
        for elems in self.jobs.path_schema.output_key:
            line+=[f'cp -rfv {elems} {output_path} ']
            if store_scratch:
                line+=[f'cp -rfv {elems} {scratch_path} ']
        return "\n".join(line)

        
    
    def slurmscript_generate(self):
        script = []

        header = self.header_write()

        script.append(header)
        

        variable_dec = self.write_slurm_vars()

        script.append(variable_dec)

        if self.jobs.set_paths.scratch_dir!="$TMPDIR":
            script.append(f'mkdir -p {self.jobs.set_paths.scratch_dir}')

        script.append(f'mkdir -p {self.jobs.set_paths.output_dir}')


        scratch_copying = self.scratch_copying()

        

        script.append(scratch_copying)

       
        script.append(f'cd {self.jobs.set_paths.scratch_dir}')

  


        #copy_file_logic = scratch_copying(self.jobs)

        # if self.jobs.set_paths.env_path is not None:
        #     activate env 

        radix = self.radix_logic()

        script.append(radix)

        output_logic = self.output_logic_write()

        script.append(output_logic)
        
        # script = [header, variable_dec, scratch_copying, radix, output_logic]


        return "\n".join(script)




        

        
