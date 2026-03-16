# Kernel and Scheduler Architecture

> Analysis performed 2026-03-05. Firmware binaries from `captures/firmware/g2_extracted/`.

---

## 1. OS Wrapper Semantics (Startup-to-Idle Chain)

Firmware: `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin`

### Wrapper Semantic Map

| Wrapper | Inferred Symbol | Inferred Semantic | Kernel/Helper Calls |
|---:|---|---|---|
| `0x004477A2` | `os_ctx_guard` | execution-context guard (ISR/critical-section/scheduler-state check) | kernel_scheduler_state (0x00453B30) |
| `0x004477D0` | `os_kernel_start_prepare` | kernel-start gate wrapper | kernel_scheduler_state (0x00453B30) |
| `0x00447800` | `os_kernel_start_release` | kernel-start release/activate wrapper | kernel_scheduler_state (0x00453B30) |
| `0x00447838` | `os_tick_now` | tick/time read wrapper (ISR-aware) | kernel_tick_now_isr (0x00453192), kernel_tick_now (0x0045318A) |
| `0x0044784E` | `os_thread_create` | thread create wrapper (static/dynamic TCB path) | kernel_thread_create_static (0x00452AAC), kernel_thread_create_dynamic (0x00452B46) |
| `0x00447916` | `os_thread_activate` | thread activate/resume wrapper | kernel_thread_activate (0x00453B28) |
| `0x00447950` | `os_thread_close` | thread close/terminate wrapper | kernel_thread_state (0x00452E14), kernel_thread_terminate (0x00452D3A) |
| `0x0044798A` | `os_event_wait` | event-flag wait wrapper (ISR-aware backend switch) | kernel_event_op_isr (0x0045404C), kernel_event_op_isr (0x0045404C), kernel_event_op (0x00453ED4), kernel_event_op (0x00453ED4) |
| `0x00447A14` | `os_event_wait_timeout` | event-flag wait with timeout/mask semantics | kernel_tick_now (0x0045318A), kernel_event_wait (0x00453E10), kernel_tick_now (0x0045318A) |
| `0x00447DEC` | `os_event_wait_ex` | extended event wait wrapper (mode bits + timeout result codes) | kernel_event_wait_ex (0x00476F50) |

### Runtime Chain -> Wrapper Callsites

| Runtime Stage | Callsite | Wrapper | Symbol |
|---|---:|---:|---|
| dispatch-entry | `0x00487424` | `0x004477D0` | `os_kernel_start_prepare` |
| dispatch-entry | `0x0048742E` | `0x0044784E` | `os_thread_create` |
| dispatch-entry | `0x00487444` | `0x00447800` | `os_kernel_start_release` |
| stage1-worker-bootstrap | `0x004873FE` | `0x0044784E` | `os_thread_create` |
| stage1-worker-bootstrap | `0x00487418` | `0x00447916` | `os_thread_activate` |
| stage1-worker-bootstrap | `0x0048741C` | `0x00447950` | `os_thread_close` |
| stage2-supervisor-loop | `0x0048721A` | `0x00447A14` | `os_event_wait_timeout` |
| stage2-supervisor-loop | `0x00487220` | `0x00447838` | `os_tick_now` |
| stage2-descriptor-waiter | `0x00486E86` | `0x0044798A` | `os_event_wait` |
| stage2-descriptor-waiter | `0x00486E98` | `0x00447DEC` | `os_event_wait_ex` |

### Evidence Snippets

#### `0x004477A2` `os_ctx_guard`

- `0x004477A6`: `mrs r0, ipsr`
- `0x004477BA`: `mrs r0, primask`
- `0x004477C2`: `mrs r0, basepri`

#### `0x004477D0` `os_kernel_start_prepare`

- `0x004477D2`: `bl #0x4477a2`
- `0x004477E8`: `ldr.w r1, [pc, #0x5fc]`
- `0x004477F4`: `str r0, [r1]`

#### `0x00447800` `os_kernel_start_release`

- `0x00447802`: `bl #0x4477a2`
- `0x00447822`: `bl #0x4477a0`
- `0x0044782A`: `bl #0x452f78`

