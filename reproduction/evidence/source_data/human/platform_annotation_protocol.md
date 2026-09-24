
# Human Evaluation Platform and Annotation Protocol

## 1. Platform

The human evaluation was conducted on an internal web-based blinded listening platform. The platform presented one audio stimulus at a time together with the reference text, the rating questions, and a playback control. Listener identity was managed through anonymized listener IDs. System identity was never shown.

## 2. Design

- 120 long-form sources.
- 5 CV3 systems: Base, Full-SD, Random-Local, Tail-30, Tail-SD.
- 10 listeners.
- Each listener rated each source for each system.
- Total ratings: 120 × 5 × 10 = 6,000.
- Ratings per system: 120 × 10 = 1,200.

## 3. Blinding

- System labels were replaced by anonymous IDs before presentation.
- The anonymous ID mapping was randomized per listener.
- Listeners were not informed which system produced which audio.
- The reference text was shown for completion and major-content-error judgments.

## 4. Presentation Order

- For each listener and source, the five system audios were presented in randomized order.
- The order was fixed after randomization and logged.
- Each listener completed all 120 sources.
- Each source-system audio was played once by default; replay was allowed but limited.

## 5. Listening Conditions

- Listeners were instructed to use headphones in a quiet environment.
- Volume was set to a comfortable fixed level at the start of the session.
- Listeners could pause between trials.
- No system information was displayed.

## 6. Rating Questions

For each stimulus, listeners answered:

1. Completion:

   - "Did the audio render the complete reference text without obvious omission or truncation?"
   - Yes / No
2. Major content error:

   - "Did the audio contain a major content error, such as wrong words, skipped or repeated content that changes meaning, or gibberish?"
   - Yes / No
3. Naturalness MOS:

   - 1 = Bad
   - 2 = Poor
   - 3 = Fair
   - 4 = Good
   - 5 = Excellent

## 7. Quality Control

- Only listeners who completed all trials were included.
- Technical failures and corrupted audio were excluded.
- Trials with response times below a minimum threshold were flagged.
- Attention-check items were included and checked.
- Listener-level completion and exclusion records were stored.

## 8. Data Export

The platform exported one row per listener, source, and system:

```csv
listener_id,source_id,system,completion,major_error,mos
```
