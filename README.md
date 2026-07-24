# ClusterDuck 🦆

**Turn one experiment into a scalable SLURM sweep.** ClusterDuck converts Python
parameter definitions into a single, portable SLURM array script—so every task
runs exactly one configuration and writes to an organized output directory.

No handwritten job loops. No manually tracked task IDs. Define the sweep,
generate the script, and submit it.

## Why ClusterDuck?

| | |
| --- | --- |
| **One script, every combination** | Generate an entire Cartesian sweep as one SLURM array. |
| **Scale without the overhead** | Decode task parameters with constant-memory mixed-radix indexing. |
| **Control concurrency** | Use native SLURM array limits to respect cluster capacity. |
| **Fit your workflow** | Supply values as command-line options, environment variables, or rendered templates. |
| **Keep results tidy** | Give every task its own scratch and deterministic output directory. |
| **Submit with confidence** | Generated commands use safe shell quoting and validated paths. |

## Get started

```bash
git clone https://github.com/Sarathchandra2820/ClusterDuck.git
cd ClusterDuck
python3 -m pip install -e .
```

ClusterDuck requires Python 3.9 or newer. Generated template jobs also require
`python3` on the compute node for the lightweight template renderer.

## Your first sweep

Create `generate_job.py`. This 108-task sweep combines three molecules, twelve
distances, and three methods while running no more than 16 tasks at once:

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

Generate and submit:

```bash
python3 generate_job.py
sbatch gw_sweep.slurm
```

ClusterDuck generates this array directive:

```bash
#SBATCH --array=0-107%16
```

## Pass values to your workload

Each array task runs your workload once—without sweep loops in the workload
itself. By default, sweep parameters become command-line arguments:

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

### Read arguments with less boilerplate

For lightweight workloads, `ArgParses` creates command-line options on demand.
Attribute names become kebab-case options: `inputs.learning_rate()` reads
`--learning-rate`. It ignores options that your workload has not requested, so
you can read only the values it needs.

```python
# run_experiment.py
from clusterduck.jobs import args

inputs = args.ArgParses()
molecule = inputs.molecule(required=True)
distance = inputs.distance(type=float, required=True)
method = inputs.method(default="G0W0", choices=["G0W0", "evGW", "TDDFT"])

print(inputs.list_arguments())
# ['molecule', 'distance', 'method']
```

`ArgParses` accepts these optional keyword arguments for every value:

| Argument | Purpose |
| --- | --- |
| `default` | Value to use when the option is absent; when `type` is omitted, its Python type is used as the converter. |
| `type` | Converter for the supplied value, such as `int`, `float`, or `pathlib.Path`. |
| `required` | Require the option to be present. |
| `choices` | Restrict accepted values to a collection. |
| `nargs` | Accept one or more values using `argparse`'s `nargs` rules. |

For example, `inputs.basis(default="aug-cc-pvdz")` reads `--basis` and returns
`"aug-cc-pvdz"` when it is not supplied.

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

## Stage files and collect outputs

`job.stage()` copies files or directories into the unique task scratch directory.
Relative output templates are resolved from the submission directory. Parameters
used as path components cannot contain `/`, `.` or `..`.

If the workload accepts an output directory, `job.output()` passes it through
`--output-dir` by default. Use `argument=None` for programs that write into the
current directory, then collect artifacts with basename glob patterns:

```python
job.output("outputs/{method}/{distance}", argument=None)
job.collect("result*", "energies*")
```

Set `job.keep_failed_scratch = True` to retain scratch files after a failed task.

## Verify your installation

The test suite uses only the Python standard library and does not require SLURM:

```bash
python3 -m unittest discover -s tests -v
```

It validates mixed-radix coverage, Bash syntax, quoting, template rendering, and
end-to-end local execution of generated array tasks.

## What ClusterDuck does—and does not do

ClusterDuck generates scripts; it does not submit or monitor jobs. Keeping
submission explicit (`sbatch generated.slurm`) makes generation testable and avoids
surprising cluster-side effects.
