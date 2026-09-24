# Tail-SD: Terminal-Span Supervision for AR-TTS Trajectory Completion

Tail-SD is a supervision-placement method for autoregressive text-to-speech (AR-TTS). During teacher-forced training, it retains the complete successful speech trajectory in the causal self-attention forward pass, but applies direct cross-entropy (CE) supervision only to a fixed terminal speech span.

The central research question is **supervision placement**: with the speech trajectory, training budget, and normalization held fixed, does supervising the terminal speech span improve sequence completion over supervising a matched random span?

---

## Core Empirical Findings (ICASSP 2027)

1. **New-Text Confirmatory Experiment (Fun-CosyVoice3-0.5B)**:
   In prospective confirmatory testing on 500 previously unopened text sources across six paired contrasts, Tail-SD achieves a **+4.70 percentage point** completion gain over per-record-matched Random-PR (95% CI: **[3.20, 6.22]**). All six paired units are positive.
2. **Original 500-Source Panel**:
   On the original panel, strict trajectory completion improves from **57.0%** (Base) to **68.2%** (Tail-SD). Tail-SD uses **25.9%** as many active CE labels as Full-SD.  
   *Note*: The paired comparison with Full-SD is **+0.40 pp** (95% CI: **[-1.90, +2.70]**), which did not establish a difference. The paper does **not** claim that Tail-SD outperforms Full-SD.
3. **Cross-Backbone Replication (CosyVoice2-0.5B)**:
   Using CosyVoice2's own independently constructed target bank on the original panel, the terminal placement advantage replicates: Tail-SD exceeds Random-PR by **+2.90 pp** (95% CI: **[0.80, 5.10]**).
4. **Primary Research Conclusion**:
   Under a matched supervision budget, **direct supervision placement significantly impacts AR-TTS sequence completion**. Terminal placement consistently outperforms random and deterministic non-terminal placement.

### Explicit Scope and Non-Claims
To prevent scientific over-generalization, the paper explicitly notes:
- **No claim of universal superiority**: Tested on two CosyVoice backbones in English; not evaluated across all AR-TTS architectures or languages.
- **No training compute reduction**: All tokens remain in the teacher-forced causal history; active label ratios reflect loss masking only, not FLOPs, memory, or wall-clock savings.
- **No inference compute reduction**: Autoregressive decoding complexity is identical.
- **Not a Full-SD replacement**: Full-SD is retained as a dense-supervision reference; no equivalence or superiority is established.
- **Not general SOTA**: Tail-SD specifically targets trajectory completion failure; longest inputs (160–180 words) remain difficult across all methods.

See [`reproduction/PAPER_RESULTS.md`](reproduction/PAPER_RESULTS.md) for full experimental tables, including position controls, budget controls, and length breakdowns.

---

## Method at a Glance

```text
scored self-generated trajectories
        -> deterministic target bank
        -> Tail-SD / matched Random-PR / Full-SD label manifests
        -> external CosyVoice adapter + shared LoRA initialization
        -> frozen inference grid
        -> SC/WER/coverage + source-level paired bootstrap
```

For a target containing $T_i$ speech tokens, Tail-SD uses a branch-specific fixed ratio and deterministic residual allocation to obtain $K_i$. Termination records supervise the last $K_i$ speech labels plus EOS; Content records supervise the last $K_i$ speech labels and exclude EOS. Masked prefix labels do not enter CE loss, but their tokens remain in the causal history and are not detached.

Random-PR copies each record's $K_i$, EOS/special positions, CE denominator $M_i$, target tokens, and complete history. Its only change is one uniformly sampled same-length contiguous speech span. Natural overlap with the tail, including an exact match, is accepted without redraw.

---

## Installation

Python 3.10 or newer is required.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
pytest
```

The core mask and metric utilities require only NumPy and PyYAML. LoRA training helpers additionally require PyTorch. Install a compatible official CosyVoice checkout and checkpoint separately; this repository does not redistribute proprietary model weights.

---

## Prepare a Base Model

Set the model and prompt roots through environment variables or edit a configuration file:

```bash
export COSYVOICE3_MODEL_DIR=/path/to/cosyvoice3-model
export TAILSD_PROMPT_AUDIO_ROOT=/path/to/authorized/prompts
```

CosyVoice3 and CosyVoice2 use separate configuration files because their EOS and sampling interfaces differ. Do not substitute one backbone's inference contract for the other.

---

## Manifest Format

See [`docs/data_format.md`](docs/data_format.md) and [`examples/example_manifest.json`](examples/example_manifest.json). The example uses placeholder paths and synthetic identities; users must supply properly licensed text and prompt audio.

---

## Build a Target Bank

The builder consumes previously generated and scored natural/continuation manifests; it does not synthesize audio or run ASR:

```bash
python scripts/build_target_bank.py \
  --natural /path/to/natural_scored.json \
  --continuations /path/to/continuations_scored.json \
  --wer-max 0.12586206896551724 \
  --non-tail-max 0.12586206896551724 \
  --output outputs/target_bank.json
```

Thresholds above reproduce the paper configuration; new datasets require a prospectively defined calibration protocol.

---

## Build Tail-SD, Random-PR and Full-SD Labels

```bash
python scripts/build_masks.py \
  --bank outputs/target_bank.json \
  --output-dir outputs/masks \
  --termination-ratio 0.21705160991522524 \
  --content-ratio 0.29909295294208854 \
  --random-pr-seed 20260912
```

The emitted JSON files are immutable inputs to training. Random-PR is sampled once during construction and is never redrawn during training.

---

## LoRA Training

The repository provides backbone-neutral masked-CE and LoRA helpers, plus a CLI that calls a user-supplied official-model adapter:

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

The adapter must use official frontend/model APIs, load one frozen LoRA initialization for all compared arms, preserve record order, and save final checkpoint identities. No CosyVoice code is vendored here.

---

## Inference and Completion Evaluation

`tailsd.inference` defines the source × system × seed grid and validates completed artifacts. Model execution remains the responsibility of an external official-model adapter. After ASR, evaluate frozen transcripts with:

```bash
python scripts/evaluate.py \
  --input /path/to/transcripts.json \
  --left Tail-SD --right Random-PR \
  --output outputs/evaluation.json
```

Strict Completion (SC) requires real EOS emission, no length-cap truncation, phoneme/word coverage $\ge 0.95$, and zero trailing deletions. The paired bootstrap first aggregates inference seeds within each source and then resamples sources.

---

## Paper Reproduction and Results

All formal numerical results, configuration snapshots, and evidence digests are organized in [`reproduction/`](reproduction/):

- [`reproduction/PAPER_RESULTS.md`](reproduction/PAPER_RESULTS.md): Complete human-readable breakdown of the main result map, new-text confirmatory test, length stratification, position controls, budget controls, and Full-SD reference.
- [`reproduction/paper_results.json`](reproduction/paper_results.json): Consolidated machine-readable dataset generated directly from the frozen private evidence authority (`TailSD_ICASSP2027_FinalEvidence_20260918`).
- [`reproduction/evidence/`](reproduction/evidence/): Public JSON summaries for table values, length bins, auxiliary metrics, and budget controls.

To re-synchronize results against an authorized evidence package:

```bash
PYTHONPATH=. python scripts/sync_paper_results.py \
  --evidence-package /path/to/TailSD_ICASSP2027_FinalEvidence_20260918 \
  --output reproduction/paper_results.json \
  --evidence-dir reproduction/evidence
```

---

## Citation

See [`CITATION.cff`](CITATION.cff). Please cite the accompanying ICASSP 2027 paper when using this method or codebase.
