# R1 touch-task dispatcher correlation

## Disposition

The formerly unclassified function at `0x00046650` / 578 executable bytes is admitted as an R1
task/lifecycle adapter around the pinned IQS7211E provider. Its ownership is
`r1_iqs7211e_provider_adapter` / `clean_room_adapter_only_use_pinned_provider`.

This classification does not admit IQS7211E controller/register/state-machine code, Nordic or
CMSIS-FreeRTOS primitives, the shared-power provider, the logging frontend, or unresolved hardware
wrappers. Local code may reproduce only the observed event routing and board/provider call order.

## Exact noncontiguous body

Ghidra assigns seven executable ranges to this one function:

| Range | Bytes | Role |
| --- | ---: | --- |
| `0x00046650..<0x000467FA` | 426 | event-bit dispatcher, open/close policy, diagnostics, and tail branches |
| `0x0004FA8C..<0x0004FAA4` | 24 | factory marker 1 transaction |
| `0x0004FAA8..<0x0004FAC0` | 24 | factory marker 2 transaction |
| `0x0004FAC4..<0x0004FADE` | 26 | factory marker 3 transaction and one-byte result |
| `0x0004FAE4..<0x0004FAFE` | 26 | factory marker 4 transaction and two-byte result |
| `0x0004FB04..<0x0004FB1E` | 26 | factory marker 5 transaction and one-byte result |
| `0x0004FB24..<0x0004FB3E` | 26 | factory marker 6 transaction and four-byte result |

The concatenated 578-byte body has SHA-256
`3019299c9c23cbed488c51229722b18cf0166ccae126bef2cdc3a49b615fab00`. Its direct
Thumb callsite is `0x00092822` in the touch task loop. The static summarizer pins the ranges, body,
and caller set independently of the misleading maximum-end span in the function inventory.

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

Each factory transaction calls the unresolved communication-begin wrapper at `0x00046F60`, the
already pinned `r1_iqs7211e_factory_communication_end` at `0x0002F866`, and the unresolved close
wrapper at `0x00046F54`. Those callees are not silently promoted by this closure.

## Clean-room implementation rule

The event mask and sequence may be represented locally in the portable touch worker. Actual
register meanings and controller behavior must come from the pinned MIT provider references;
TWIM/GPIO/RTOS behavior must come from Nordic SDK and CMSIS-FreeRTOS; and the shared-power seam must
remain fail-closed until its provider is authenticated. The factory cases must remain internal
adapter callbacks rather than a generally exposed command sender.

The summarizer is static, performs no live GPIO or I2C operation, and exposes no factory transport.

## Reproduce

```sh
python3 tools/summarize_r1_touch_task_dispatcher.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
