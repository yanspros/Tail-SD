"""Per-record-matched Random-PR supervision control."""
from __future__ import annotations

import random
import sys
from copy import deepcopy
from typing import Any, Iterable, Mapping

from .io import canonical_sha256


def build_random_pr_masks(
    tail_records: Iterable[Mapping[str, Any]],
    seed: int,
) -> dict[str, Any]:
    """Draw one inclusive-uniform legal start per record, in input order.

    The supplied order is the frozen canonical draw order. Tail overlap and an
    exact tail match are legal and never trigger a redraw.
    """
    source = [deepcopy(dict(row)) for row in tail_records]
    rng = random.Random(int(seed))
    state_before = canonical_sha256(rng.getstate())
    rows = []
    for draw_index, row in enumerate(source):
        length = int(row["T_i"])
        k_i = int(row["K_i"])
        if not 0 < k_i <= length:
            raise ValueError(f"illegal K_i at draw {draw_index}: {k_i}/{length}")
        start = rng.randrange(0, length - k_i + 1)
        end = start + k_i
        tail_start = int(row["tail_start"])
        tail_end = int(row["tail_end_exclusive"])
        overlap = max(0, min(end, tail_end) - max(start, tail_start))
        special = [int(value) for value in row.get("active_eos_special_positions", [])]
        result = {
            "record_index": int(row.get("record_index", draw_index)),
            "draw_index": draw_index,
            "record_id": row["record_id"],
            "source_id": row.get("source_id"),
            "branch": row["branch"],
            "T_i": length,
            "K_i": k_i,
            "sampled_start": start,
            "sampled_end_exclusive": end,
            "active_speech_positions": list(range(start, end)),
            "active_eos_special_positions": special,
            "M_i": k_i + len(special),
            "tail_start": tail_start,
            "overlap_length": overlap,
            "exact_tail_match": start == tail_start and end == tail_end,
            "partial_overlap": 0 < overlap < k_i,
            "zero_overlap": overlap == 0,
            "target_history_identity": row.get("target_history_identity"),
            "full_teacher_forced_history_retained": True,
        }
        result["mask_sha256"] = canonical_sha256(result)
        rows.append(result)
    return {
        "schema_version": 1,
        "method": "Random-PR",
        "rng": {
            "implementation": "Python standard library random.Random",
            "python_version": sys.version.split()[0],
            "seed": int(seed),
            "draw_function": "randrange(0, T_i-K_i+1)",
            "draw_order": "input canonical bank order",
            "draw_count": len(rows),
            "state_sha256_before_draws": state_before,
            "state_sha256_after_draws": canonical_sha256(rng.getstate()),
            "no_redraw": True,
        },
        "records": rows,
        "audit": audit_random_pr_match(source, rows),
    }


def audit_random_pr_match(tail_records: Iterable[Mapping[str, Any]], random_records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    tails = [dict(row) for row in tail_records]
    randoms = [dict(row) for row in random_records]
    if len(tails) != len(randoms):
        raise ValueError("Tail-SD and Random-PR record counts differ")
    details = []
    for index, (tail, random_row) in enumerate(zip(tails, randoms)):
        legal = 0 <= int(random_row["sampled_start"]) <= int(tail["T_i"]) - int(tail["K_i"])
        checks = {
            "record_id": random_row["record_id"] == tail["record_id"],
            "K_i": int(random_row["K_i"]) == int(tail["K_i"]),
            "eos_special": random_row["active_eos_special_positions"] == tail["active_eos_special_positions"],
            "M_i": int(random_row["M_i"]) == int(tail["M_i"]),
            "target_history": random_row.get("target_history_identity") == tail.get("target_history_identity"),
            "legal_span": legal and int(random_row["sampled_end_exclusive"]) - int(random_row["sampled_start"]) == int(tail["K_i"]),
            "draw_index": int(random_row["draw_index"]) == index,
        }
        details.append({"record_id": tail["record_id"], "checks": checks})
    keys = ("K_i", "eos_special", "M_i", "target_history", "legal_span", "draw_index", "record_id")
    return {
        "record_count": len(details),
        "match_counts": {key: sum(row["checks"][key] for row in details) for key in keys},
        "all_match": all(all(row["checks"].values()) for row in details),
        "exact_tail_matches": sum(bool(row.get("exact_tail_match")) for row in randoms),
        "partial_overlaps": sum(bool(row.get("partial_overlap")) for row in randoms),
        "zero_overlaps": sum(bool(row.get("zero_overlap")) for row in randoms),
        "records": details,
    }
