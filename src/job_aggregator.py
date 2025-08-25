import os,json
from var_t import Var_t, Jobs

class JobAggregator:
    """Aggregates jobs and writes them to JSON files."""
    def __init__(self, jobs, outdir=None):
        self.jobs = jobs
        self.names = jobs.export_vartype()
        if outdir is None:
            outdir = ""
        else:
            self.outdir = outdir
            os.makedirs(outdir, exist_ok=True)

        # Precompute configs with IDs + outdir
        self.configs = []
        for i, cfg in enumerate(jobs.generate_configs()):
            params = dict(zip(self.names, cfg))
            # outdir_nested = os.path.join("outputs", *map(str, cfg))
            self.configs.append({
                "job_id": i,
                "params": params,
            })

    def __repr__(self):
        return "\n".join(f"{i}: {c}" for i, c in enumerate(self.configs))

    def write_master_json(self, filename="all_jobs.json"):
        """Write a single JSON containing all job configs."""
        path = os.path.join(self.outdir, filename)
        with open(path, "w") as f:
            json.dump(self.configs, f, indent=2)
        print(f"✅ Wrote {len(self.configs)} jobs to {path}")

    

# Example usage
if __name__ == "__main__":
    j = Jobs()
    # j.add(Var_t([1, 2]))
    # j.add(Var_t(["sym_in_out","sym_out_in"]))
    # j.add(Var_t((10, 30, 10)))   # expands to [10, 20, 30]
    # j.add(Var_t(5))              # single value

    j.add(Var_t('ent_params',["random","symmetric"]))
    j.add(Var_t('ent_struct',["sym_in_out","sym_out_in","forward","backward"]))
    j.add(Var_t('lr',[0.01,0.05]))
    j.add(Var_t('layer',(10, 30, 10)))   # expands to [10, 20, 30]
    print("All configs:")

    agg = JobAggregator(j)
    print("generating json file with all the configs")
    # agg.write_master_json()
    print(agg)
   
  
    print("Var types:")
    print(j.export_vartype())
