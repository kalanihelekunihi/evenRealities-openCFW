# G2 EvenAI timer recovery

The authenticated G2 2.2.6.10 Apollo image retains
`app\gui\EvenAI\even_ai_timer.c`. Its two path-correlated Ghidra bodies are a
lower bound, not the linked object: source-order control-flow recovery closes
13 functions across physical interval `[0x004E2E10,0x004E31CC)`. The object is
956 bytes: 856 reachable instruction bytes and one 100-byte compiler literal
pool. The complete interval, every body, all 57 direct calls, all 28 direct BL
entries, the absence of stored entry pointers/indirect calls/interior targets,
and both adjacent boundaries are hash-pinned by
`tools/analyze_g2_even_ai_timer.py`.

## Recovered object

The object owns parallel common and heartbeat state machines. Each uses a
12-byte private record:

| Offset | Field |
|---:|---|
| `+0x00` | start tick |
| `+0x04` | duration in ticks |
| `+0x08` | state (`1` armed, `2` expired) |
| `+0x09` | armed flag |

The common record is at `0x20074008`; the heartbeat record follows at
`0x20074014`. Start records the current tick and requested duration only when
the first-party role predicate returns one. Check uses wrap-safe unsigned
arithmetic, `(current_tick - start_tick) >= duration`, then changes state to
two and disarms. Stop and deinit both clear state and armed. The aggregate
start wrapper passes the caller's interval to the common timer and fixes the
heartbeat interval at 10,000 ticks. One common-timeout branch restarts the
common timer at 3,000 ticks. Aggregate deinit, start, and process wrappers close
the final three source-order bodies.

Six functions have exact retained diagnostic names: common/heartbeat deinit,
stop, and process-timeout. The two starts, two checks, and three aggregate
wrappers use explicitly qualified semantic labels. A historical, differently
addressed firmware decompilation corroborates several names and the same state
machine shape, but is not accepted as source or boundary evidence.

## Third-party provider closure

There are 45 direct external calls:

| Provider | Calls | Provenance result |
|---|---:|---|
| EasyLogger | 30 | Source-admitted 2.2.99-equivalent core, selected commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`; G2 adapters remain separately bounded |
| CMSIS-FreeRTOS `osKernelGetTickCount` | 4 | Exact v10.5.1 `cmsis_os2.c` family, selected commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`; CMSIS_5 5.9.0 dependency commit `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c` |
| IAR DLIB `memset` | 1 | Bounded/recreated runtime leaf; EWARM 9.20+ floor and 9.60.2 leading candidate remain unchanged |
| G2 role, sync, and EvenAI service policy | 10 | First-party provider seams at `0x0045A568`, `0x00464F76`, `0x0049832E`, and `0x00498528` |

The key negative result is that this translation unit does **not** use
`osTimerNew`, `osTimerStart`, FreeRTOS software timers, or any embedded timer
implementation. It is first-party tick/deadline logic over the already
source-owned CMSIS tick wrapper. Consequently it yields no new third-party
version discriminator and leaves no opaque third-party definition inside the
object.

## Production source route

`components/apollo_main/core_overlay/even_ai_timer.c` now implements all 13
functions as C over explicit tick, role, sync, state, and control-provider
seams. The route preserves the two private records, unsigned wrap-safe expiry,
role-one start gate, fixed 10,000/3,000 tick intervals, sync payload `{7,7,4}`,
and EvenAI control command three. Diagnostic-only EasyLogger calls are omitted.

Each function is compiled in isolation and admitted under strict relocation
contracts for both reviewed compiler profiles. The linked leaves total 502
bytes in both `apple-clang` and `linux-clang`, use 22 reviewed relocations, and
replace all 856 stock instruction bytes. Portable runtime tests cover role
gating, ordinary and wrapping deadlines, timeout state transitions, payload
and provider calls, fixed restart intervals, and aggregate lifecycle wrappers.
The 100-byte stock literal/diagnostic pool remains typed retained data rather
than executable software.

The software functional gap is closed. Live scheduler timing, shared-state
concurrency, EvenAI service integration, and BLE synchronization validation is
**blocked by unavailable physical evidence**; no hardware operations were
performed and this result does not declare firmware functional completeness.
