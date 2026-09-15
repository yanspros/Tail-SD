#!/usr/bin/env python3
"""Classify transcripts, aggregate sources and optionally compare systems."""
from __future__ import annotations

import argparse
from collections import defaultdict

from tailsd.io import dump_json, load_json
from tailsd.metrics import aggregate_sources, classify, paired_bootstrap


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSON records with reference/hypothesis/eos/cap/system")
    parser.add_argument("--output", required=True)
    parser.add_argument("--left")
    parser.add_argument("--right")
    parser.add_argument("--bootstrap-seed", type=int, default=20260820)
    parser.add_argument("--bootstrap-resamples", type=int, default=10000)
    args = parser.parse_args()
    value = load_json(args.input)
    source = value if isinstance(value, list) else value["records"]
    scored = []
    for row in source:
        scored.append({**row, **classify(bool(row["eos_generated"]), bool(row["cap_hit"]), row["reference"], row["hypothesis"])})
    grouped = defaultdict(list)
    for row in scored:
        grouped[str(row["system"])].append(row)
    result = {"records": scored, "systems": {system: aggregate_sources(rows) for system, rows in sorted(grouped.items())}}
    if args.left or args.right:
        if not args.left or not args.right:
            parser.error("--left and --right must be supplied together")
        result["paired_strict_completion"] = paired_bootstrap(
            grouped[args.left], grouped[args.right], seed=args.bootstrap_seed, resamples=args.bootstrap_resamples
        )
    dump_json(args.output, result)


if __name__ == "__main__":
    main()
