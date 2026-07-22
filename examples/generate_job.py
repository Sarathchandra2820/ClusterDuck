from clusterduck import Job


job = Job(
    name="gw_sweep",
    command=["python3", "run_experiment.py"],
    concurrency=16,
)
job.sweep("molecule", ["ethylene", "benzene", "pyrene"])
job.sweep("distance", range(3, 15))
job.sweep("method", ["G0W0", "evGW", "TDDFT"])
job.resources(time="02:00:00", memory="8G", partition="tc", cpus_per_task=4)
job.stage("run_experiment.py")
job.output("outputs/{molecule}/{distance}/{method}")
job.write("gw_sweep.slurm")

print(f"Generated gw_sweep.slurm with {job.task_count} tasks")
