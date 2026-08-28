# G2 BLE OTA and Ring profile recovery

Status: OTA and Ring software closures are production-routed. Their hardware
validation is blocked by unavailable physical evidence.

This audit authenticates the last two retained paths under
`platform\ble\profiles`. OTA is a production-routed product adaptation of
AmbiqSuite's AMOTA application skeleton. Ring is a first-party product profile
with no matching public implementation and an independently authored
production implementation.

| module | physical interval | functions / body bytes | non-code | lineage |
|---|---:|---:|---:|---|
| OTA | `[0x004BDB90,0x004BDE4C)` | 7 / 620 | 80 | four Ambiq-skeleton derivatives, three G2-local adapters |
| Ring | `[0x004C46C0,0x004C4CEC)` | 7 / 1,446 | 134 | seven G2-local functions |

The analyzer authenticates all 14 bodies / 2,066 bytes, both complete physical
objects / 2,280 bytes, direct-start ingress, 112 body call sites, three stored
callbacks, retained paths, diagnostics, provider calls, and zero direct branch
targets in strict function interiors:

```text
make ble-ota-ring-profiles-closure
```

## AMOTA origin and version bound

G2 keeps four discriminating Ambiq AMOTA application choices:

- application events `0xA0` and `0xA1` remain reset and disconnect;
- the CCC handler retains the exact `ccc state ind value:%d handle:%d idx:%d`
  diagnostic and `ATTS_CCC_STATE_IND` role;
- a handler initializer stores the WSF handler and initializes the service
  provider;
- a public WSF handler wrapper dispatches into the profile message switch.

The public SparkFun history has four authenticated AmbiqSuite imports:

| release | commit | `amota_main.c` blob |
|---|---|---|
| 2.2.0 | `ca79fc6e140d25b0c596a5c87c3d311cd2710ad9` | `d52a9b38ac214bca0bf24cde9878905879928570` |
| 2.3.2 | `8f2a86b4b4a200291ea607fd94e585d6e4f15447` | `baeab1b7c8ee72f98f6c274b989c1d0b45d8f347` |
| 2.4.2 | `c4b62222921b1b87ddd21108cdaeaa4c4cf9f76d` | `fe280136fb8d0066e65d5bb0ff17aea765ab7690` |
| 2.5.1 | `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f` | `91a80afc7faea435e947a4e0c3841c41ba0ec481` |

The complete source changes at every import, while `amotaProcCccState` is
byte-identical across all four extracted sources (normalized extraction
SHA-256 `3742662b…e4a2`) and the event/handler skeleton survives. No
version-specific changed code remains in the small G2 wrapper, so the binary
cannot select one release. OpenCFW admits exact 2.5.1 source and headers under
`third_party/ambiqsuite-amota-profile` because the same authenticated release
is already selected for adjacent Ambiq/Cordio sources. This is a reproducible
oracle, not a claim that Even used commit `de5c6ba3` directly.

## G2 OTA delta

G2 replaces AMOTA's application/service state with a four-byte control block:
connection ID, handler ID, CCC-enabled flag, and connection-ready flag. The
reduced dispatcher handles connection/CCC events plus:

- `0xA0`: request product OTA reset;
- `0xA1`: close the active connection after a 200-unit timer;
- `0xA7`: send data through provider handle `0x0824`.

The stored `APP_EvenOtaWriteCback` forwards to the separate Even OTA provider.
The disconnect and send helpers allocate 12-byte WSF messages. These actions
are G2-local; upstream AMOTA supplies their ancestry and event semantics, not
source-identical implementations.

## OTA production closure

`components/apollo_main/core_overlay/ble_ota_profile.c` implements all seven
linked entries as BSD-3-Clause, selector-isolated C. Seven guarded redirects
replace all 620 stock body bytes with 376 compiled Thumb bytes plus eight
alignment bytes. Seventeen strict relocations bind only the recovered Cordio,
OTA, reset, connection, timer, and transport providers. The directly addressed
80-byte literal/callback pool remains authenticated stock data.

Host contracts cover the recovered CCC-message ABI, every event branch,
connection-role cancellation, reset/disconnect timing requests, allocation
failure, write forwarding, notification handle `0x0824`, and all seven target
selectors. The canonical Apple overlay/component/package are 193,066 /
3,716,462 / 4,494,956 bytes with SHA-256 values
`a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`,
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`,
and `03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.
The 1,963,573-byte flash plan hashes to
`ef7a204c200024422defd2cb9e0064a5aa4278bb14533e4007bd0daf2db1e67f`.
No hardware was accessed or flashed. OTA CCC, reset, disconnect, notification
timing, and peer interoperability are blocked by unavailable authorized
G2/EM9305 hardware or captured physical evidence.

## Ring production closure

Ring maintains a connection ID, handler ID, three-handle discovery list, and a
16-bit connection epoch. On connection open it discovers a 128-bit product
service, then schedules three epoch-qualified CCC writes at 500, 700, and 900
units. ATT events `0x05`, `0x0D`, and `0x0E` feed the matching RX handle.
Product event `0xAC` notifies through the discovered TX handle; its public send
helper allocates the same 12-byte WSF message shape used by the adjacent G2
adapters.

Exact searches for `APP_BleRingHandlerInit`, `_ringEnableCccd`, and the product
diagnostics found no public source. Neither AmbiqSuite nor public Packetcraft
contains this service. The Ring object therefore has no separate third-party
version or commit to recover.

`components/apollo_main/core_overlay/ble_ring_profile.c` independently
implements all seven linked entries as MIT, selector-isolated C.
Seven guarded redirects replace all 1,446 stock body bytes with 632 compiled
Thumb bytes plus eight alignment bytes. Twenty-three strict relocations bind
only the recovered Cordio discovery/ATT/WSF, connection-role, delayed-event,
and sibling-source interfaces. The directly addressed 134-byte callback and
literal pool remains authenticated stock data.

Host contracts cover the recovered 12-byte control/message ABIs, handler
initialization, service discovery, 16-bit epoch packing and cancellation,
500/700/900 delayed CCC writes, connect/close transitions, ATT RX forwarding,
TX command delivery, queued allocation, allocation failure, and all seven
target selectors. The same canonical image identities and deployment-plan pin
listed above authenticate this placement. No hardware was accessed or flashed.
Physical discovery, CCC timing, ATT handle behavior, controller concurrency,
and peer interoperability are blocked by unavailable authorized G2/EM9305
hardware or captured evidence.

## Boundary

No software gap remains in this two-module closure. Both modules still require
real dual-device/controller evidence; their physical gates are explicitly
blocked rather than treated as open software work. This does not assert wider
firmware completeness: other ledger rows remain open.
