from jobs import Var_t, Jobs
from job_aggregator import JobAggregator
import os 

# current_dir = os.getcwd()
# job_name = "test_job"
# time = "00:10:00"
# mem = "4GB"
# n_jobs = 10
# concurrency = 5



# j= Jobs()
# j.add(Var_t('ent_params',["random","symmetric"]))
# j.add(Var_t('ent_struct',["sym_in_out","sym_out_in","forward","backward"]))
# j.add(Var_t('lr',[0.01,0.05]))
# j.add(Var_t('layer',(10, 30, 10)))   # expands to [10, 20, 30]

# lis = j.export_vartype()

# agg = JobAggregator(j,outdir='config')

# print(agg)

# agg.write_master_json()



# print(f'current directory --> {current_dir}')


# cluster_settings = [

#      "#!/bin/bash\n",
#         f"#SBATCH --job-name={job_name}\n",
#         # f"#SBATCH --output={os.path.join('./out', '%x-%a.out')}\n",
#         # f"#SBATCH --error={os.path.join('./err', '%x-%a.err')}\n",
#         f"#SBATCH --time={time}\n",
#         f"#SBATCH --mem={mem}\n",
#         f"#SBATCH --partition=tc\n",
#         f"#SBATCH --mail-type=None\n",
#         f"#SBATCH --array=0-{n_jobs-1}%{concurrency}\n",


# ] 

# vectorized_params = []

# var_assignments = [f'{config}={{${config}}}\n' for config in lis]

# echo_commands = [f'echo ${config}\n' for config in lis]


# print(var_assignments)

# with open(f'../{job_name}.sh','w') as f:
#     f.writelines(cluster_settings + var_assignments + echo_commands )

import os
import itertools

def sanitize_for_path(s):
    # light sanitization to avoid spaces/slashes in folder names
    s = str(s)
    s = s.replace("/", "_").replace(" ", "_")
    return s

def generate_slurm_from_jobs(
    jobs,
    jobname="fragvqe",
    partition="tc",
    time="8-0:00:00",
    py_module_line="module load python || true",
    venv_line="",  # e.g., 'source ~/envs/frag/bin/activate'
    runner_cmd="python run_cluster.py"
):
    names = jobs.export_vartype()
    sweeps = [v.sweep for v in jobs.var_type]
    lengths = [len(s) for s in sweeps]

    # total jobs
    total = 1
    for L in lengths:
        total *= L

    # --- header
    lines = []
    lines += [
        "#!/bin/bash",
        f"#SBATCH --job-name={jobname}",
        f"#SBATCH --partition={partition}",
        f"#SBATCH --time={time}",
        f"#SBATCH --output=logs/%x-%a.out",
        f"#SBATCH --error=logs/%x-%a.err",
        f"#SBATCH --array=0-{total-1}",
        "",
        "set -euo pipefail",
        py_module_line,
    ]
    if venv_line:
        lines.append(venv_line)
    lines.append("")

    # --- index decomposition
    lines += [
        "# Vectorisation: mixed-radix index decomposition",
        "tid=${SLURM_ARRAY_TASK_ID}",
    ]
    stride = 1
    for name, L in zip(names, lengths):
        lines.append(f"{name}_idx=$(( (tid / {stride}) % {L} ))")
        stride *= L
    lines.append("")

    # --- embed arrays of values for each param
    lines.append("# Lookup arrays for parameter values")
    for name, sweep in zip(names, sweeps):
        # stringify & sanitize for bash array
        vals = " ".join(sanitize_for_path(x) for x in sweep)
        lines.append(f"{name}_arr=({vals})")
        lines.append(f'{name}=${{{name}_arr[${name}_idx]}}')
    lines.append("")

    # --- build CLI args generically
    arg_join = " ".join(f"--{n} ${{{n}}}" for n in names)
    lines += [
        "# Build CLI args (all params)",
        f'ARGS="{arg_join}"',
        ""
    ]

    # --- output structure (deterministic order = sorted names or original order)
    # Use original order for readability; choose sorted(names) if you prefer stability across code edits.
    out_parts = "/".join("${" + n + "}" for n in names if len(jobs.var_type[names.index(n)].sweep) > 1)
    lines += [
        "# Output path (nested by parameter values)",
        f'outdir="outputs/{out_parts}"',
        "mkdir -p \"$outdir\"",
        ""
    ]

    # --- work in node-local scratch
    lines += [
        "# Use node-local scratch for fast I/O; move results at end",
        'workdir="${TMPDIR:-/tmp}/job_${SLURM_ARRAY_TASK_ID}"',
        "mkdir -p \"$workdir\"",
        "trap 'rm -rf \"$workdir\"' EXIT",
        "cd \"$workdir\"",
        "",
        "# Echo for debugging",
        'echo "TID=$tid"',
        "echo ARGS=\"$ARGS\"",
        'echo "OUTDIR=$outdir"',
        ""
    ]

    # --- run and finalize
    lines += [
        f"{runner_cmd} $ARGS --outdir \"$outdir\" > \"$workdir/out.log\" 2>&1 || {{",
        '  echo "Job failed: $tid" >&2',
        "  # Optionally keep scratch artifacts or move for debugging:",
        "  # mv \"$workdir\" \"${outdir}/workdir_failed_${tid}\"",
        "  exit 1",
        "}",
        "mv \"$workdir/out.log\" \"$outdir/\"",
        'echo "Done $tid → $outdir"',
        ""
    ]

    return "\n".join(lines)


j = Jobs()
j.add(Var_t("ent_params", ["random","symmetric"]))
j.add(Var_t("ent_struct", ["sym_in_out","sym_out_in","forward","backward"]))
j.add(Var_t("lr", [0.01, 0.05]))
j.add(Var_t("layer", (10)))


slurm = generate_slurm_from_jobs(j, jobname="fragvqe", partition="tc", time="0-4:00:00")
with open("run.sh","w") as f:
    f.write(slurm)

