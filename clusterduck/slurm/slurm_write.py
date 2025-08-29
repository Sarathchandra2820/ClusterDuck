from clusterduck.jobs.jobs import Job
from clusterduck.utils.radix_helper import generate_radix_block


class SlurmWrite:

    jobs: Job

    def header_write(self) -> str:
        """Generic SLURM header builder from job settings."""
        opts = self.jobs.settings.sbatch_opts
        header = ["#!/bin/bash"]

        for key, val in opts.items():
            header.append(f"#SBATCH --{key}={val}")

        # Load modules or other cluster-specific defaults
        for elem in self.jobs.settings.module_load:
            header.append(f"module load {elem}")
        return "\n".join(header)
   

    def radix_logic(self):
        schema = self.jobs.path_schema.struct_path(self.jobs.settings)
        schema = schema.split('/')
        lines = generate_radix_block(schema)
     

        return lines 
    
    # def scratch_copying(self.jobs)

    #     return scratch_copying 
    
    # def output_logic_write(self.jobs)

    #     retun blah blah blah 
    
    def slurmscript_generate(self):

        header = self.header_write()

        #copy_file_logic = scratch_copying(self.jobs)

        # if self.jobs.set_paths.env_path is not None:
        #     activate env 

        radix = self.radix_logic()
        
        script = [header, radix]


        return '\n'.join(script)




        

        
