# G2 BLE OTA and Ring profile recovery

Status: authenticated object closure and AMOTA provenance recovery; no
production routing.

This audit closes the last two open retained paths under
`platform\ble\profiles`. OTA is a product rewrite of AmbiqSuite's AMOTA
application skeleton. Ring is a first-party product profile with no matching
public implementation.

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

## Ring boundary

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

## Boundary

The source oracle and both stock objects remain production-excluded. A future
implementation must qualify WSF allocation, service discovery, ATT handle
lifetimes, delayed CCC cancellation/epoch behavior, OTA reset/disconnect
timing, and real dual-device/controller behavior before routing.
