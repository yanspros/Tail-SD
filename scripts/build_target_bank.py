#!/usr/bin/env python3
"""Build deterministic target candidates from frozen scored manifests."""
from __future__ import annotations

import argparse

from tailsd.io import dump_json, load_json
from tailsd.target_construction import build_content_candidates, build_termination_candidates, select_quota


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--natural", required=True, help="JSON list or object with records")
    parser.add_argument("--continuations", required=True, help="JSON list or object with records")
    parser.add_argument("--wer-max", type=float, required=True)
    parser.add_argument("--non-tail-max", type=float, required=True)
    parser.add_argument("--termination-quota", type=int, default=58)
    parser.add_argument("--content-quota", type=int, default=65)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    def rows(path):
        value = load_json(path)
        return value if isinstance(value, list) else value["records"]

    natural = rows(args.natural)
    continuation = rows(args.continuations)
    termination_pool = build_termination_candidates(natural, continuation, args.wer_max, args.non_tail_max)
    content_pool = build_content_candidates(natural, args.wer_max, args.non_tail_max)
    termination = select_quota(termination_pool, args.termination_quota)
    content = select_quota(content_pool, args.content_quota)
    dump_json(args.output, {
        "schema_version": 1,
        "status": "TARGET_BANK_CONSTRUCTED",
        "thresholds": {"wer_max": args.wer_max, "non_tail_error_rate_max": args.non_tail_max},
        "quotas": {"termination": args.termination_quota, "content": args.content_quota},
        "eligible_counts": {"termination": len(termination_pool), "content": len(content_pool)},
        "records": termination + content,
    })


if __name__ == "__main__":
    main()
