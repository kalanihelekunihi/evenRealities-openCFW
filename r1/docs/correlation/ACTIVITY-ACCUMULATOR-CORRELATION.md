# Activity cumulative-counter accumulator correlation

## Scope and source boundary

This closure reconstructs only the R1-owned policy between an admitted activity provider and the
existing activity history cache. The input is an eight-byte cumulative record containing steps,
all kilocalories, and active kilocalories. It does **not** implement accelerometer interpretation,
step detection, locomotion classification, energy estimation, or any GoMore algorithm. Those
operations remain licensed-provider boundaries.

The implementation is in `r1/src/r1_health.c` and its public types are in
`r1/include/openr1/r1_health.h`. It uses caller-owned state and has no private SRAM, BLE,
sensor, flash, or signing dependency.

## Exact recovered functions

| Application range | Bytes | Clean-room symbol | SHA-256 |
|---|---:|---|---|
| `0x00048D48..<0x00048D96` | 78 | `r1_activity_pending_delta_accessor` | `b807b4e462d853fe5044855ff754544bc03b523dcbf68f8de44e837184bec661` |
| `0x00048E68..<0x00048FE4` | 380 | `r1_activity_periodic_accumulator` | `9e8d594396de8cfaac2ec0bb9b6b66e954b1c07dbb8447da87bd362611fbb0fe` |
| `0x00049068..<0x00049164` | 252 | `r1_activity_explicit_refresh_accumulator` | `a5436baeea82dcfdcd92ffa967adab36803e28864c6d6f0e32d3989ba3dcdbde` |
| `0x0005AA14..<0x0005AB0A` | 246 | `r1_activity_delta_cache_accumulator` | `90c63f8ffa27c90d548d4f0bb7f1400cf354a3aa8833e3314a249a61d7ca7f82` |
| `0x0008A7F4..<0x0008A80A` | 22 | `r1_activity_event_storage_consumer` | `2c8c030600448ff01d2b39b56cedf3e5d64b5211934d814b71ee53143c769d29` |

`0x00049068` is an exact manual inventory supplement because Ghidra did not retain it as a
standalone function. Its entry, end, length, and digest are independently pinned. The ownership
ledger classifies these five functions as `r1_product_specific / clean_room_behavior_only`; this
does not claim or reproduce the original source.

## Recovered state and event shapes

`r1_activity_accumulator` preserves the exact logical 24-byte state:

| Offset | Field |
|---:|---|
| `+0` | raw window-published byte |
| `+1` | raw transition-pending byte |
| `+2` | retained/reserved `UInt16LE` |
| `+4` | transition-start timestamp `UInt32LE` |
| `+8` | baseline steps `UInt32LE` |
| `+12` | baseline all-kcal `UInt16LE` |
| `+14` | baseline active-kcal `UInt16LE` |
| `+16` | current steps `UInt32LE` |
| `+20` | current all-kcal `UInt16LE` |
| `+22` | current active-kcal `UInt16LE` |

Internal event `0x000B` is exactly 12 bytes: all-kcal delta, active-kcal delta, low 16 bits of the
step delta, duration within the current 600-second window, and firmware timestamp. All multibyte
fields are little-endian. A zero-delta event is valid and publishable.

## Policy reproduced

- Periodic input refreshes the current cumulative snapshot. Publication is allowed only at window
  remainders `595...599`, once per window. Earlier calls clear the publication flag.
- Explicit refresh evaluates the last current snapshot at any remainder and deliberately preserves
  the raw publication byte. It does not manufacture a public response.
- Exact local-day start rebases the counters and clears the publication flag without emitting.
- Any cumulative counter rollback rebases without emitting; the periodic path marks the window as
  published.
- A sleep-result status of `1` or wear-fusion state `0` is unavailable and immediately rebases.
  Wear states other than `0` and `2` are transitional: the baseline is retained for 900 seconds inclusive
  and rebased at 901 seconds.
- Pending-delta access returns an all-zero record when the source is unavailable or the counters
  rolled backward.
- The cache consumer resolves both `timestamp-duration` and `timestamp`, records the entire delta
  in the start bucket even when the interval crosses a boundary, adds to that bucket, and applies
  independent packed-field wrapping: steps 12 bits, active kcal 10 bits, all kcal 10 bits.

## Verification

Host tests cover early/tail/repeated windows, explicit refresh, exact midnight, rollback, all
availability states, the inclusive 900-second grace boundary, low-16 step behavior, pending-delta
redaction, exact event bytes, two bucket-resolution calls, cross-boundary placement, and independent
packed-field wrapping. The project verifier additionally pins every recovered body above, rebuilds
the ownership ledger, runs strict C11 plus ASAN/UBSAN, compiles the freestanding Cortex-M4 target,
and retains all seven APIs in the Nordic SDK image.

The linked API addresses are `0x00032B00` (initialize), `0x00032B0A` (periodic), `0x00032C42`
(refresh), `0x00032D1A` (pending delta), `0x00032D72` (encode), `0x00032DAC` (decode), and
`0x00032DF2` (cache consumer). The retained `.openr1_health_api` table is at `0x0003B274` with
size `0x110`. The verified unsigned application is 94,804 bytes text, 236 bytes data, and 132,544 bytes BSS. Its HEX and BIN SHA-256 values are
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.

The security boundary is unchanged: this code does not alter signing, rollback, update validation,
ACLs, or protection state.
