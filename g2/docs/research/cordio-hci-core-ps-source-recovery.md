# Ambiq Cordio HCI platform-shim recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

Stock G2 links 9 of the 20 definitions in the later Ambiq
`hci_core_ps.c` source family. The physical object is exactly
`[0x00530C00,0x00530D74)`, 372 bytes: 360 executable bytes and a 12-byte
literal pool. The surviving functions are the four core receive/handler
routines plus `HciGetBdAddr`, `HciGetBufSize`, `HciGetLeSupFeat`,
`HciGetMaxRxAclLen`, and `HciLeAdvExtSupported`.

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

## Source-family and license boundary

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

Stock implements that later ABI and behavior. With no retained path or source
diagnostics, the later import remains a reconstruction oracle rather than a
resolved historical producing commit. The file is proprietary under the Arm
Cordio SLA. openCFW copies no source/header/object bytes and records only
clean-room metadata and independently described behavior.

## Reproduction

```sh
python3 tools/analyze_g2_cordio_hci_core_ps.py --json
python3 -m unittest tests.test_analyze_g2_cordio_hci_core_ps
```

Production source ownership and stock-byte replacement remain zero.
