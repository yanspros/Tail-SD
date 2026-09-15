"""Tail-SD and Full-SD label-mask construction.

The allocation exactly follows the formal CV3/CV2 implementation:

1. floor the branch aggregate budget ``ratio * sum(T_i)``;
2. floor every per-record ``ratio * T_i``;
3. give one residual label to the earliest records in canonical bank order,
   after filtering that order by branch.

Termination records supervise the speech tail plus EOS. Content records
supervise only the speech tail. All positions remain in the causal forward;
the mask controls direct cross-entropy participation only.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Any, Iterable, Mapping


BRANCHES = ("termination", "content")


def _length(record: Mapping[str, Any]) -> int:
    for key in ("T_i", "speech_token_count", "recovery_speech_token_count"):
        if key in record:
            value = int(record[key])
            if value <= 0:
                raise ValueError(f"speech-token length must be positive: {value}")
            return value
    raise KeyError("record needs T_i, speech_token_count, or recovery_speech_token_count")


def _record_id(record: Mapping[str, Any], index: int) -> str:
    return str(record.get("record_id") or record.get("record_key") or record.get("source_id") or f"record_{index:06d}")


def allocate_tail_masks(
    records: Iterable[Mapping[str, Any]],
    branch_ratios: Mapping[str, float],
) -> dict[str, Any]:
    """Allocate deterministic branch-wise fixed-ratio terminal masks.

    The input iterable is the canonical bank order. No sorting is performed.
    """
    source = [deepcopy(dict(row)) for row in records]
    if not source:
        raise ValueError("records cannot be empty")
    by_branch: dict[str, list[tuple[int, dict[str, Any], int]]] = defaultdict(list)
    for index, row in enumerate(source):
        branch = str(row.get("branch", "")).lower()
        if branch not in BRANCHES:
            raise ValueError(f"unknown branch at record {index}: {branch!r}")
        by_branch[branch].append((index, row, _length(row)))
    if set(by_branch) != set(BRANCHES):
        raise ValueError("both termination and content branches are required")

    allocated: dict[int, dict[str, Any]] = {}
    branch_audit: dict[str, Any] = {}
    for branch in BRANCHES:
        rows = by_branch[branch]
        ratio = float(branch_ratios[branch])
        if not 0.0 < ratio <= 1.0:
            raise ValueError(f"invalid ratio for {branch}: {ratio}")
        total = sum(length for _, _, length in rows)
        aggregate_budget = int(ratio * total)
        floors = [int(ratio * length) for _, _, length in rows]
        residual = aggregate_budget - sum(floors)
        if not 0 <= residual < len(rows):
            raise ValueError(f"invalid residual for {branch}: {residual}")
        for local_index, ((index, row, length), floor_count) in enumerate(zip(rows, floors)):
            k_i = floor_count + int(local_index < residual)
            if not 0 < k_i <= length:
                raise ValueError(f"illegal K_i for {_record_id(row, index)}: {k_i}/{length}")
            start = length - k_i
            special = [length] if branch == "termination" else []
            allocated[index] = {
                "record_index": index,
                "record_id": _record_id(row, index),
                "source_id": row.get("source_id"),
                "branch": branch,
                "T_i": length,
                "ratio": ratio,
                "floor_ratio_count": floor_count,
                "residual_increment": local_index < residual,
                "K_i": k_i,
                "tail_start": start,
                "tail_end_exclusive": length,
                "active_speech_positions": list(range(start, length)),
                "active_eos_special_positions": special,
                "M_i": k_i + len(special),
                "full_teacher_forced_history_retained": True,
            }
        branch_audit[branch] = {
            "record_count": len(rows),
            "target_speech_token_total": total,
            "fixed_ratio": ratio,
            "aggregate_speech_label_budget": aggregate_budget,
            "per_record_floor_sum": sum(floors),
            "residual_count": residual,
            "residual_rule": "earliest records in canonical bank order filtered by branch",
            "active_eos_special_labels": len(rows) if branch == "termination" else 0,
            "active_total_ce_labels": aggregate_budget + (len(rows) if branch == "termination" else 0),
        }

    result = [allocated[index] for index in range(len(source))]
    tail_speech = sum(row["K_i"] for row in result)
    tail_total = sum(row["M_i"] for row in result)
    return {
        "schema_version": 1,
        "method": "Tail-SD",
        "allocation_contract": "branch aggregate floor, per-record floor, earliest-record residual allocation",
        "records": result,
        "branch_audit": branch_audit,
        "overall": {
            "record_count": len(result),
            "active_speech_labels": tail_speech,
            "active_total_ce_labels": tail_total,
            "full_teacher_forced_history_retained": True,
        },
    }


def build_full_sd_labels(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Build the dense label reference on the same target bank and history."""
    rows = []
    for index, item in enumerate(records):
        record = dict(item)
        branch = str(record.get("branch", "")).lower()
        if branch not in BRANCHES:
            raise ValueError(f"unknown branch at record {index}: {branch!r}")
        length = _length(record)
        special = [length] if branch == "termination" else []
        rows.append({
            "record_index": index,
            "record_id": _record_id(record, index),
            "source_id": record.get("source_id"),
            "branch": branch,
            "T_i": length,
            "active_speech_positions": list(range(length)),
            "active_eos_special_positions": special,
            "M_i": length + len(special),
            "full_teacher_forced_history_retained": True,
        })
    return {
        "schema_version": 1,
        "method": "Full-SD",
        "records": rows,
        "overall": {"record_count": len(rows), "active_total_ce_labels": sum(row["M_i"] for row in rows)},
    }


def mask_on_valid_positions(valid_positions: list[int], row: Mapping[str, Any]) -> list[bool]:
    """Map speech/EOS-relative positions onto a full causal label sequence."""
    length = int(row["T_i"])
    if len(valid_positions) != length + 1:
        raise ValueError("valid positions must contain T_i speech labels followed by EOS")
    active = [False] * (max(valid_positions) + 1)
    for position in row["active_speech_positions"]:
        active[valid_positions[int(position)]] = True
    for position in row["active_eos_special_positions"]:
        active[valid_positions[int(position)]] = True
    if sum(active) != int(row["M_i"]):
        raise ValueError("active-label budget does not match M_i")
    return active
