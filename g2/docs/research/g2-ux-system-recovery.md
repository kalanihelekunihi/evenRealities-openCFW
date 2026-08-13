# G2 UX system-status object and provider recovery

Status: read-only, fail-closed closure of the stock 2.2.6.10
`app\ux\ux_system\ux_system.c` translation unit. No overlay, package, signer,
flash, BLE, filesystem, or hardware state is changed.

## Result

The retained path originally appeared to own one 88-byte Ghidra function.
That function is only `RPC_SyncRingStatusWithPeer`. The same path pointer is
referenced nineteen times across the surrounding code, and a stored Thumb
pointer at `0x006A4744` recovers the 2,232-byte
`UX_LocalSystemStatusSyncHandler` that baseline Ghidra missed.

The complete object is `[0x0047CE90,0x0047D9C4)`: eleven functions / 2,668
function-envelope bytes followed by one 200-byte compiler pool, for 2,868
physical bytes. Recursive Thumb recovery reaches all 985 instructions and all
2,668 body bytes; there are no embedded data islands.

| Function | Stock interval | Bytes | Recovery basis |
|---|---:|---:|---|
| peer BLE-status sender | `[0x0047CE90,0x0047CED6)` | 70 | two internal calls |
| peer ring-status sender | `[0x0047CED6,0x0047CF28)` | 82 | two internal calls |
| peer ring-query sender | `[0x0047CF28,0x0047CF60)` | 56 | one internal call |
| `UX_LocalSystemStatusSyncHandler` | `[0x0047CF60,0x0047D818)` | 2,232 | exact retained name/path and stored callback |
| `RPC_SyncRingStatusWithPeer` | `[0x0047D818,0x0047D870)` | 88 | exact retained name/path and two external calls |
| BLE-status reply sender | `[0x0047D870,0x0047D8B8)` | 72 | four external calls |
| self/peer OTA getters | `[0x0047D8B8,0x0047D8CE)` | 22 | two external calls |
| `UX_GetSystemBLEStatus` | `[0x0047D8CE,0x0047D8E4)` | 22 | exact retained diagnostic and 33 calls |
| self/peer ring getters | `[0x0047D8E4,0x0047D8FC)` | 24 | five external calls |

Ten functions were already defined in the immutable 7,370-function corpus;
only the stored status handler was absent. A clean no-analysis Ghidra replay
seeded at `0x0047CF60` independently recovered its full return and decompiled
the same dispatch. The checked analyzer reconstructs every function from the
authenticated image and rejects escaped branches, unresolved jump tables,
interior entries, or unaccounted targets.

## Status protocol

The callback consumes an eight-byte record whose first word selects the
following retained diagnostic IDs:

| ID | Retained name | State effect |
|---:|---|---|
| 1 | `SYSTEM_OTA_STATUS_ID` | updates self/peer OTA bits 0/1 and drives the OTA/display transition path |
| 2 | `SYSTEM_BLE_STATUS_ID` | updates self/peer BLE bits 2/3; states 2/3 also clear/set the appropriate ring bit |
| 3 | `SYSTEM_BLE_STATUS_REPLY_ID` | accepts a peer BLE reply and updates bit 3 |
| 4 | `SYSTEM_BLE_STATUS_RING_MAC_SET_ID` | updates bit 6 and clears both ring bits when the MAC becomes unset |
| 5 | `SYSTEM_BLE_STATUS_RING_QUERY_ID` | returns current ring status when the receiving side owns the ring |
| 6 | `SYSTEM_BLE_STATUS_RING_REPLY_ID` | applies the peer ring reply to bit 5 and ring-connect state |

The packed byte at `0x20075043` therefore contains self/peer OTA in bits 0/1,
self/peer BLE in bits 2/3, self/peer ring state in bits 4/5, and the ring-MAC
flag in bit 6. `UX_GetSystemBLEStatus` is true only when both BLE bits are set.
Changes to that aggregate status emit `CB_EVENT_BLE_STATUS_CHANGE` through the
existing first-party event provider.

The three peer helpers send service `0x0103` records containing message ID,
self role, peer role, and state. `RPC_SyncRingStatusWithPeer` first calls the
already closed `APP_MasterRingMacIsSet`; if no MAC exists it logs and returns.
Otherwise ring ownership selects either a status record or a query. The reply
helper posts the same eight-byte shape through the local message path.

## Dependency and commit result

No third-party implementation is embedded. The 147 external direct calls are:

| Boundary | Calls | Source state |
|---|---:|---|
| EasyLogger diagnostics | 95 | 2.2.99-equivalent core; selected `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| G2 role and system lifecycle policy | 35 | private first-party providers |
| G2 status RPC and event transport | 8 | private first-party providers |
| G2 BLE central ring policy | 9 | already object-closed first-party providers |

The object has no direct CMSIS-FreeRTOS, Cordio, nanopb, littlefs, DLIB, or
other utility call. EasyLogger supplies diagnostics only and contributes no
status algorithm. Consequently this pass adds no dependency family, no new
version discriminator, and no candidate upstream commit that could supply the
private UX policy. The exact `ux_system.c` source and producing Even commit
remain unavailable.

## Topology and boundary

Fifty-one image-wide BL sites land on reviewed entries: sixteen are internal
and 35 external. The handler has the sole stored Thumb pointer. There are zero
BL decodes to strict interiors and zero unrecovered direct targets inside the
physical object.

The object starts immediately after an independent IAR arithmetic-runtime
function ending at `0x0047CE90`. Its 200-byte terminal pool contains all
status strings, templates, the packed-state address, and the single retained
path pointer. Code resumes at `0x0047D9C4` with a separate ring-policy helper
cluster that calls the public getters but does not reference this path.

The production overlay contains no UX-system source or redirect. A future
clean-room replacement must define the eight-byte status ABI and validate
role, OTA/display, BLE, and ring transitions on disposable paired hardware
before production admission.

## Reproduction

```sh
make ux-system-closure
```

This authenticates the functions, compiler pool, retained strings and path,
all call edges, stored callback, adjacent boundaries, EasyLogger source pin,
and aggregate first-party frontier. It performs no hardware operation.
