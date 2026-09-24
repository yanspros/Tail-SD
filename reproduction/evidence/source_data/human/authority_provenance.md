Authority Chain and Data Provenance

- `raw_log.csv` is the sole raw-derived authority for human evaluation.
- `platform_summary_export.csv` is regenerated strictly from `raw_log.csv`.
- `platform_summary_export_original.csv` is retained only for provenance and audit purposes.
- The original platform-side export contained minor numerical discrepancies (e.g., 1 count difference in Tail-SD completion, floating point MOS sums). These stem from platform-side rounding/weighting and do not affect the rounded Table VI values.
- The paper's Table VI is computed strictly from `raw_log.csv`.
