#!/usr/bin/env python3
"""Generate the small public paper-results snapshot from a private evidence package."""
from __future__ import annotations

import argparse
from pathlib import Path

from tailsd.io import dump_json, file_sha256, load_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-package", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--markdown-output", help="optional generated human-readable result summary")
    args = parser.parse_args()
    source = Path(args.evidence_package) / "paper_numbers.json"
    data = load_json(source)
    allowed = {
        key: data[key]
        for key in ("cv3_primary", "random_pr_original", "random_pr_mask_repeats", "cv2_transfer")
        if key in data
    }
    # Remove private provenance paths while retaining the private authority digest.
    def redact(value):
        if isinstance(value, dict):
            return {key: redact(item) for key, item in value.items() if key not in {"source_file"}}
        if isinstance(value, list):
            return [redact(item) for item in value]
        return value
    public = {
        "schema_version": 1,
        "status": "GENERATED_FROM_FROZEN_PRIVATE_EVIDENCE",
        "private_evidence_paper_numbers_sha256": file_sha256(source),
        "results": redact(allowed),
        "deprecated_statistics_included": False,
        "human_evaluation": {"status": "NOT_INCLUDED_SERVER_AUTHORITY_IS_LOCAL_TO_PAPER_WORKSTATION"},
    }
    dump_json(args.output, public)
    if args.markdown_output:
        cv3 = allowed["cv3_primary"]
        cv2 = allowed["cv2_transfer"]
        repeat = allowed["random_pr_mask_repeats"]["new_M1_M2_primary_summary"]["value"]

        def sc(system):
            return 100 * cv3["systems"][system]["strict_completion"]["value"]

        def comparison(name):
            value = cv3["comparisons"][name]["value"]
            return f"{value['delta_pp']:+.2f} pp [{value['ci95_pp'][0]:+.2f}, {value['ci95_pp'][1]:+.2f}]"

        cv2_primary = cv2["comparisons"]["primary_tail_sd_minus_random_pr"]["value"]
        lines = [
            "# Generated paper-result snapshot",
            "",
            "> Generated from the frozen private evidence authority; do not edit by hand.",
            "",
            "## CV3 strict completion",
            "",
            "| System | SC |",
            "| --- | ---: |",
            *[f"| {name} | {sc(name):.1f}% |" for name in ("Base", "Full-SD", "Random-Local", "Tail-30", "Tail-SD")],
            "",
            "- Tail-SD - Base: " + comparison("tail_vs_base"),
            "- Tail-SD - Random-Local: " + comparison("tail_vs_random_local"),
            "- Tail-SD - Full-SD: " + comparison("tail_vs_full_sd") + "; paired comparison did not establish a difference.",
            "- Tail-SD - Tail-30: " + comparison("tail_vs_tail30"),
            "",
            "## Per-record Random-PR controls",
            "",
            f"- Additional M1/M2 masks x paired initializations: {100*repeat['point_estimate']:+.2f} pp "
            f"[{100*repeat['ci95'][0]:+.2f}, {100*repeat['ci95'][1]:+.2f}].",
            "- This is finite sensitivity analysis over fixed masks, not a population-level mask-uncertainty claim.",
            "",
            "## CosyVoice2 transfer on the shared/open E11 panel",
            "",
            "| System | SC |",
            "| --- | ---: |",
            *[f"| {name} | {100*cv2['systems'][name]['value']['strict_complete_rate']:.1f}% |" for name in ("Base", "Full-SD", "Random-PR", "Tail-SD")],
            "",
            f"- Primary Tail-SD - Random-PR: {cv2_primary['delta_sc_percentage_points']:+.2f} pp "
            f"[{cv2_primary['ci95_percentage_points'][0]:+.2f}, {cv2_primary['ci95_percentage_points'][1]:+.2f}].",
            "",
            "Active CE-label participation is not a FLOPs, compute or training-time saving.",
            "",
        ]
        target = Path(args.markdown_output)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text("\n".join(lines), encoding="utf-8")
        temporary.replace(target)


if __name__ == "__main__":
    main()
