This is a lean code to generate slurm job script given some input variation.
Given some inputs [v1,v2,v3,...] and each input has a variation [{L1},{L2},{L3},...], the code generates job objects that will be vectorised using the slurm arrays and radix vectorisation to be performed on different compute nodes. 
This tool offers create customisibility interms of setting folder structure and control job submission (including batching, applying filters for which jobs to be run in parallel)