#### `0x00447838` `os_tick_now`

- `0x0044783A`: `bl #0x4477a2`
- `0x00447842`: `bl #0x453192`
- `0x00447848`: `bl #0x45318a`

#### `0x0044784E` `os_thread_create`

- `0x0044785C`: `bl #0x4477a2`
- `0x004478EC`: `bl #0x452aac`
- `0x00447904`: `bl #0x452b46`

#### `0x00447916` `os_thread_activate`

- `0x00447918`: `bl #0x453b28`

#### `0x00447950` `os_thread_close`

- `0x0044796E`: `bl #0x452e14`
- `0x0044797C`: `bl #0x452d3a`

#### `0x0044798A` `os_event_wait`

- `0x004479A8`: `bl #0x4477a2`
- `0x004479C4`: `bl #0x45404c`
- `0x004479FA`: `bl #0x453ed4`
- `0x00447A0A`: `bl #0x453ed4`

#### `0x00447A14` `os_event_wait_timeout`

- `0x00447A1E`: `bl #0x4477a2`
- `0x00447A48`: `bl #0x45318a`
- `0x00447A5A`: `bl #0x453e10`
- `0x00447A90`: `bl #0x45318a`

#### `0x00447DEC` `os_event_wait_ex`

- `0x00447E06`: `bl #0x4477a2`
- `0x00447E38`: `bl #0x476f50`

### Interpretation

- Startup callback chain now resolves to named wrapper semantics: context guard, kernel-start gate, thread create/activate/close, and event wait primitives.
- Stage2 idle behavior is concretely an event-flag wait loop (`os_event_wait_timeout`) with tick/time reads (`os_tick_now`).
- Descriptor waiter paths use event waits (`os_event_wait`, `os_event_wait_ex`), consistent with user-impact trigger handling from BLE/input/ring events.

---

## 2. Scheduler Core (Wrapper Backends)

Firmware: `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin`

### Helper Semantic Map

| Helper | Inferred Symbol | Inferred Semantic | Direct Helper Calls | Xref Count |
|---:|---|---|---|---:|
| `0x00452AAC` | `kernel_thread_create_static` | create thread object from provided static control block | kernel_thread_init_core (0x00452BC4), kernel_thread_ready_insert (0x00452C88), kernel_thread_init_core (0x00452BC4), kernel_thread_ready_insert (0x00452C88) | 3 |
| `0x00452B46` | `kernel_thread_create_dynamic` | allocate/create dynamic stack + control block for thread | kernel_thread_init_core (0x00452BC4), kernel_thread_ready_insert (0x00452C88) | 3 |
| `0x00452BC4` | `kernel_thread_init_core` | initialize thread metadata/priority/queues in TCB | _none_ | 2 |
| `0x00452C88` | `kernel_thread_ready_insert` | insert thread into ready structures and update scheduler counters | _none_ | 2 |
| `0x00452D3A` | `kernel_thread_terminate` | remove thread from scheduler lists and terminate/free resources | _none_ | 4 |
| `0x00452E14` | `kernel_thread_state_classify` | classify thread state for close/terminate gating | _none_ | 2 |
| `0x0045318A` | `kernel_tick_now` | read current system tick/timebase | _none_ | 8 |
| `0x00453192` | `kernel_tick_now_isr` | read tick/timebase in ISR-safe path | _none_ | 1 |
| `0x00453B28` | `kernel_thread_activate` | activate/resume thread in scheduler | _none_ | 7 |
| `0x00453B30` | `kernel_scheduler_state` | query scheduler/dispatch state | _none_ | 9 |
| `0x00453E10` | `kernel_event_wait` | wait on event flags with optional timeout and mask | _none_ | 2 |
| `0x00453ED4` | `kernel_event_op` | event flag operations (set/clear/inc/mode variants) in thread context | _none_ | 4 |
| `0x0045404C` | `kernel_event_op_isr` | event flag operations in ISR/critical context | _none_ | 3 |
| `0x00476F50` | `kernel_event_wait_ex` | extended event wait helper used by wait_ex wrapper | kernel_scheduler_state (0x00453B30) | 2 |

