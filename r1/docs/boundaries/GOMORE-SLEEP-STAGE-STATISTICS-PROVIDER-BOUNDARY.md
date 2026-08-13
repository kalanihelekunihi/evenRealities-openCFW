# GoMore sleep-stage statistics provider boundary

## Decision

Three formerly unclassified functions / 796 executable bytes belong to the already established
GoMore sleep-algorithm closure. They are source-gated as
`gomore_health_algorithm_candidate` with disposition
`vendor_source_required_not_redistributable`. openR1 does not recreate these routines in C;
the path requires an authenticated, licensed GoMore source or binary provider.

This classification is based on exact bytes and exclusive call topology, not address proximity.
The two statistics blocks are called only by the SHA-pinned finalizer at `0x00068F8C`. Their shared
40-byte stage lookup helper is called only from those two blocks.

## Exact closure

| Recovered range | Bytes | SHA-256 | Observed role |
| --- | ---: | --- | --- |
| `0x00068FD4..<0x0006911A` | 326 | `afa31edc4912f2d02293bdd725b6762bcbb8ee3663e36c6a15e2347f389a7f60` | interval, awake, sleep, and efficiency statistics |
| `0x00069128..<0x000692D6` | 430 | `7602275b0249f68eed4ef03295b1c3ae05adc949d71b71ea9b81f668afbeda0c` | stage fractions, ratios, and durations |
| `0x0006951E..<0x00069546` | 40 | `68704b376c6239caa65d6a5679c08e552872b91e475fa5b93670777d3a83ead4` | timestamp-indexed stage lookup helper |

The complete caller census is:

- `0x00068FA4 -> 0x00068FD4`;
- `0x00068FB4 -> 0x00069128`;
- `0x00069050 -> 0x0006951E`;
- `0x000691A6 -> 0x0006951E`.

There are no other direct Thumb branch callers to any of these entries in the recovered
application. The finalizer and its surrounding range were already included in the SHA-pinned
sleep-algorithm audit; this supplemental closure fixes the function-level ownership omission.

## Observable compatibility contract

The recovered final result contains a seven-value interval/efficiency block and a
twelve-value stage-statistics block. Epoch counts are converted to minutes using a `0.5`
multiplier. The
second block includes NREM, REM, light, and deep fractions; stage ratios; and wake/REM/light/deep
durations. A zero ratio denominator produces `0.0`. Unknown nonzero stage values count as sleep
only in the first block.

These observations define the provider ABI and validation surface. They do not authorize a local
implementation of GoMore's sleep algorithm or statistics policy. A licensed provider adapter may
consume the R1-compatible stage stream and must reproduce the documented output contract.

## Reproduction

Run the read-only verifier against the recovered image:

```sh
python3 tools/evidence/summarize_r1_gomore_sleep_stage_statistics.py
```

The script verifies the application SHA-256, every function body, the caller-set digests, the
796-byte census, and the fail-closed provider disposition. It reads no live health data, executes
no vendor algorithm, and emits no algorithm code.
