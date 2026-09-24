# Paper Reproduction and Results Snapshot

This directory contains the frozen results, reproduction configs, and public evidence corresponding to the ICASSP 2027 submission. Start with the [source-evidence guide](evidence/README.md) for result/protocol JSON, matching audits, capability support, and the separately frozen human-rating records.

- **Human-Readable Results Summary**: [`PAPER_RESULTS.md`](PAPER_RESULTS.md) provides the complete report across Fun-CosyVoice3-0.5B and CosyVoice2-0.5B (including E13 confirmatory test, length bins, E14 position controls, E16 budget controls, Full-SD reference, and diagnostics).
- **Consolidated Machine-Readable Results**: [`paper_results.json`](paper_results.json) contains all formal metrics and statistics generated from the frozen evidence authority with internal server paths redacted.
- **Structured Evidence Summaries**: The [`evidence/`](evidence/) directory contains component-level JSON summaries:
  - [`evidence/table_values.json`](evidence/table_values.json): Table values for main contrasts.
  - [`evidence/e13_length_bins.json`](evidence/e13_length_bins.json): Complete ten-bin length breakdown.
  - [`evidence/e13_e14_aux_metrics.json`](evidence/e13_e14_aux_metrics.json): Auxiliary WER, coverage, and halting rates.
  - [`evidence/e16_budget_sensitivity.json`](evidence/e16_budget_sensitivity.json): Detailed budget sensitivity across 0.5×, 1.0×, and 2.0×.
  - [`evidence/claim_to_evidence.json`](evidence/claim_to_evidence.json): Formal mapping from paper claims to underlying evidence.

The YAML files record the exact hyperparameters and evaluation settings needed to understand the experiments without bundling private checkpoints, raw audio, or internal test manifests.

To refresh against an authorized evidence package:

```bash
PYTHONPATH=. python scripts/sync_paper_results.py \
  --evidence-package /path/to/TailSD_ICASSP2027_FinalEvidence_20260918 \
  --output reproduction/paper_results.json \
  --evidence-dir reproduction/evidence \
  --human-summary reproduction/evidence/source_data/human/summary.json
```
