# Tail-SD method contract

## Supervision placement

Tail-SD operates on a successful self-generated speech-token target. The
complete target remains in the teacher-forced causal forward pass. A binary
label mask decides which positions participate directly in mean
cross-entropy; it does not shorten the sequence, remove prefix tokens, detach
prefix states or change the target.

For branch `b` and record speech length `T_i`, the formal allocation is:

1. `B_b = floor(r_b * sum_i T_i)` for the branch aggregate budget.
2. `K_i_base = floor(r_b * T_i)` for each record.
3. Allocate the residual `B_b - sum_i K_i_base` one label at a time to the
   earliest records in canonical bank order after filtering by branch.

The published ratios are:

- Termination: `0.21705160991522524`
- Content: `0.29909295294208854`

For Termination, the terminal `K_i` speech labels and EOS are active. For
Content, only terminal speech labels are active and EOS is excluded.

## Random-PR control

Random-PR is a per-record matched placement control. It copies the Tail-SD
target, `T_i`, `K_i`, EOS/special positions, `M_i` and full history. For each
record in canonical draw order, it samples exactly once:

```python
start = random.Random(seed).randrange(0, T_i - K_i + 1)
```

The selected interval is `[start, start + K_i)`. Tail overlap and exact-tail
coincidence are valid outcomes and do not trigger a redraw. A generated mask
manifest, rather than future PRNG replay, is the final training authority.

## Full-SD reference

Full-SD uses the same target bank and complete history, with all speech labels
active. Its branch-specific EOS/special rule remains the same: Termination EOS
is included and Content EOS is excluded.

## Completion diagnostics

The public evaluator uses the formal automatic definitions:

- SC: EOS, no cap hit, coverage >= 0.95 and trailing deletions = 0.
- HC predicate: EOS, no cap hit, coverage <= 0.85 and trailing deletions >= 10.
- Coverage: `(reference words - deletions) / reference words`.
- Non-tail error rate: `(all alignment errors - trailing deletions) / reference words`.

The category precedence is cap-truncated, early-EOS, complete, incomplete
without EOS, then residual other failure. HC is an additional predicate on the
early-EOS category, not a disjoint category to add to all residual failures.

## Evidence boundary

The results support an observed supervision-placement advantage in the tested
settings. They do not establish universality across AR-TTS architectures,
languages or every random mask. Active CE-label participation is not a direct
measure of FLOPs or training time.
