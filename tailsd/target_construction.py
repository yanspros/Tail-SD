"""Deterministic selection over already generated and scored trajectories.

This module does not synthesize audio or run ASR. It preserves the selection
semantics used to build the formal CV3 target bank: first failure in frozen
seed order, strict-complete quality filtering, then deterministic quality
ranking of candidate recoveries.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Any, Iterable, Mapping, Sequence


def is_strict_complete(row: Mapping[str, Any]) -> bool:
    classification = row.get("classification")
    return bool(
        classification in {"COMPLETE", "SC"}
        and row.get("eos_generated", row.get("eos", False))
        and not row.get("cap_hit", False)
        and float(row.get("text_coverage_ratio", row.get("coverage", 0.0))) >= 0.95
        and int(row.get("trailing_deleted_words", row.get("trailing_deletions", -1))) == 0
    )


def is_hc(row: Mapping[str, Any]) -> bool:
    return bool(
        row.get("eos_generated", row.get("eos", False))
        and not row.get("cap_hit", False)
        and float(row.get("text_coverage_ratio", row.get("coverage", 1.0))) <= 0.85
        and int(row.get("trailing_deleted_words", row.get("trailing_deletions", 0))) >= 10
    )


def _seed(row: Mapping[str, Any]) -> int:
    return int(row.get("seed", row.get("natural_seed", row.get("continuation_seed", -1))))


def first_matching(rows: Sequence[Mapping[str, Any]], predicate) -> dict[str, Any] | None:
    ordered = sorted((dict(row) for row in rows), key=_seed)
    return next((row for row in ordered if predicate(row)), None)


def recovery_rank(row: Mapping[str, Any]) -> tuple[float, float, float, int]:
    """Formal CV3 target ranking: low non-tail, high coverage, low WER, low seed."""
    return (
        float(row["non_tail_error_rate"]),
        -float(row.get("text_coverage_ratio", row.get("coverage"))),
        float(row["wer"]),
        _seed(row),
    )


def quality_reasons(
    row: Mapping[str, Any],
    wer_max: float,
    non_tail_max: float,
    paired_failure_non_tail: float | None = None,
) -> list[str]:
    reasons = []
    if not is_strict_complete(row):
        reasons.append("STRICT_COMPLETE_INVARIANT_FAILED")
    if float(row["wer"]) > float(wer_max):
        reasons.append("WER_ABOVE_THRESHOLD")
    if float(row["non_tail_error_rate"]) > float(non_tail_max):
        reasons.append("NON_TAIL_ERROR_ABOVE_THRESHOLD")
    if paired_failure_non_tail is not None and not float(row["non_tail_error_rate"]) < float(paired_failure_non_tail):
        reasons.append("NOT_BETTER_THAN_PAIRED_OTHER_FAILURE")
    return reasons


def build_termination_candidates(
    natural_rows: Iterable[Mapping[str, Any]],
    continuation_rows: Iterable[Mapping[str, Any]],
    wer_max: float,
    non_tail_max: float,
) -> list[dict[str, Any]]:
    natural: dict[str, list[dict[str, Any]]] = defaultdict(list)
    continuation: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in natural_rows:
        natural[str(row["source_id"])].append(dict(row))
    for row in continuation_rows:
        continuation[str(row["source_id"])].append(dict(row))
    selected = []
    for source_id in sorted(natural):
        failure = first_matching(natural[source_id], is_hc)
        if failure is None:
            continue
        candidates = []
        for row in continuation.get(source_id, []):
            reasons = quality_reasons(row, wer_max, non_tail_max)
            if not reasons:
                candidates.append(deepcopy(row))
        if not candidates:
            continue
        target = min(candidates, key=recovery_rank)
        selected.append({
            "branch": "termination",
            "source_id": source_id,
            "failed_natural": failure,
            "selected_target": target,
            "selection_rule": "first HC by natural seed; eligible continuation ranked by non-tail, -coverage, WER, seed",
        })
    return selected


def build_content_candidates(
    natural_rows: Iterable[Mapping[str, Any]],
    wer_max: float,
    non_tail_max: float,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in natural_rows:
        grouped[str(row["source_id"])].append(dict(row))
    selected = []
    for source_id in sorted(grouped):
        rows = sorted(grouped[source_id], key=_seed)
        failure = first_matching(rows, lambda row: row.get("classification") == "OTHER_FAILURE")
        if failure is None:
            continue
        failure_rate = float(failure["non_tail_error_rate"])
        candidates = [
            row for row in rows
            if _seed(row) != _seed(failure)
            and not quality_reasons(row, wer_max, non_tail_max, failure_rate)
        ]
        if not candidates:
            continue
        target = min(candidates, key=recovery_rank)
        selected.append({
            "branch": "content",
            "source_id": source_id,
            "failed_natural": failure,
            "selected_target": target,
            "selection_rule": "first OTHER_FAILURE; alternate strict-COMPLETE ranked by non-tail, -coverage, WER, seed",
        })
    return selected


def select_quota(candidates: Iterable[Mapping[str, Any]], quota: int, rank_fields: Sequence[str] | None = None) -> list[dict[str, Any]]:
    """Take a fixed quota without introducing outcome-dependent tie-breaking.

    If ``rank_fields`` is omitted, preserve the supplied frozen candidate
    order. Otherwise use the caller's predeclared tuple of fields and source_id
    as a final deterministic identity tie-break.
    """
    rows = [dict(row) for row in candidates]
    if len({str(row["source_id"]) for row in rows}) != len(rows):
        raise ValueError("at most one candidate per source and branch is required")
    if rank_fields:
        rows.sort(key=lambda row: tuple(row[field] for field in rank_fields) + (str(row["source_id"]),))
    if len(rows) < int(quota):
        raise ValueError(f"eligible supply {len(rows)} is below quota {quota}")
    return rows[: int(quota)]
