# Reproducibility Notes

## What is Included

This repository includes deterministic target-selection utilities, Tail-SD and Random-PR mask construction, dense Full-SD labels, masked-CE loss and LoRA training helpers, sequence completion metrics, and source-clustered paired bootstrap testing. Unit tests cover the core mathematical and algorithmic contracts without downloading model weights.

## What Users Must Provide

- A compatible official CosyVoice checkout and checkpoint.
- Text and prompt audio assets.
- An adapter implementing the official frontend, target loading, training, speech-token decoding, and checkpoint save/reload operations.
- OpenAI Whisper or an explicitly fixed ASR installation when reproducing the paper evaluator.

Third-party model weights, audio corpora, and FST assets are intentionally absent.

## Paper Experiment Boundaries

- **CV3 Primary Panel**: Compares Tail-SD against Base, Full-SD, Random-Local, and Tail-30 under frozen protocols.
- **Random-PR Matching**: Matches Tail-SD per record in $K_i$, EOS/special token positions, CE denominator, and complete causal history.
- **E13 Confirmatory Test**: 500 new unopened texts across six paired contrasts between Tail-SD and matched Random-PR (+4.70 pp [3.20, 6.22]).
- **E14 Position Controls**: Post-hoc comparison of Head, Middle, and Tail supervision on the opened E13 panel. The prespecified primary contrast within this post-hoc study is Tail minus NonTerminal (+12.98 pp [10.95, 15.03]).
- **E16 Budget Sensitivity**: Post-hoc sensitivity across 0.5× (13.0%), 1.0× (25.9%), and 2.0× (51.8%) active label budgets.
- **CosyVoice2 Replication**: Uses an independently constructed E08 training bank, evaluated on the shared/open CV3 E11 500-source panel. It is not an independent second test set.
- **Scope**: Both tested backbones are in the CosyVoice family; broader architectures and languages remain untested.
- **Longest Requests**: Sequences beyond 100 words experience substantial completion degradation; the 160–180 word bin remains unreliable across all models (~1% completion).

Tail-SD used 25.9% as many active CE labels as Full-SD in the CV3 formal bank. This describes supervision-label participation only; it is not a FLOPs, compute, memory, or wall-clock saving.

## Identity Discipline

Freeze and record hashes for the base model, source manifest, prompt binding, target bank, masks, LoRA initialization, record order, checkpoints, and scoring inputs. Compared systems should differ only in the declared experimental factor. Inference seeds belonging to one source remain in the same bootstrap cluster.

The paper-evidence package is represented in `reproduction/paper_results.json` by the SHA-256 digest of `paper_numbers_20260918.json`. The [evidence guide](../reproduction/evidence/README.md) maps the released source outputs, protocols, and matching audits to manuscript tables. The release index records original and public SHA256 separately because absolute private paths are redacted; numeric and boolean values are unchanged.

## Human Evaluation

The separately maintained Windows package contains 6,000 de-identified ratings: ten listeners, 120 sources, five CV3 systems, and 1,200 ratings per system. Completion and Major Error are binary judgments; naturalness uses a 1–5 MOS scale. The platform protocol specifies visible reference text, system blinding, listener/source-specific randomized order, headphones, and quiet surroundings. Results are pooled within system and descriptive only; they do not directly validate the new-text Random-PR comparison.

The public files permit checking the complete rating grid, sums, rounded Table VI values, and recorded stimulus mapping. Audio, session timestamps, presentation-order logs, and participant identity/contact mappings are not included. This release does not independently verify listening sessions or audio identity. Original platform exports and raw-derived summaries remain distinct.

## Implementation Details

CV3 uses exact branch ratios 10779/49661 and 15432/51596, not the rounded 21.7%/29.9% display values. Per-record counts first take the floor; residual labels go one each to the earliest records in frozen within-branch order. CV2 reuses the ratios on its own bank and first floors each ratio-scaled branch total.

CV2 uses one paired LoRA initialization (seed 20260820), one Random-PR mask (seed 20260912) fixed for four training passes, and separate inference seeds 0/1. Native unsplit decoding uses top-k 25, speech/text-token ratio limits 2–20, and a 20n cap for n CV2 text tokens, with neither top-p nor temperature. CV3's decoder contract must not be substituted.

CV3's 58/65 target counts are the natural training-set yield after within-source/branch quality selection, without quota truncation. CV2 first selects eligible targets within source/branch, then globally ranks the branch pools to preset 58/65 quotas. These equal counts arise from different selection rules; see the deposited frozen protocols rather than treating the generic target-builder example as a turnkey experiment reproduction.
