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
- **E14 Position Controls**: Post-hoc comparison of Head, Middle, and Tail supervision on the opened E13 panel. The primary pre-registered contrast is Tail minus NonTerminal (+12.98 pp [10.95, 15.03]).
- **E16 Budget Sensitivity**: Post-hoc sensitivity across 0.5× (13.0%), 1.0× (25.9%), and 2.0× (51.8%) active label budgets.
- **CosyVoice2 Replication**: Uses an independently constructed E08 training bank, evaluated on the shared/open CV3 E11 500-source panel. It is not an independent second test set.
- **Scope**: Both tested backbones are in the CosyVoice family; broader architectures and languages remain untested.
- **Longest Requests**: Sequences beyond 100 words experience substantial completion degradation; the 160–180 word bin remains unreliable across all models (~1% completion).

Tail-SD used 25.9% as many active CE labels as Full-SD in the CV3 formal bank. This describes supervision-label participation only; it is not a FLOPs, compute, memory, or wall-clock saving.

## Identity Discipline

Freeze and record hashes for the base model, source manifest, prompt binding, target bank, masks, LoRA initialization, record order, checkpoints, and scoring inputs. Compared systems should differ only in the declared experimental factor. Inference seeds belonging to one source remain in the same bootstrap cluster.

The private paper evidence package is represented in `reproduction/paper_results.json` by the SHA-256 digest of `paper_numbers_20260918.json`.
