# Reproducibility notes

## What is included

This candidate includes deterministic target-selection utilities, Tail-SD and
Random-PR mask construction, dense Full-SD labels, masked-CE helpers,
completion diagnostics and source-clustered paired bootstrap. Unit tests cover
the paper's core contracts without downloading a model.

## What users must provide

- A compatible official CosyVoice checkout and legally obtained checkpoint.
- Legally obtained text and prompt audio.
- An adapter implementing the official frontend, target loading, training,
  speech-token decoding and checkpoint save/reload operations.
- Whisper or another explicitly fixed ASR installation when reproducing the
  paper evaluator.

Third-party weights, corpora, audio and FST resources are intentionally absent.

## Paper experiment boundary

- CV3 primary experiments compare Tail-SD with Base, Full-SD, Random-Local and
  Tail-30 under frozen protocols.
- Random-PR matches Tail-SD per record in `K_i`, EOS/special positions, CE
  denominator and complete target/history.
- Mask-realization repeats cover the original mask and two additional frozen
  masks across two paired initializations. This is finite sensitivity analysis,
  not uncertainty over every possible random mask.
- CosyVoice2 uses an independently constructed E08 training bank, while its
  evaluation reuses the shared/open CV3 E11 500-source panel. It is not a second
  untouched test set.
- Both tested backbones are in the CosyVoice family; broader architectures and
  languages remain untested.
- The longest tested requests remain unreliable.

Tail-SD used about 25.9% as many active CE labels as Full-SD in the CV3 formal
bank. This describes supervision-label participation only; it is not a FLOPs,
compute or wall-clock saving.

## Identity discipline

Freeze and record hashes for the base model, source manifest, prompt binding,
target bank, masks, LoRA initialization, record order, checkpoints and scoring
inputs. Compared systems should differ only in the declared experimental
factor. Inference seeds belonging to one source remain in the same bootstrap
cluster.

The private paper evidence package is represented in
`reproduction/paper_results.json` by the SHA-256 of its `paper_numbers.json`.
Large formal assets are not distributed.
