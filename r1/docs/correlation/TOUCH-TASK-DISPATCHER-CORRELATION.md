# R1 touch-task dispatcher correlation

## Disposition

The formerly unclassified legacy Ghidra inventory row at `0x00046650` / 578 executable bytes is
admitted as an R1 task/lifecycle adapter around the pinned IQS7211E provider. Its ownership is
`r1_iqs7211e_provider_adapter` / `clean_room_adapter_only_use_pinned_provider`.

This classification does not admit IQS7211E controller/register/state-machine code, Nordic or
CMSIS-FreeRTOS primitives, the shared-power provider, the logging frontend, or unresolved hardware
wrappers. Local code may reproduce only the observed event routing and board/provider call order.

## Corrected function boundaries

Ghidra assigns seven executable ranges to one noncontiguous inventory row. Independent Thumb
disassembly corrects that representation: the 426-byte dispatcher restores its stack before each
`b.w` tail branch, and every target below has its own prologue and return. The six tail targets are
therefore independent exact functions, not continuation blocks of the dispatcher.

| Range | Bytes | SHA-256 | Role |
| --- | ---: | --- | --- |
| `0x00046650..<0x000467FA` | 426 | part of legacy aggregate below | event-bit dispatcher, open/close policy, diagnostics, and tail branches |
| `0x0004FA8C..<0x0004FAA4` | 24 | `55d4fdd20707269b2b817d69bbd7c2638d974e8112b03e368f0d0ee8806c02e0` | `r1_iqs7211e_factory_marker_1` |
| `0x0004FAA8..<0x0004FAC0` | 24 | `2fea003d0e94afb223365c2091177c68a227795756c76891b220756238cbe53a` | `r1_iqs7211e_factory_marker_2` |
| `0x0004FAC4..<0x0004FADE` | 26 | `97f954019770ae2aed8bc4b741003667505ac33e3b4c6536f7fd9b7effd5deec` | `r1_iqs7211e_factory_marker_3`; store one-byte input at record offset 1 |
| `0x0004FAE4..<0x0004FAFE` | 26 | `c449f36740ef6af253a88b29a37e1137573bf1c0dbfcf78151dc796c102e497f` | `r1_iqs7211e_factory_marker_4`; store two-byte input at record offset 6 |
| `0x0004FB04..<0x0004FB1E` | 26 | `967654e9b8fe0390e2073837afb92d4b28304c9f934d8cb34ccd5220e10fd786` | `r1_iqs7211e_factory_marker_5`; store one-byte input at record offset 2 |
| `0x0004FB24..<0x0004FB3E` | 26 | `3453a55e55a8ead4030b1f2b1ab8b482662803542786731c8bb6b74e85e034b9` | `r1_iqs7211e_factory_marker_6`; store four-byte input at record offset 8 |
| `0x00050304..<0x00050338` | 52 | `8e00eee36d082b3292c05cc5d56b08a255fe15049d9e009cd546e84300c4fc86` | `r1_touch_lifecycle_disable_plan`; client 0/1 slot `18(0,0)` then slot `0c` |
| `0x00050338..<0x0005036C` | 52 | `7e574c6aad94c1e6af24277e385a0a999b49c78c021c75492fb8971845b2eea6` | `r1_touch_lifecycle_enable_plan`; client 0/1 slot `08` then slot `18(1,0)` |

The concatenated 578-byte body has SHA-256
`3019299c9c23cbed488c51229722b18cf0166ccae126bef2cdc3a49b615fab00`. Its direct
Thumb callsite is `0x00092822` in the touch task loop. The static summarizer preserves this legacy
aggregate for reproducibility, while the ownership ledger adds six exact manual-provenance entries
so the explicit-entry census no longer treats their starts as unproven bounding-range addresses.

The two lifecycle entries are adjacent symmetric functions over the same two-record table at
`0x20007688`. Client indices 0 and 1 select record offsets 0 and 4; every other index is a no-op.
Disable dispatches generic-device slot `18` with `(0,0)` and then slot `0c`. Enable dispatches slot
`08` and then slot `18` with `(1,0)`. The clean implementation returns this exact two-operation
plan and never dereferences the production device table or invokes a GPIO, power, or bus provider.

## Event routing

| Event bit | Recovered action |
| --- | --- |
| `0x000001` | invoke the separately bounded ready/IRQ worker |
| `0x000002` | mark active, acquire shared-power client bit 2, schedule raw delay `0x800`, delay one tick, and invoke hardware open |
| `0x000004` | log and close hardware; when ATI recovery is pending, replace the one-shot restart timer with raw delay `0x66` |
| `0x000010` | emit the ALP ATI diagnostic only |
| `0x000020` | emit the trackpad ATI diagnostic only |
| `0x000040...0x000800` | perform six factory marker transactions numbered 1 through 6 |
| `0x400000` | invoke the separate deferred-callback path |
| `0x800000` | enter the fatal task/storage path and remain in the RTOS delay loop |

Each factory transaction calls the exact record-begin helper at `0x00046F60`, the already pinned
`r1_iqs7211e_factory_communication_end` at `0x0002F866`, and the exact record-commit helper at
`0x00046F54`, in that order. The transparent `r1_iqs7211e_factory_record` type exposes only the
observed marker and result fields; host tests pin call order, status propagation, all four result
offsets, and null/missing-provider failure. No public factory transport is exposed.

## Clean-room implementation rule

The event mask and sequence may be represented locally in the portable touch worker. Actual
register meanings and controller behavior must come from the pinned MIT provider references;
TWIM/GPIO/RTOS behavior must come from Nordic SDK and CMSIS-FreeRTOS; and the shared-power seam must
remain fail-closed until its provider is authenticated. The factory cases must remain internal
adapter callbacks rather than a generally exposed command sender.

The summarizer is static, performs no live GPIO or I2C operation, and exposes no factory transport.
The six reconstructed factory-marker functions operate only through typed begin/end/commit
callbacks and caller-owned state. The two lifecycle functions expose only typed slot-order plans;
they do not expose a raw generic-device dispatcher.

## Reproduce

```sh
python3 tools/evidence/summarize_r1_touch_task_dispatcher.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
