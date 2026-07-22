"""ClusterDuck: lightweight vectorized SLURM job generation."""

from clusterduck.core.bindings import Argument, Environment, TemplateVariable
from clusterduck.jobs.jobs import Job
from clusterduck.slurm.slurm_write import SlurmWrite

__version__ = "0.2.0"

__all__ = [
    "Argument",
    "Environment",
    "Job",
    "SlurmWrite",
    "TemplateVariable",
]
