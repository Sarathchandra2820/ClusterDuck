from __future__ import annotations

from typing import Iterable


def generate_radix_block(names: Iterable[str], task_count: int = 0) -> str:
    """Generate Bash that maps one array index to one Cartesian combination."""
    ordered = list(names)
    lines = [
        ': "${SLURM_ARRAY_TASK_ID:?SLURM_ARRAY_TASK_ID is required}"',
        '[[ "$SLURM_ARRAY_TASK_ID" =~ ^[0-9]+$ ]] || { echo "Invalid SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID" >&2; exit 2; }',
        "clusterduck_index=$SLURM_ARRAY_TASK_ID",
    ]
    if task_count:
        lines.append(
            f'(( clusterduck_index < {task_count} )) || {{ echo "SLURM_ARRAY_TASK_ID is outside the configured sweep" >&2; exit 2; }}'
        )

    # Decode from the last parameter to the first. This avoids materializing
    # configurations and needs no precomputed radix table.
    for name in reversed(ordered):
        lines.extend(
            [
                f"{name}_index=$((clusterduck_index % ${{#{name}_values[@]}}))",
                f"clusterduck_index=$((clusterduck_index / ${{#{name}_values[@]}}))",
                f'{name}="${{{name}_values[${name}_index]}}"',
            ]
        )
    return "\n".join(lines)
