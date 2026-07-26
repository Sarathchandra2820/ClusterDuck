#!/usr/bin/env bash
#SBATCH --job-name=Water_cluster_run
#SBATCH --array=0-39
#SBATCH --time=2:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB
#SBATCH --partition=tc

set -euo pipefail

module load miniconda/23
module load shared/2024
module load imkl/2024.2.0
export MKL_THREADING_LAYER=GNU
export MKL_INTERFACE_LAYER=LP64
export PYTHONPATH=/home/username/clusterduck

declare -a N_values=(2 4 5 8 10)
declare -a basis_values=(aug-cc-pvdz aug-cc-pvtz)
declare -a omp_cores_values=(2 4 8 16)

: "${SLURM_ARRAY_TASK_ID:?SLURM_ARRAY_TASK_ID is required}"
[[ "$SLURM_ARRAY_TASK_ID" =~ ^[0-9]+$ ]] || { echo "Invalid SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID" >&2; exit 2; }
clusterduck_index=$SLURM_ARRAY_TASK_ID
(( clusterduck_index < 40 )) || { echo "SLURM_ARRAY_TASK_ID is outside the configured sweep" >&2; exit 2; }
omp_cores_index=$((clusterduck_index % ${#omp_cores_values[@]}))
clusterduck_index=$((clusterduck_index / ${#omp_cores_values[@]}))
omp_cores="${omp_cores_values[$omp_cores_index]}"
basis_index=$((clusterduck_index % ${#basis_values[@]}))
clusterduck_index=$((clusterduck_index / ${#basis_values[@]}))
basis="${basis_values[$basis_index]}"
N_index=$((clusterduck_index % ${#N_values[@]}))
clusterduck_index=$((clusterduck_index / ${#N_values[@]}))
N="${N_values[$N_index]}"

submit_dir="$PWD"
scratch_root="${TMPDIR:-/tmp}"
workdir="${scratch_root}/clusterduck_${SLURM_JOB_ID:-local}_${SLURM_ARRAY_TASK_ID}_$$"
mkdir -p "$workdir"
clusterduck_cleanup() {
  status=$?
  trap - EXIT
  rm -rf -- "$workdir"
  exit "$status"
}
trap clusterduck_cleanup EXIT

clusterduck_path_value="${omp_cores}"
if [[ "$clusterduck_path_value" == */* || "$clusterduck_path_value" == "." || "$clusterduck_path_value" == ".." ]]; then
  echo "Unsafe value for output path parameter omp_cores: $clusterduck_path_value" >&2
  exit 2
fi
clusterduck_path_value="${basis}"
if [[ "$clusterduck_path_value" == */* || "$clusterduck_path_value" == "." || "$clusterduck_path_value" == ".." ]]; then
  echo "Unsafe value for output path parameter basis: $clusterduck_path_value" >&2
  exit 2
fi
clusterduck_path_value="${N}"
if [[ "$clusterduck_path_value" == */* || "$clusterduck_path_value" == "." || "$clusterduck_path_value" == ".." ]]; then
  echo "Unsafe value for output path parameter N: $clusterduck_path_value" >&2
  exit 2
fi
output_dir="water_cluster_run/${omp_cores}/${basis}/${N}"
if [[ "$output_dir" != /* ]]; then output_dir="${submit_dir}/${output_dir}"; fi
mkdir -p "$output_dir"
cd "$workdir"

command_workdir="$workdir"/examples
[[ -d "$command_workdir" ]] || { echo "Missing working directory: $command_workdir" >&2; exit 2; }
cd "$command_workdir"

export OMP_NUM_THREADS="${omp_cores}"
clusterduck_command=(python water_cluster.py --N "${N}" --basis "${basis}" --output-dir "$output_dir")
echo "ClusterDuck task ${SLURM_ARRAY_TASK_ID}: ${clusterduck_command[*]}"
"${clusterduck_command[@]}"
echo "ClusterDuck task ${SLURM_ARRAY_TASK_ID} completed"
