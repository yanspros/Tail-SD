#!/usr/bin/env python3
"""Build Tail-SD, Random-PR and Full-SD manifests from one bank."""
from __future__ import annotations

import argparse
from pathlib import Path

from tailsd.io import dump_json, load_json
from tailsd.masks import allocate_tail_masks, build_full_sd_labels
from tailsd.random_pr import build_random_pr_masks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--termination-ratio", type=float, default=0.21705160991522524)
    parser.add_argument("--content-ratio", type=float, default=0.29909295294208854)
    parser.add_argument("--random-pr-seed", type=int, default=20260912)
    args = parser.parse_args()
    value = load_json(args.bank)
    records = value if isinstance(value, list) else value["records"]
    tail = allocate_tail_masks(records, {"termination": args.termination_ratio, "content": args.content_ratio})
    random_pr = build_random_pr_masks(tail["records"], args.random_pr_seed)
    full = build_full_sd_labels(records)
    root = Path(args.output_dir)
    dump_json(root / "tail_sd_masks.json", tail)
    dump_json(root / "random_pr_masks.json", random_pr)
    dump_json(root / "full_sd_labels.json", full)


if __name__ == "__main__":
    main()
