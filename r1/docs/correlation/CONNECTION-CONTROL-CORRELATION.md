# R1 BLE connection-control correlation

Snapshot: 2026-08-13.

## Closure

The application function at `0x00045184` is admitted as R1 product orchestration, not as Nordic,
Arm, FreeRTOS, or another third-party implementation. Ghidra inventories 1,736 executable bytes.
Its complete image-locked range is `0x00045184..<0x00045B16` (2,450 bytes including embedded
literal and diagnostic-string islands) with SHA-256
`084b42ae5e9f0fd5e5c7942052086d26ab67b547a666b87c7fcf8982858bcac1`.

The only direct caller is `0x00091FD2`, the BLE-thread lifecycle. The body repeatedly receives a
pointer from authenticated CMSIS-FreeRTOS `osMessageQueueGet`, switches on R1 event IDs, invokes
bounded product role/address/advertising seams, and finally releases the event with authenticated
FreeRTOS `vPortFree`.

| Recovered route | Product behavior |
| --- | --- |
| event `0x00000002` | consume `pairAuth` role selection, update phone/glasses state, and request Peer Manager security when the phone link is not encrypted |
| events `0x10`, `0x20`, `0x40` | forward recovered connection lifecycle states to the product notification seam |
| event `0x00000200` | compare a connected glasses peer with either supplied six-byte target, disconnect a mismatch, store both targets, then choose fast advertising or stop advertising from role occupancy |
| event `0x00004000` | replace the two persisted target addresses |

The Ghidra-omitted delayed callback at `0x000882AC..<0x000882EC` is also admitted as R1 product
orchestration (64 bytes, SHA-256
`28d8568d7f96013e7c9255881ce0b659f1ed3071d7bd35492f99de6ad18027ab`). Its argument packs a
16-bit connection/context above an eight-bit selector. A `0xFFFF` context returns without an
effect; selectors `0`, `1`, and `2` enqueue the empty connection-lifecycle events `0x40`, `0x10`,
and `0x20`; other selectors enter the fatal-error boundary. The transparent
`r1_connection_control_delayed_event_plan` in `../../src/r1_peer_target.c` reproduces only that
deterministic route as `IGNORE`, `ENQUEUE`, or `FATAL`. Six recovered callback-pointer literals
are byte-pinned; live BLE-thread queueing and fatal/log implementations remain external.

The event consumer is therefore recorded as `r1_product_specific` with disposition
`clean_room_behavior_only` and clean symbol `r1_ble_connection_control_event_consumer`. This is an
ownership/admission result, not a claim that recovered C syntax, private helper bodies, or linked
addresses are reproduced.

## `pairAuth` contract

The system handler at `0x000842EC` uses a 12-byte protocol header. Any declared length other than
12 is treated as payload-present in stock firmware; it does not perform a minimum one-byte bound.
Value `01` assigns or checks the incoming session as the phone role, queues event type `2`, then
replies on that incoming session with one zero byte. The handler does not perform a cryptographic
challenge and role assignment is not product authorization.

The event consumer checks the link's encrypted state. If it is not encrypted, it calls Nordic
`pm_conn_secure(connection, false)` and tolerates `NRF_SUCCESS` and `NRF_ERROR_BUSY` (`0x11`). If
already encrypted it schedules the recovered follow-up timing. OpenR1 preserves the secure provider
boundary: Peer Manager owns pairing, bonding, encryption, FDS data, and security-event dispatch.
The local runtime also hardens the stock route by rejecting short payloads and duplicate role
ownership; a bond remains transport identity and does not set `authorized`.

## `advStart` and two-target contract

The handler at `0x00083D04` requires 12 payload bytes representing two independent six-byte target
addresses. Stock accepts declared lengths `0...11` because of unsigned 16-bit subtraction wrap and
rejects declared lengths `12...23`; this unsafe malformed-frame behavior is evidence only and is
not reproduced. On its successful route the response is sent before allocation or queue delivery,
and event `0x200` uses the current EUS session rather than the incoming request session. Allocation
or queue failure is therefore not reflected in the stock response.

The consumer:

1. reads the connected glasses peer address when a glasses link exists;
2. accepts a match against either supplied target (no right/left meaning is assigned);
3. schedules disconnect after raw delay `0x5000` for a nonmatching peer;
4. stores both targets even after a mismatch and persists them at device-info offsets 8 and 14;
5. starts fast advertising mode `3` when either phone or glasses is absent; or
6. stops advertising when both roles are occupied and the connected glasses address matched.

The official two-target store does not contain a phone address. The exact persistent setter at
`0x000738A8` has only three direct callers: reset erases both slots at `0x00046052`, the store path
writes both at `0x0004D9E2`, and `removeRingNotify` erases both at `0x000844E6`.