### Wrapper -> Helper Mapping

| Wrapper | Helper | Callsites |
|---|---|---|
| `os_ctx_guard (0x004477A2)` | `kernel_scheduler_state (0x00453B30)` | 0x004477B2 |
| `os_kernel_start_prepare (0x004477D0)` | `kernel_scheduler_state (0x00453B30)` | 0x004477E0 |
| `os_kernel_start_release (0x00447800)` | `kernel_scheduler_state (0x00453B30)` | 0x00447810 |
| `os_tick_now (0x00447838)` | `kernel_tick_now (0x0045318A)` | 0x00447848 |
| `os_tick_now (0x00447838)` | `kernel_tick_now_isr (0x00453192)` | 0x00447842 |
| `os_thread_create (0x0044784E)` | `kernel_thread_create_static (0x00452AAC)` | 0x004478EC |
| `os_thread_create (0x0044784E)` | `kernel_thread_create_dynamic (0x00452B46)` | 0x00447904 |
| `os_thread_activate (0x00447916)` | `kernel_thread_activate (0x00453B28)` | 0x00447918 |
| `os_thread_close (0x00447950)` | `kernel_thread_terminate (0x00452D3A)` | 0x0044797C |
| `os_thread_close (0x00447950)` | `kernel_thread_state_classify (0x00452E14)` | 0x0044796E |
| `os_event_wait (0x0044798A)` | `kernel_event_op (0x00453ED4)` | 0x004479FA, 0x00447A0A |
| `os_event_wait (0x0044798A)` | `kernel_event_op_isr (0x0045404C)` | 0x004479C4, 0x004479D8 |
| `os_event_wait_timeout (0x00447A14)` | `kernel_tick_now (0x0045318A)` | 0x00447A48, 0x00447A90 |
| `os_event_wait_timeout (0x00447A14)` | `kernel_event_wait (0x00453E10)` | 0x00447A5A |
| `os_event_wait_ex (0x00447DEC)` | `kernel_event_wait_ex (0x00476F50)` | 0x00447E38 |

### Cross-Domain Caller Samples

| Helper | Caller Region Buckets | Sample Callsites |
|---|---|---|
| `kernel_thread_create_static` | 0x00440000:1, 0x00450000:1, 0x00470000:1 | 0x004478EC, 0x00452FAA, 0x004767C6 |
| `kernel_thread_create_dynamic` | 0x00440000:1, 0x004C0000:1, 0x004D0000:1 | 0x00447904, 0x004CE1A0, 0x004D43AC |
| `kernel_thread_init_core` | 0x00450000:2 | 0x00452B2E, 0x00452BAC |
| `kernel_thread_ready_insert` | 0x00450000:2 | 0x00452B34, 0x00452BB2 |
| `kernel_thread_terminate` | 0x004C0000:2, 0x00440000:1, 0x004D0000:1 | 0x0044797C, 0x004CE1C4, 0x004CE2E4, 0x004D43DE |
| `kernel_thread_state_classify` | 0x00440000:1, 0x00450000:1 | 0x0044796E, 0x00453A1A |
| `kernel_tick_now` | 0x00440000:3, 0x00480000:2, 0x00470000:1, 0x00490000:1, 0x004F0000:1 | 0x00447848, 0x00447A48, 0x00447A90, 0x00476A2A, 0x00486C06, 0x00486CCE, 0x00493764, 0x004FD38A |
| `kernel_tick_now_isr` | 0x00440000:1 | 0x00447842 |
| `kernel_thread_activate` | 0x00440000:2, 0x00470000:2, 0x004C0000:1, 0x004D0000:1, 0x00510000:1 | 0x00447918, 0x00448FAA, 0x004773C8, 0x0047740A, 0x004CE264, 0x004D43DA, 0x0051D620 |
| `kernel_scheduler_state` | 0x00470000:5, 0x00440000:4 | 0x004477B2, 0x004477E0, 0x00447810, 0x00448FA2, 0x004768EE, 0x00476F9C, 0x004774F4, 0x004777EA, 0x00477916 |
| `kernel_event_wait` | 0x00440000:1, 0x00510000:1 | 0x00447A5A, 0x0051D638 |
| `kernel_event_op` | 0x00440000:2, 0x004C0000:1, 0x00510000:1 | 0x004479FA, 0x00447A0A, 0x004CE2C4, 0x0051D682 |
| `kernel_event_op_isr` | 0x00440000:2, 0x00510000:1 | 0x004479C4, 0x004479D8, 0x0051D552 |
| `kernel_event_wait_ex` | 0x00440000:1, 0x00480000:1 | 0x00447E38, 0x0048852A |

