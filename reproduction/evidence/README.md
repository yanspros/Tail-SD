# Evidence for the Tail-SD ICASSP submission

Release date: 2026-09-24. Authors: Yanliang Li, Dejun Zhang, and Lei Zhang (YiXin-AILab, YIXIN). This deposit supports the current manuscript, *Tail-Focused Self-Distillation: Supervision Placement for Improving Completion in Autoregressive Text-to-Speech*. The manuscript is a submission, not a claim of acceptance.

## Start here

The [release index](source_data/index.json) binds each published file to its original SHA256 and records the public SHA256. The [checksum list](source_data/SHA256SUMS) verifies released bytes. Private absolute paths were redacted in machine JSON; all numeric and boolean leaves were preserved. The separately frozen Windows human files were copied byte-for-byte. Original protocols and historical gates are evidence records, not a new certification by the release script.

| Manuscript result | Released evidence |
| --- | --- |
| Table I: original CV3 panel and dense reference | [CV3 summaries, paired differences, protocol, label budgets](source_data/machine/prior_final_evidence_20260917/cv3_primary/) |
| Table II: new-text matched placement | [Primary summary](source_data/machine/prior_final_evidence_20260917/e13_unopened500/primary_placement_summary.json), [six paired units](source_data/machine/prior_final_evidence_20260917/e13_unopened500/pairwise_units.json), [protocol and identity audits](source_data/machine/prior_final_evidence_20260917/e13_unopened500/) |
| Table III: deterministic position controls | [Primary and component contrasts](source_data/machine/prior_final_evidence_20260917/e14_position_study/primary_position_summary.json), [masks and matching audit](source_data/machine/prior_final_evidence_20260917/e14_position_study/) |
| Table IV: budget sensitivity | [Budget summaries, paired units, system outputs and matching audit](source_data/machine/e16_budget_sensitivity/) |
| Table V: CV2 transfer | [CV2 summaries, paired intervals, bank/training audit](source_data/machine/prior_final_evidence_20260917/cv2_transfer/) |
| Section 3.5: capability retention | [Summary](source_data/capability/capability_summary.json), [archived gate](source_data/capability/capability_gate.json) |
| Table VI: descriptive human evaluation | [Human evidence](source_data/human/) and the data dictionary below |
| Supporting masks, length subgroups, E15 limitations | [Mask repeats](source_data/machine/prior_final_evidence_20260917/random_pr_masks/), [length/auxiliary metrics and E15 audit](source_data/machine/mechanism_and_length_handoff/) |

The six new-text comparisons use two Tail-SD checkpoints and three random masks per initialization, not six independent Tail-SD models. E14 and E16 reuse that opened panel post hoc. CV2 reuses the original CV3 evaluation panel with its own training bank. Full-SD is a dense reference, not an equivalence result or a 100%-tail budget point. E15 remains diagnostic only.

## Human evaluation

- [raw_log.csv](source_data/human/raw_log.csv): 6,000 de-identified listener/source/system rows; 10 listeners, 120 sources, five systems, 1,200 ratings per system.
- [platform_annotation_protocol.md](source_data/human/platform_annotation_protocol.md): platform and rating protocol.
- [source_manifest_120.csv](source_data/human/source_manifest_120.csv): source/bin metadata.
- [source_system_audio_seed_map.csv](source_data/human/source_system_audio_seed_map.csv): 600 stimulus mappings, inference seed 0, recorded audio hashes and configuration metadata. File paths are historical locators, not downloadable audio.
- [platform_summary_export.csv](source_data/human/platform_summary_export.csv): raw-derived totals and means used for Table VI.
- [platform_summary_export_original.csv](source_data/human/platform_summary_export_original.csv): earlier platform export, retained for provenance; it is not the final table authority.
- [summary.json](source_data/human/summary.json): checked integer sums and explicit paper rounding.
- [aggregation_script.py](source_data/human/aggregation_script.py): archived aggregation implementation; running it writes its derived outputs in the working directory. The read-only verification command below is preferred for checking this deposit.
- [authority_provenance.md](source_data/human/authority_provenance.md): distinction between original export and raw-derived authority.

| Raw column | Meaning | Values |
| --- | --- | --- |
| listener_id | De-identified participant code | L01–L10; no identity key included |
| source_id | Study source identifier | S001–S120 |
| system | CV3 synthesis system | Base, Full-SD, Random-Local, Tail-30, Tail-SD |
| completion | No obvious omission/truncation | 0/1 |
| major_error | Major content error | 0/1 |
| mos | Naturalness rating | Integers 1–5 |

Aggregates are pooled rating proportions and arithmetic MOS. Ratings sharing a listener/source are not independent statistical replicates; no human significance test or new CI is introduced. The source-derived counts are 838 Tail-SD completion ratings and 178 Random-Local major-error ratings, matching 69.8% and 14.8% in the manuscript after rounding.

Checks verify row counts, keys, sums, labels, and recorded identities. They do not independently authenticate platform sessions or audio. Audio, participant contact/identity mappings, presentation-order/session logs, and quality-control event logs are not included. Protocol descriptions must not be mistaken for raw execution logs. Human–new-text separation in the archived amendment is provenance-level, not a newly performed per-source overlap check.

## Verification and provenance

From the repository root:

```bash
python scripts/verify_submission_evidence.py
```

To reproduce the export from the author's local frozen packages:

```bash
python scripts/export_submission_evidence.py \
  --evidence-package /path/to/TailSD_ICASSP2027_FinalEvidence_20260918 \
  --human-package /path/to/Human_Evaluation \
  --capability-package /path/to/Evidence_v2 \
  --output reproduction/evidence/source_data
```

This is a deterministic file export and consistency check, not model evaluation, ASR, or bootstrap. Original hashes and embedded payload hashes refer to original source bytes; public hashes refer to published copies. Source-relative paths and JSON pointers remain locators; some point to unbundled original artifacts. Files marked NOT_IMPORTED for human data inside the unchanged historical machine package retain their historical scope; the separate Windows package above governs Table VI.

The repository-wide `audits/SHA256SUMS` checks the current Git-tracked file bytes (excluding itself). Text uses LF line endings; deposited source files retain their original bytes. Its prior snapshot is retained as `audits/SHA256SUMS.historical_pre20260924`. Historical experiment gates and audit reports are not rewritten by this release.

## Access, reuse and scope

These files are publicly accessible in this repository; use a commit-specific GitHub URL when citing this version. No DOI, IRB approval, or new data license is asserted. See [LICENSE_NOTICE.md](../../LICENSE_NOTICE.md): the owner has not selected an open reuse license. Model weights, checkpoints, generated audio, LibriTTS audio, Wikipedia reference text, and participant identity/contact mappings are not distributed. Obtain third-party assets through their official sources and terms.

The deposit permits inspection of frozen outputs, matching contracts, and human aggregates. It is not a claim that every raw execution artifact or trained model is public, or that a reviewer cannot raise substantive questions.
