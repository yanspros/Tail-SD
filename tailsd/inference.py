"""Manifest helpers for reproducible, backend-owned inference.

No third-party model is bundled. The official CosyVoice repository remains
responsible for frontend normalization, prompt extraction and waveform decode.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping


def build_path_grid(sources: Iterable[Mapping[str, Any]], systems: Iterable[str], seeds: Iterable[int]) -> list[dict[str, Any]]:
    rows = []
    for system in systems:
        for source in sources:
            for seed in seeds:
                source_id = str(source["source_id"])
                rows.append({
                    "path_id": f"{system}__{source_id}__seed{int(seed)}",
                    "system": str(system),
                    "source_id": source_id,
                    "seed": int(seed),
                    "text": source["text"],
                    "prompt_audio_path": source["prompt_audio_path"],
                    "status": "PENDING",
                })
    if len({row["path_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate inference path identity")
    return rows


def validate_generation_record(row: Mapping[str, Any]) -> None:
    required = ("path_id", "system", "source_id", "seed", "eos_generated", "cap_hit", "audio_path")
    missing = [key for key in required if key not in row]
    if missing:
        raise ValueError(f"generation record missing fields: {missing}")
    if row.get("status") != "COMPLETE_VERIFIED":
        raise ValueError("only COMPLETE_VERIFIED artifacts may enter scoring")


class BackendContract:
    """Documentation-only interface expected from a model adapter."""

    def generate(self, *, text: str, prompt_audio_path: str, seed: int, config: Mapping[str, Any]) -> Mapping[str, Any]:  # pragma: no cover
        raise NotImplementedError
