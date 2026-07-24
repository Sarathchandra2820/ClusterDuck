from __future__ import annotations

from pathlib import Path
import re
import shlex
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from clusterduck.core.bindings import (
    Argument,
    InputBinding,
    TemplateSpec,
    TemplateVariable,
)
from clusterduck.core.path_schema import PathSchema
from clusterduck.core.set_paths import Set_paths
from clusterduck.core.settings import Settings


Command = Union[str, Sequence[str]]


class Job:
    """Declarative specification for one vectorized SLURM job array."""

    def __init__(
        self,
        name: Optional[str] = None,
        command: Optional[Command] = None,
        concurrency: Optional[int] = None,
        settings: Optional[Settings] = None,
        set_paths: Optional[Set_paths] = None,
        path_schema: Optional[PathSchema] = None,
    ) -> None:
        self.settings = settings or Settings()
        self.set_paths = set_paths or Set_paths()
        self.path_schema = path_schema or PathSchema()
        self.bindings: Dict[str, InputBinding] = {}
        self.command: List[str] = []
        self.output_template: Optional[str] = None
        self.output_argument: Optional[str] = "--output-dir"
        self.collect_patterns: List[str] = []
        self.templates: List[TemplateSpec] = []
        self.stdin: Optional[str] = None
        self.keep_failed_scratch = False

        if name is not None:
            self.settings.job_name = name
        if concurrency is not None:
            self.settings.concurrency = concurrency
        if command is not None:
            self.set_command(command)

    def set_command(self, command: Command) -> "Job":
        if isinstance(command, str):
            command = shlex.split(command)
        self.command = [str(part) for part in command]
        if not self.command:
            raise ValueError("command cannot be empty")
        return self

    def sweep(
        self,
        name: str,
        values: Any,
        bind: Optional[InputBinding] = None,
    ) -> "Job":
        self.settings.add_vars(name, values)
        self.bindings[name] = bind or Argument()
        return self

    add_param = sweep

    def resources(self, **options: Any) -> "Job":
        aliases = {
            "memory": "mem",
            "cpus_per_task": "cpus-per-task",
            "mail_type": "mail-type",
            "mail_user": "mail-user",
        }
        for key, value in options.items():
            self.settings.add(aliases.get(key, key), value)
        return self

    def modules(self, *names: str) -> "Job":
        self.settings.module_load.extend(names)
        return self

    def export(self, **variables: Any) -> "Job":
        for key, value in variables.items():
            self.settings.add_export(key, value)
        return self

    def stage(self, *paths: Union[str, Path]) -> "Job":
        for path in paths:
            text = str(path)
            if text not in self.set_paths.dependencies:
                self.set_paths.dependencies.append(text)
        return self

    def output(
        self,
        template: str,
        argument: Optional[str] = "--output-dir",
    ) -> "Job":
        self.output_template = str(template)
        self.output_argument = argument
        return self

    def output_root(
        self,
        path: str,
        *,
        hierarchy: Optional[Sequence[str]] = None,
        argument: Optional[str] = "--output-dir",
    ) -> "Job":
        if hierarchy is None:
            hierarchy = [
                variable.name
                for variable in self.settings.variable.var
                if len(variable.sweep) > 1
            ]

        unknown = set(hierarchy) - set(self.settings.variable.export_names())
        if unknown:
            raise ValueError(
                f"unknown output hierarchy variables: {', '.join(sorted(unknown))}"
            )

        suffix = "/".join(f"{{{name}}}" for name in hierarchy)
        self.output_template = str(Path(path) / suffix) if suffix else str(path)
        self.output_argument = argument
        return self

    def collect(self, *patterns: str) -> "Job":
        self.collect_patterns.extend(patterns)
        return self

    def template(self, source: str, destination: str) -> "Job":
        destination_path = Path(destination)
        if destination_path.is_absolute() or ".." in destination_path.parts:
            raise ValueError("template destination must stay inside the task work directory")
        self.templates.append(TemplateSpec(source, destination))
        self.stage(source)
        return self

    def use_stdin(self, path: str) -> "Job":
        self.stdin = path
        return self

    @property
    def task_count(self) -> int:
        return self.settings.task_count

    def validate(self) -> None:
        if not self.settings.job_name:
            raise ValueError("job name is required")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", self.settings.job_name):
            raise ValueError("job name may only contain letters, numbers, dots, underscores and hyphens")
        if not self.command:
            raise ValueError("job command is required")
        if any("\x00" in part or "\n" in part or "\r" in part for part in self.command):
            raise ValueError("command arguments cannot contain NUL or newline characters")
        concurrency = self.settings.concurrency
        if concurrency is not None and (not isinstance(concurrency, int) or concurrency < 1):
            raise ValueError("concurrency must be a positive integer")

        parameter_names = set(self.settings.variable.export_names())
        missing = parameter_names.difference(self.bindings)
        # Old add_vars() users receive the same sensible default as sweep().
        for name in missing:
            self.bindings[name] = Argument()

        if self.output_template is None and self.set_paths.output_dir:
            suffix = self.path_schema.value_template(self.settings)
            self.output_template = str(Path(self.set_paths.output_dir) / suffix) if suffix else self.set_paths.output_dir
        if self.output_template is None:
            raise ValueError("an output path template is required")
        if not self.output_template:
            raise ValueError("output path template cannot be empty")

        staged = list(self.set_paths.dependencies)
        if self.set_paths.input_script:
            staged.append(self.set_paths.input_script)
        basenames = [Path(path).name for path in staged]
        if len(basenames) != len(set(basenames)):
            raise ValueError("staged inputs must have unique basenames")

        destinations = [spec.destination for spec in self.templates]
        if len(destinations) != len(set(destinations)):
            raise ValueError("template destinations must be unique")

        readable_templates = []
        for spec in self.templates:
            source = Path(spec.source)
            if source.is_file():
                readable_templates.append(source.read_text(encoding="utf-8"))
        if readable_templates:
            combined = "\n".join(readable_templates)
            for name, binding in self.bindings.items():
                if isinstance(binding, TemplateVariable):
                    placeholder = binding.placeholder_for(name)
                    markers = ("{{ " + placeholder + " }}", "{{" + placeholder + "}}")
                    if not any(marker in combined for marker in markers):
                        raise ValueError(f"missing template placeholder: {placeholder}")

    def write(self, path: Union[str, Path]) -> Path:
        from clusterduck.slurm.slurm_write import SlurmWrite

        destination = Path(path)
        destination.write_text(SlurmWrite(self).slurmscript_generate(), encoding="utf-8")
        return destination
