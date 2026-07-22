# Changelog

## 0.2.0 - 2026-07-22

- Add declarative `Job` API with argument, environment, and template bindings.
- Generate correct SLURM array ranges and concurrency limits.
- Replace configuration materialization with constant-memory task counting and decoding.
- Execute workloads in isolated scratch directories and support value-based outputs.
- Add shell quoting, validation, failure propagation, and optional scratch retention.
- Add standard-library unit and local end-to-end tests.
- Remove generated caches, stale scripts, and import-time filesystem side effects.

## 0.1.0

- Initial sweep, path, and SLURM generation prototype.
