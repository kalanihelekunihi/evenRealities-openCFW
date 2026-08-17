# R1 BLE transmit-queue dispatch correlation

## Disposition

Three functions / 572 executable bytes are admitted as R1 product-specific message-envelope and
BLE transmit-queue producer behavior. Two are Ghidra inventory rows; the independently bounded
type-1 veneer is a manual provenance supplement. They are `r1_product_specific` /
`clean_room_behavior_only`.

The closure does not admit FreeRTOS heap code, CMSIS-FreeRTOS queue/thread operations, Arm
`memmove`, Nordic/R1 logging, the BLE transmit worker, or unresolved connection-handle accessors.
Those implementations remain separately source-routed or blocked.

## Exact closure

| Entry | Bytes | Role |
| --- | ---: | --- |
| `0x00034064` | 12 | rearrange arguments, select dispatch type 0, and tail-call the common producer |
| `0x00034070` | 548 | select dispatch type 2 and own the noncontiguous common producer at `0x0003E274..<0x0003E48C` |
| `0x0003407C` | 12 | rearrange arguments, select dispatch type 1, and tail-call the common producer |

The type-2 function consists of `0x00034070..<0x0003407C` plus
`0x0003E274..<0x0003E48C`; its concatenated body SHA-256 is
`3b6bf6bff7c54cec4699a678cfe67eb59980abdf8864d2b38407d04fa3bf56f0`. The type-0
veneer has SHA-256 `87384ba4fcae559338b8fda5ebfc680ea269ac253c14573d9a2be3e0898c4183`.
Three callsites target type 0 and five target type 2, including the pinned IQS7211E IRQ worker and
R1 structured-log cache. The type-1 veneer is exactly `0x0003407C..<0x00034088`, SHA-256
`a92c0d0743114a1354d18c5b9db682c06ea1ecc1eae9e3528ec178501b944077`; the exported call graph
has no direct caller, so it remains compiled but dormant rather than being attached to a new route.

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
and `0x0004CBA4` are not promoted by this closure. The three transparent veneers
`r1_ble_tx_queue_dispatch_type0`, `r1_ble_tx_queue_dispatch_type1`, and
`r1_ble_tx_queue_dispatch_type2` preserve the forced dispatch word and bounded envelope encoding;
they expose no live BLE sender or queue implementation.

## Channel-1 task-entry supplement

Ghidra exported only the odd label `LAB_000920ec+1`, but the rebuilt image contains an independent
128-byte task body at `0x000920EC..<0x0009216C`, SHA-256
`a5c8694c233c107da3df11c43b95747523afd8c1d9fbfb41531dd964096fcecb`. Its entry waits on
startup synchronization group 10, creates a queue of twenty four-byte envelope pointers, and
enters the stock fail-stop if queue creation fails. It then signals group 10, registers the
`"ble_gtx"` task with raw watchdog interval 10,000, and waits forever on the low 24 thread flags.
Flag bit 0 calls the already admitted queue drain at `0x00044F50`. Flag bit 23 signals task
suspension and enters an indefinite delay; zero or a CMSIS error-flag result returns to the wait.

`r1_channel1_task_plan_startup` and `r1_channel1_task_plan_flags` preserve those exact constants
and decisions in typed portable C. The Nordic integration's `channel1_worker` and
`openr1_scheduler_initialize` supply the live CMSIS queue/thread composition. That integration
stores owned `r1_tx_event` values instead of stock heap pointers, so no stock allocation or opaque
envelope is required while the recovered 20-record capacity and wake/drain behavior remain
explicit.

## BAE8 input task-entry supplement

The adjacent odd label `LAB_00092178+1` is likewise a complete task. Its executable body is
`0x00092178..<0x0009223E` / 198 bytes, SHA-256
`75497f7603d5c266081039ff61cb0821fccef22bc7c4aaeb80aedda9809d934b`; the two zero bytes at
`0x0009223E...0x0009223F` are alignment before the literal pool and are not claimed as code. The
task waits on startup synchronization group 2, creates fifty four-byte envelope-pointer records,
signals group 2, registers `"ble_msgrx"` with raw watchdog interval 10,000, then waits on the low
24 thread flags. Bit 22 drains the input queue through `0x000450CC`. Bit 23 feeds once more,
signals suspension for group 2, and enters an indefinite delay. Zero and CMSIS error-flag results
skip both actions and return to the wait; the stock body also retains diagnostic-only logging for
provider wait errors.

`r1_bae8_input_task_plan_startup` and `r1_bae8_input_task_plan_flags` encode the exact queue,
sync, watchdog, wait-mask, dispatch, error, and suspension decisions. The source-built Nordic and
Zephyr BAE8 bindings receive and dispatch typed values directly, avoiding stock heap-pointer
records while preserving the recovered 50-record capacity at the portable boundary.

