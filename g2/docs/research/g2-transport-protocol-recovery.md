# G2 multipart transport-protocol linked-object recovery

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status: production source replacement complete; hardware validation blocked.
The complete G2 `2.2.6.10` object retained as
`platform\protocols\transport_protocol\transport_protocol.c` is bounded,
function-mapped, clean-room implemented, and routed into the production
component and complete source package. No hardware or flash state was changed.

## Result

The physical object is `[0x004B892C,0x004B9A80)`: 4,436 bytes, SHA-256
`586bbbe6936ab46ca99434ca4d05d85a8b8031d457cb9b3d587e21f96adff3d4`.
Thirteen functions account for 4,134 bytes; four non-executable alignment and
literal-pool intervals account for the remaining 302 bytes. Their concatenated
SHA-256 values are respectively
`28112dd512e93b63735bd152bacc19314949603ceec591e0f5e4900645ba3bb1`
and `3ee27abef3889ff223b4c47ca6a27bb2400e282effc396757f76fe8fab422edc`.

Seven functions are retained-path anchors. Six adjacent helpers are recovered
by source order, call topology, behavior, and a prior G2 naming corpus. Baseline
Ghidra missed the 310-byte `_rxNextPacketTimeout` body at
`[0x004B8C6C,0x004B8DA2)`; recursive Thumb decoding from its stored pointer at
`0x004B9A18` reaches the authenticated `pop {r4,r5,r6,r7,pc}` at
`0x004B8DA0`. There is no other direct target inside the object that lacks a
mapped entry.

The preceding `[0x004B871E,0x004B892C)` bytes are the final pool of a BLE
handler lookup. The next executable body at `0x004B9A80` is an independent
Cordio advertising helper. Thus neither neighbor is absorbed into the
transport object.

## Function inventory

| Entry | Function | Bytes | Role |
|---:|---|---:|---|
| `0x004B892C` | `TPL_Init` | 230 | bind service callbacks, clear receive contexts, create send mutex |
| `0x004B8A12` | `_getOrCreateContext` | 400 | match or allocate one of four multipart contexts |
| `0x004B8BA2` | context free | 58 | cancel timeout, free assembly storage, clear slot |
| `0x004B8BDC` | mark packet | 56 | update packet bitmap and count |
| `0x004B8C14` | packet-seen test | 48 | test a packet-number bit |
| `0x004B8C44` | schedule receive timeout | 40 | schedule service/sync/pipe tuple after 1,500 ms |
| `0x004B8C6C` | `_rxNextPacketTimeout` | 310 | post WSF event `0xB8` to the BLE handler |
| `0x004B8DA2` | `TPL_RxPacketTimeoutHandler` | 474 | find/free timed-out context and respond with status 3 |
| `0x004B8F7C` | `_rxSyncEventCallback` | 150 | report synchronization/dual-glasses failure |
| `0x004B9012` | `_tplReponse` | 212 | construct and transmit an eight-byte response header |
| `0x004B910C` | `TPL_ReceivePacket` | 1,274 | validate, reassemble, CRC-check, and dispatch incoming data |
| `0x004B9640` | `TPL_SendPacket` | 832 | fragment and transmit at most 4,096 payload bytes |
| `0x004B9984` | reset receive contexts | 50 | cancel timeout and release all four contexts |

Eight names survive as current function strings. Five conservative descriptive
labels avoid promoting semantically misleading names from the prior corpus;
the exact aliases and evidence are preserved in
`tools/manifests/g2-transport-protocol-function-map.tsv`.

Whole-image ingress is closed: 26 raw direct entry sites, five external direct
entries, 193 body calls, 21 internal body calls, and two stored Thumb pointers.
There are no strict-interior BL decodes and no unresolved direct object target.

## Recovered wire and lifecycle behavior

This is a G2-local `0xAA` multipart protocol, not TinyFrame. Each fragment has
an eight-byte header followed by data. The header carries source/destination
nibbles, a synchronization/sequence byte, fragment data length, total-fragment
count, fragment number, service identifier, and pipe/response flags. The final
fragment's data length includes the trailing two-byte CRC.

`TPL_SendPacket` rejects null/empty input and payloads larger than `0x1000`,
acquires a CMSIS mutex for 100 ticks, copies the payload into a static 4 KiB
buffer, computes one CRC over the complete unfragmented payload, and fragments
according to the current BLE payload capacity minus eleven bytes. It appends
the CRC only to the final fragment and invokes the configured transmit callback.

`TPL_ReceivePacket` supports single- and multi-fragment paths. Multipart state
is keyed by packet/header identifiers in one of four 0x38-byte contexts and
uses a packet bitmap to suppress duplicates. Intermediate fragments reschedule
one shared 1,500 ms timeout. The final fragment removes the CRC length,
recomputes the checksum over the complete payload, dispatches valid service
data through the configured callback table, and frees the context. Invalid
CRC, packet-count mismatch, pipe error, duplicate input, and timeout have
distinct return/response paths.

## Checksum and TinyFrame boundary