OpenR1 keeps the externally callable `advStart` command refused in the normal dispatcher:
product authorization remains fail-closed and unrefusing requires the bound composition to
pass end-to-end authorization and owned-hardware validation. As of 2026-08-14 the
composition itself is bound and host-tested behind that refusal:

- `r1_connection_control_plan_adv_start` (in `../../src/r1_peer_target.c`) composes the
  recovered consumer policy over the existing target-validity and match helpers: store both
  targets unconditionally, schedule the raw `0x5000` delayed disconnect for a mismatching
  connected glasses peer, start fast advertising while either role is unoccupied, and stop
  advertising only when both roles are occupied and the peer matched.
- `r1_peer_target_persist` writes both targets at device-info offsets 8 and 14; the SDK
  `openr1_connection_control_adv_start` entry point drives it through the
  production-initialized `r1_kv_store` (`kv.bin`), reads the connected glasses peer address
  from the GAP connected-event cache in `openr1_bae8`, schedules the disconnect through
  `r1_delayed_event_schedule`, and drives the Nordic `ble_advertising` start/stop hooks.

The delayed-event timer driver is now bound (update 2026-08-14): a CMSIS one-shot timer in
`../../platform/nrf52840/sdk/openr1_connection_control.c` steps the portable
`r1_delayed_event_state` through `r1_delayed_event_timer_step`, and a fired disconnect event
issues Nordic `sd_ble_gap_disconnect` with
`BLE_HCI_REMOTE_USER_TERMINATED_CONNECTION`, tolerating an already-closed handle
(`BLE_ERROR_INVALID_CONN_HANDLE`) as the desired end state. The millisecond delay is
converted to kernel ticks with `osKernelGetTickFreq` (the recovered 1,024-Hz tick), rounding
up and never arming a zero-tick timer; the stock empty-table `0xFFFFFFFF`-millisecond reload
is suppressed because it carries no event. A mutex serializes the scheduler path against the
timer-daemon callback. One binding stays deliberately unbound rather than inventing
behavior: command/peer byte-order reconciliation with the first-party sender (an e2e
validation concern). The durability commit is fail-closed: a kv persist failure blocks the
disconnect and advertising actions, and a full delayed-event table or timer failure is
recorded but tolerated, matching the stock response-before-effect ordering.
Host tests cover the planner branches, the offset-8/14 persistence, a full kv commit/reopen
cycle over memory flash, and the delayed-event schedule composition.

Update (2026-08-13): the Nordic SDK application now binds the role-occupancy half of this
contract. `openr1_advertising_set_role_occupancy` reads phone/glasses occupancy from the runtime
link roles through `r1_runtime_role_occupancy` and drives the official `ble_advertising` provider:
fast advertising runs while either role is unoccupied and advertising stops once both roles are
occupied. The binding fires on pair-role assignment (the registered role handler) and on link
disconnect. In the SDK application today the only role-assignment signal is `pairAuth` selecting
the phone role; the glasses-role planner (`r1_runtime_plan_bae8_event` link groups) still has no
bound channel parser, so glasses occupancy never becomes true on target and the both-occupied stop
path is unreachable until that binding lands. Unassigned links occupy no role.

## Provider boundary

This function calls source-routed provider functions as callees; their implementation does not
become part of the R1 product closure:

- Nordic SDK 17.1.0: `pm_conn_secure` and exact `nrf_log_frontend_std_0`,
  `nrf_log_frontend_std_1`, and `nrf_log_frontend_std_3` bodies;
- Arm CMSIS-FreeRTOS 10.5.1: `osMessageQueueGet`; and
- authenticated FreeRTOS-Kernel 10.5.1: `vPortFree`.

The adjacent common logging facade at `0x000914EC` and `0x00091638` is not Nordic's frontend
family. It remains unclassified along with unresolved timer/role/accessor callees. Classifying the
event consumer does not absorb, recreate, or grant implementation permission for any such callee.

The linked target already uses official Nordic Peer Manager and `ble_advertising` providers for
the admitted portions. Local code is limited to recovered R1 configuration, role policy, bounded
address planning, and adapters into those providers.

## Reproducible evidence

Run:

```sh
python3 tools/evidence/summarize_r1_connection_control.py \
  research/decompilation/rebuild/rebuilt-application.bin
python3 tools/evidence/emulate_r1_connection_control.py \
  research/decompilation/rebuild/rebuilt-application.bin
```

The summarizer authenticates the application image, ten related ranges, both registration records,
the complete direct-call sets for the event consumer and its critical role/security/address/
advertising operations, malformed-length boundaries, and the product/provider split. The emulator
executes 11 production-Thumb handler groups in private RAM with role, Peer Manager, response,
allocation, queue, timer, disconnect, advertising, persistence, and live-address effects
intercepted. It does not access BLE or physical hardware.
