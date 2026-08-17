# R1 private event-bus correlation

## Decision

The R1 private event bus is R1 product code with no attributable third-party provider: the
publisher, subscriber multicast, and subscription insert are classified `r1_product_specific` /
`clean_room_behavior_only` in the function-ownership ledger. OpenR1 implements the pinned
behavior as a portable clean-room module in `../../src/r1_event_bus.c` with the public interface
in `../../include/openr1/r1_event_bus.h`. The stock heap linked lists, lazy CMSIS mutex, and
RTOS queue send are not recreated; the queue handoff is an injected sink and synchronization is
the platform's responsibility.

## Exact function split

| Stock extent | Bytes | SHA-256 (body range) | Role |
| --- | ---: | --- | --- |
| `0x0008D8FC..<0x0008D9C6` | 202 | `dda68ce96d537f40a139557653a7c7c90c7ed366f37ec3f67deed27fa818a2e3` | `r1_event_publish`: window validate, payload stage, queue handoff |
| `0x0008B028..<0x0008B0F2` | 202 | `4acb7d1b645f879364f0a622a2aa3887ec6d0223bd32dc2fce3d7435ff20d2d0` | `r1_event_subscriber_multicast`: slot walk, listener invoke, cross-context republish |
| `0x0008AF8C..<0x0008B01E` | 146 | `8a485b83574ad31fb809605f5be66fcc8abe3b2bc5984d65b3a8d2675cf325ec` | `r1_event_subscribe`: five-slot subscription insert |
| `0x0005DCB0..<0x0005DCCC` | 28 | `90515482d1ab401834fb39a0647c6d3adebabe299132540585adbfb7824d9b2b` | `r1_event_bus_lock`: lazy `osMutexNew` + acquire on mutex `0x20006794` |
| `0x0005DCD4..<0x0005DCE2` | 14 | `db6d8ef83d808f6310f95ef190f16e778b9b3f3c9c723ee9a5a42b4363f0831b` | `r1_event_bus_unlock` |
| `0x000924C0..<0x000924F2` | 50 | `cca20557110adcc080e287f2ab267b486e2f2dd5782de8e82e43bd269f48d23f` | `r1_event_bus_enqueue`: RTOS queue send of the event record |
| `0x0008D888..<0x0008D8EE` | 102 | `2f3e64601f0b0cc9c0724c0ded69b869370d2c45e35f8b985046456580ca0f60` | `r1_event_dispatch_by_id`: consumer-side dispatch over the three id-range tables |
| `0x00092580..<0x00092662` | 226 | `0ac741e032d68ca7006c9a30e3b230852ab11e0fd4ca5b51ffe28c95051c1ef3` | sensor/event consumer-task orchestration omitted from Ghidra's function inventory |

The lock/unlock pair, the queue enqueue, and the dispatcher remain provider-side seams in the
portable module; only the three ledger-pinned bus functions are implemented locally.

## Sensor/event consumer task

The independently byte-pinned task entry waits on synchronization group 5, creates 50 records of
16 bytes, and enters the stock fail-stop when queue creation fails. On success it initializes the
sensor-stream framework, creates the accelerometer singleton, registers the R1 stream namespace,
creates the temperature singleton, and initializes health services, in that order. It then signals
group 5, registers `"sensor"` with raw watchdog interval `10000`, and publishes empty private event
5 before entering the loop.

Each iteration obtains its wait timeout from `sensor_stream_timer_poll`. A successful low-24-bit
wait drains 16-byte event records through `r1_event_dispatch_by_id` on bit 22, invokes the selected
motion-interrupt dispatcher on bit 1, and uses the group-5 signal/indefinite-delay path on bit 23.
Zero and high-bit error returns perform none of those actions and wait again. The transparent
`r1_sensor_task_plan_startup` and `r1_sensor_task_plan_flags` functions preserve this orchestration;
sensor acquisition, RTOS operations, watchdog service, event dispatch, motion handling, and health
initialization keep their separately admitted typed boundaries.

## Recovered contract

- **Subscriber table.** Five slots at `0x20015708`, one per module event class. The pinned
  registration topology (thirteen callsites) is slot 0 = material wall-clock/timezone
  transition, slot 1 = local-hour boundary, slot 2 = midnight follow-up (no subscribers in this
  image), slot 3 = sleep-status policy, slot 4 = wear-status policy; slot 4 carries six
  callbacks. Subscribe validates `slot < 5`, lazily creates the per-slot head, rejects a
  callback already present in the same slot (return 0), and otherwise appends at the tail with
  the caller's owner context (a default context when the caller passes none), returning 1.
- **Event-id windows.** The publisher's three first-match-wins compares accept
  `0x0001...0x0FFF` (sensor), then `0x1000...0x1FFF` (system), then `0x2000...0x2FFF`
  (storage; the third compare accepts any id below `0x3000`). Id zero and ids at or above
  `0x3000` match no window and are dropped with return 0. Each window selects its own queue;
  a NULL queue handle also returns 0.
- **Payloads and queue handoff.** The publisher builds a 12-byte record `{UInt32 event id,
  UInt32 payload length, 4-byte inline payload or heap pointer}`. Payloads up to 4 bytes are
  copied inline; larger payloads take a bounded heap copy that is freed when the queue send
  fails. Publish returns 1 on handoff, 0 otherwise; several pinned callers ignore the result.
  Observed pinned payloads range from 0 to 65 bytes (event `0x2004`), and the multicast
  republish wrapper adds an 8-byte header, so no pinned flow exceeds 73 bytes.
