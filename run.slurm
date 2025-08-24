#!/bin/bash
#SBATCH --job-name=fragvqe
#SBATCH --partition=tc
#SBATCH --time=0-4:00:00
#SBATCH --output=logs/%x-%a.out
#SBATCH --error=logs/%x-%a.err
#SBATCH --array=0-15

set -euo pipefail
module load python || true

# Vectorisation: mixed-radix index decomposition
tid=${SLURM_ARRAY_TASK_ID}
ent_params_idx=$(( (tid / 1) % 2 ))
ent_struct_idx=$(( (tid / 2) % 4 ))
lr_idx=$(( (tid / 8) % 2 ))
layer_idx=$(( (tid / 16) % 1 ))

# Lookup arrays for parameter values
ent_params_arr=(random symmetric)
ent_params=${ent_params_arr[$ent_params_idx]}
ent_struct_arr=(sym_in_out sym_out_in forward backward)
ent_struct=${ent_struct_arr[$ent_struct_idx]}
lr_arr=(0.01 0.05)
lr=${lr_arr[$lr_idx]}
layer_arr=(10)
layer=${layer_arr[$layer_idx]}

# Build CLI args (all params)
ARGS="--ent_params ${ent_params} --ent_struct ${ent_struct} --lr ${lr} --layer ${layer}"

# Output path (nested by parameter values)
outdir="outputs/${ent_params}/${ent_struct}/${lr}/${layer}"
mkdir -p "$outdir"

# Use node-local scratch for fast I/O; move results at end
workdir="${TMPDIR:-/tmp}/job_${SLURM_ARRAY_TASK_ID}"
mkdir -p "$workdir"
trap 'rm -rf "$workdir"' EXIT
cd "$workdir"

# Echo for debugging
echo "TID=$tid"
echo ARGS="$ARGS"
echo "OUTDIR=$outdir"

python run_cluster.py $ARGS --outdir "$outdir" > "$workdir/out.log" 2>&1 || {
  echo "Job failed: $tid" >&2
  # Optionally keep scratch artifacts or move for debugging:
  # mv "$workdir" "${outdir}/workdir_failed_${tid}"
  exit 1
}
mv "$workdir/out.log" "$outdir/"
echo "Done $tid → $outdir"