### Evidence Snippets

#### `0x00452AAC` `kernel_thread_create_static`

- `0x00452B10`: `str r4, [r5, #0x30]`
- `0x00452B2E`: `bl #0x452bc4`
- `0x00452B34`: `bl #0x452c88`

#### `0x00452B46` `kernel_thread_create_dynamic`

- `0x00452B58`: `bl #0x476ca4`
- `0x00452B64`: `bl #0x476ca4`
- `0x00452BAC`: `bl #0x452bc4`
- `0x00452BB2`: `bl #0x452c88`

#### `0x00452BC4` `kernel_thread_init_core`

- `0x00452C02`: `str.w sb, [r6, #0x54]`
- `0x00452C4E`: `str.w sb, [r6, #0x2c]`
- `0x00452C78`: `bl #0x441212`

#### `0x00452C88` `kernel_thread_ready_insert`

- `0x00452C94`: `ldr r0, [r1]`
- `0x00452CA4`: `str r4, [r5]`
- `0x00452CD6`: `ldr.w r0, [pc, #0x760]`
- `0x00452D1C`: `bl #0x4411a0`

#### `0x00452D3A` `kernel_thread_terminate`

- `0x00452D50`: `bl #0x486480`
- `0x00452D76`: `adds r1, r4, #4`
- `0x00452D96`: `bl #0x453b02`
- `0x00452DA6`: `bl #0x453ac2`

#### `0x00452E14` `kernel_thread_state_classify`

- `0x00452E3E`: `ldr.w r0, [pc, #0x8bc]`
- `0x00452E56`: `movs r0, #2`
- `0x00452E94`: `movs r0, #4`

#### `0x00453E10` `kernel_event_wait`

- `0x00453E3A`: `ldrb.w r0, [r0, #0x6c]`
- `0x00453E58`: `movs r1, #1`
- `0x00453E96`: `ldr r0, [r6]`
- `0x00453EA2`: `add.w r0, r0, r4, lsl #2`

#### `0x00453ED4` `kernel_event_op`

- `0x00453F2A`: `uxtb.w sb, sb`
- `0x00453F46`: `add.w r0, r6, r4, lsl #2`
- `0x00453F6A`: `add.w r0, r6, r4, lsl #2`
- `0x00453F74`: `movs r0, r1`

#### `0x0045404C` `kernel_event_op_isr`

- `0x004540A6`: `cmp.w sb, #0`
- `0x004540BE`: `add.w r1, r7, r4, lsl #2`
- `0x004540E2`: `add.w r1, r7, r4, lsl #2`
- `0x004540EC`: `movs r1, r2`

### Interpretation

- Startup wrappers now have explicit scheduler-core backends, reducing symbol ambiguity around thread creation, ready-list insertion, and event wait operations.
- Helper xrefs appear in multiple address regions beyond startup stages, supporting that these semantics are runtime-wide primitives rather than startup-local stubs.
- Remaining ambiguity is mostly RTOS-internal naming granularity, not call-tree ownership from boot to idle.

---

## 3. Idle/Wait Calltree

Firmware: `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin`

### Startup-to-Worker Anchor

```
0x005B415C: load callback from [0x20003DB4] -> 0x00487423
0x00487422: dispatch callback entry (Thumb ptr 0x00487423)
stage2 worker analyzed: 0x004871BC
```

### Stage-2 Wait Loop

- loop interval constant: `0x0000EA60` at `0x0048722E`
- primary wait calls:
  - `0x0048723A` -> `os_event_wait_timeout` (`0x00447A34`)
  - `0x00487240` -> `os_tick_now` (`0x00447858`)
