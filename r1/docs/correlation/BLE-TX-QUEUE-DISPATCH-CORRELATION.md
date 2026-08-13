# R1 BLE transmit-queue dispatch correlation

## Disposition

Two formerly unclassified functions / 560 executable bytes are admitted as R1 product-specific
message-envelope and BLE transmit-queue producer behavior. They are `r1_product_specific` /
`clean_room_behavior_only`.

The closure does not admit FreeRTOS heap code, CMSIS-FreeRTOS queue/thread operations, Arm
`memmove`, Nordic/R1 logging, the BLE transmit worker, or unresolved connection-handle accessors.
Those implementations remain separately source-routed or blocked.

## Exact closure

| Entry | Bytes | Role |
| --- | ---: | --- |
| `0x00034064` | 12 | rearrange arguments, select dispatch type 0, and tail-call the common producer |
| `0x00034070` | 548 | select dispatch type 2 and own the noncontiguous common producer at `0x0003E274..<0x0003E48C` |

The type-2 function consists of `0x00034070..<0x0003407C` plus
`0x0003E274..<0x0003E48C`; its concatenated body SHA-256 is
`3b6bf6bff7c54cec4699a678cfe67eb59980abdf8864d2b38407d04fa3bf56f0`. The type-0
veneer has SHA-256 `87384ba4fcae559338b8fda5ebfc680ea269ac253c14573d9a2be3e0898c4183`.
Three callsites target type 0 and five target type 2, including the pinned IQS7211E IRQ worker and
R1 structured-log cache.

## Envelope and queue behavior

The common producer rejects a null payload or unavailable queue. It allocates
`align4(payload_length + 15)` bytes, then stores:

| Offset | Field |
| ---: | --- |
| `0x00` | caller message identifier |
| `0x04` | dispatch type selected by the veneer |
| `0x08` | payload length |
| `0x0C` | copied payload bytes |

Before enqueue, it samples CMSIS queue count and capacity and emits a diagnostic when occupancy is
at least 90 percent. It calls the abstract queue with priority zero and raw timeout 100. Success
sets worker thread flag 1 and returns zero. Failure logs, frees the envelope, and returns minus one.

The common body contains type-0/type-1 connection-handle guards. The accessors at `0x0004CB34`
and `0x0004CBA4` are not promoted by this closure, and type 1 has no separately admitted veneer.

## Clean-room implementation rule

Local code may preserve the bounded envelope layout, dispatch-type selection, queue warning,
timeout, worker signal, and failure cleanup. It must call authenticated FreeRTOS/CMSIS and
toolchain implementations and the existing abstract BLE worker boundary. This static summarizer
reads no private payload and exposes no live BLE sender.

## Reproduce

```sh
python3 tools/summarize_r1_ble_tx_queue_dispatch.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
