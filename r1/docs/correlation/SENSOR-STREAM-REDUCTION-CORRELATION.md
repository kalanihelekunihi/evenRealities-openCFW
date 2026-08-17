# Sensor-stream framework reduction correlation (owner-authorized, 2026-08)

## Decision

Under the "Owner-authorized full reduction (2026-08-14)" section of
[`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md), the 32-function family
`unknown_sensor_stream_framework_candidate` is reduced from the recovered
decompilation evidence to compilable C at
[`../../reconstructed/sensor_stream/`](../../reconstructed/sensor_stream/).
The reconstruction is not vendor source and is never presented as such;
every file carries the provenance banner.  The boundary doc
[`../boundaries/SENSOR-STREAM-FRAMEWORK-BOUNDARY.md`](../boundaries/SENSOR-STREAM-FRAMEWORK-BOUNDARY.md)
remains the provenance record of why no upstream source could be admitted.

Stock image: application, load base `0x00027000`, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

## Evidence extraction path

- Ghidra bodies: `research/decompilation/application/decompiler-output.c`
  (all 32 entries present; none required re-disassembly).
- Literal pools, the pooled `"acc"`/`"temp"` name bytes (`0x00089D98` =
  `0x00636361`, `0x0008A1BC` = `0x706d6574`), the const provider vtables at
  `0x0009A590` (acc -> R1 motion adapter hooks `0x0006F401` open /
  `0x0006F301` close / `0x0006F4A1` read) and `0x0009A5A8` (temp -> R1
  product hooks `0x000918FD`/`0x000918F9`/`0x00091901`), the dispatch Thumb
  pointer `0x0008A1E1` at `0x00089ACC`, the `bx lr` keep-alive callback
  `0x0008A559` at `0x0008A580`, and the RAM state roots were read from the
  byte-exact rebuilt image
  (`research/decompilation/rebuild/rebuilt-application.bin`).
- Callee attribution (per `docs/FUNCTION-OWNERSHIP.csv`):
  `0x000855A0`/`0x00095D48` = FreeRTOS heap (Nordic port family);
  `0x0005D8E6` (first), `0x0005D8EE` (next), `0x0005D998` (remove),
  `0x0005D94A` (push-back allocate), `0x00077E30`/`0x00077E3C`
  (one-instruction link setters) = generic-registry family (still blocked);
  `0x0007D28C` = CMSIS-FreeRTOS tick fallback; `0x000914EC`/`0x00091638` =
  R1 log-level/tagged-log path, `0x000799C0`/`0x000799C8`/`0x000799D6` =
  Nordic nRF_LOG backend; `0x000277AA`/`0x0002775C`/`0x000277F0`/
  `0x000277FE` = toolchain memset/memmove/strlen/strcmp thunks;
  `0x00089EEC` = R1 product stream-namespace creation (a caller, not part of
  the family).

## Recovered layout

- Stream object (`0x38` bytes): `+0x00` inline 8-byte name (NUL-padded),
  `+0x0C` provider vtable (`+0x00` open, `+0x04` close, `+0x08` read; hooks
  receive the stored context), `+0x10` current aggregate rate byte, `+0x14`
  sample buffer (`rate * sample_size * 2` bytes), `+0x18` write cursor /
  valid-bytes, `+0x1C` sample size uint16, `+0x20` timer node, `+0x24`
  context, `+0x28` flags (bit 0 timer-to-list-back, bit 1 dispatch active,
  bit 2 pending unregister), `+0x2C` embedded listener-list descriptor.
- Listener node (`0x18` payload + 8 link bytes): `+0x00` owner object,
  `+0x04` 8-byte capped name (tail not cleared), `+0x0D` requested rate
  ("ord") byte, `+0x0E` mode byte (0 batch at wrap, 1 per-sample with
  fractional accumulator), `+0x10` callback, `+0x14` uint16 flags (bit 0
  deferred-delete, bits 1..15 rate accumulator).  Links: previous at
  node+stride, next at node+stride+4.
- Timer node (`0x18` payload + links): `+0x00` period ticks, `+0x04` last
  expiry tick, `+0x08` callback, `+0x0C` context (stream object for the
  dispatch), `+0x10` repeat (`0xFFFFFFFF` = forever), `+0x14` flags (bit 0
  stopped, bit 1 active/auto-release).
- Registry node (`8`-byte payload + links): `+0x04` object pointer; payload
  word 0 is never initialized by stock.
- List descriptor: `+0x00` link stride (`align4(payload)`), `+0x04` head,
  `+0x08` tail.
- Housekeeping block (stock `0x2001A2BC`, `0x30` bytes): timer-list
  descriptor at `+0x00`, enabled `+0x0C`, drift-correction byte `+0x0D`
  (`100 - busy%`, `0` when the percentage reaches 101; the recovered
  constant is the ASCII `'d'`), released-during-poll `+0x0E`,
  created-during-poll `+0x0F`, next-wakeup `+0x10`, poll reentrancy guard
  `+0x14`, drift busy-tick accumulator `+0x1C`, drift window mark `+0x20`,
  zero-tick quirk counter `+0x24` (bumps when the tick source reads 0, wraps
  past 100), wake hook/context `+0x28`/`+0x2C`.
- Further roots: registry descriptor `0x2001A1B0`, sink staging block
  `0x2001A1BC..0x2001A293` (4-word descriptor `+0x00`, 6-word `+0x10`,
  6-word sign-extending `+0x28`, clamped triples `+0xC0`/`+0xCC`), tick-hook
  RAM word `0x2001A2AC+8` (overrides the CMSIS fallback when non-NULL).
- The reconstruction static-asserts every recovered offset for the 32-bit
  target ABI only; on wider host ABIs the C layout legitimately widens, and
  the link stride/offset arithmetic adapts to the pointer width (same clause
  as the rtc_device pilot).

## Per-function contract and reconstruction decisions

| Stock extent | Bytes | Reconstructed symbol | Contract |
| --- | ---: | --- | --- |
| `0x0005D8FE..<0x0005D90D` | 16 | `sensor_stream_list_descriptor_init` | stride = align4(payload), head/tail NULL |
| `0x0005D90E..<0x0005D949` | 60 | `sensor_stream_list_push_front_allocate` | allocate stride+8 node, push front, fix head/tail; NULL on allocation failure; the two one-instruction registry-family link setters are inlined |
| `0x0005D986..<0x0005D997` | 18 | `sensor_stream_list_idle` | 1 when descriptor NULL or both heads NULL |
| `0x0007D0D8..<0x0007D153` | 122 | `sensor_stream_resample_copy` | nearest-neighbour resample: count = min(target, round(min(valid, source)*target/source)), source index `(i*source)/target` clamped to valid-1; returns bytes copied; 0 on any NULL/zero argument |
| `0x000896F0..<0x000897B7` | 200 | `sensor_stream_object_create` | hard-faults on NULL name/provider or zero sample size (reconstruction: fault hook + NULL); 0x38 alloc, zero, clear flags bits 1-2, name cap 8, listener descriptor stride 0x18, conditional context store, registry insert (insert failure logged, object still returned) |
| `0x000897E8..<0x0008984B` | 100 | `sensor_stream_register_by_name` | lookup by stream name; NULL + `register not find obj:%s` when unknown |
| `0x00089890..<0x00089A60` | 464 | `sensor_stream_listener_register` | rate capped at 1 (`only support 1 ord`); first listener sets object rate, allocates `rate*sample_size*2`, runs the optional open hook, starts the timer at `1024/rate` (front/back per object flags bit 0); later higher rate resizes via the resample helper and retimes (`reset timer,%s, tick:%d`) |
| `0x00089B08..<0x0008A1AA` | 562 (4 ranges) | `sensor_stream_listener_unregister` | exact-pointer match; during dispatch mark + defer; otherwise immediate remove/free, then max-rate shrink + retime, or buffer/timer release + optional close hook on empty |
| `0x00089D54..<0x00089D83` | 48 | `sensor_stream_object_lookup` | registry walk with stride-nonzero guard; name compare; NULL when absent |
| `0x00089D88..<0x00089D93` | 12 | `sensor_stream_acc_object_create` | fixed `create("acc", 0xBC, vtable 0x9A590, NULL)`; vtable bound explicitly (R1 motion adapter family) |
| `0x00089D9C..<0x00089DF7` | 92 | `sensor_stream_object_insert` | lazy descriptor init (stride 8), push-back node, `+0x04` = object; 0 + `list insert fail` on failure |
| `0x00089E50..<0x00089E87` | 56 | `sensor_stream_sink_triple_clamped_secondary` | max(0, *x/y/z) into sinks +0xCC/D0/D4 |
| `0x00089E8C..<0x00089EC3` | 56 | `sensor_stream_sink_triple_clamped_primary` | max(0, *x/y/z) into sinks +0xC0/C4/C8 |
| `0x00089EC8..<0x00089ED1` | 10 | `sensor_stream_sink_store4` | 4-word staging store at sinks +0x00 |
| `0x00089ED8..<0x00089EE5` | 14 | `sensor_stream_sink_store6` | 6-word staging store at sinks +0x10 |
| `0x0008A03C..<0x0008A04D` | 18 | `sensor_stream_sink_store6_sign_extended` | 6-word staging store at sinks +0x28, fourth word sign-extended from int8 |
| `0x0008A1AC..<0x0008A1B7` | 12 | `sensor_stream_temp_object_create` | fixed `create("temp", 2, vtable 0x9A5A8, NULL)`; vtable bound explicitly (R1 product family) |
| `0x0008A1C4..<0x0008A1CF` | 12 | `sensor_stream_ticks_elapsed` | `tick_now() - then`, 32-bit wrap |
| `0x0008A1D0..<0x0008A1DB` | 12 | `sensor_stream_tick_now` | RAM hook when installed, else CMSIS fallback; explicit 0 when neither is bound |
| `0x0008A1E0..<0x0008A310` | 422 (2 ranges) | `sensor_stream_timer_dispatch` | validate provider read/buffer/rate/sample-size; stale-cursor reset; one sample read at the cursor; cursor advance/wrap; listener walk under dispatch bit 1 skipping deferred entries; mode 1 per-sample (fractional accumulator) and mode 0 batch-at-wrap (rate match: `chunk & 0xFFFF`; mismatch: resample into the second buffer half); clear bit 1; pending bit 2 -> deferred removal + rebalance/release tail |
| `0x0008A310..<0x0008A363` | 84 | `sensor_stream_timer_create_front` | push-front node; period/callback/context/last stored; repeat `0xFFFFFFFF`; flags bit 1; created mark; kick |
| `0x0008A368..<0x0008A3BB` | 84 | `sensor_stream_timer_create_back` | same via the registry-family push-back provider |
| `0x0008A3C0..<0x0008A3EB` | 44 | `sensor_stream_timer_release` | remove from timer list, released mark, free; NULL hard-faults in stock |
| `0x0008A3F0..<0x0008A3FD` | 14 | `sensor_stream_housekeeping_enable` | store enable byte; kick when nonzero |
| `0x0008A404..<0x0008A457` | 84 | `sensor_stream_timer_expire` | stopped -> 0; on expiry decrement positive repeat, record tick, fire callback unless repeat was 0; exhausted timers auto-release (flags bit 1) or stop |
| `0x0008A45C..<0x0008A539` | 222 | `sensor_stream_timer_poll` | reentrancy/disabled -> 1; expiry scan with rescan on create/release marks; minimum remaining (0xFFFFFFFF when idle); busy-tick accumulation; every >499-tick window store `100 - busy%` (0 at >=101); zero-tick quirk counter |
| `0x0008A540..<0x0008A551` | 18 | `sensor_stream_housekeeping_kick` | clear next-wakeup; invoke optional wake hook with its context |
| `0x0008A55C..<0x0008A57B` | 32 | `sensor_stream_initialize` (recovered tail) | timer-list init (stride 0x18), enable(1) + kick, 1000-tick keep-alive timer whose callback is the `bx lr` stub `0x0008A558` |
| `0x0008A584..<0x0008A59D` | 26 | `sensor_stream_timer_stop` | set flags bit 0; NULL hard-faults in stock |
| `0x0008A5C0..<0x0008A5CF` | 16 | `sensor_stream_object_set_back_insert` | bit-0 insert into object flags; NULL object silently ignored (kept) |
| `0x0008A5D0..<0x0008A5E3` | 20 | `sensor_stream_timer_set_period` | period store; NULL hard-faults in stock |
| `0x0008A5E4..<0x0008A5FB` | 24 | `sensor_stream_timer_remaining` | saturating `period - elapsed`, 0 once elapsed >= period |

## Divergences from the stock binary (all deliberate)

1. **Explicit provider bindings.**  Stock calls the FreeRTOS heap, the
   registry-family list walkers, the CMSIS tick fallback, and the
   nRF_LOG/RTT path directly.  The reconstruction binds each through
   `sensor_stream_providers`; unbound mandatory providers fail explicitly
   (NULL/false/no-op) instead of faulting.  The two singleton vtables (R1
   motion adapter / R1 product code) bind through
   `sensor_stream_bind_singleton_providers`, and the RAM tick hook through
   `sensor_stream_set_tick_hook`.
2. **Fault loops become explicit failures.**  Stock hangs in a privileged
   `setBasePriority` loop on NULL object/name/listener/timer arguments and
   on buffer/timer allocation failure.  The reconstruction invokes the
   optional fault hook (the target `app_error` path does not return) and
   then returns NULL / returns early.
3. **Zero-rate first registration.**  Stock computes a zero buffer size,
   the heap returns NULL, and the fault loop hangs (the listener stays
   registered).  The reconstruction faults explicitly before allocating;
   the partial state (registered listener, no buffer) is preserved.
4. **Timer flags word zeroed at creation.**  Stock node memory is not
   cleared, so the upper flags bits held heap garbage; the reconstruction
   zeroes the word before the recovered bit operations.
5. **Timer callback arity.**  Stock stores the raw dispatch address and
   invokes it with the node; the reconstruction's callback type carries the
   explicit framework state as a first argument (the node still carries the
   stream-object context at `+0x0C`).  Observable behavior is unchanged.
6. **Dead-store elision.**  The drift byte's intermediate store of the raw
   percentage (immediately overwritten) is collapsed to the final value.
7. **Diagnostics surfaced, not emitted.**  The recovered message strings
   (`lisent register fail` including the typo, `only support 1 ord`,
   `reset timer,%s, tick:%d`, `register not find obj:%s`, `unregister not
   find obj:%s`, `%s not found in %s, skip unregister`, `obj malloc fail`,
   `list insert fail`) reach the optional diagnostic hook with the first
   argument; actual formatting/transport stays with the Nordic/SEGGER
   logging providers.
8. **No libc in the freestanding unit.**  Name compare/copy, zeroing, and
   the resample element copies use local loops, matching the r1
   freestanding convention (no `string.h`).
9. **Host-ABI link arithmetic.**  On 64-bit hosts the link words widen; the
   node stride and link offsets adapt to the pointer width while every
   recovered 32-bit layout is static-asserted for the target ABI.

Preserved exactly: the 8-byte name caps (listener name tail not cleared),
the rate cap at 1 with its diagnostic, the `1024/rate` period formula, the
`rate*sample_size*2` buffer with second-half scratch, the cursor wrap and
stale-cursor reset, the `chunk & 0xFFFF` batch-length truncation, the
fractional accumulator including its bit-0 preservation, the
deferred-unregister protocol (bits and ordering), the max-rate shrink with
resample of the valid bytes, the empty-list release ordering (buffer, then
timer, then close hook with the stored context), the repeat-count expiry
semantics, the rescan-on-change poll loop, the `100 - busy%` drift byte
with its 499-tick window and 101 clamp, the zero-tick counter quirk, and
the 1000-tick no-op keep-alive timer created at initialization.

## Host test mapping (`tests/test_reconstructed_sensor_stream.c`)

- `test_sensor_stream_list_primitives`: stride alignment, idle polarity
  (NULL descriptor is idle), push-front link integrity, allocation failure,
  unbound allocator.
- `test_sensor_stream_resample_copy`: identity, 4->2 decimation (indices
  0/2), 2->4 upsampling (0/0/1/1), valid-bytes clamp, element size 2,
  rounded-to-zero production, every malformed argument.
- `test_sensor_stream_object_lifecycle` / `.._object_insert_paths`: field
  layout, name cap and truncation, registry visibility, insert-failure
  quirk (object still returned, `list insert fail`), bad-argument fault
  hook, `obj malloc fail`, uninitialized-registry and unbound-provider
  lookups.
- `test_sensor_stream_registration`: unknown-stream diagnostic, NULL
  faults, first-listener buffer/open/timer (`1024` ticks, front vs back
  insertion), rate cap diagnostic, zero-rate explicit fault with preserved
  partial state, buffer OOM fault.
- `test_sensor_stream_dispatch_per_sample`: short-read suppression,
  per-sample delivery, fractional accumulator (constructed aggregate rate
  2), NULL-callback and deferred-listener skips, validation chain.
- `test_sensor_stream_dispatch_batch`: wrap-only delivery, chunk length,
  mismatch resample into the scratch half, unused mode bytes never fire.
- `test_sensor_stream_unregistration` / `.._rebalance`: unknown-stream /
  unknown-listener diagnostics, deferred removal completed by the dispatch
  tail (three frees, close hook with context), same-rate no-op removal,
  max-rate shrink (`4 -> 2`, period `512`, cursor `8`, `reset timer`
  diagnostic), empty-list release.
- `test_sensor_stream_timer_creation_and_release` / `.._small_ops`: node
  fields, front/back order, kick/wake hook, release marks, stop/period
  stores, NULL faults.
- `test_sensor_stream_timer_expiry_and_poll`: remaining-time saturation,
  one-shot auto-release, exhausted-stop path, disabled/reentrant poll
  returns 1, idle minimum `0xFFFFFFFF`.
- `test_sensor_stream_poll_rescan_and_drift`: expiry during poll, the
  zero-tick counter (increments at tick 0, wraps past 100), drift byte
  (`100 - 0%` at the first window, `93` for a scripted busy window), hook
  override/unhook, 32-bit tick wraparound.
- `test_sensor_stream_tick_sources` / `.._singletons` / `.._sinks`: hook
  precedence and explicit zero, acc/temp fixed configuration (sizes 0xBC/2)
  and unbound failure, staging stores with int8 sign extension, clamped
  triples, NULL no-ops.

## Integration state

The module carries host tests and compiles under the strict host flags and
the freestanding Cortex-M4 object flags. The source-built Zephyr target now
initializes and polls the framework on the recovered 1,024-Hz timebase, binds
its heap to Zephyr, composes its list seams with the reconstructed generic
device-registry list family, and creates the fixed `"acc"`/`0xBC` and
`"temp"`/two-byte singletons. The accelerometer vtable reads the installed Bosch/ST FIFO through the typed
motion adapter, builds the exact 188-byte batch, applies persisted `nv_r1`
axis offsets, and exposes typed listener registration/unregistration. The
temperature vtable binds the exact no-op open/close hooks at `0x000918F8` and
`0x000918FC` and the `0x00091900` two-byte read hook to one calibrated GXT310
pair. It validates the exact length, stores UInt16LE, and exposes the same typed
listener lifecycle. No listener is invented at startup. The separately evidenced
temperature one-shot control now registers `"once"` only on an explicit call and composes the
five-sample event/cache path; other GoMore/activity consumers still require separately admitted
bindings.