- recovered backedges:
  - `0x0048724C` -> `0x00487228` (blo)
  - `0x00487252` -> `0x0048722E` (blo)
  - `0x00487256` -> `0x0048722E` (b)

### Event-Dispatch Lanes (Stage-2)

| Callsite | Gate Shift (`lsls r0,r4,#N`) | Dispatcher |
|---:|---:|---:|
| `0x004872B4` | `26` | `0x00487074` |
| `0x004872FE` | `31` | `0x00487074` |
| `0x00487342` | `30` | `0x00487074` |
| `0x00487386` | `29` | `0x00487074` |
| `0x004873CA` | `28` | `0x00487074` |
| `0x0048740E` | `27` | `0x00487074` |

### Descriptor Waiter Helper

- descriptor base literal: `0x20003DB4` with field read `+0x1C` at `0x00486EB6`
- waiter calls:
  - `0x00486EA6` -> `os_event_wait` (`0x004479AA`)
  - `0x00486EB8` -> `os_event_wait_ex` (`0x00447E0C`)

### Interpretation

- The stage-2 worker has a stable poll/wait backedge loop centered on `os_event_wait_timeout` + `os_tick_now`, matching idle/event-wait behavior.
- Event bitmasks are fanned into `0x00487074` through repeated bit-gate lanes in `0x00487258`, then control returns to the wait loop.
- Descriptor-side waits in `0x00486E9A` read a `+0x1C` field from a runtime object and use both normal and extended wait wrappers, supporting descriptor-mediated idle gating.

---

## 4. Box Firmware Task Map

Firmware: `captures/firmware/g2_extracted/firmware_box.bin`

### Main Handoff to Scheduler

| Callsite | Callee |
|---:|---:|
| `0x0800A4DE` | `0x08002F64` |
| `0x0800A4E2` | `0x0800A6F0` |
| `0x0800A4E6` | `0x0800678C` |
| `0x0800A4EA` | `0x0800A718` |

- fallback trap branch: `0x0800A4EE` -> `0x0800A4EE`

### Scheduler Object Bring-Up (0x0800678C)

#### Thread-Like Objects (`0x0800A860`)

| Callsite | Entry Ptr | Entry Fn | Ctx Ptr (`r3`) | Handle Slot | Priority Arg (`r1`) |
|---:|---:|---:|---:|---:|---:|
| `0x08006796` | `0x08009B89` | `0x08009B88` | `0x0800D084` | `0x10` | `0` |
| `0x080067A8` | `0x0800B965` | `0x0800B964` | `0x0800D0A4` | `0x18` | `1` |
| `0x080067B8` | `0x0800949D` | `0x0800949C` | `0x0800D0B4` | `0x1C` | `1` |
| `0x080067C8` | `0x0800B605` | `0x0800B604` | `0x0800D0C4` | `0x20` | `1` |
| `0x080067D8` | `0x0800B9A9` | `0x0800B9A8` | `0x0800D094` | `0x14` | `0` |
| `0x080067E8` | `0x0800A989` | `0x0800A988` | `0x0800D0D4` | `0x24` | `0` |

#### Queue/Wait Objects (`0x0800A754`) and Pool Init (`0x0800A64E`)

| Callsite | Wrapper | Entry Ptr | Ctx/Arg Ptr | Handle Slot |
|---:|---:|---:|---:|---:|
| `0x080067F6` | `0x0800A754` | `0x08006C41` | `0x0800D108` | `0x2C` |
| `0x08006804` | `0x0800A754` | `0x08007D45` | `0x0800D12C` | `0x30` |
| `0x08006812` | `0x0800A754` | `0x08007025` | `0x0800D150` | `0x34` |
| `0x08006820` | `0x0800A754` | `0x08008105` | `0x0800D0E4` | `0x28` |
| `0x0800682A` | `0x0800A64E` | `0x0800D084` | `-` | `0x38` |

### Task Entry Wait/Loop Signatures

#### `0x08009B88`

- wait-primitive calls: _none in sampled entry range_
- backedges: _none in sampled entry range_
- transitive wait wrappers: _none detected_
- idle/wfi evidence: _none detected_

