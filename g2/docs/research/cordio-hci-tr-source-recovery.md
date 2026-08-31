# Ambiq Cordio HCI transport recovery

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

Stock G2 links three of the four definitions in the later Ambiq `hci_tr.c`
source family. The physical object is exactly `[0x0053013C,0x00530364)`, 552
bytes: 524 executable bytes and a 28-byte receive-state literal pool.
`hciTrSendAclData`, `hciTrSendCmd`, and `hciTrSerialRxIncoming` survive;
`hciTrReceivingPacket` is source-only.

The full four-definition inventory is now implemented in
`components/shared/cordio/runtime_cordio_hci_tr.c`. All three linked entries
are production-routed: 454 compiled bytes under six strict relocations replace
all 524 bounded stock body bytes, while the source-only getter is compiled as
part of the maintained translation unit and independently target-compiled.
The source is project-original clean-room code derived from the authenticated
machine-code contract and public HCI/WSF interfaces; it copies no proprietary
source, header, or object bytes.

Four direct `BL` sites reach all three entries: two driver receive paths and
one sender each from the HCI ACL and command layers. Six calls leave the TU for
the Ambiq driver, HCI core receive path, receive-length getter, and WSF
allocators. Neither an aligned nor an unaligned stored entry pointer exists,
and no aligned pointer reaches a strict body interior. The exact source and
stock body ledger is
[`ambiq-cordio-hci-tr-function-map.tsv`](../../tools/manifests/ambiq-cordio-hci-tr-function-map.tsv).

## Exact stock boundaries

| Object | Interval | Bytes | SHA-256 |
|---|---:|---:|---|
| Physical translation unit | `[0x0053013C,0x00530364)` | 552 | `89831c5be3644e40fe6007f24df12f2929d7ffe4ae525ab190e28e7d9e9fc069` |
| Concatenated linked bodies | 3 spans | 524 | `d217aa89caa7a78189e74d3513eccaee24eda36191bda2abb082f946cb03908f` |
| Literal pool | `[0x00530348,0x00530364)` | 28 | `46a5db920b131ce56c0ca1c85324be54e0c33aef5cb7284cd022f2c5ed8f4d59` |

The tail contains the only image references to the receive state:

| Literal | SRAM | Meaning |
|---:|---:|---|
| `0x00530348` | `0x20074654` | current data write pointer |
| `0x0053034C` | `0x20074F30` | remaining/header byte count |
| `0x00530350` | `0x20074FCD` | `g_bHCIReceivingPacket` |
| `0x00530354` | `0x20074650` | allocated packet pointer |
| `0x00530358` | `0x20074FCF` | packet type |
| `0x0053035C` | `0x20074FCE` | receive state |
| `0x00530360` | `0x2007464C` | four-byte temporary header |

The next function at `0x00530364` belongs to another TU.

## Send ownership and receive behavior

`hciTrSendAclData` derives the packet length from the ACL header, calls the
Ambiq driver with HCI type 2, and returns the full length only when the driver
writes all bytes; otherwise it returns zero. `hciTrSendCmd` similarly submits
type 1 and returns a Boolean exact-write result. Neither transport function
frees nor completes the transmit buffer. The HCI core owns completion after
observing the return status.

The receive routine is a persistent byte-state machine. It accepts event type
4 with a two-byte header and ACL type 2 with a four-byte header, discards an
invalid packet type, rejects ACL payloads above `HciGetMaxRxAclLen()`, and
rejects event payloads above 255 bytes. ACL packets use `WsfMsgDataAlloc`,
events use `WsfMsgAlloc`, and complete packets pass to `hciCoreRecv`. Invalid
lengths and allocation failures reset the state and report the caller's full
input length as consumed. The maintained implementation makes that reset
atomic across state, in-progress flag, packet/data pointers, indicator, and
byte count. This closes two failure-state hazards visible in the stock
instruction sequence: a rejected packet cannot retain a stale queued buffer
pointer, and `hciTrReceivingPacket()` cannot remain asserted after rejection.

## Production admission

| Function | Stock bytes | Compiled bytes | Strict relocations |
|---|---:|---:|---:|
| `hciTrSendAclData` | 42 | 52 | 1 (`HciDrvWrite`) |
| `hciTrSendCmd` | 32 | 32 | 1 (`HciDrvWrite`) |
| `hciTrSerialRxIncoming` | 450 | 370 | 4 (`hciCoreRecv`, `HciGetMaxRxAclLen`, both WSF allocators) |

All leaves have four-byte alignment with zero added padding. Six manifest
regions account for the three replaced stock entries and three appended source
leaves. Host tests exercise exact partial/full driver writes, null TX, event
and ACL assembly, every-byte chunking, multiple packets in one input, invalid
types, excessive ACL payloads, allocation failure, and null non-empty RX. The
complete translation unit also compiles freestanding for Cortex-M55.

The canonical production artifacts after admission are overlay 365,962 bytes
(`cd1bdd4d...`), component 3,889,358 bytes (`2992bad3...`), package
4,667,852 bytes (`17cfb154...`), and flash plan 3,812,398 bytes
(`a289db69...`). The flash plan has `(5696, 2, 5, 6)` flash, unresolved,
container-only, and protected regions; both unresolved regions remain explicit
hardware evidence blocks.

## Source-family and license boundary

AmbiqSuite R2.5.1 has the same four-definition inventory but different
transport ownership and weaker receive validation:

```text
blob    acf4b4fdd1d30bdfbce53e142196c713fba5d0eb
bytes   8,452
sha256  38c0851a30bfeb2ddb1f04ddf1d004c76eda013395c6ee36524ba52d99b288cb
```

Its send functions are `void` and complete or free buffers in the transport.
The selected later R4.4.1 reconstruction oracle returns send status to the
core and adds the stock receive checks:

```text
commit  4264b9309e03064ffad13a0468d5d0c1110c5288
blob    2fab7d10b369ff14d90339f75eda614a66239735
bytes   8,821
sha256  81461dd10e01fac253df692f163f62e2174899e2e51f68c48f15b0cd07c9a6fd
```

This makes the later family an exact behavioral/ABI oracle, not a proven
historical generating commit. The file is proprietary under the Arm Cordio
SLA. openCFW copies no source/header/object bytes and records only clean-room
metadata and independently described behavior.

## Reproduction

```sh
python3 tools/analyze_g2_cordio_hci_tr.py --json
make cordio-hci-tr-closure
```

Live controller byte transport, ACL/event delivery, RF/timing, and paired-
temple behavior remain blocked because the authorized right temple is
nonresponsive and the left temple must remain stock. No signing, flashing, or
installation was performed.
