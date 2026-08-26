# Cordio DM device-privacy exclusion audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The optional `dm_dev_priv.c` translation unit is not linked into the stock G2
image. All 18 upstream definitions are source-only/dead-stripped for this
product configuration. There are no stock function addresses or byte hashes to
assign to them.

This is a positive default-routing result, not merely a missing source path.
The stock boot image initializes the 21-entry `dmFcnIfTbl` at `0x20000694` so
that component 1 (`DM_ID_DEV_PRIV`) points to `dmFcnDefault` at `0x0078A850`.
That interface contains `dmEmptyReset` and two copies of `dmEmptyHandler`.
The just-closed `dm_dev.c` privacy-event producer therefore terminates safely
through the no-op message handler.

## Binary exclusion proof

The fail-closed analyzer authenticates all of the following:

- the decoded IAR boot table contains 21 pointers; slot 7 is the linked
  `dm_dev.c` interface and every other slot, including slot 1, is the default;
- the default-interface bytes at `[0x0078A850,0x0078A85C)` hash to
  `203372a811e7881325fe55a1ef19871303192cfda3e2d76d8d08db14afb459ef`;
- `dmEmptyReset` and `dmEmptyHandler` occupy
  `[0x004D29BE,0x004D29C2)` and hash to
  `fd7165fc6672b624f26b42214654f5e37cadfc0f97f94634045b87ad1f4a4704`;
- all nine firmware literal cells for `dmFcnIfTbl` are accounted for, and
  their install sites write offsets 0, 8, `0x14`, `0x18`, `0x20`, `0x24`, and
  `0x3C`—never the device-privacy slot at offset 4;
- no literal for `0x20000698`, retained `dm_dev_priv.c` path/name, seven-entry
  privacy action table, or three-entry privacy interface table exists; and
- all 69 direct calls to `WsfMsgAlloc` were censused. None implements the
  upstream Start allocation of six bytes/event 8 or Stop allocation of four
  bytes/event 9.

The absence of `DmDevPrivInit` is decisive: that API must install the component
1 interface. Neighboring privacy-event producers do not imply inclusion
because the default interface is intentionally safe.

Reproduce the proof with:

```sh
python3 tools/analyze_g2_cordio_dm_dev_priv.py --json
```

All 18 optional definitions now also exist as maintained, host-tested C in
`components/shared/cordio/runtime_cordio_dm_dev_priv.c` and compile as one
Cortex-M55 translation unit. The implementation covers timer/address
generation, AES completion, pending-RPA policy, advertising/scanning/
connection state, HCI/message/reset/init, and public start/stop behavior.
`make cordio-dm-dev-priv-closure` pins that source and test evidence while
preserving zero production routes: adding a redirect would contradict the
authenticated default-routed product configuration.

## Public source and configuration oracle

The optional public implementation remains useful for a future
privacy-enabled configuration. Packetcraft r20.05 through r20.05c use the
same Apache-2.0 blob:

```text
commit  3656312d6b73e2a2c1c8b33ee0385bc199dd97e6
blob    fe1af93bc232a888f564513282b4da3c56acbee5
bytes   19,050
sha256  aae3783dc9adce996027fc7b4505bde8399c3c8630ea6ecb79bf8905683cc475
```

AmbiqSuite R2.4.2 and R2.5.1 carry the older Packetcraft r19.02 blob
`8a42edcbeebfc52b57e23e14fd56918102ff6dc7` (18,980 bytes, SHA-256
`347270af4706005c3f654a59d9b88aad04e21ca42019f809a339a9543de5590c`).
Only `dmDevPrivActCtrl` and `DmDevPrivInit` change at r20.05; the latter gains
task locking. Later official Ambiq R4.4.1 imports corroborate the r20 blob but
do not establish historical G2 provenance.

No stock body survives to discriminate these source versions. The compatible
optional choice is based instead on the surrounding proved r20 shift-three DM
message ABI. A future build must also preserve the product value
`DM_NUM_ADV_SETS=2`, although public r20 defaults to one.

Exact source spans, body hashes, identities, and exclusion status are pinned
in:

- `tools/manifests/packetcraft-cordio-dm-dev-priv-function-map.tsv`
- `tools/manifests/packetcraft-cordio-dm-dev-priv-provenance.tsv`

## Lorelei readiness

The repository preserves
`research/readiness/dm-dev-priv/`, 5,603 bytes,
SHA-256
`c9f7fd834d2407091fc3933eea923681c2eb7126805260c4f87eda1ba4ef5307`.
Its thirteen inner hashes authenticate the 18-function public source
inventory, exact 18-input compile closure, two compiler profiles, 24 provider
seams, and two non-vacuous links with zero unresolved symbols. The archive
contains no firmware, upstream source/header bytes, objects, ELFs,
decompilation, disassembly, maps, or caches.

Lorelei proved that the optional source is build-ready. Local binary closure
supersedes the artifact's conservative “stock linkage pending” caveat with the
proved exclusion above. Production ownership remains unchanged: zero source
bytes were added and zero stock bytes were replaced.

The next linked target is `dm_main.c`, which owns the default interface,
component dispatch table, and global HCI/message routing used by this proof.
