import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from clusterduck import Argument, Environment, Job, TemplateVariable
from clusterduck.slurm import SlurmWrite


class SlurmGenerationTests(unittest.TestCase):
    def make_job(self):
        job = Job("test_job", ["python", "run.py"], concurrency=2)
        job.sweep("molecule", ["water molecule", "benzene"])
        job.sweep("distance", [3, 4, 5], Argument("--distance"))
        job.output("outputs/{molecule}/{distance}")
        return job

    def test_array_header_and_command(self):
        script = SlurmWrite(self.make_job()).slurmscript_generate()
        self.assertIn("#SBATCH --job-name=test_job", script)
        self.assertIn("#SBATCH --array=0-5%2", script)
        self.assertIn('--molecule "${molecule}"', script)
        self.assertIn('--distance "${distance}"', script)
        self.assertIn('output_dir="outputs/${molecule}/${distance}"', script)

    def test_environment_binding(self):
        job = Job("environment", ["printenv", "METHOD"], concurrency=1)
        job.sweep("method", ["G0W0"], Environment("METHOD"))
        job.output("outputs/{method}", argument=None)
        script = SlurmWrite(job).slurmscript_generate()
        self.assertIn('export METHOD="${method}"', script)
        self.assertNotIn("--method", script)

    def test_legacy_settings_and_path_objects_still_generate(self):
        job = Job()
        job.settings.job_name = "legacy"
        job.settings.concurrency = 3
        job.settings.add_vars("method", ["G0W0", "evGW"])
        job.set_command(["python", "run.py"])
        job.set_paths.output_dir = "outputs"
        job.set_paths.dependancies = ["run.py"]
        script = SlurmWrite()
        script.jobs = job
        generated = script.slurmscript_generate()
        self.assertIn("#SBATCH --array=0-1%3", generated)
        self.assertIn('output_dir="outputs/${method}"', generated)
        self.assertEqual(job.set_paths.dependencies, ["run.py"])

    def test_unknown_output_placeholder_is_rejected(self):
        job = Job("invalid", ["true"])
        job.sweep("method", ["G0W0"])
        job.output("outputs/{missing}")
        with self.assertRaises(ValueError):
            SlurmWrite(job).slurmscript_generate()

    def test_generated_script_passes_bash_syntax_check(self):
        script = SlurmWrite(self.make_job()).slurmscript_generate()
        result = subprocess.run(
            ["bash", "-n"],
            input=script,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_working_directory_is_scratch_relative(self):
        job = self.make_job()
        job.working_directory("calculation files")
        script = SlurmWrite(job).slurmscript_generate()
        self.assertIn(
            "command_workdir=\"$workdir\"/'calculation files'",
            script,
        )
        self.assertIn('cd "$command_workdir"', script)

    def test_unsafe_working_directories_are_rejected(self):
        job = self.make_job()
        for path in ("", "/shared/calculation", "../calculation", "input/../../shared"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    job.working_directory(path)

    def test_out_of_range_task_id_is_rejected(self):
        script = SlurmWrite(self.make_job()).slurmscript_generate()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "job.slurm"
            path.write_text(script, encoding="utf-8")
            environment = os.environ.copy()
            environment["SLURM_ARRAY_TASK_ID"] = "6"
            result = subprocess.run(
                ["bash", str(path)],
                cwd=directory,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("outside the configured sweep", result.stderr)


class LocalIntegrationTests(unittest.TestCase):
    def test_every_array_index_runs_one_unique_configuration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            worker = root / "run_experiment.py"
            worker.write_text(
                """import argparse, json
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--molecule', required=True)
p.add_argument('--distance', required=True, type=int)
p.add_argument('--output-dir', required=True, type=Path)
a = p.parse_args()
a.output_dir.mkdir(parents=True, exist_ok=True)
(a.output_dir / 'result.json').write_text(json.dumps(vars(a), default=str))
""",
                encoding="utf-8",
            )

            job = Job("integration", [sys.executable, worker.name], concurrency=2)
            job.sweep("molecule", ["water molecule", "benzene"])
            job.sweep("distance", [3, 4, 5])
            job.stage(worker)
            job.output("outputs/{molecule}/{distance}")
            script = root / "integration.slurm"
            job.write(script)

            seen = set()
            for task_id in range(job.task_count):
                environment = os.environ.copy()
                environment.update(
                    {
                        "SLURM_ARRAY_TASK_ID": str(task_id),
                        "SLURM_JOB_ID": "localtest",
                        "TMPDIR": str(root / "scratch"),
                    }
                )
                result = subprocess.run(
                    ["bash", str(script)],
                    cwd=root,
                    env=environment,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

            for result_file in (root / "outputs").glob("*/*/result.json"):
                result = json.loads(result_file.read_text(encoding="utf-8"))
                seen.add((result["molecule"], result["distance"]))
            self.assertEqual(
                seen,
                {
                    (molecule, distance)
                    for molecule in ("water molecule", "benzene")
                    for distance in (3, 4, 5)
                },
            )

    def test_command_runs_from_staged_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "calculation files"
            project.mkdir()
            worker = project / "worker.py"
            worker.write_text(
                """import argparse
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--output-dir', type=Path, required=True)
a = p.parse_args()
a.output_dir.mkdir(parents=True, exist_ok=True)
(a.output_dir / 'cwd.txt').write_text(Path.cwd().name)
""",
                encoding="utf-8",
            )

            job = Job("working_directory", [sys.executable, worker.name])
            job.stage(project)
            job.working_directory(project.name)
            job.output(str(root / "outputs"))
            script = root / "working-directory.slurm"
            job.write(script)

            environment = os.environ.copy()
            environment.update(
                {
                    "SLURM_ARRAY_TASK_ID": "0",
                    "SLURM_JOB_ID": "workdir",
                    "TMPDIR": str(root / "scratch"),
                }
            )
            result = subprocess.run(
                ["bash", str(script)],
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                (root / "outputs/cwd.txt").read_text(encoding="utf-8"),
                project.name,
            )

    def test_template_binding_renders_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            template = root / "calculation.in.template"
            template.write_text("method={{ method }}\ndistance={{distance}}\n", encoding="utf-8")
            worker = root / "consume_template.py"
            worker.write_text(
                """import argparse
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--output-dir', type=Path, required=True)
a = p.parse_args()
a.output_dir.mkdir(parents=True, exist_ok=True)
(a.output_dir / 'rendered.txt').write_text(Path('calculation.in').read_text())
""",
                encoding="utf-8",
            )

            job = Job("template", [sys.executable, worker.name], concurrency=1)
            job.sweep("method", ["G0W0"], TemplateVariable())
            job.sweep("distance", [3.5], TemplateVariable())
            job.template(str(template), "calculation.in")
            job.stage(worker)
            job.output(str(root / "outputs/{method}/{distance}"))
            script = root / "template.slurm"
            job.write(script)

            environment = os.environ.copy()
            environment.update(
                {
                    "SLURM_ARRAY_TASK_ID": "0",
                    "SLURM_JOB_ID": "template",
                    "TMPDIR": str(root / "scratch"),
                }
            )
            result = subprocess.run(
                ["bash", str(script)],
                cwd=root,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            rendered = root / "outputs/G0W0/3.5/rendered.txt"
            self.assertEqual(rendered.read_text(encoding="utf-8"), "method=G0W0\ndistance=3.5\n")


if __name__ == "__main__":
    unittest.main()
