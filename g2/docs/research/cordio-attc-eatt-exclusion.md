# Cordio enhanced ATT client exclusion audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The optional `attc_eatt.c` translation unit is not linked into stock G2. All
20 source definitions are source-only/dead-stripped; no stock span is assigned
to them.

`AttHandlerInit` installs `eattFcnDefault=0x007851F0` at
`attCb.pEnClient` (`attCb+0x48`). A linked `EattcInit` must replace it with
the TU-owned `attcFcnIf`. The exact five-cell whole-image `attCb` literal
closure contains no such replacement, so enhanced client data, confirmation,
message, and connection callbacks remain the no-op defaults.

The provider topology independently excludes the request surface:

- The packet-building APIs use the linked `attMsgAlloc`; its complete 26-site
  caller set contains only already-classified legacy/common ATT code.
- Enhanced slot selection and L2CAP callbacks use `attcCcbByConnId`; its exact
  callers are only `0x004B5656`, `0x0053133A`, and `0x00531712` in the
  closed legacy/core client paths.
- The shared `eattcSendMsg` path is rooted by those absent request builders,
  while its three callbacks are rooted only by the absent `attcFcnIf`.
- The separately audited EATT core and L2CAP CoC translation units both have
  zero linked functions.
- The public r20 source tree contains no C consumer of any enhanced-client API
  outside this TU, and stock contains no relevant source/name marker.

The inventory includes the free-slot helper, three interface callbacks, the
common message sender, 14 public request/command APIs, and `EattcInit`. Exact
source-span hashes are pinned in
`packetcraft-cordio-attc-eatt-function-map.tsv`.

## Optional source lineage

Packetcraft r20.05 through r20.05c provides the compatible Apache-2.0 source:

```text
blob    45305ddb59ed34713f02f9a2783b62eca25cfc04
bytes   26,255
sha256  8f5e062300131697f705461eecdf57b1639e4b2168520dea5b8395e40e62f713
```

The later official AmbiqSuite R4.4.1 import only rewrites the
`attcCcbByConnId` null test into an explicit assignment and comparison. Its
blob is `3555f7784b6f16f634a60bdd5658d6e9ecc24288`, SHA-256
`c09d391bca06db1ba4129ee778848927576b4bb7adf33a118db4d80eafa53345`.
No stock definition remains to discriminate the spelling.

Public source routes:

- [Packetcraft r20.05c `attc_eatt.c`](https://github.com/packetcraft-inc/cordio/blob/3656312d6b73e2a2c1c8b33ee0385bc199dd97e6/ble-host/sources/stack/att/attc_eatt.c)
- [Official later AmbiqSuite R4.4.1 import](https://github.com/AmbiqAI/neuralSPOT/blob/4264b9309e03064ffad13a0468d5d0c1110c5288/extern/AmbiqSuite/R4.4.1/third_party/cordio/ble-host/sources/stack/att/attc_eatt.c)

## Reproduction

```sh
python3 tools/analyze_g2_cordio_attc_eatt.py --json
python3 -m unittest tests.test_analyze_g2_cordio_attc_eatt
```

Production ownership and source replacement remain zero. With the core,
client, and server EATT TUs plus L2CAP CoC all excluded, the enhanced bearer
implementation is completely absent even though common ATT code retains the
r20/R4 multi-bearer ABI.