- **Multicast.** For a populated slot the multicast walks the subscriber list in registration
  order under the bus mutex. A payload under 5 bytes is additionally stashed inline in the slot
  head. Listeners owned by the calling context are invoked directly with the payload pointer;
  listeners owned by another context are notified through a two-entry context-to-event-id
  routing table that republishes `{subscriber head, UInt16 length, payload}` through the
  publisher, once per routing entry. An unpopulated slot returns 0. The stock multicast indexes
  the slot array without a bounds check.
- **Reset semantics.** The table is zero-filled BSS: at power-on every slot is empty and the
  first subscribe creates each slot head. No runtime clear exists in the stock image.

## Clean-room implementation

`r1_event_bus` is caller-owned state with no heap, no globals, and no hardware access:

- `r1_event_bus_subscribe` preserves slot validation, callback-identity duplicate rejection,
  and append-at-tail ordering over a fixed pool of eight listeners per slot
  (`R1_EVENT_BUS_SLOT_CAPACITY` covers the pinned maximum of six). A full slot returns
  `R1_ERROR_CAPACITY` instead of the stock allocation-failure halt; duplicates return
  `R1_ERROR_STATE`.
- `r1_event_bus_multicast` delivers to a slot's listeners in registration order with explicit
  pointer+length arguments (the stock callback receives only the pointer). The out-of-range
  slot index that stock firmware would dereference returns `R1_ERROR_ARGUMENT`. An empty slot
  is a successful zero-delivery reported through the delivered count, making the stock 0
  return explicit. The cross-context republish depends on the caller's RTOS task identity and
  a mutable routing table; it is left to the platform and is not recreated.
- `r1_event_bus_publish` classifies the exact three windows, stages one bounded copy of up to
  `R1_EVENT_BUS_PAYLOAD_LIMIT` (128) bytes — covering both the inline and heap-copy stock
  paths and every pinned call site — and hands a typed event record to the injected queue
  sink. Oversized payloads return `R1_ERROR_LENGTH`, an unbound sink returns
  `R1_ERROR_UNSUPPORTED` (the stock NULL queue-handle return 0), and a rejecting sink returns
  `R1_ERROR_CAPACITY` (the stock queue-full return 0).
- `r1_event_bus_reset` restores the zero-filled power-on state: no subscribers and no queue
  binding.

Security-relevant bounds: the slot index is validated before any table access, the subscriber
pool is fixed at eight per slot, and the staged payload copy is bounded at 128 bytes, so no
attacker-influenced length or slot value can drive an out-of-bounds access or unbounded
allocation. The stock allocation-failure infinite loops are not reproduced. No BLE command,
internal-event injection surface, flash mutation, or RTOS object is exposed.

## Platform queue binding (Nordic SDK)

Update (2026-08-14): the queue handoff is now bound in the SDK application by
`../../platform/nrf52840/sdk/openr1_event_bus.c`, following the established
`openr1_scheduler.c` queue/thread idiom (static CMSIS control blocks and stacks):

- One CMSIS message queue per event-id window (sensor, system, storage), each carrying the
  recovered 12-byte record `{UInt32 event id, UInt32 payload length, 4-byte inline payload or
  heap pointer}`. Payloads up to 4 bytes travel inline; larger payloads take a bounded heap
  copy (`R1_EVENT_BUS_PAYLOAD_LIMIT`, 128 bytes, is enforced by the publisher) that is freed
  when the queue send fails and after delivery. The per-window queue depth is 8, a local
  bound: the stock queue depths are not recovered.
- The sink never blocks: the queue put uses a zero timeout, so a full queue frees the heap
  copy and fails the handoff, which `r1_event_bus_publish` surfaces as `R1_ERROR_CAPACITY`
  (the stock queue-full return 0). The SoftDevice event thread can therefore publish without
  ever sleeping on a full queue.
- One consumer thread drains all three queues after a thread-flag wake and delivers each
  record through `r1_event_bus_multicast`.
- **Divergence.** The stock consumer-side per-id dispatch table (`0x0008D888`,
  `r1_event_dispatch_by_id`) and the two-entry cross-context republish routing table are not
  recovered — the routing table depends on RTOS task identity and mutable target state that
  the evidence does not pin. The consumer therefore delivers same-context to every populated
  slot in ascending slot order instead of republishing cross-context. No production publisher
  exists yet; a future publisher with class-specific listeners must first recover the
  id-to-slot mapping.
- `openr1_databases_initialize` binds the sink through `openr1_event_bus_bind`. A bind
  failure is recorded in the databases last-error word and leaves the sink unbound, so
  `r1_event_bus_publish` keeps returning `R1_ERROR_UNSUPPORTED`. The bus instance is
  reachable through `openr1_databases_event_bus`, and `openr1_event_bus_last_error` exposes
  the sticky first consumer-side failure; both are retained in the image for review.

The host test `test_event_bus_queue_roundtrip` models this contract end to end: the 12-byte
record, per-window bounded queues, inline and heap-copy payload staging, full-queue rejection
with heap-copy release, and same-context consumer multicast with post-delivery frees.

Host tests cover the window boundaries (`0x0000`/`0x0001`/`0x0FFF`/`0x1000`/`0x1FFF`/`0x2000`/
`0x2FFF`/`0x3000`), inline-limit and bounded-copy payloads, empty payloads, oversized payload
rejection, unbound and rejecting queue handoffs, duplicate and cross-slot subscriptions,
full-table refusal, multicast argument validation, empty-slot delivery, registration-order
fan-out, and reset semantics.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_frontier_128_202.py
python3 tools/evidence/summarize_r1_time_health_rollover.py
make -C r1 test && make -C r1 sanitize && make -C r1 arm-objects && make -C r1 sim
```