## Shared transmit task-entry supplement

The output-side sibling at `0x0009227C..<0x000922FC` is another 128-byte omitted task, SHA-256
`c7aa95dfd7e4c12af796c706385ec6f28cb3de700daae8146fa3548f59d2f025`. It waits on sync group
3, creates fifty four-byte envelope-pointer records, signals group 3, and registers
`"ble_msgtx"` with raw watchdog interval 10,000. Its low-24-bit flag loop drains through
`0x00044F50` on bit 0 and uses the common non-returning feed/suspend helper `0x00045C20` on bit
23. Queue-creation failure enters the stock fail-stop.

`r1_shared_tx_task_plan_startup` and `r1_shared_tx_task_plan_flags` preserve this exact task
contract. The live source-built scheduler's `shared_queue` and `runtime_worker` implement the
transparent 50-record EUS/explicit transmit path with owned typed events.

## Factory-input task-entry supplement

The factory-marker input sibling is `0x0009230C..<0x0009238C` / 128 bytes, SHA-256
`65da7625dd83c8f74a802a46676632679fc978ef5268b4981207facb30d45a45`. It waits on sync group
6 and creates eight four-byte pointer records. On success it runs, in order, wear-buffer fill,
sensor-stream framework initialization, accelerometer singleton creation, R1 stream-namespace
registration, and temperature singleton creation before signalling group 6. Each loop obtains a
timer-derived wait from `sensor_stream_timer_poll`, drains the factory-marker queue through
`0x00045F3C` on bit 22, uses the non-returning group-6 suspend path on bit 23, and otherwise runs
the periodic watchdog operation at `0x000500FC`. Queue failure enters the stock fail-stop.

`r1_factory_input_task_plan_startup` preserves the complete five-action order;
`r1_factory_input_task_plan_flags` preserves dispatch, provider-error, suspension, periodic-action,
and repeat decisions. The referenced wear, sensor-stream, registration, and watchdog functions are
already separately source-routed and remain independent typed callees.

The bit-22 drain target is independently pinned at `0x00045F3C..<0x00045FB0` / 116 executable
bytes, SHA-256
`9298cf72c25a75bacd23e7a94304495fd904b00ac66131020a9de33346cd516f`; the two words beginning at
`0x00045FB0` are literals, not part of the body. Each non-null queue record carries a 16-bit type
at offset 0, a 32-bit payload length at offset 8, and payload bytes at offset 12. Lengths greater
than three with exact `AT^` prefix are terminated at `payload[length]` and routed to the AT parser;
other records call the standard dispatcher with the type and the low 16 bits of the length. Every
non-null record is then released. `r1_factory_input_record_plan_dispatch` preserves the routing,
length truncation, and release decision while adding an explicit payload-capacity requirement
before the terminator write; the queue, parser, dispatcher, and allocator remain external typed
bindings.

## Main BLE task-entry supplement

The separately authenticated main BLE task is `0x00091F54..<0x0009208C` / 312 bytes, SHA-256
`01659a473563e3f5d469f43efb036354a8f9fac857d2b9399b135d244c6051e6`. Its creator at
`0x00044F48` stores the exact odd Thumb pointer `0x00091F55`. The task waits on sync group 4,
creates eight four-byte records, fail-stops on allocation failure, commits peer state, configures
the Nordic BLE bootstrap, signals group 4, starts callback timers at raw intervals `3072` and
`10240`, and registers `"ble"` with watchdog interval `10000`.

The valid low-24-bit flag loop polls the SoftDevice before and after dispatch. It routes bit 22 to
the connection-control consumer; bit 7 takes precedence over bits 8 and 10 for advertising stop
versus restart modes 3/4; bits 13, 2, 11, and 12 select the peripheral watchdog, buttonless-DFU
preparation, and low/high TX-power actions. Bit 23 feeds, signals group 4, and waits indefinitely.
Zero/high-bit provider errors skip dispatch and perform the ordinary watchdog feed/re-wait. These
decisions are explicit in `r1_ble_task_plan_startup` and `r1_ble_task_plan_flags`; Nordic SDK,
peer persistence, BLE control, DFU, TX-power, timer, and watchdog operations retain their existing
typed source boundaries.

## Clean-room implementation rule

Local code may preserve the bounded envelope layout, dispatch-type selection, queue warning,
timeout, worker signal, and failure cleanup. It must call authenticated FreeRTOS/CMSIS and
toolchain implementations and the existing abstract BLE worker boundary. This static summarizer
reads no private payload and exposes no live BLE sender.

## Reproduce

```sh
python3 tools/evidence/summarize_r1_ble_tx_queue_dispatch.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
