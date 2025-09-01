from clusterduck.jobs.jobs import Job
from clusterduck.slurm.slurm_write import SlurmWrite
import os



j1 = Job()

# Add SLURM options
j1.settings.concurrency=8
j1.settings.job_name="test_job"
j1.settings.add("time", "02:00:00")           # --time=2 hours
j1.settings.add("mem", "8GB")                 # --mem=8GB
j1.settings.add("partition", "tc")            # --partition=tc
j1.settings.add("array", "0-9%2")             # --array=0-9%2
j1.settings.add("mail-type", "END,FAIL")      # --mail-type=END,FAIL
j1.settings.add("mail-user", "you@uni.nl")    # --mail-user=...
j1.settings.add("cpus-per-task", "4")         # --cpus-per-task=4
j1.settings.add("output", "./out/%x-%A_%a.out")  # --output=...
j1.settings.add("error", "./err/%x-%A_%a.err")   # --error=...

j1.settings.module_load = ["shared", "2024", "slurm"]
j1.settings.add_export('AMSHOME','/scistor/tc/huw587/amshome')
j1.settings.add_export('AMSBIN','/scistor/tc/huw587/amshome')
j1.settings.add_export('AMSBIN','/scistor/tc/huw587/amshome')

j1.settings.add_vars('molecule',["ethylene","benzene","pyrene"])
j1.settings.add_vars('distance',(3,14,1))
j1.settings.add_vars('method',["G0W0","evGW","TDDFT"])
# j1.settings.add_vars("basis_set", ["STO-3G", "cc-pVDZ", "cc-pVTZ"])
# j1.settings.add_vars("charge", [0, 1, -1])
# j1.settings.add_vars("spin_multiplicity", [1, 3])
# j1.settings.add_vars("n_cas_electrons", (2, 10, 2))   # expands 2,4,6,8,10
# j1.settings.add_vars("n_cas_orbitals", (4, 12, 2))    # expands 4,6,8,10,12


j1.set_paths.input_script = os.path.join(os.getcwd(),'test_job.sh')
j1.set_paths.scratch_dir = "$TMPDIR" #os.path.join(os.getcwd(),'scratch')
j1.set_paths.dependancies = [os.path.join(os.getcwd(),'run.sh'), os.path.join(os.getcwd(),'run.slurm')]
j1.set_paths.output_dir = os.path.join(os.getcwd(),"outdir")
j1.path_schema.output_key = ['params*','energies*']



# for elems in j1.settings.variable.var:
#     print(f'declare {elems.name} , elems.sweep)                                 
# s = Settings()
# print(s)

# schema = j1.path_schema.struct_path(j1.settings)
# print(schema)
s = SlurmWrite()
s.jobs = j1
lines1 = s.slurmscript_generate()

with open('test_header.sh','w') as f:
    f.write(lines1)