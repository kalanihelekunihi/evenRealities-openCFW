# GoMore activity-state classifier provider boundary

## Decision

Six formerly unclassified functions / 1,890 executable bytes form the complete private
activity-state window-classifier closure beneath the GoMore output orchestrator. All six are now
owner-authorized clean-room source: the top-level routine is
`gomore_primitives_activity_window_update`, and its five statistical/conditioning dependencies
are transparent typed primitives. No executable bytes, private model data, or opaque provider are
needed to build this closure.

| Entry | Bytes | Boundary role |
| --- | ---: | --- |
| `0x0006138C` | 834 | `gomore_primitives_activity_window_update` |
| `0x00064A98` | 110 | classifier-private range statistic; source-owned |
| `0x0006859C` | 382 | classifier-private peak statistic; now source-admitted as `gomore_primitives_peak_statistics` |
| `0x00069FA8` | 108 | classifier-private crossing-interval statistic; source-owned |
| `0x00093FAC` | 174 | `gomore_primitives_activity_score_variability_adjust` |
| `0x00096E74` | 282 | `gomore_primitives_activity_state_classify250` |

The `0x0006138C` address extent is 858 bytes. Its Ghidra function body is 834 executable bytes
because three eight-byte `TBB` data tables embedded in that extent are defined data, not
instructions. The audit pins the four executable segments, all three tables, and the adjacent
literal pool separately.

## Ownership evidence

The sole direct caller of `0x0006138C` is the GoMore output orchestrator at `0x0005FF94`, through
callsites `0x000604E2` and `0x000604F6`. The remaining five functions are private to this closure:

```text
0x0005FF94
  -> 0x0006138C
       -> 0x00093FAC
       -> 0x00096E74
            -> 0x00064A98
            -> 0x0006859C
            -> 0x00069FA8
```

The top-level routine conditions its score, shifts one 250-float window, appends nominal
25-sample inputs, and evaluates a decision after 250 accumulated samples. It maintains seven
internal states and emits a compact two-byte state result. The exact transition thresholds,
180-to-600-sample adaptive holds, 0.5-to-0.25 score threshold, confidence mapping, three embedded
seven-entry dispatch tables, and complete literal pool are pinned. The reconstruction also retains
the production equal-rate-copy behavior for accepted counts 23...27: counts below 25 retain old
tail values, while 26 and 27 overwrite the first one or two metadata words inside the bounded
1,028-byte state object.

`0x0006138C` also calls the source-owned equal-rate window transform at `0x000882EC`. Shared Arm
toolchain floating-point helpers, `powf`, and `sqrtf` remain assigned to the toolchain runtime and
are intentionally excluded from this source set.

The host suite covers positive and negative threshold transitions, adaptive holds, transitional
states, score resets, zero-channel behavior, invalid-input immutability, and the metadata-spill
quirk. A Unicorn harness executes the stock top-level routine with deterministic decision hooks and
asserts the same state bytes, counters, thresholds, outputs, and copy behavior.

```sh
python3 tools/evidence/summarize_r1_gomore_activity_state_classifier.py
PYTHONPATH=/tmp/openr1-unicorn python3 tools/evidence/emulate_r1_activity_window.py \
  research/decompilation/rebuild/rebuilt-application.bin
```
