#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Run one example calculation")
    parser.add_argument("--molecule", required=True)
    parser.add_argument("--distance", required=True, type=float)
    parser.add_argument("--method", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "molecule": args.molecule,
        "distance": args.distance,
        "method": args.method,
        "energy": -0.123 * args.distance,
    }
    (args.output_dir / "result.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
