# Tail-SD release candidate

Tail-SD is a supervision-placement method for autoregressive text-to-speech
(AR-TTS). It keeps the complete successful teacher-forced trajectory in the
causal forward pass, while applying direct cross-entropy (CE) only to a fixed
terminal speech span. The research question is placement: with supervision
quantity and trajectory held fixed, does the terminal span work better than a
matched random contiguous span?

This directory is a clean release candidate. It contains small method,
manifest, evaluation and testing utilities. It does **not** contain model
weights, audio, Wikipedia text, LibriTTS data, Whisper weights or WeText FST
assets. It has not been published, and the project license still needs an
owner decision; see [LICENSE_NOTICE.md](LICENSE_NOTICE.md).

## Method at a glance

```text
scored self-generated trajectories
        -> deterministic target bank
        -> Tail-SD / matched Random-PR / Full-SD label manifests
        -> external CosyVoice adapter + shared LoRA initialization
        -> frozen inference grid
        -> SC/WER/coverage + source-level paired bootstrap
```

For a target containing `T_i` speech tokens, Tail-SD uses a branch-specific
fixed ratio and deterministic residual allocation to obtain `K_i`. Termination
records supervise the last `K_i` speech labels plus EOS; Content records
supervise the last `K_i` speech labels and exclude EOS. Masked prefix labels do
not enter CE, but their tokens remain in the full causal history and are not
detached.

Random-PR copies each record's `K_i`, EOS/special positions, CE denominator
`M_i`, target and complete history. Its only change is one uniformly sampled
same-length contiguous speech span. Natural overlap with the tail, including
an exact match, is accepted without redraw.

## Installation

Python 3.10 or newer is required.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
pytest
```

The core mask and metric utilities need only NumPy and PyYAML. LoRA training
helpers additionally require PyTorch. Install a compatible official CosyVoice
checkout and checkpoint separately; this repository does not download them.

## Prepare a base model

Set the model and prompt roots through environment variables or edit a copied
configuration file:

```bash
export COSYVOICE3_MODEL_DIR=/path/to/cosyvoice3-model
export TAILSD_PROMPT_AUDIO_ROOT=/path/to/authorized/prompts
```

CosyVoice3 and CosyVoice2 use separate configuration files because their EOS
and sampling interfaces differ. Do not substitute one backbone's inference
contract for the other.

## Manifest format

See [docs/data_format.md](docs/data_format.md) and
[examples/example_manifest.json](examples/example_manifest.json). The example
uses placeholder paths and synthetic identities; users must supply properly
licensed text and prompt audio.

## Build a target bank

The builder consumes previously generated and scored natural/continuation
manifests; it does not synthesize or run ASR:

```bash
python scripts/build_target_bank.py \
  --natural /path/to/natural_scored.json \
  --continuations /path/to/continuations_scored.json \
  --wer-max 0.12586206896551724 \
  --non-tail-max 0.12586206896551724 \
  --output outputs/target_bank.json
```

Thresholds above reproduce one paper configuration; new datasets require a
prospectively defined calibration protocol rather than silently inheriting
them.

## Build Tail-SD, Random-PR and Full-SD labels

```bash
python scripts/build_masks.py \
  --bank outputs/target_bank.json \
  --output-dir outputs/masks \
  --termination-ratio 0.21705160991522524 \
  --content-ratio 0.29909295294208854 \
  --random-pr-seed 20260912
```

The emitted JSON files are immutable inputs to training. Random-PR is sampled
once during construction and is never redrawn during training.

## LoRA training

The release provides backbone-neutral masked-CE and LoRA helpers, plus a thin
CLI that calls a user-supplied official-model adapter:

```bash
python scripts/train.py --help
python scripts/train.py \
  --backend-factory my_adapter:create_backend \
  --bank outputs/target_bank.json \
  --mask outputs/masks/tail_sd_masks.json \
  --order /path/to/frozen_training_order.json \
  --config configs/cosyvoice3_tailsd.yaml \
  --output-dir outputs/tail_sd
```

The adapter must use the official frontend/model APIs, load one frozen LoRA
initialization for all compared arms, preserve record order and save final
checkpoint identities. No CosyVoice implementation is vendored here.

## Inference and completion evaluation

`tailsd.inference` defines the source × system × seed grid and validates
completed artifacts. Model execution remains the responsibility of an
external official-model adapter. After ASR, evaluate frozen transcripts with:

```bash
python scripts/evaluate.py \
  --input /path/to/transcripts.json \
  --left Tail-SD --right Random-PR \
  --output outputs/evaluation.json
```

Strict Completion (SC) requires real EOS, no cap hit, coverage at least 0.95,
and zero trailing deletions. The paired bootstrap first aggregates inference
seeds within each source and then resamples sources.

## Paper reproduction and results

Small, public-safe result/config snapshots are in [reproduction](reproduction/),
including the generated [paper result summary](reproduction/PAPER_RESULTS.md).
`reproduction/paper_results.json` is generated from the frozen private evidence
package by `scripts/sync_paper_results.py`; it is not hand-entered. Large formal
assets remain private and are represented only by an authority digest.

The central evidence concerns terminal placement versus matched random
placement. The Tail-SD versus Full-SD comparison is a dense-supervision
reference and did not establish a difference. Active CE-label participation is
not a FLOPs, compute-time or wall-clock saving claim.

## Scope

The evidence covers two CosyVoice-family AR-TTS backbones. Random-position
sensitivity was examined using two paired initializations and three fixed mask
realizations on CV3. The CV2 evaluation reused the shared/open E11 panel, not a
second untouched test set. Broader architectures and languages remain
untested, and the longest tested requests remain unreliable.

## Citation

See [CITATION.cff](CITATION.cff). Author list, paper identifier and publication
metadata are explicit TODOs and must be filled by the project owner before a
public release.

## Release status

This is a candidate for human review, not a public release. Review licensing,
authorship, third-party notices and the external model adapter before creating
a GitHub repository.
