#!/bin/bash
#SBATCH --job-name=test_job
#SBATCH --time=00:10:00
#SBATCH --mem=4GB
#SBATCH --partition=tc
#SBATCH --mail-type=None
#SBATCH --array=0-9%5
ent_params={$ent_params}
ent_struct={$ent_struct}
lr={$lr}
layer={$layer}
echo $ent_params
echo $ent_struct
echo $lr
echo $layer
