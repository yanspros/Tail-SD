# Tail-SD: Official Paper Results and Reproduction Evidence (ICASSP 2027)

> **Authority Document**: `TailSD_ICASSP2027_FinalEvidence_20260918` (Frozen 2026-09-18).  
> **Machine-Readable Snapshot**: [`paper_results.json`](paper_results.json)  
> **Structured Public Evidence**: [`evidence/table_values.json`](evidence/table_values.json), [`evidence/e13_length_bins.json`](evidence/e13_length_bins.json), [`evidence/e13_e14_aux_metrics.json`](evidence/e13_e14_aux_metrics.json), [`evidence/e16_budget_sensitivity.json`](evidence/e16_budget_sensitivity.json), [`evidence/claim_to_evidence.json`](evidence/claim_to_evidence.json)  
> **Confidence Intervals**: Completion/placement intervals use 10,000 paired source-bootstrap resamples (seed `20260820`), retaining both inference seeds within source and conditional on the evaluated checkpoints/masks. Human evaluation is descriptive; the E15 diagnostic has the separate clustering limitation recorded below.

---

## 1. Main Result Map

The empirical evaluation of Tail-SD is structured into prospective confirmatory tests, cross-backbone replication, post-hoc controls, and diagnostics across Fun-CosyVoice3-0.5B (CV3) and CosyVoice2-0.5B (CV2). Readers do not need to decipher internal experiment IDs to navigate the evidence:

