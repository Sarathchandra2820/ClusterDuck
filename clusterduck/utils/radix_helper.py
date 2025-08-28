def generate_radix_block(schema) -> str:

    """
    schema: ordered list of variable names, e.g. ["molecule","method","distance"]
    returns: bash code string that computes indices and extracts values
    """
    lines = []
    n = len(schema)

    # Length variables
    for i, key in enumerate(schema):
        lines.append(f"L{i}=${{{{#{key}_vals[@]}}}}   # {key}")

    lines.append("")  # spacing

    # Radices
    for i, key in enumerate(schema):
        if i < n - 1:
            later = [f"L{j}" for j in range(i + 1, n)]
            prod = " * ".join(later)
            lines.append(f"R{i}=$(( {prod} ))  # product of later lengths")
        else:
            lines.append(f"R{i}=1")

    lines.append("")
    lines.append("k=${SLURM_ARRAY_TASK_ID}")
    lines.append("")

    # Indices
    for i, key in enumerate(schema):
        lines.append(f"i{i}=$(( (k / R{i}) % L{i} ))")

    lines.append("")

    # Assign values
    for i, key in enumerate(schema):
        lines.append(f'{key}="${{{key}_vals[$i{i}]}}"')

    return "\n".join(lines)


