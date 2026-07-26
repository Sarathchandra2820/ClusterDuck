# ClusterDuck

ClusterDuck is a small Python library that turns parameter sweeps into a single
vectorized SLURM array script. Each array task decodes one Cartesian combination,
runs one workload, and writes to its own output directory.

## Why

- One generated Bash script for an entire sweep.
- Constant-memory mixed-radix task decoding.
- Native SLURM array concurrency limits.
- Command-line, environment-variable, and text-template inputs.
- Per-task scratch directories with deterministic cleanup.
- Safe shell quoting and validated output paths.

## Install

```bash
git clone https://github.com/Sarathchandra2820/ClusterDuck.git
cd ClusterDuck
python3 -m pip install -e .
```

ClusterDuck requires Python 3.9 or newer. Generated template jobs also require
`python3` on the compute node for the lightweight template renderer.

## Generate a sweep

Create `generate_job.py`:

```python
from clusterduck import Job

job = Job(
    name="gw_sweep",
    command=["python3", "run_experiment.py"],
    concurrency=16,
)

job.sweep("molecule", ["ethylene", "benzene", "pyrene"])
job.sweep("distance", range(3, 15))
job.sweep("method", ["G0W0", "evGW", "TDDFT"])

job.resources(
    time="02:00:00",
    memory="8G",
    partition="tc",
    cpus_per_task=4,
)

job.stage("run_experiment.py")
job.output("outputs/{molecule}/{distance}/{method}")
job.write("gw_sweep.slurm")

print(job.task_count)  # 108
```

Generate and submit it:

```bash
python3 generate_job.py
sbatch gw_sweep.slurm
```

The generated array directive is:

```bash
#SBATCH --array=0-107%16
```

## Workload input scheme

The workload runs exactly one configuration. It does not contain sweep loops.
By default, sweep parameters become command-line arguments:

```python
# run_experiment.py
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--molecule", required=True)
parser.add_argument("--distance", required=True, type=float)
parser.add_argument("--method", required=True)
parser.add_argument("--output-dir", required=True, type=Path)
args = parser.parse_args()

args.output_dir.mkdir(parents=True, exist_ok=True)
(args.output_dir / "result.json").write_text(
    json.dumps(vars(args), default=str, indent=2),
    encoding="utf-8",
)
```

ClusterDuck invokes it as if you had run:

```bash
python3 run_experiment.py \
  --molecule benzene \
  --distance 4 \
  --method G0W0 \
  --output-dir /path/to/outputs/benzene/4/G0W0
```

### Explicit command-line options

```python
from clusterduck import Argument

job.sweep("learning_rate", [0.01, 0.05], bind=Argument("--lr"))
```

### Environment variables

```python
from clusterduck import Environment

job.sweep("threads", [2, 4, 8], bind=Environment("OMP_NUM_THREADS"))
```

The workload reads `OMP_NUM_THREADS` from its environment.

### Input templates

For programs that consume a text input file:

```text
# calculation.in.template
method={{ method }}
distance={{ distance }}
```

```python
from clusterduck import Job, TemplateVariable

job = Job("simulation", ["simulator"], concurrency=8)
job.sweep("method", ["G0W0", "evGW"], TemplateVariable())
job.sweep("distance", [3.0, 3.5, 4.0], TemplateVariable())
job.template("calculation.in.template", "calculation.in")
job.use_stdin("calculation.in")
job.output("outputs/{method}/{distance}", argument=None)
job.collect("result*")
job.write("simulation.slurm")
```

Only explicit `{{ name }}` placeholders are replaced.

## Staging and outputs

`job.stage()` copies files or directories into the unique task scratch directory.
Relative output templates are resolved from the submission directory. Parameters
used as path components cannot contain `/`, `.` or `..`.

Commands run from the task scratch root by default. To run from a staged
subdirectory, set a scratch-relative working directory:

```python
job.stage("calculation")
job.working_directory("calculation")
```

This runs the configured command from `$workdir/calculation`. Absolute paths and
paths containing `..` are rejected so the working directory remains inside the
task scratch area.

If the workload accepts an output directory, `job.output()` passes it through
`--output-dir` by default. Use `argument=None` for programs that write into the
current directory, then collect artifacts with basename glob patterns:

```python
job.output("outputs/{method}/{distance}", argument=None)
job.collect("result*", "energies*")
```

Set `job.keep_failed_scratch = True` to retain scratch files after a failed task.

## Test

The test suite uses only the Python standard library and does not require SLURM:

```bash
python3 -m unittest discover -s tests -v
```

It validates mixed-radix coverage, Bash syntax, quoting, template rendering, and
end-to-end local execution of generated array tasks.

## Scope

ClusterDuck generates scripts; it does not submit or monitor jobs. Keeping
submission explicit (`sbatch generated.slurm`) makes generation testable and avoids
surprising cluster-side effects.
