"""Frozen completion diagnostics and source-level paired bootstrap."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


WORD = re.compile(r"[A-Za-z]+(?:['\u2019-][A-Za-z]+)?")


def words(text: str) -> list[str]:
    return [match.group().lower().replace("\u2019", "'") for match in WORD.finditer(text)]


def align(reference: Sequence[str], hypothesis: Sequence[str]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    n, m = len(reference), len(hypothesis)
    costs = [[0] * (m + 1) for _ in range(n + 1)]
    for index in range(1, n + 1):
        costs[index][0] = index
    for index in range(1, m + 1):
        costs[0][index] = index
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            costs[i][j] = min(
                costs[i - 1][j] + 1,
                costs[i][j - 1] + 1,
                costs[i - 1][j - 1] + (reference[i - 1] != hypothesis[j - 1]),
            )
    operations = []
    i, j = n, m
    while i or j:
        if i and j and costs[i][j] == costs[i - 1][j - 1] + (reference[i - 1] != hypothesis[j - 1]):
            operations.append({"op": "match" if reference[i - 1] == hypothesis[j - 1] else "substitution", "reference_index": i - 1, "hypothesis_index": j - 1})
            i, j = i - 1, j - 1
        elif i and costs[i][j] == costs[i - 1][j] + 1:
            operations.append({"op": "deletion", "reference_index": i - 1, "hypothesis_index": None})
            i -= 1
        else:
            operations.append({"op": "insertion", "reference_index": None, "hypothesis_index": j - 1})
            j -= 1
    operations.reverse()
    counts = {kind: sum(item["op"] == kind for item in operations) for kind in ("insertion", "deletion", "substitution")}
    counts["errors"] = sum(counts.values())
    return operations, counts


def diagnostics(reference: str, hypothesis: str) -> dict[str, Any]:
    ref, hyp = words(reference), words(hypothesis)
    operations, counts = align(ref, hyp)
    trailing = []
    for operation in reversed(operations):
        if operation["op"] != "deletion":
            break
        trailing.append(operation)
    trailing.reverse()
    non_tail_errors = counts["errors"] - len(trailing)
    denominator = max(1, len(ref))
    return {
        "reference_word_count": len(ref),
        "hypothesis_word_count": len(hyp),
        "alignment": operations,
        "word_error_counts": counts,
        "wer": counts["errors"] / denominator,
        "text_coverage_ratio": (len(ref) - counts["deletion"]) / denominator,
        "trailing_deleted_words": len(trailing),
        "tail_missing_ratio": len(trailing) / denominator,
        "non_tail_error_count": non_tail_errors,
        "non_tail_error_rate": non_tail_errors / denominator,
    }


def classify(eos_generated: bool, cap_hit: bool, reference: str, hypothesis: str) -> dict[str, Any]:
    diag = diagnostics(reference, hypothesis)
    if cap_hit:
        label, reason = "CAP_TRUNCATED", "generation cap or hard stop observed"
    elif eos_generated and diag["text_coverage_ratio"] <= 0.90 and diag["trailing_deleted_words"] >= 5:
        label, reason = "EARLY_EOS", "real EOS and terminal-tail criterion"
    elif eos_generated and diag["text_coverage_ratio"] >= 0.95 and diag["trailing_deleted_words"] == 0:
        label, reason = "COMPLETE", "real EOS and strict-complete criterion"
    elif not eos_generated:
        label, reason = "CONTENT_INCOMPLETE_WITHOUT_EOS", "no real terminal EOS"
    else:
        label, reason = "OTHER_FAILURE", "residual automatic category"
    return {
        **diag,
        "eos_generated": bool(eos_generated),
        "cap_hit": bool(cap_hit),
        "classification": label,
        "classification_reason": reason,
        "strict_complete": label == "COMPLETE",
        "hc_early_eos": bool(label == "EARLY_EOS" and diag["text_coverage_ratio"] <= 0.85 and diag["trailing_deleted_words"] >= 10),
    }


def aggregate_sources(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    paths = [dict(row) for row in rows]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in paths:
        grouped[str(row["source_id"])].append(row)
    sources = []
    for source_id, values in sorted(grouped.items()):
        values.sort(key=lambda row: int(row["seed"]))
        sources.append({
            "source_id": source_id,
            "path_count": len(values),
            "strict_complete": float(np.mean([row["classification"] == "COMPLETE" for row in values])),
            "any_incomplete": bool(any(row["classification"] != "COMPLETE" for row in values)),
            "hc_early_eos": bool(any(row["hc_early_eos"] for row in values)),
            "wer": float(np.mean([row["wer"] for row in values])),
            "coverage": float(np.mean([row["text_coverage_ratio"] for row in values])),
            "non_tail_error_rate": float(np.mean([row["non_tail_error_rate"] for row in values])),
        })
    counts = Counter(row["classification"] for row in paths)
    return {
        "path_count": len(paths),
        "source_count": len(sources),
        "classification_counts": dict(counts),
        "source_metrics": {
            "strict_complete_rate": float(np.mean([row["strict_complete"] for row in sources])),
            "hc_early_eos_any_seed_rate": float(np.mean([row["hc_early_eos"] for row in sources])),
            "wer": float(np.mean([row["wer"] for row in sources])),
            "coverage": float(np.mean([row["coverage"] for row in sources])),
        },
        "source_rows": sources,
    }


def bootstrap_differences(differences: Sequence[float], seed: int = 20260820, resamples: int = 10000) -> dict[str, Any]:
    values = np.asarray(differences, dtype=np.float64)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("differences must be a non-empty one-dimensional vector")
    rng = np.random.default_rng(int(seed))
    sampled = values[rng.integers(0, len(values), size=(int(resamples), len(values)))].mean(axis=1)
    return {
        "source_count": int(len(values)),
        "point_estimate": float(values.mean()),
        "bootstrap_resamples": int(resamples),
        "bootstrap_seed": int(seed),
        "ci95": [float(np.quantile(sampled, 0.025)), float(np.quantile(sampled, 0.975))],
    }


def paired_bootstrap(
    left_paths: Iterable[Mapping[str, Any]],
    right_paths: Iterable[Mapping[str, Any]],
    metric: str = "strict_complete",
    seed: int = 20260820,
    resamples: int = 10000,
) -> dict[str, Any]:
    """Aggregate inference seeds within source, then resample paired sources."""
    left = {row["source_id"]: row for row in aggregate_sources(left_paths)["source_rows"]}
    right = {row["source_id"]: row for row in aggregate_sources(right_paths)["source_rows"]}
    if set(left) != set(right):
        raise ValueError("paired source identities differ")
    differences = [float(left[source][metric]) - float(right[source][metric]) for source in sorted(left)]
    return {"metric": metric, **bootstrap_differences(differences, seed=seed, resamples=resamples)}
