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