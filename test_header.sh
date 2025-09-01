#!/bin/bash
#SBATCH --array=0-8%108
#SBATCH --time=02:00:00
#SBATCH --mem=8GB
#SBATCH --partition=tc
#SBATCH --array=0-9%2
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=you@uni.nl
#SBATCH --cpus-per-task=4
#SBATCH --output=./out/%x-%A_%a.out
#SBATCH --error=./err/%x-%A_%a.err
module load shared
module load 2024
module load slurm
export AMSHOME="/scistor/tc/huw587/amshome"
export AMSBIN="/scistor/tc/huw587/amshome"
declare -a molecule_vals=("ethylene" "benzene" "pyrene")
declare -a distance_vals=(3 4 5 6 7 8 9 10 11 12 13 14)
declare -a method_vals=("G0W0" "evGW" "TDDFT")
mkdir -p /Users/sarath/Documents/Research/other_projects/clusterduck/outdir
cp -rfv /Users/sarath/Documents/Research/other_projects/clusterduck/test_job.sh $TMPDIR
cp -rfv /Users/sarath/Documents/Research/other_projects/clusterduck/run.sh /Users/sarath/Documents/Research/other_projects/clusterduck/run.slurm $TMPDIR
cd $TMPDIR
L0=${#molecule_vals[@]}  # molecule
L1=${#distance_vals[@]}  # distance
L2=${#method_vals[@]}  # method

R0=$(( L1 * L2 ))  # product of later lengths
R1=$(( L2 ))  # product of later lengths
R2=1

k=${SLURM_ARRAY_TASK_ID}

i0=$(( (k / R0) % L0 ))
i1=$(( (k / R1) % L1 ))
i2=$(( (k / R2) % L2 ))

molecule="${molecule_vals[$i0]}"
distance="${distance_vals[$i1]}"
method="${method_vals[$i2]}"
cp -rfv params* /Users/sarath/Documents/Research/other_projects/clusterduck/outdir/molecule/distance/method 
cp -rfv energies* /Users/sarath/Documents/Research/other_projects/clusterduck/outdir/molecule/distance/method 