#!/bin/bash
#SBATCH --job-name=test_job
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
L0=${{#molecule_vals[@]}}   # molecule
L1=${{#distance_vals[@]}}   # distance
L2=${{#method_vals[@]}}   # method
L3=${{#basis_set_vals[@]}}   # basis_set
L4=${{#charge_vals[@]}}   # charge
L5=${{#spin_multiplicity_vals[@]}}   # spin_multiplicity
L6=${{#n_cas_electrons_vals[@]}}   # n_cas_electrons
L7=${{#n_cas_orbitals_vals[@]}}   # n_cas_orbitals

R0=$(( L1 * L2 * L3 * L4 * L5 * L6 * L7 ))  # product of later lengths
R1=$(( L2 * L3 * L4 * L5 * L6 * L7 ))  # product of later lengths
R2=$(( L3 * L4 * L5 * L6 * L7 ))  # product of later lengths
R3=$(( L4 * L5 * L6 * L7 ))  # product of later lengths
R4=$(( L5 * L6 * L7 ))  # product of later lengths
R5=$(( L6 * L7 ))  # product of later lengths
R6=$(( L7 ))  # product of later lengths
R7=1

k=${SLURM_ARRAY_TASK_ID}

i0=$(( (k / R0) % L0 ))
i1=$(( (k / R1) % L1 ))
i2=$(( (k / R2) % L2 ))
i3=$(( (k / R3) % L3 ))
i4=$(( (k / R4) % L4 ))
i5=$(( (k / R5) % L5 ))
i6=$(( (k / R6) % L6 ))
i7=$(( (k / R7) % L7 ))

molecule="${molecule_vals[$i0]}"
distance="${distance_vals[$i1]}"
method="${method_vals[$i2]}"
basis_set="${basis_set_vals[$i3]}"
charge="${charge_vals[$i4]}"
spin_multiplicity="${spin_multiplicity_vals[$i5]}"
n_cas_electrons="${n_cas_electrons_vals[$i6]}"
n_cas_orbitals="${n_cas_orbitals_vals[$i7]}"