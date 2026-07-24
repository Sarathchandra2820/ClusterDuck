from clusterduck import * 


water_c_job = Job(name = "Water_cluster_run",
                  command = ['python', 'water_cluster.py'])

water_c_job.resources(time = "2:00:00",
                      nodes = 1,
                      ntasks = 1,
                      cpus_per_task = 1,
                      mem = "4GB",
                      partition = "tc")

water_c_job.modules("python/3.10.4", "mkl", "openmpi")

water_c_job.export(PYTHONPATH = "/home/username/clusterduck")

water_c_job.sweep("N", [2,4,5,8,10])
water_c_job.sweep("basis", ["aug-cc-pvdz", "aug-cc-pvtz"])
water_c_job.sweep("omp_cores", [2,4,8,16], Environment("OMP_NUM_THREADS"))

water_c_job.output_root("water_cluster_run", hierarchy = ["omp_cores", "basis", "N"])
print(water_c_job.output_template)
water_c_job.write("water_cluster_run.sbatch")