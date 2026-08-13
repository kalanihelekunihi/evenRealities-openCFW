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

OpenR1 currently keeps the externally callable `advStart` command refused in the normal dispatcher
until durable target storage, current-peer lookup, delayed-disconnect scheduling, and role-aware
advertising integration are all bound and tested together. The recovered planner is admissible R1
behavior; enabling only a subset would create a misleading and potentially unsafe compatibility
surface.

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
