# Cordio DM local-device source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The stock `dm_dev.c` translation unit is completely bounded at
`[0x004B2DF8,0x004B3098)`: 12 linked functions / 626 code bytes, a 44-byte
literal pool, and two bytes of trailing alignment. Its complete 672-byte
physical SHA-256 is
`1fced11091cb40594dae51a943c599abd9a58562f6a5bfa9152e2dd2c7cf5cbc`.
Six unused source APIs have no body, caller, or registered pointer and are
classified source-only/dead-stripped in stock; all six remain maintained and
target-compilable.

## Source lineage

Lorelei compiled the official Packetcraft r20.05c source at commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, blob
`57d8627584cc4583f7955bd72510c5834c489285`. That Apache-2.0 file is a
stable public architecture oracle, but it lacks two later Ambiq behaviors.

The strongest source candidate is the official AmbiqAI/neuralSPOT
AmbiqSuite R4.4.1 tree at commit
`4264b9309e03064ffad13a0468d5d0c1110c5288`, blob
`cb169ff9d07eac7dbea2f25723cc6816c5c8d48e`, SHA-256
`da6094bd77961d1e42f7ccdd78d0551f9888860bcd3ba5c43fbfe4981130dc3e`.
Its 18 definitions explain every stock discriminator:

- separate translators for vendor-command complete, vendor-specific event,
  and hardware error;
- `DmDevReset` clearing a stale in-progress reset flag;
- the retained privacy trace at exact source line 214; and
- the r20 three-bit component/message namespace.

The file carries its own Apache-2.0 notice. The official Git history is a
later import with truncated ancestry, so this is an exact implementation
family/source candidate, not a claim that the G2 build used that Git commit.
Exact historical and header identities are pinned in
`tools/manifests/packetcraft-cordio-dm-dev-provenance.tsv`.

## Binary closure

The exact stock spans, body hashes, official R4.4.1 source lines, callers,
registered ingress, and six stripped APIs are recorded in
`tools/manifests/packetcraft-cordio-dm-dev-function-map.tsv`. The twelve
concatenated bodies total 626 bytes and hash to
`18db99eb155b8e577a441b25aecd914e7d64953c7674b9e6f37739d131c32dd8`.

Ingress closes over 29 direct Thumb `BL` sites and exactly three registered
Thumb pointers:

- `dmDevAct[0]` at `0x0078EFF4` points to `dmDevActReset`;
- the device component interface at `0x0078A844` contains
  `dmEmptyReset`, `dmDevHciHandler`, and `dmDevMsgHandler`.

No aligned stored pointer or exterior direct call targets a strict body
interior. The HCI handler start at `0x004B2E64`, missed by the original
Ghidra function census, is independently closed by its raw Thumb prologue,
four-way switch, and registered interface pointer.

The retained source path is at `0x006E0010`; its only pointer cell is
`0x004B3084`, loaded at four logger sites inside
`dmDevPassEvtToDevPriv`.

## Dispatch and ABI

Stock proves the following configuration and ABI:

```text
dmCb = 0x20073B78
  +0x00 localAddr[6]
  +0x08 application callback
  +0x0C handlerId
  +0x10 resetting
  +0x11 advFiltPolicy[2]
  +0x13 scanFiltPolicy
  +0x14 initFiltPolicy
  +0x15 syncOptions

dmFcnIfTbl = 0x20000694, 21 component pointers
DM_ID_DEV_PRIV = 1
DM_ID_CONN_CTE = 13
DM_NUM_ADV_SETS = 2
```

`dmDevActReset` resets all 21 registered components exactly once and then
starts the HCI reset sequence. The HCI handler accepts events 0, 18, 19, and
20, translating them to DM events `0x20`, `0x7B`, `0x7A`, and `0x79`.
`DmDevReset` emits message `0x38`; the connection-CTE bridge emits `0x6F`.
Those values independently exclude the older shift-four r19/AmbiqSuite 2.x
message ABI.

The device-privacy bridge constructs the observed six-byte message and calls
component 1. The connection-CTE bridge constructs the four-byte WSF header
and calls component 13. `DmDevSetRandAddr` copies the six-byte address before
submitting the HCI command. `DmDevVsInit` survives as an ABI-preserving
10-byte leaf; the Apollo3 provider it wraps is empty in this product.

## Lorelei handoff

The repository preserves
`research/readiness/dm-dev/`, 5,555 bytes, SHA-256
`4135de1c84d6df7cf597ab59746e50be65ddc6d73d0143b2631fd461a19a85b6`.
Its fourteen inner hashes authenticate the 17-function Packetcraft source
inventory, exact 16-file include closure, two compiler profiles, fourteen
provider seams, and two non-vacuous links with zero unresolved symbols. It
contains no firmware, upstream source, headers, objects, ELFs, decompilation,
disassembly, maps, or caches.

Local analysis expands Lorelei's one conservative 354-byte anchor to the
complete stock module and the later official 18-definition source family.
Reproduce both layers with:

```sh
python3 tools/analyze_g2_cordio_dm_dev.py --json
python3 tools/verify_research_corpus.py --json
```

## Production admission

`runtime_cordio_dm_dev.c` implements all eighteen definitions. Twelve guarded
redirects replace all 626 linked stock body bytes with 448 compiled Cortex-M55
bytes plus 18 alignment bytes under nine strict relocations. The six
stock-absent whitelist/filter-policy APIs are also selector-compiled without
claiming stock coverage. The 44-byte literal pool and two-byte trailing pad
remain separately authenticated compatibility data.

Host tests cover the 21-component reset traversal and in-progress guard, all
four HCI translations, callback/null behavior, device-privacy and
connection-CTE bridge layouts, reset allocation/send and failure, random
address copying, whitelist forwarding, all filter-policy modes and bounds,
and the product's empty vendor initializer. Full and all eighteen isolated
Cortex-M55 builds, exact routing, component, manifest, deterministic package,
and flash-plan checks pass. The canonical overlay/component/package sizes are
357,394 / 3,880,790 / 4,659,284 bytes; the 3,586,814-byte flash plan has 5,160
placed, two unresolved, five container-only, and six protected regions.

No image was signed, flashed, or installed. Live HCI reset sequencing,
controller event timing, random-address programming, filter/privacy behavior,
and paired-temple interoperability remain blocked by unavailable authorized
responsive G2/EM9305 physical evidence.
