# Cordio ATT client-supported-features source recovery

Status date: 2026-08-25
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The linked ATT client-supported-features translation unit is now bounded to
ten functions / 4,814 code bytes inside
`[0x0052C6C0,0x0052DA0C)`. The enclosing 4,940-byte interval contains another
126 bytes of decoded literal/string/data pools. Eight bodies retain the
original `atts_csf.c` path; source order and exact leaf semantics recover the
two adjacent eight-byte bodies missed by the path map.

Stock behavior selects the public Packetcraft r20.05--r20.05c source family,
commit `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, while retaining
Ambiq/r19-era exported API spellings and adding local connection validation,
trace, assert, and EasyLogger expansion. This is a high-confidence
source-family/behavior pin, not a claim that the complete stock translation
unit is byte-for-byte pristine upstream source.

`AttsCsfInit` has no standalone stock body. The only two raw references to
the control-block base are this module's literal cells, and there is no
separate or inlined initializer write site. BSS zero initialization already
establishes the callback and hash-update defaults, so the initializer is
classified dead-stripped rather than opaque.

All ten callable entries are production-routed from maintained Apache-2.0 C.
Ten guarded redirects replace 4,814 authenticated stock function bytes with
502 selector-isolated Cortex-M55 text bytes plus 12 alignment bytes under one
strict relocation. The fixed control block remains at `0x20073E04`, and the
only external business provider is the authenticated pending-database-hash
response routine at `0x00534DD8`.

## Upstream provenance

AmbiqSuite R2.4.2 and R2.5.1 contain byte-identical `atts_csf.c` files. That
14,169-byte blob is also exactly Packetcraft r19.02:

- commit `86372d84ef0386d8834ed036e613c8f2ded1ff16`;
- Git blob `65fe480443d5b8a2a123c73bcbb80ac967cc0d86`;
- SHA-256 `f3273e984187e61b4d732f09a660f27e40782165ece787b812719b3ca2d12eac`.

Packetcraft r20.05 through r20.05c use an invariant 14,270-byte source:

- selected r20.05c commit
  `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`;
- Git blob `ed4f051194b77827ec991f0d5c0c38969ea7548a`;
- SHA-256 `1464bff0dbb063ce0e69c5781b73fd7b95656afcd8f710084449298189f2f747`;
- tracked authenticated copy
  `third_party/cordio/ble-host/sources/stack/att/atts_csf.c`.

Both source generations carry Apache-2.0 notices. The stock
`AttsCsfWriteFeatures` body is the release discriminator: it masks all three
r20 feature bits with `0x07`, rejects only a prior-nonzero value being replaced
by zero, and ORs accepted bits into the cached byte. The r19/AmbiqSuite 2.5.1
source has the older one-feature/bit-clearing policy and cannot explain stock.

The exact provenance ledger is
`tools/manifests/packetcraft-cordio-atts-csf-provenance.tsv`. It also pins the
r20.05c `att_api.h`, `att_defs.h`, `atts_main.h`, and `cfg_stack.h` blobs.

## Stock function map

| Function | Stock interval | Bytes | Direct BL callers | Status |
|---|---:|---:|---:|---|
| `attsCsfSetHashUpdateStatus` | `0x52C6C0..0x52C914` | 596 | 3 | r20 behavior + vendor diagnostics |
| `attsCsfGetHashUpdateStatus` | `0x52C914..0x52C91C` | 8 | 2 | source-order leaf closed |
| `attsCsfIsClientChangeAware` | `0x52C928..0x52CA9C` | 372 | 1 | r20 behavior + connId validation |
| `attsCsfActClientState` | `0x52CAA8..0x52D06E` | 1,478 | 1 | state machine/callback closed |
| `AttsCsfSetClientsChangeAwarenessState` | `0x52D090..0x52D35A` | 714 | 2 | r20 semantics, Ambiq-era spelling |
| `AttsCsfConnOpen` | `0x52D370..0x52D4E0` | 368 | 4 | record copy/clear + validation |
| `AttsCsfRegister` | `0x52D4E0..0x52D4E8` | 8 | 1 | source-order leaf closed |
| `AttsCsfWriteFeatures` | `0x52D508..0x52D7B6` | 686 | 1 | r20 release discriminator closed |
| `AttsCsfGetFeatures` | `0x52D7C4..0x52D8EE` | 298 | 3 | bounded copy + validation |
| `AttsCsfGetChangeAwareState` | `0x52D8EE..0x52DA0C` | 286 | 2 | r20 semantics, Ambiq-era spelling |
| `AttsCsfInit` | no stock body | 0 | 0 | dead-stripped; BSS-zero defaults |

Exact body hashes, public source-span hashes, and all caller addresses are in
`tools/manifests/packetcraft-cordio-atts-csf-function-map.tsv`. The ten body
slices concatenate to SHA-256
`15ae8f65b2be9207298e92daca09ef40bcb3afc808f1240452afcd83ddca3ffa`;
the full enclosing interval hashes to
`adc127436a4dc6d6c2170c6e8a09801d9a3928ae597f4bb5b57804f9be562f09`.

The exhaustive ingress audit found 20 real direct BL sites, no legitimate
exterior interior branch, and no stored function entry/interior pointer. One
aligned instruction-word coincidence and one unaligned data-table coincidence
are explicitly rejected by the analyzer rather than silently treated as
pointers.

## Control-block and behavior closure

The global `attsCsfCb` begins at `0x20073E04`:

```text
+0x00..+0x05  three records, each { csf byte, awareness-state byte }
+0x06..+0x07  alignment
+0x08..+0x0B  write callback pointer
+0x0C         database-hash-update byte
```

This proves `DM_CONN_MAX=3`, a two-byte client record, and callback ABI
`callback(connId, state, &csf)`. Awareness states are 0 aware, 1 pending,
2 database-read-pending, and 3 unaware. The recovered constants include
robust-caching bit 1, command bit `0x40`, database-hash UUID `0x2B2A`, service
changed handle `0x0012`, errors length `0x0D`, database out-of-sync `0x12`,
and value-not-allowed `0x13`.

Stock adds explicit `connId == 0` guards to accessors that pristine public
r20 source indexes directly. The invalid-connection results are false,
`0x0E`, state 3, no copy, or no-op as appropriate. Logger/assert source-line
constants extend through line 444, while public r20.05c ends at line 415.
Those facts prevent a whole-file exact-source claim. The production source
implements each observed `connId == 0` result (false, ATT `0x0E`, state 3,
no copy, or no-op). Vendor trace/assert/logger expansion is intentionally not
copied because it changes diagnostics, not the recovered ATT result or state.

## Lorelei result and reproducibility

The compact returned artifact is
`research/readiness/atts-csf/`:

- 6,406 bytes, SHA-256
  `ab9cdee2b5c6b71f7b7da15168b20faeedcbadfe5bdf2bacea99108c12f51322`;
- 15 members, with 14 payload hashes authenticated by its inner manifest;
- two bounded ARM GCC 13.2.1 probes (`-Os` and `-O1`);
- four external seams: `WsfTrace`, `attsCheckPendDbHashReadRsp`, `memcpy`, and
  `memset`;
- zero unresolved symbols in both closure links.

The artifact intentionally excludes firmware, upstream source, decompilation
text, objects, ELFs, and compiler/project caches. GCC output is much smaller
than stock because the public source does not reproduce the vendor diagnostic
expansion; therefore this was a readiness/closure probe, not a raw-match
matrix. The distilled build, closure, source, provider, and coverage-ranking
tables are in `tools/manifests/readiness-cordio-atts-csf-*.tsv`.

Run the fail-closed audit from `openCFW`:

```sh
python3 tools/analyze_g2_cordio_atts_csf.py --json
python3 tools/verify_research_corpus.py --json
```

Production admission is fail-closed through
`tools/analyze_g2_cordio_atts_csf.py`, host behavior tests, ten isolated
Cortex-M55 leaf builds, component/manifest ownership, deterministic package,
and flash-plan checks. The canonical overlay/component/package are 335,892 /
3,859,288 / 4,637,782 bytes with SHA-256
`ae1f288b7b97cc3eab981468653e27caf89a821b68589c45a8303b78b40682e0`,
`51271353d72b4814e3716ed48c91872df252a9fce495992f69c54613343b6926`,
and `2cc1f2700428796d333f8f07f17fa9073565a40f85dcb32fe8acc75e8dd46860`.
No image was signed, flashed, or installed. Live robust-caching,
database-hash/service-changed exchange, callback ordering, ATT peer behavior,
and EM9305 controller timing are explicitly blocked by unavailable authorized
responsive G2/EM9305 physical evidence. Remaining ATT server modules continue
as separate software gaps.
