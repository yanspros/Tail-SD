# Data and manifest format

All manifests are JSON objects with a `records` array, or a JSON array where a
CLI explicitly permits it. Stable identities should be hashes of bytes or
canonical structured values, not mutable filenames alone.

## Source / inference record

Required user-facing fields:

| Field | Meaning |
| --- | --- |
| `source_id` | Stable source identity |
| `text` | Complete input text; no automatic splitting by this package |
| `prompt_audio_path` | User-supplied, licensed prompt WAV path |
| `seed` | Frozen inference or natural-generation seed |
| `prompt_id` | Stable prompt binding identity |

Model adapters should append normalized-text, token, prompt-feature, generated
speech-token, WAV and trace identities, as well as EOS, cap and runtime status.

## Scored trajectory

Target construction expects at least:

- `source_id`, `seed`, `classification`
- `eos_generated`, `cap_hit`
- `wer`, `text_coverage_ratio`, `trailing_deleted_words`
- `non_tail_error_rate`

Termination continuations use the same metric fields plus a frozen
continuation seed and exact-prefix provenance. Content targets are alternate
natural strict-complete paths from the same source.

## Target-bank record

Each bank record needs:

- `record_id`, `source_id`, `branch`
- speech length as `T_i`, `speech_token_count`, or
  `recovery_speech_token_count`
- target/history identity and paths needed by the user's model adapter
- failure-to-target provenance and the frozen selection evidence

`branch` is `termination` or `content`. The canonical array order is meaningful
for residual allocation, Random-PR draws and training order; do not sort it
implicitly.

## Mask record

Tail-SD emits `T_i`, `K_i`, active speech positions, EOS/special positions and
`M_i`. Random-PR additionally records `draw_index`, sampled interval, overlap
statistics and a per-mask hash. Full-SD lists every speech position.

See the synthetic [example manifest](../examples/example_manifest.json). It
contains no real audio or research data.
