# Runtime Startup and Task Model

This document is the clean-room runtime architecture baseline for the Apollo510b main image. It records what is identified strongly enough to shape `openCFW` startup, what is still inferred, and what must remain open.

## Identified Reset-to-Idle Chain

### Apollo Main Runtime

The currently anchored boot-to-runtime chain is:

```text
bootloader handoff
  -> app base 0x00438000
  -> reset entry 0x005C9776
     -> init-table walk 0x005C97F8
     -> startup hub 0x005B4088
     -> dynamic callback load from [0x20003DB4]
     -> callback value 0x00487423 (entry 0x00487422)
     -> worker bootstrap 0x004873F4
     -> stage2 worker 0x0048719C
     -> wait/tick loop
```

### Shared Runtime Descriptor Object

Top-level startup/runtime descriptor base:

- `0x20003DB4`

Identified fields:

| Offset | State | Meaning |
|---|---|---|
| `+0x00` | Identified | startup callback pointer |
| `+0x04` | Partial | teardown/secondary callback seed |
| `+0x08` | Identified | worker handle field populated after bootstrap |
| `+0x1C` | Partial | wait/sync field used by runtime helpers |

### Worker Bring-Up

The post-dispatch chain is anchored strongly enough to preserve this model:

```text
0x00487422
  -> kernel-start prepare
  -> thread create (entry 0x004873F5)
0x004873F4
  -> writes worker handle to [0x20003DB4 + 0x08]
  -> creates next worker (entry 0x0048719D)
0x0048719C
  -> runtime setup helpers
  -> steady wait/tick loop
```

### Wait/Idle Mechanics

Instruction-level closure now identifies:

- event wait with timeout
- tick read
- loop backedges
- descriptor waiter using `[0x20003DB4 + 0x1C]`

This is enough to preserve the architectural pattern:

- descriptor-seeded bootstrap
- worker creation in stages
- event-driven steady-state loop rather than a monolithic polling loop

## Identified Task Ownership

String and call-tree evidence close the major runtime task families:

| Task / Area | State | Notes |
|---|---|---|
| `thread_ble_msgrx` | Identified | BLE receive/service dispatch entry |
| `thread_ble_msgtx` | Identified | BLE response and outbound queue path |
| `thread_ble_wsf` | Identified | Cordio/WSF wait domain |
| `thread_input` | Identified | touch/input event handling |
| `thread_audio` | Identified | codec/audio runtime path |
| `thread_ring` | Identified | ring relay/runtime lane |
| `thread_notification` | Identified | notification/file-related user event path |
| `thread_evenai` | Identified | voice/EvenAI task family |
| `display_thread` | Identified | display/render ownership |
| thread-pool workers | Partial | general async worker pool exists; full role split is not closed |

## Identified Internal Ownership Graph

The main control flow from BLE service routing into subsystems is:

```text
BLE RX task
  -> service handler
     -> display path -> display_thread -> JBD driver
     -> settings/input path -> touch/gesture/wear logic
     -> audio path -> codec host/dfu boundary
     -> ring path -> ring relay handlers
     -> case path -> box UART relay
  -> BLE notify/response path
```

This model is strong enough for a clean-room runtime skeleton.

## Inferred but Not Fully Closed

| Area | Current Inference | Why It Is Not Fully Closed |
|---|---|---|
| OS-wrapper names | `os_thread_create`, `os_event_wait_timeout`, `os_event_wait_ex`, and related helper names match observed semantics | Names are semantic lifts, not vendor symbols |
| Scheduler-core backend names | helper families under `0x452*`, `0x453*`, `0x476*` correspond to thread/event primitives | Exact RTOS-family equivalence is still not fully proven |
| Descriptor fan-out object list | sub-descriptor table under `0x00487548` likely corresponds to runtime callback domains | Exact ownership of each sub-descriptor remains incomplete |
| Thread-pool role split | worker pool supports general asynchronous work across services | exact queue ownership and dispatch policy remain open |
| Left/right runtime authority | left/right role split is real, with master/slave behavior and mixed audio/ring ownership | exact ownership split for some runtime paths remains mixed in evidence |

## Unidentified / Still Open

| Area | Why It Matters |
|---|---|
| Full symbolized reset-to-idle call graph | Needed for a faithful startup rewrite rather than a compatible skeleton |
| Exact meaning of descriptor field `+0x04` | Needed if `openCFW` mirrors the full descriptor object layout |
| Exact ownership of each descriptor-fanout child object | Needed for higher-fidelity runtime service/task decomposition |
| Exact task/queue mapping for all worker-pool lanes | Needed before claiming scheduler parity |
| Complete left/right/ring authority split | Needed for multi-endpoint correctness |

## Clean-Room Guidance

- Preserve a staged startup model: early init, descriptor/context seed, worker/task creation, then event-driven steady state.
- Model the top-level runtime around explicit task ownership rather than a single giant dispatcher.
- Treat helper names as semantic labels only.
- Keep left/right role handling configurable until authority closure is tighter.

## Source Documents

- `../firmware/device-boot-call-trees.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/g2-service-handler-index.md`
- `../firmware/re-gaps-tracker.md`
- `../firmware/analysis/2026-03-05-g2-reset-startup-callgraph.md`
- `../firmware/analysis/2026-03-05-g2-runtime-entry-chain.md`
- `../firmware/analysis/2026-03-05-g2-os-wrapper-semantics.md`
- `../firmware/analysis/2026-03-05-g2-scheduler-core-semantics.md`
- `../firmware/analysis/2026-03-05-g2-idle-wait-calltree.md`
