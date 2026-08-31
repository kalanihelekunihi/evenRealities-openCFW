# Ambiq Cordio HCI platform-shim recovery

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status date: 2026-08-25
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

Stock G2 links 9 of the 20 definitions in the later Ambiq
`hci_core_ps.c` source family. The physical object is exactly
`[0x00530C00,0x00530D74)`, 372 bytes: 360 executable bytes and a 12-byte
literal pool. The surviving functions are the four core receive/handler
routines plus `HciGetBdAddr`, `HciGetBufSize`, `HciGetLeSupFeat`,
`HciGetMaxRxAclLen`, and `HciLeAdvExtSupported`.

All 20 definitions are now maintained in
`components/shared/cordio/runtime_cordio_hci_core_ps.c`. The nine linked
entries are production-routed: 514 compiled bytes plus six alignment bytes
under 13 strict relocations replace all 360 bounded stock body bytes. The
eleven source-only getters remain in every translation-unit compile and also
target-compile independently for Cortex-M55.

The other eleven definitions are source-only getters:

- `HciGetWhiteListSize`, `HciGetAdvTxPwr`, `HciGetNumBufs`, and
  `HciGetSupStates`;
- `HciGetResolvingListSize`, `HciLlPrivacySupported`,
  `HciGetMaxAdvDataLen`, and `HciGetNumSupAdvSets`;
- `HciGetPerAdvListSize`, `HciGetLocalVerInfo`, and
  `HciGetLeSupFeat32`.

Twenty-one direct `BL` sites reach all nine linked entries. There is no
aligned stored entry pointer and no strict-interior pointer. The complete
source-line/body-hash and stock-body ledger is
[`ambiq-cordio-hci-core-ps-function-map.tsv`](../../tools/manifests/ambiq-cordio-hci-core-ps-function-map.tsv).

## Exact stock boundaries

| Object | Interval | Bytes | SHA-256 |
|---|---:|---:|---|
| Physical translation unit | `[0x00530C00,0x00530D74)` | 372 | `af477f877f3e5fff17af792d0e5cb5ac459bdbb84b784725d701bd911bfed904` |
| Concatenated linked bodies | 9 spans | 360 | `2ed7114bc4a26f3ef70c1cc230ca031567fbb537290e90af0360eac0af34d9c0` |
| Literal pool | `[0x00530D68,0x00530D74)` | 12 | `960d7b2734426f4a19a4a5469fc95148b7e92f971d4723ee47b053b3e8ad47a6` |

The three literal words are `hciCoreCb=0x20071478`, external
`hciCb=0x20073870`, and `hciCoreCb.bdAddr=0x200714E0`. The preceding
translation unit supplies the public ACL-send wrapper; the following one
begins at `0x00530D74`.

## Behavior and ABI

`hciCoreInit` calls the command-layer initializer. Completed-packet handling
decrements each matching connection's outstanding and queued counts,
reenables flow below the low watermark, and returns the aggregate completed
buffer count to the transmitter. `hciCoreRecv` queues controller messages and
raises the HCI receive event.

`HciCoreHandler` handles command timeouts, drains the receive queue, dispatches
events into the closed `hci_evt.c` port, advances reset sequencing, reassembles
ACL data, and separately dispatches ISO data through `hciCb+0x18` or frees it
when no ISO callback is registered. That explicit ISO branch is absent from
AmbiqSuite R2.5.1.

The LE-feature getter loads two words from `hciCoreCb+0x88`, clears the
connection-parameter-request feature bit, and returns a 64-bit value. The
remaining linked leaves expose the BD-address pointer, controller ACL-buffer
size, maximum reassembled receive length, and whether the controller reports
any extended-advertising sets.

The maintained implementation additionally saturates malformed completed-
packet counts instead of allowing the stock byte counters to underflow,
checks callback presence, rejects and frees unknown receive types, and bases
extended-advertising support on `numSupAdvSets` at authenticated offset
`+0x94`. The last item corrects the linked stock getter's load from `+0x91`,
which is the resolving-list-size field populated by reset sequencing.

## Public behavior source and proprietary boundary

Packetcraft r20.05c publishes the dual-chip core platform behavior under
Apache-2.0:

```text
commit  3656312d6b73e2a2c1c8b33ee0385bc199dd97e6
blob    0730013ce6d4bb992b6a48695e30bddae757c8ae
bytes   12,231
sha256  730395b8be404d357cf498fa1caee5630dcf95d66b2ea1c817e35932d5be0dd8
```

That public file supplies the reusable initialization, completed-packet,
receive/handler, callback, and getter behavior. openCFW adapts it to the
authenticated G2 `hciCoreCb`/`hciCb` layout and adds the hardening above.

AmbiqSuite R2.5.1 has 18 definitions, a 32-bit feature getter, and no ISO
receive branch:

```text
blob    6c289296e001369d09febef042d041cc298e2315
bytes   11,618
sha256  c852f27f4cfc66cc01e9bb4676cb282e528778d658b4d88e9cff21e7fd247acb
```

The selected later official R4.4.1 reconstruction oracle has 20 definitions,
the 64-bit getter, and ISO dispatch:

```text
commit  4264b9309e03064ffad13a0468d5d0c1110c5288
blob    863085f75f368ac8ad2a8b741dd51231bffcabcf
bytes   12,960
sha256  dca9e769828eedab03b15d99ffd0e1e726d8935af2e22eaa901bb897e05853cd
```

Stock implements that later ABI and behavior. The later Ambiq import remains
a proprietary corroborating oracle rather than a resolved historical
producing commit or source donor. No proprietary source/header/object bytes
are copied.

## Production admission

The nine guarded routes cover the exact stock spans. Source leaves occupy
`[0x007ED8B0,0x007EDAB6)` with three two-byte alignment regions. Twenty-one
manifest regions account for nine replaced bodies, nine source leaves, and
three alignment spans. Host tests cover initialization, saturating completed-
packet accounting, flow re-enable, event enqueue/wakeup, command timeout,
event/reset, ACL reassembly, ISO delivery, absent callbacks, unknown packet
types, and every getter offset.

The canonical overlay is 366,482 bytes (`83b08847...`), the component is
3,889,878 bytes (`677b2ed9...`), the package is 4,677,076 bytes
(`fbb300c7...`), and the flash plan is 3,937,595 bytes (`289c21af...`).
The plan retains exactly two unresolved hardware regions.

## Reproduction

```sh
python3 tools/analyze_g2_cordio_hci_core_ps.py --json
make cordio-hci-core-ps-closure
```

Live HCI controller, ACL/event/ISO, RF, reset, and timing validation remains
blocked because the authorized right temple is nonresponsive and the left
temple must remain stock. No signing, flashing, or installation was performed.
