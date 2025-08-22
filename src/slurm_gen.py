from jobs import Var_t, Jobs
from job_aggregator import JobAggregator
import os 

current_dir = os.getcwd()
job_name = "test_job"
time = "00:10:00"
mem = "4GB"
n_jobs = 10
concurrency = 5



j= Jobs()
j.add(Var_t('ent_params',["random","symmetric"]))
j.add(Var_t('ent_struct',["sym_in_out","sym_out_in","forward","backward"]))
j.add(Var_t('lr',[0.01,0.05]))
j.add(Var_t('layer',(10, 30, 10)))   # expands to [10, 20, 30]

lis = j.export_vartype()

agg = JobAggregator(j,outdir='config')

print(agg)

agg.write_master_json()



print(f'current directory --> {current_dir}')


cluster_settings = [

     "#!/bin/bash\n",
        f"#SBATCH --job-name={job_name}\n",
        # f"#SBATCH --output={os.path.join('./out', '%x-%a.out')}\n",
        # f"#SBATCH --error={os.path.join('./err', '%x-%a.err')}\n",
        f"#SBATCH --time={time}\n",
        f"#SBATCH --mem={mem}\n",
        f"#SBATCH --partition=tc\n",
        f"#SBATCH --mail-type=None\n",
        f"#SBATCH --array=0-{n_jobs-1}%{concurrency}\n",


] 

var_assignments = [f'{config}={{${config}}}\n' for config in lis]

echo_commands = [f'echo ${config}\n' for config in lis]


print(var_assignments)

with open(f'../{job_name}.sh','w') as f:
    f.writelines(cluster_settings + var_assignments + echo_commands )

