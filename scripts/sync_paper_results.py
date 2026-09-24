#!/usr/bin/env python3
"""Generate the small public paper-results snapshot from a private evidence package."""
from __future__ import annotations

import argparse
from pathlib import Path

from tailsd.io import dump_json, file_sha256, load_json


def redact(value):
    """Redact private server file paths while retaining JSON pointers, status, and hashes."""
    if isinstance(value, dict):
        new_dict = {}
        for k, v in value.items():
            if k in ("source_file", "source_path"):
                new_dict[k] = "Internal evidence path retained privately"
            elif k in ("file", "files") and isinstance(v, (str, list)):
                new_dict[k] = (
                    "Internal evidence path retained privately"
                    if isinstance(v, str)
                    else ["Internal evidence path retained privately"] * len(v)
                )
            else:
                new_dict[k] = redact(v)
        return new_dict
    elif isinstance(value, list):
        return [redact(item) for item in value]
    elif isinstance(value, str) and (value.startswith("phases/") or value.startswith("/gpfs01/")):
        return "Internal evidence path retained privately"
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-package", required=True, help="Path to evidence package directory")
    parser.add_argument("--output", required=True, help="Output path for paper_results.json")
    parser.add_argument("--evidence-dir", help="Optional directory to export public evidence JSON summaries")
    parser.add_argument("--human-summary", help="Checked Windows human-rating summary; imported separately from machine evidence")
    args = parser.parse_args()

    pkg = Path(args.evidence_package)
    if pkg.is_dir():
        candidates = [
            pkg / "paper_numbers_20260918.json",
            pkg / "paper_numbers.json",
        ]
        source = next((c for c in candidates if c.exists()), None)
        if source is None:
            raise FileNotFoundError(f"Could not find paper_numbers.json in {pkg}")
    else:
        source = pkg
        pkg = source.parent

    data = load_json(source)
    allowed_keys = (
        "cv3_primary",
        "random_pr_masks",
        "cv2_transfer",
        "e13_unopened500",
        "e14_position_study",
        "e16_budget_sensitivity",
        "e15_mechanism_diagnostic",
        "authority_precedence",
        "excluded_deprecated_statistics",
    )
    allowed = {key: data[key] for key in allowed_keys if key in data}

    # Ingest length bins and aux metrics if available in mechanism_and_length_handoff
    handoff_dir = pkg / "mechanism_and_length_handoff"
    if (handoff_dir / "e13_length_bin_placement.json").exists():
        allowed["e13_length_bins"] = load_json(handoff_dir / "e13_length_bin_placement.json")
    if (handoff_dir / "e13_e14_aux_metrics.json").exists():
        allowed["e13_e14_aux_metrics"] = load_json(handoff_dir / "e13_e14_aux_metrics.json")

    public = {
        "schema_version": 2,
        "status": "GENERATED_FROM_FROZEN_PRIVATE_EVIDENCE",
        "document_gate": data.get("document_gate", "PAPER_EVIDENCE_PACKAGE_TAILSD_ICASSP2027_20260918_FROZEN"),
        "private_evidence_paper_numbers_sha256": file_sha256(source),
        "results": redact(allowed),
        "deprecated_statistics_included": False,
        "human_evaluation": {
            "status": "EXTERNAL_WINDOWS_AUTHORITY_NOT_IMPORTED",
            "scope": (
                "Descriptive Completion, Major Error and 1-5 naturalness MOS cover the original five systems on CV3 "
                "(Base, Full-SD, Random-Local, Tail-30, Tail-SD); it does not cover the E13 "
                "new-text Tail-SD vs Random-PR comparison."
            ),
        },
    }
    if args.human_summary:
        human = load_json(args.human_summary)
        if human.get("status") != "DESCRIPTIVE_EXPORT_CHECKED":
            raise ValueError("Expected a checked descriptive human summary")
        public["human_evaluation"] = human
    dump_json(args.output, public)
    print(f"Wrote synchronized results to {args.output}")

    if args.evidence_dir:
        ev_dir = Path(args.evidence_dir)
        ev_dir.mkdir(parents=True, exist_ok=True)
        # Export sanitized table values
        if (pkg / "table_values_20260918.json").exists():
            dump_json(ev_dir / "table_values.json", redact(load_json(pkg / "table_values_20260918.json")))
            print(f"Exported {ev_dir / 'table_values.json'}")
        if (pkg / "claim_to_evidence_20260918.json").exists():
            dump_json(ev_dir / "claim_to_evidence.json", redact(load_json(pkg / "claim_to_evidence_20260918.json")))
            print(f"Exported {ev_dir / 'claim_to_evidence.json'}")
        if (handoff_dir / "e13_length_bin_placement.json").exists():
            dump_json(ev_dir / "e13_length_bins.json", redact(load_json(handoff_dir / "e13_length_bin_placement.json")))
            print(f"Exported {ev_dir / 'e13_length_bins.json'}")
        if (handoff_dir / "e13_e14_aux_metrics.json").exists():
            dump_json(ev_dir / "e13_e14_aux_metrics.json", redact(load_json(handoff_dir / "e13_e14_aux_metrics.json")))
            print(f"Exported {ev_dir / 'e13_e14_aux_metrics.json'}")
        if (pkg / "e16_paper_handoff.json").exists():
            dump_json(ev_dir / "e16_budget_sensitivity.json", redact(load_json(pkg / "e16_paper_handoff.json")))
            print(f"Exported {ev_dir / 'e16_budget_sensitivity.json'}")


if __name__ == "__main__":
    main()
