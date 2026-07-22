from __future__ import annotations

from pathlib import Path
import re
import shlex
from string import Formatter
from typing import List, Optional

from clusterduck.core.bindings import Argument, Environment, TemplateVariable
from clusterduck.jobs.jobs import Job
from clusterduck.utils.radix_helper import generate_radix_block


_SHELL_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _quote(value: object) -> str:
    return shlex.quote(str(value))


def _double_quoted_template(template: str, allowed_names: set) -> str:
    """Render a validated Python-format path as a safe Bash double-quoted value."""
    pieces: List[str] = []
    for literal, field_name, format_spec, conversion in Formatter().parse(template):
        pieces.append(
            literal.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("$", "\\$")
            .replace("`", "\\`")
        )
        if field_name is not None:
            if field_name not in allowed_names:
                raise ValueError(f"unknown output path placeholder: {field_name}")
            if format_spec or conversion:
                raise ValueError("output path placeholders cannot use formatting or conversion")
            pieces.append("${" + field_name + "}")
    return '"' + "".join(pieces) + '"'


def _template_fields(template: str) -> List[str]:
    return [field for _, field, _, _ in Formatter().parse(template) if field is not None]


class SlurmWrite:
    def __init__(self, jobs: Optional[Job] = None) -> None:
        self.jobs = jobs

    @property
    def job(self) -> Job:
        if self.jobs is None:
            raise ValueError("a Job must be assigned before generating a script")
        return self.jobs

    def header_write(self) -> str:
        self.job.validate()
        settings = self.job.settings
        array = f"0-{self.job.task_count - 1}"
        if settings.concurrency is not None:
            array += f"%{settings.concurrency}"

        lines = [
            "#!/usr/bin/env bash",
            f"#SBATCH --job-name={settings.job_name}",
            f"#SBATCH --array={array}",
        ]
        for key, value in settings.sbatch_opts.items():
            if "\n" in value or "\r" in value:
                raise ValueError(f"invalid newline in SBATCH option: {key}")
            lines.append(f"#SBATCH --{key}={value}")
        return "\n".join(lines)

    def write_slurm_vars(self) -> str:
        lines = []
        for variable in self.job.settings.variable.var:
            values = " ".join(_quote(value) for value in variable.sweep)
            lines.append(f"declare -a {variable.name}_values=({values})")
        return "\n".join(lines)

    def radix_logic(self) -> str:
        return generate_radix_block(
            self.job.settings.variable.export_names(), self.job.task_count
        )

    def _stage_lines(self) -> List[str]:
        staged = list(self.job.set_paths.dependencies)
        if self.job.set_paths.input_script and self.job.set_paths.input_script not in staged:
            staged.append(self.job.set_paths.input_script)

        lines: List[str] = []
        for number, source in enumerate(staged):
            variable = f"clusterduck_stage_{number}"
            lines.extend(
                [
                    f"{variable}={_quote(source)}",
                    f'if [[ "${{{variable}}}" != /* ]]; then {variable}="${{submit_dir}}/${{{variable}}}"; fi',
                    f'[[ -e "${{{variable}}}" ]] || {{ echo "Missing staged input: ${{{variable}}}" >&2; exit 2; }}',
                    f'cp -R -- "${{{variable}}}" "$workdir/"',
                ]
            )
        return lines

    def _template_lines(self) -> List[str]:
        bindings = [
            (name, binding)
            for name, binding in self.job.bindings.items()
            if isinstance(binding, TemplateVariable)
        ]
        lines: List[str] = []
        for spec in self.job.templates:
            source = Path(spec.source).name
            command = ["python3", "-", source, spec.destination]
            for name, binding in bindings:
                command.extend([binding.placeholder_for(name), f'"${{{name}}}"'])
            rendered = " ".join(
                token if token.startswith('"${') else _quote(token) for token in command
            )
            lines.extend(
                [
                    f"{rendered} <<'CLUSTERDUCK_TEMPLATE_PY'",
                    "from pathlib import Path",
                    "import sys",
                    "source, destination = sys.argv[1:3]",
                    "pairs = zip(sys.argv[3::2], sys.argv[4::2])",
                    "content = Path(source).read_text(encoding='utf-8')",
                    "for name, value in pairs:",
                    "    content = content.replace('{{ ' + name + ' }}', value)",
                    "    content = content.replace('{{' + name + '}}', value)",
                    "destination_path = Path(destination)",
                    "destination_path.parent.mkdir(parents=True, exist_ok=True)",
                    "destination_path.write_text(content, encoding='utf-8')",
                    "CLUSTERDUCK_TEMPLATE_PY",
                ]
            )
        return lines

    def _command_lines(self) -> List[str]:
        command = [_quote(part) for part in self.job.command]
        lines: List[str] = []

        for name, binding in self.job.bindings.items():
            if isinstance(binding, Argument):
                command.extend([_quote(binding.option_for(name)), f'"${{{name}}}"'])
            elif isinstance(binding, Environment):
                lines.append(f'export {binding.variable}="${{{name}}}"')
            elif not isinstance(binding, TemplateVariable):
                raise TypeError(f"unsupported binding for {name}: {type(binding).__name__}")

        if self.job.output_argument:
            command.extend([_quote(self.job.output_argument), '"$output_dir"'])

        lines.append("clusterduck_command=(" + " ".join(command) + ")")
        lines.append('echo "ClusterDuck task ${SLURM_ARRAY_TASK_ID}: ${clusterduck_command[*]}"')
        if self.job.stdin:
            lines.append(f'"${{clusterduck_command[@]}}" < {_quote(self.job.stdin)}')
        else:
            lines.append('"${clusterduck_command[@]}"')
        return lines

    def _collect_lines(self) -> List[str]:
        patterns = list(self.job.collect_patterns) + list(self.job.path_schema.output_key)
        lines: List[str] = []
        for pattern in patterns:
            if "/" in pattern or pattern in {".", ".."}:
                raise ValueError("collection patterns must be basename glob patterns")
            lines.extend(
                [
                    "while IFS= read -r -d '' artifact; do",
                    '  cp -R -- "$artifact" "$output_dir/"',
                    f"done < <(find . -mindepth 1 -maxdepth 1 -name {_quote(pattern)} -print0)",
                ]
            )
        return lines

    def slurmscript_generate(self) -> str:
        self.job.validate()
        settings = self.job.settings
        parameter_names = set(settings.variable.export_names())
        output_value = _double_quoted_template(self.job.output_template or "", parameter_names)

        lines = [
            self.header_write(),
            "",
            "set -euo pipefail",
            "",
        ]
        for module in settings.module_load:
            lines.append(f"module load {_quote(module)}")
        for key, value in settings.export_opts.items():
            if not _SHELL_NAME.fullmatch(key):
                raise ValueError(f"invalid exported variable name: {key}")
            lines.append(f"export {key}={_quote(value)}")
        if settings.module_load or settings.export_opts:
            lines.append("")

        lines.extend(
            [
                self.write_slurm_vars(),
                "",
                self.radix_logic(),
                "",
                'submit_dir="$PWD"',
            ]
        )

        scratch = self.job.set_paths.scratch_dir
        if scratch is None or scratch == "$TMPDIR":
            lines.append('scratch_root="${TMPDIR:-/tmp}"')
        else:
            lines.append(f"scratch_root={_quote(scratch)}")
        lines.extend(
            [
                'workdir="${scratch_root}/clusterduck_${SLURM_JOB_ID:-local}_${SLURM_ARRAY_TASK_ID}_$$"',
                'mkdir -p "$workdir"',
                "clusterduck_cleanup() {",
                "  status=$?",
                "  trap - EXIT",
            ]
        )
        if self.job.keep_failed_scratch:
            lines.extend(
                [
                    '  if (( status == 0 )); then rm -rf -- "$workdir";',
                    '  else echo "Task failed; scratch retained at $workdir" >&2; fi',
                ]
            )
        else:
            lines.append('  rm -rf -- "$workdir"')
        lines.extend(["  exit \"$status\"", "}", "trap clusterduck_cleanup EXIT", ""])
        lines.extend(self._stage_lines())
        for name in _template_fields(self.job.output_template or ""):
            lines.extend(
                [
                    f'clusterduck_path_value="${{{name}}}"',
                    'if [[ "$clusterduck_path_value" == */* || "$clusterduck_path_value" == "." || "$clusterduck_path_value" == ".." ]]; then',
                    f'  echo "Unsafe value for output path parameter {name}: $clusterduck_path_value" >&2',
                    "  exit 2",
                    "fi",
                ]
            )
        lines.extend(
            [
                f"output_dir={output_value}",
                'if [[ "$output_dir" != /* ]]; then output_dir="${submit_dir}/${output_dir}"; fi',
                'mkdir -p "$output_dir"',
                'cd "$workdir"',
                "",
            ]
        )
        lines.extend(self._template_lines())
        if self.job.templates:
            lines.append("")
        lines.extend(self._command_lines())
        lines.extend(self._collect_lines())
        lines.append('echo "ClusterDuck task ${SLURM_ARRAY_TASK_ID} completed"')
        return "\n".join(lines).rstrip() + "\n"

    def write(self, path: str) -> Path:
        destination = Path(path)
        destination.write_text(self.slurmscript_generate(), encoding="utf-8")
        return destination
