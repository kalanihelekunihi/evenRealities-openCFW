# GoMore activity-state classifier provider boundary

## Decision

Six formerly unclassified functions / 1,890 executable bytes form a private activity-state
window-classifier closure beneath the already gated GoMore output orchestrator. They are now
routed to `gomore_health_algorithm_candidate` with disposition
`vendor_source_required_not_redistributable`. OpenR1 does not recreate the classifier,
statistical decision rules, thresholds, or state transitions.

| Entry | Bytes | Boundary role |
| --- | ---: | --- |
| `0x0006138C` | 834 | seven-state, windowed activity classifier |
| `0x00064A98` | 110 | classifier-private range statistic |
| `0x0006859C` | 382 | classifier-private peak statistic |
| `0x00069FA8` | 108 | classifier-private crossing-interval statistic |
| `0x00093FAC` | 174 | classifier-private input conditioner |
| `0x00096E74` | 282 | classifier-private window decision |

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

The top-level routine accumulates 25-sample transformed windows and evaluates a decision after
250 samples. It maintains seven internal states and emits a compact two-byte state result. The
three embedded seven-entry dispatch tables and the complete literal pool are SHA-pinned so this
classification cannot silently drift into a generic application-policy rewrite.

`0x0006138C` also calls the already gated GoMore window transform at `0x000882EC`. Shared Arm
toolchain floating-point helpers, `powf`, and `sqrtf` remain assigned to the toolchain runtime and
are intentionally excluded from this provider set.

These observations establish ownership and a provider integration boundary; they are not a
clean-room specification for reproducing the private algorithm. A matching licensed GoMore
provider remains required. Until one is admitted, the OpenR1 health engine must keep this path
disabled and expose capability absence rather than substitute an inferred classifier.

```sh
python3 scripts/firmware/summarize_r1_gomore_activity_state_classifier.py
```