The only checksum target is `0x0049ACD4`, called at `0x004B91D8`,
`0x004B9486`, and `0x004B97B0`. It is the first-party resumable
CRC-16/CCITT implementation: polynomial `0x1021`, MSB-first, null seed
`0xFFFF`, no final XOR. OpenCFW already source-owns that leaf in
`linux-clang`; see
[`first-party-crc16-ccitt-source-boundary-audit.md`](first-party-crc16-ccitt-source-boundary-audit.md).

This corrects the earlier frontier shorthand that associated the object with
generic transport CRC work. It does not call the standard reflected CRC-32
leaf, and it does not call TinyFrame's reflected CRC-16/ARC implementation.
An exhaustive scan of all 193 direct body calls and all aligned words in the
physical object finds zero edges into the authenticated TinyFrame interval
`[0x004916C8,0x004922F6)`. The word “TinyFrame” is absent from the object too.
The two transports can therefore be reconstructed independently.

## Third-party provider resolution

No third-party function definition is embedded in this object. All upstream
relationships end at providers already admitted or independently bounded:

| Provider seam | Object edges | Origin and version | Reusable commit boundary | Assessment |
|---|---:|---|---|---|
| mutex create/acquire/release and tick | 5 | ARM CMSIS-FreeRTOS `v10.5.1` | `d213f261b5be6bb29a7cce8b84071706b72f4d53` | exact wrapper source family; CMSIS_5 dependency is 5.9.0 commit `2b7495b8…` |
| `WsfMsgAlloc` / `WsfMsgSend` | 2 | Packetcraft Cordio | exact public definitions at r19.02 `86372d84ef0386d8834ed036e613c8f2ded1ff16`; retained through selected r20.05c `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6` | provider bodies are outside this object; G2 packaging belongs to the later Ambiq/Cordio lineage |
| synchronized allocation/free | 2 wrapper calls | mattconte TLSF v3.1-compatible behind G2 wrappers | source-equivalent `a1f743ffac0305408b39e791e0ffb45f6d9bc777` through selected `deff9ab509341f264addbd3c8ada533678591905` | indirect allocator/free entries are already production source-owned |
| diagnostics | 140 | EasyLogger 2.2.99 core plus G2 integration | core-equivalent `cd93d9c768415f4b7279f2d3ef2366ce15ea087c` through selected `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` | logging dominates calls but supplies no protocol algorithm |
| delayed work | 6 | G2 event loop | private commit unobservable | first-party wrappers are already source-owned |
| memory copy/fill | 11 | G2 runtime boundary | private commit unobservable | bounded primitive seam, no hidden protocol behavior |
| CCITT checksum | 3 | G2 first-party utility | clean-room OpenCFW source | production source-owned in `linux-clang` |
| TinyFrame | 0 | MightyPork/TinyFrame | authenticated core interval `eb75483e…a29167a` | explicitly not a dependency |

The provider ledger is executable data in
`tools/manifests/g2-transport-protocol-provider-map.tsv`. The analyzer pins its
contents and independently validates the CMSIS-FreeRTOS, Cordio, TLSF,
EasyLogger, and TinyFrame provenance records.

## Cross-version shortcut

The prior G2 corpus places the same thirteen functions in the same order at
`0x0049A3F0` through `0x0049B47A`. Every body has the exact same size as the
current function, and every entry is shifted uniformly by `+0x1E53C` in
`2.2.6.10`. This is strong evidence that the transport implementation and
compiler decisions stayed structurally stable while the link layout moved.
It is useful as a naming and topology shortcut, but it is not substituted for
current evidence: every current body, pool, boundary, call, and stored pointer
is independently authenticated.

The exact private source revision and producing commit remain unavailable.
Provider commits cannot identify that first-party revision, so no fabricated
whole-object upstream identity is claimed.

## Production admission

`components/apollo_main/core_overlay/transport_protocol.c` owns all thirteen
functions. The target build emits 2,538 bytes of Thumb text plus 14 alignment
bytes and applies 55 strict relocations. Branch patches redirect all 4,134
stock body bytes while the four authenticated official gaps/literal pools
(302 bytes) remain retained. The replacement is present in the core component,
source manifest, and complete source package.

The host oracle covers single- and multi-fragment transmission and reception,
CRC success and failure, duplicate suppression, receive timeout and WSF event
delivery, callback dispatch, mutex-acquire failure, and malformed-length
rejection. Thirteen isolated selector builds prove that every admitted entry
is independently compilable under the production target contract.

Hardware qualification is explicitly blocked, not waived. No authorized
responsive G2 peer is physically available for live single/multipart,
retransmission, timeout, CRC-failure, or dual-glasses callback evidence. The
authorized right temple is nonresponsive, and the left temple must remain on
stock firmware. This is the remaining physical-evidence tail.

## Reproduce

```sh
make transport-protocol-closure
```

This runs the fail-closed analyzer, host/selector implementation tests, and
aggregate retained-path frontier reconciliation. Software production admission
is complete; the command reports the unavailable-hardware validation blocker.