#### `0x0800B964`

- wait-primitive calls: _none in sampled entry range_
- backedges: _none in sampled entry range_
- transitive wait wrappers: _none detected_
- idle/wfi evidence: _none detected_

#### `0x0800949C`

- wait-primitive calls: _none in sampled entry range_
- backedges: _none in sampled entry range_
- transitive wait wrappers: _none detected_
- idle/wfi evidence: _none detected_

#### `0x0800B604`

- wait-primitive calls: _none in sampled entry range_
- backedges: _none in sampled entry range_
- transitive wait wrappers: _none detected_
- idle/wfi evidence: _none detected_

#### `0x0800B9A8`

- wait-primitive calls: _none in sampled entry range_
- backedges: _none in sampled entry range_
- transitive wait wrappers: _none detected_
- idle/wfi evidence: _none detected_

#### `0x0800A988`

- wait-primitive calls: _none in sampled entry range_
- backedges: _none in sampled entry range_
- transitive wait wrappers: _none detected_
- idle/wfi evidence: _none detected_

#### `0x08006C40`

- wait-primitive calls:
  - `0x08006C68` -> `os_event_bits_wrapper` (`0x0800A5EA`)
  - `0x08006C7E` -> `os_event_bits_wrapper` (`0x0800A5EA`)
  - `0x08006C8C` -> `os_event_bits_wrapper` (`0x0800A5EA`)
  - `0x08006CB2` -> `os_event_bits_wrapper` (`0x0800A5EA`)
  - `0x08006CDA` -> `os_event_bits_wrapper` (`0x0800A5EA`)
  - `0x08006D62` -> `os_event_bits_wrapper` (`0x0800A5EA`)
  - `0x08006DEC` -> `os_event_bits_wrapper` (`0x0800A5EA`)
  - `0x08006E14` -> `os_event_bits_wrapper` (`0x0800A5EA`)
  - `0x08006E3C` -> `os_event_bits_wrapper` (`0x0800A5EA`)
  - `0x08006E84` -> `os_ctx_guard_wrapper` (`0x0800A5C8`)
  - `0x08006ECC` -> `os_ctx_guard_wrapper` (`0x0800A5C8`)
  - `0x08006F1E` -> `os_event_bits_wrapper` (`0x0800A5EA`)
  - `0x08006F50` -> `os_ctx_guard_wrapper` (`0x0800A5C8`)
- backedges:
  - `0x08006CE8` -> `0x08006CD2` (b)
  - `0x08006D1E` -> `0x08006D12` (b)
  - `0x08006D4C` -> `0x08006D2E` (b)
  - `0x08006D98` -> `0x08006D58` (b)
  - `0x08006D9C` -> `0x08006D8C` (b)
  - `0x08006DDA` -> `0x08006DB4` (b)
- transitive wait wrappers:
  - `0x08006C68 -> 0x0800A5EA` (os_event_bits_wrapper); nested: kernel_event_clear@0x0800C264
  - `0x08006C7E -> 0x0800A5EA` (os_event_bits_wrapper); nested: kernel_event_clear@0x0800C264
  - `0x08006C8C -> 0x0800A5EA` (os_event_bits_wrapper); nested: kernel_event_clear@0x0800C264
  - `0x08006CB2 -> 0x0800A5EA` (os_event_bits_wrapper); nested: kernel_event_clear@0x0800C264
  - `0x08006CDA -> 0x0800A5EA` (os_event_bits_wrapper); nested: kernel_event_clear@0x0800C264
  - `0x08006D32 -> 0x08002550` (callee_wait_wrapper); nested: os_ctx_guard_wrapper@0x0800A5C8
  - `0x08006D62 -> 0x0800A5EA` (os_event_bits_wrapper); nested: kernel_event_clear@0x0800C264
  - `0x08006DB8 -> 0x08002550` (callee_wait_wrapper); nested: os_ctx_guard_wrapper@0x0800A5C8
- idle/wfi evidence: _none detected_

#### `0x08007D44`

