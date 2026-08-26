# Cordio DM main-router source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The stock `dm_main.c` translation unit is completely bounded at
`[0x004D299C,0x004D2B98)`: all 16 source functions survive, totaling 484
code bytes plus a 24-byte literal gap. The 508-byte physical interval hashes
to `b45dd5bb498ca7f31fc5c60b4eea5571d0a3a76b279d93831641302c463674de`.
Twenty-nine direct calls, fifteen aligned stored entry pointers, and zero
strict-interior pointers close ingress. No API is source-only.

All sixteen definitions are now implemented and production-routed. Fourteen
guarded redirects plus two exact two-byte copies cover all 484 stock body
bytes with 524 compiled Cortex-M55 bytes plus 20 alignment bytes under two
strict relocations.

## Exact R4.4.1 data fingerprint

Three stock table dimensions select the official AmbiqSuite R4.4.1 family:

| Family | HCI routes | event lengths | component slots |
|---|---:|---:|---:|
| Packetcraft r19 / AmbiqSuite R2.4.2 | 68 | 71 | 14 |
| AmbiqSuite R2.5.1 | 72 | 72 | 14 |
| Packetcraft r20.05-c | 86 | 90 | 21 |
| **AmbiqSuite R4.4.1 / stock G2** | **90** | **92** | **21** |

The stock tables are:

- `dmHciToIdTbl [0x006E006C,0x006E00C6)`, 90 bytes, SHA-256
  `6a01e464d577fb127d88ad65cc81002de6041494b34f3a3784abb6fc716e528f`;
- `dmEvtCbackLen [0x006D1904,0x006D19BC)`, 92 `uint16_t` entries / 184
  bytes, SHA-256
  `e2d84537496c845a86cfb034cdb743e8528a1e87c146aab5399239709a1b4935`;
- `dmFcnIfTbl` at SRAM `0x20000694`, 21 component pointers.

The unusual route value 22 for the first peer-SCA callback is present in both
stock and official R4.4.1 and is preserved fail-closed.

The exact later public corroboration is AmbiqAI/neuralSPOT commit
`4264b9309e03064ffad13a0468d5d0c1110c5288`, Git blob
`6ffb4e76585b685582fc2c3dd01049a477b06481`, SHA-256
`ff9424decca9109d2aa3718ef8521f8eacc083031ff6085791cb77546bc4e3b6`.
The file is Apache-2.0. That repository deliberately truncated history and
postdates G2, so it authenticates exact source content and family—not the
historical commit that generated the firmware.

## Router ABI

The stock ABI is the R4 three-bit message namespace:

```text
DM_NUM_IDS = 21
DM_MSG_START(id) = id << 3
message ordinal mask = 0x07

dmCb = 0x20073B78, sizeof 0x18
dmFcnIfTbl = 0x20000694
dmFcnIf_t = { reset, hciHandler, msgHandler }

DM_CONN_MAX = 3
DM_SYNC_MAX = 1
DM_NUM_ADV_SETS = 2
DM_NUM_PHYS = 2
```

The decoded boot table defaults every component to `dmFcnDefault` except
device ID 7. Later component initializers replace enabled slots. This explains
why the absent device-privacy component safely consumes no-op handlers.

`dmHciEvtCback` gates ordinary traffic while reset is in progress and routes
HCI events through the 90-entry table. `DmHandler` routes WSF messages using
`event >> 3`. `DmSizeOfEvt` indexes the exact 92-entry size table.
`DmHandlerInit` registers the HCI callback. The address-type leaves translate
identity types only while link-layer privacy is enabled, and the two public
PHY wrappers hard-code the product's two-PHY configuration.

## Lorelei handoff

The repository preserves
`research/readiness/dm-main/`, 7,244 bytes, SHA-256
`e27a68f880fa770fff90ced66ba7c59179ee9003455314464d953b5726489650`.
Its fifteen inner hashes cover public r20.05c and official R4.4.1 lanes, Os/O1
objects, four non-vacuous zero-unresolved closures, exact source identities,
and the candidate discriminator. It excludes firmware, upstream source,
headers, objects, ELFs, disassembly, and caches.

The R4 compiler lane uses seven authenticated official inputs and public r20
fallback headers plus two structural placeholder maxima. It is therefore a
useful structural hybrid, not an exact full R4 build configuration.

Reproduce the local and returned-evidence checks with:

```sh
python3 tools/analyze_g2_cordio_dm_main.py --json
python3 tools/verify_research_corpus.py --json
```

## Production admission

`runtime_cordio_dm_main.c` owns the complete router surface. Production uses
the authenticated 90-byte HCI route table and 184-byte event-size table at
their retained addresses, the 21-entry interface table at `0x20000694`, and
the recovered `dmCb` offsets. The implementation rejects null events,
out-of-range HCI events and components (including stock route value 22),
reset-gated traffic, malformed advertising elements, null callbacks, and the
undersized LESC receive-ACL case without unsigned underflow.

Host tests cover HCI and WSF routing, reset gating, component 3 forwarding,
registration/error callbacks at the 69-byte LESC boundary, advertising data,
handler initialization, privacy/address translation, all event-size bounds,
and one/two/three-PHY indexing. The full module and all sixteen isolated
Cortex-M55 profiles compile with warnings as errors. Exact patch routing,
component ownership, manifest tiling, deterministic package, and flash-plan
gates pass.

The canonical overlay/component/package sizes are 357,938 / 3,881,334 /
4,659,828 bytes. The 3,618,112-byte flash plan has 5,204 placed, two
unresolved, five container-only, and six protected regions. No image was
signed, flashed, or installed. Live HCI event ordering, reset-time controller
behavior, LESC/controller sizing, peer exchange, RF/timing, and paired-temple
interoperability remain blocked by unavailable authorized responsive
G2/EM9305 physical evidence.

The next linked dependency is `dm_priv.c`, adjacent near
`[0x004D2544,0x004D293C)`, which owns component ID 6. The Ambiq HCI event port
remains the next retained-path source target for closing the producer side of
the exact R4 event ordering.