| Natural Language Title | Study Code | Backbone / Panel | Central Contrast / Scope | Primary Outcome | Status / Reference |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **New-Text Confirmatory Comparison** | `E13` | CV3 / Unopened 500-source panel | Tail-SD vs. matched Random-PR (6 paired units) | **+4.70 pp** [3.20, 6.22] | [Section 2](#2-e13--new-text-matched-random-pr-comparison) |
| **Length-Stratified Subgroups** | `E13-Length` | CV3 / 10 length bins (40–180 words) | Performance across sentence length tiers | +7.92 pp in 60–79w; drops to ~1% in 160–180w | [Section 3](#3-length-stratified-results) |
| **Position Controls (Head / Middle / Tail)** | `E14` | CV3 / Opened E13 panel | Tail-SD vs. Head-PR and Middle-PR | Primary (Tail − NonTerminal): **+12.98 pp** [10.95, 15.03] | [Section 4](#4-e14--position-controls-head-vs-middle-vs-tail) |
| **Supervision-Budget Controls** | `E16` | CV3 / Opened E13 panel | 0.5× (13.0%), 1.0× (25.9%), 2.0× (51.8%) budgets | +4.55 pp, +4.70 pp, +2.50 pp (advantage persists) | [Section 5](#5-e16--supervision-budget-controls) |
| **Dense-Supervision Reference** | `Full-SD Ref` | CV3 / Original 500-source panel | Tail-SD vs. Full-SD (dense labels) | **+0.40 pp** [-1.90, +2.70] (no difference established) | [Section 6](#6-full-sd-reference) |
| **Cross-Backbone Replication** | `CV2 Transfer` | CV2 / Shared E11 panel | Tail-SD vs. Random-PR with own E08 bank | **+2.90 pp** [0.80, 5.10] | [Section 7](#7-cosyvoice2-replication) |
| **Subjective Evaluation Scope** | `Human Eval` | CV3 / Original 5 systems | Completion, Major Error, and 1–5 naturalness MOS | Covers original 5 systems; does not cover E13 | [Section 8](#8-human-evaluation-scope) |
| **Mechanistic Diagnostic & Limitations** | `E15 / Limits` | CV3 / Opened E13 panel | Fixed-prefix EOS logit separation & boundaries | Diagnostic only; complete mechanism unproven | [Section 9](#9-diagnostics-and-limitations) |

---

## 2. E13 — New-Text Matched Random-PR Comparison

The primary confirmatory test of supervision placement was conducted on a prospectively frozen, unopened panel of **500 new text sources** sampled from English Wikipedia, using 2 independent inference seeds per source (1,000 total trajectories per system).

### Primary Placement Result

Under exact per-record matching—where each pair shares identical target speech tokens, causal history, active cross-entropy token count $K_i$, normalization denominator $M_i$, and EOS token supervision—terminal placement consistently outperforms random contiguous placement:

$$\text{Tail-SD} - \text{Random-PR} = \mathbf{+4.70\text{ percentage points}} \quad (95\%\text{ CI: } [3.20, 6.22])$$

All six of the pre-specified paired contrast units across two model initializations (`init20260822` and `init20260823`) and three independently drawn random mask sets (`M0`, `M1`, and `M2`) yielded strictly positive gains:

| Contrast Unit | Tail-SD Strict Completion | Random-PR Strict Completion | $\Delta$ Strict Completion (pp) | 95% Bootstrap CI (pp) |
| :--- | :---: | :---: | :---: | :---: |
| `Tail-SD (init 20260822) − Random-PR (M0, init 20260822)` | 67.3% | 61.8% | **+5.50 pp** | [+2.90, +8.20] |
| `Tail-SD (init 20260823) − Random-PR (M0, init 20260823)` | 67.0% | 62.7% | **+4.30 pp** | [+1.90, +6.70] |
| `Tail-SD (init 20260822) − Random-PR (M1, init 20260822)` | 67.3% | 64.7% | **+2.60 pp** | [+0.10, +5.20] |
| `Tail-SD (init 20260823) − Random-PR (M1, init 20260823)` | 67.0% | 63.4% | **+3.60 pp** | [+1.30, +5.90] |
| `Tail-SD (init 20260822) − Random-PR (M2, init 20260822)` | 67.3% | 60.2% | **+7.10 pp** | [+4.50, +9.80] |
| `Tail-SD (init 20260823) − Random-PR (M2, init 20260823)` | 67.0% | 61.9% | **+5.10 pp** | [+2.70, +7.50] |
| **Primary 6-Unit Source-Clustered Average** | **67.15%** | **62.45%** | **+4.70 pp** | **[+3.20, +6.22]** |

System-level baseline benchmarks on this panel:
- **Base (Pre-trained zero-shot)**: 55.5% strict completion
- **Full-SD (Dense supervision)**: 66.9% strict completion

### Descriptive Auxiliary Comparisons (WER and Coverage)

Completion gains accompany lower WER, higher word coverage, and lower HC point estimates in the existing ASR outputs; these auxiliary comparisons are descriptive:

| Metric | Tail-SD (Equal Weight) | Random-PR (Equal Weight) | Descriptive Difference ($\Delta$) | Direction |
| :--- | :---: | :---: | :---: | :--- |
| **Strict Completion (SC)** | 67.15% | 62.45% | **+4.70 pp** | Higher is better |
| **Word Error Rate (WER)** | 13.59% | 15.24% | **-1.65 pp** | Lower is better |
| **Word Coverage** | 92.19% | 89.81% | **+2.38 pp** | Higher is better |
| **Sources with Any-Seed High-Confidence Premature EOS (HC)** | 12.70% | 19.53% | **-6.83 pp** | Lower is better |

> **Important Note**: WER and coverage are descriptive secondary comparisons derived from the primary evaluation scoring pipeline. They do not constitute an independent second-ASR verification.

---

## 3. Length-Stratified Results

To evaluate performance across difficulty regimes without selection bias, the 500 sources in E13 are partitioned into **ten length bins** of 50 sources each (eight five-word bins from 40–79, plus 100–119 and 160–180 words). All ten bins are reported below, including negative, near-zero, and zero-crossing bins:

| Length Bin | Target Word Range | Base SC | Full-SD SC | Tail-SD Mean SC | Random-PR Mean SC | Tail − Random ($\Delta$) | Empirical Subgroup Behavior |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `L40_44` | 40–44 words | 92.0% | 96.0% | 95.00% | 95.17% | **-0.17 pp** | Near ceiling; slight negative difference (-0.0017) |
| `L45_49` | 45–49 words | 90.0% | 93.0% | 97.00% | 93.17% | **+3.83 pp** | Positive placement gain |
| `L50_54` | 50–54 words | 81.0% | 89.0% | 90.00% | 86.00% | **+4.00 pp** | Positive placement gain |
| `L55_59` | 55–59 words | 78.0% | 84.0% | 83.50% | 84.83% | **-1.33 pp** | Small negative difference (-0.0133) |
| `L60_64` | 60–64 words | 64.0% | 79.0% | 81.50% | 74.00% | **+7.50 pp** | Substantial placement gain |
| `L65_69` | 65–69 words | 67.0% | 84.0% | 78.50% | 76.00% | **+2.50 pp** | Moderate positive gain |
| `L70_74` | 70–74 words | 48.0% | 74.0% | 74.50% | 63.00% | **+11.50 pp** | Peak placement gain |
| `L75_79` | 75–79 words | 33.0% | 56.0% | 54.50% | 44.33% | **+10.17 pp** | Substantial placement gain |
| `L100_119`| 100–119 words| 2.0% | 13.0% | 16.00% | 7.83% | **+8.17 pp** | Severe completion collapse across all models |
| `L160_180`| 160–180 words| 0.0% | 1.0% | 1.00% | 0.17% | **+0.83 pp** | Near-zero completion across all models |

### Key Observations
1. **Intermediate Length Window**: The terminal placement advantage is concentrated in sentences between 60 and 79 words (pooled 200 sources: Tail-SD 72.25% vs. Random-PR 64.33%, $\Delta = +7.92\text{ pp}$).
2. **Negative and Ceiling Regimes**: Small negative differences occur in `L40_44` (-0.17 pp) where models operate near ceiling, and in `L55_59` (-1.33 pp).
3. **Longest Inputs Remain Unsolved**: For texts beyond 100 words, strict completion drops precipitously across all systems. In `L160_180`, completion is 0.0% for Base, 1.0% for Full-SD, 1.0% for Tail-SD, and 0.17% for Random-PR. **Tail-SD does not solve long-form AR-TTS instability**.

---

## 4. E14 — Position Controls (Head vs. Middle vs. Tail)

To test whether the advantage of Tail-SD is uniquely terminal or shared by any fixed contiguous placement, a post-hoc position study was performed on the opened E13 panel comparing **Head-PR**, **Middle-PR**, and **Tail-SD** under matched per-record speech-label counts, EOS/special-label positions, CE normalization, and target trajectories.

### Study Definition and Hierarchy
- **Nature of Experiment**: This is a *post-hoc position control study* on the opened E13 panel. It is **not** an independent second confirmatory set.
- **Prespecified Primary Contrast Within This Post-hoc Study**: **Tail minus NonTerminal** (the combined average of Head-PR and Middle-PR).

### Results

| System / Contrast | Strict Completion Rate | $\Delta$ vs. Tail-SD (pp) | 95% Bootstrap CI (pp) |
| :--- | :---: | :---: | :---: |
| **Head-PR** (`init20260822`: 51.3%, `init20260823`: 50.1%) | 50.70% | — | — |
| **Middle-PR** (`init20260822`: 58.5%, `init20260823`: 56.8%) | 57.65% | — | — |
| **Tail-SD** (`init20260822`: 67.3%, `init20260823`: 67.0%) | 67.15% | — | — |
| **Tail-SD minus Head-PR** | — | **+16.45 pp** | [+14.05, +18.95] |
| **Tail-SD minus Middle-PR** | — | **+9.50 pp** | [+7.45, +11.60] |
| **Tail minus NonTerminal (Primary Contrast)** | — | **+12.98 pp** | **[+10.95, +15.03]** |
| *Middle-PR minus Head-PR (Descriptive)* | — | *+6.95 pp* | *(Descriptive point estimate)* |

Individual cell units:
- Tail-SD vs. Head-PR (`init20260822`): +16.00 pp [13.00, 19.00]
- Tail-SD vs. Head-PR (`init20260823`): +16.90 pp [14.00, 19.90]
- Tail-SD vs. Middle-PR (`init20260822`): +8.80 pp [6.20, 11.50]
- Tail-SD vs. Middle-PR (`init20260823`): +10.20 pp [7.60, 12.80]

Deterministic head supervision severely impairs completion (50.70%), performing worse than un-finetuned Base (55.5%). Middle supervision achieves intermediate completion (57.65%), but remains significantly inferior to terminal placement (67.15%).

---

## 5. E16 — Supervision-Budget Controls

To investigate whether the terminal-placement advantage depends on a specific label budget, a post-hoc sensitivity study on the opened E13 panel evaluated three direct-supervision budget scaling levels:
- **0.5× Budget**: $\approx 12.98\%$ active CE labels relative to Full-SD (13,164 active labels)
- **1.0× Budget (Default)**: $\approx 25.91\%$ active CE labels relative to Full-SD (26,269 active labels; reused from E13)
- **2.0× Budget**: $\approx 51.77\%$ active CE labels relative to Full-SD (52,480 active labels)

All budgets use two paired initializations (`init20260822`, `init20260823`). The default budget reuses three Random-PR masks; each outer budget uses one frozen mask. These are matched contrasts, not ensemble predictions.

### Detailed Budget Results

| Budget Tier | Active CE Labels / Ratio | Tail-SD SC | Random-PR SC | Contrast Unit | $\Delta$ (pp) | 95% Bootstrap CI (pp) |
| :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **0.5×** | 13,164 (12.98%) | 65.6% | 61.1% | `Tail-SD − Random-PR (init 20260822)` | +4.50 pp | [+1.90, +7.10] |
| | | 65.9% | 61.3% | `Tail-SD − Random-PR (init 20260823)` | +4.60 pp | [+2.30, +7.00] |
| | | **65.75%** | **61.20%** | **Aggregate 0.5× Contrast** | **+4.55 pp** | **[+2.75, +6.40]** |
| **1.0×** | 26,269 (25.91%) | 67.3% / 67.0% | 62.45% (avg) | Reused E13 Confirmatory (6 units) | — | — |
| | | **67.15%** | **62.45%** | **Aggregate 1.0× Contrast** | **+4.70 pp** | **[+3.20, +6.22]** |
| **2.0×** | 52,480 (51.77%) | 66.7% | 64.7% | `Tail-SD − Random-PR (init 20260822)` | **+2.00 pp** | **[-0.40, +4.40]** |
| | | 69.0% | 66.0% | `Tail-SD − Random-PR (init 20260823)` | +3.00 pp | [+0.60, +5.40] |
| | | **67.85%** | **65.35%** | **Aggregate 2.0× Contrast** | **+2.50 pp** | **[+0.75, +4.30]** |

### Critical Boundaries
1. **Placement Advantage Persists**: Terminal placement maintains a positive advantage over matched random placement across all tested budgets (+4.55 pp, +4.70 pp, +2.50 pp).
2. **Confidence Interval Spanning Zero at 2.0×**: For `init20260822` under the 2.0× budget, the 95% bootstrap confidence interval spans zero: **[-0.40, +4.40]**.
3. **No Monotonicity Claim**: The empirical differences (+4.55, +4.70, +2.50 pp) across three points do **not** prove a monotonic budget curve or that 25.9% is an optimal threshold.
4. **Active Label Ratio $\neq$ Compute Savings**: Active CE labels measure only loss masking during teacher-forced forward passes. They do not establish a reduction in FLOPs, GPU memory, or wall-clock training time. Full-SD is a dense reference, not a "100% Tail budget" point.

---

## 6. Full-SD Reference

Full-SD applies cross-entropy supervision across all speech tokens and EOS tokens in every record.

### Official Formal Comparison (Original CV3 Panel)

| System | Strict Completion | Active CE Labels | Tail-SD minus system (pp) | 95% CI (pp) |
| :--- | ---: | :--- | ---: | :--- |
| Base | 57.0% | Not applicable (no adaptation) | +11.20 | [+8.70, +13.80] |
| Full-SD | 67.8% | 101,380 (100.0%) | +0.40 | [-1.90, +2.70] |
| Random-Local | 63.7% | 26,269 (25.9%) | +4.50 | [+2.10, +6.90] |
| Tail-30 | 66.2% | 30,495 (30.1%) | +2.00 | [-0.30, +4.30] |
| Tail-SD | 68.2% | 26,269 (25.9%) | Reference | — |

### Supervision Disentanglement Rationale
- In CV3 training, Full-SD supervises the EOS token across all records (including Content-continuation records). Tail-SD and Random-PR supervise EOS only on Termination records. This creates an asymmetric Content-EOS supervision difference.
- To isolate the effect of **direct-supervision placement** under the tested matching conditions, the paper designates EOS-matched **Random-PR** as the primary scientific control.
- Full-SD is retained as a dense-supervision reference.

### Strict Claim Prohibitions
- **Do NOT claim superiority**: The paired comparison did not establish a difference (+0.40 pp, 95% CI [-1.90, +2.70]).
- **Do NOT claim equivalence or non-inferiority**: No equivalence margin or non-inferiority test was pre-registered or evaluated.
- **Do NOT cite historical unreproducible CI**: The deprecated historical interval `[+0.15, +2.70]` must not be used. The only reproducible formal interval is `[-1.90, +2.70]`.

---

## 7. CosyVoice2 Replication

To test whether the supervision placement advantage transfers across model backbones, Tail-SD was evaluated on **CosyVoice2-0.5B**.

### Configuration and Controls
- **Independent Training Bank**: Constructed from CosyVoice2 self-generated continuations (`E08`, 123 target records), completely independent of CV3 training targets.
- **Evaluation Panel**: Tested on the shared/open E11 500-source panel with native CosyVoice2 decoding.
- **Backbone Scope**: CosyVoice2 belongs to the same CosyVoice architectural family; this experiment tests cross-backbone transfer within the family, not general universality across all AR-TTS models.

### Results

| System | Strict Completion | Tail-SD minus system (pp) | 95% CI (pp) |
| :--- | ---: | ---: | :--- |
| Base | 44.0% | +4.40 | [+2.20, +6.60] |
| Full-SD | 48.3% | +0.10 | [-2.10, +2.30] |
| Random-PR | 45.5% | +2.90 | [+0.80, +5.10] |
| Tail-SD | 48.4% | Reference | — |

The terminal-placement advantage replicates on CosyVoice2 ($\Delta = +2.90\text{ pp}$, 95% CI $[+0.80, +5.10]$). On CosyVoice2, the EOS supervision contract for Full-SD differs from CV3; we report the observed outcomes factually without post-hoc conjecture.

---

## 8. Human Evaluation Scope

An external system-blinded study evaluated Completion, Major Error, and 1–5 naturalness MOS on 120 sources from ten length bins (12 sources per bin). Ten listeners each rated all five systems: 1,200 valid ratings per system and 6,000 rows in total. Reference text was shown; presentation order was randomized per listener and source. Listeners were instructed to use headphones in quiet surroundings. Binary ratings and MOS were pooled within system.

| System | Completion (%) | Major Error (%) | Naturalness MOS |
| :--- | ---: | ---: | ---: |
| Base | 59.2 | 18.3 | 4.02 |
| Full-SD | 69.2 | 10.8 | 4.06 |
| Random-Local | 64.2 | 14.8 | 4.03 |
| Tail-30 | 67.5 | 11.7 | 4.05 |
| Tail-SD | 69.8 | 10.0 | 4.06 |

These are descriptive comparisons, without a new human-rating significance test. They characterize the original five systems, not the new-text Tail-SD versus Random-PR contrast. The [de-identified ratings, protocol, mapping, and source-derived summary](evidence/README.md#human-evaluation) support Table VI. The derived summary uses raw-log counts (Tail-SD completion 838; Random-Local major errors 178); the original platform export is preserved separately, not silently overwritten.

---

## 9. Diagnostics and Limitations

### E15 Mechanistic Diagnostic (Termination Separation)
To examine whether terminal supervision improves the model's internal termination decision, fixed-prefix EOS logit separation was analyzed between continue paths (154 paths, 117 sources) and stop paths (555 paths, 317 sources) on the opened E13 panel:
- **Tail-SD EOS-Logit Separation**: 7.30 (95% CI [6.70, 7.90])
- **Base EOS-Logit Separation**: 5.67 (95% CI [5.12, 6.23])
- **Head-PR EOS-Logit Separation**: 6.28 (95% CI [5.71, 6.84])
- **Middle-PR EOS-Logit Separation**: 6.28 (95% CI [5.71, 6.86])

**Diagnostic Boundaries**:
1. Tail-SD exhibits larger EOS-logit separation than Base, Head-PR, and Middle-PR, but the pre-registered criterion for a mechanistic interpretation was **not fully satisfied**.
2. Twelve sources appeared in both continue and stop strata and were not jointly clustered by the existing bootstrap.
3. EOS-logit separation is **not** termination-probability separation and must not be described as a probability difference. The diagnostic is purely descriptive.

### Comprehensive Paper Limitations
1. **Architectural Scope**: Evaluated on Fun-CosyVoice3-0.5B and CosyVoice2-0.5B. Both belong to the CosyVoice family; universality across dissimilar AR-TTS backbones remains untested.
2. **Language Scope**: Evaluations are strictly English-focused (Wikipedia / LibriTTS-derived text). Multilingual performance is untested.
3. **Long Input Collapse**: Completion collapses near 1% on 160–180 words across all systems. Tail-SD does not solve long-form AR-TTS instability.
4. **No Full-SD Dominance**: Tail-SD does not outperform Full-SD in a statistically established manner (+0.40 pp [-1.90, +2.70]).
5. **No Compute Advantage**: Active CE labels represent loss masking; no FLOPs, memory, or wall-clock savings have been demonstrated. AR decoding is unchanged.