- wait-primitive calls:
  - `0x08007EE0` -> `transport_wait_step` (`0x080034FC`)
  - `0x08007EEA` -> `transport_wait_step` (`0x080034FC`)
  - `0x08007F0C` -> `arch_idle_wfi` (`0x08004EE8`)
  - `0x08007FA6` -> `os_ctx_guard_wrapper` (`0x0800A5C8`)
- backedges:
  - `0x08007F6E` -> `0x08007F56` (bne)
  - `0x08007F7C` -> `0x08007F56` (b)
  - `0x08007FAA` -> `0x08007D58` (b)
  - `0x08007FDC` -> `0x08007F80` (bpl)
- transitive wait wrappers:
  - `0x08007D58 -> 0x08002A2C` (callee_wait_wrapper); nested: transport_wait_step@0x080034FC
  - `0x08007EF6 -> 0x08002BE8` (callee_wait_wrapper); nested: transport_wait_step@0x080034FC
- idle/wfi evidence:
  - `0x08007F0C -> 0x08004EE8` (arch_idle_wfi); wfi/wfe at 0x08004EFE

#### `0x08007024`

- wait-primitive calls:
  - `0x080070A8` -> `transport_wait_step` (`0x080034FC`)
  - `0x080070B2` -> `transport_wait_step` (`0x080034FC`)
  - `0x080070D4` -> `arch_idle_wfi` (`0x08004EE8`)
  - `0x08007156` -> `transport_wait_step` (`0x080034FC`)
  - `0x08007160` -> `transport_wait_step` (`0x080034FC`)
  - `0x08007186` -> `arch_idle_wfi` (`0x08004EE8`)
- backedges:
  - `0x080070D8` -> `0x08007076` (b)
  - `0x080072BA` -> `0x0800728E` (b)
  - `0x080072EC` -> `0x0800719C` (b)
  - `0x080072F6` -> `0x080072EC` (bne)
  - `0x080072FE` -> `0x080072EC` (bne)
  - `0x08007334` -> `0x0800719C` (b)
- transitive wait wrappers:
  - `0x080070BE -> 0x08002BE8` (callee_wait_wrapper); nested: transport_wait_step@0x080034FC
  - `0x0800716C -> 0x08002BE8` (callee_wait_wrapper); nested: transport_wait_step@0x080034FC
  - `0x080073A6 -> 0x0800BCA8` (callee_wait_wrapper); nested: os_ctx_guard_wrapper@0x0800A5C8
- idle/wfi evidence:
  - `0x080070D4 -> 0x08004EE8` (arch_idle_wfi); wfi/wfe at 0x08004EFE
  - `0x08007186 -> 0x08004EE8` (arch_idle_wfi); wfi/wfe at 0x08004EFE

#### `0x08008104`

- wait-primitive calls:
  - `0x08008132` -> `os_ctx_guard_wrapper` (`0x0800A5C8`)
  - `0x080081C0` -> `os_ctx_guard_wrapper` (`0x0800A5C8`)
- backedges:
  - `0x08008174` -> `0x08008160` (b)
  - `0x08008178` -> `0x0800816A` (b)
  - `0x080081C4` -> `0x08008118` (b)
  - `0x080081CA` -> `0x080081BE` (b)
- transitive wait wrappers: _none detected_
- idle/wfi evidence: _none detected_

### Scheduler Start Gate

- `0x0800A718` checks scheduler state (`==1`), updates to `2`, then calls `0x0800C09C`.
- `0x0800C09C` runs kernel-start path and transitions to runtime scheduler context.
- core wait setup call observed in start path: `0x0800C0C2 -> 0x0800C81E` (`kernel_wait_queue_wait_ex`).

### Interpretation

- Case boot now has instruction-level proof from app-main into scheduler object creation, then scheduler-start handoff, with a fallback trap branch only if start returns.
- `0x0800678C` builds multiple worker domains (thread-like + queue/wait objects) backed by distinct context sub-structures under a common runtime table.
- This narrows the idle boundary: steady wait behavior is owned by scheduler-started tasks rather than the app-main function body.
- Queue-domain task paths now include explicit low-power idle evidence via `arch_idle_wfi` (`0x08004EE8`, `wfi` at `0x08004EFE`).
