# G2 time KVDB recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
production-routed under the reviewed apple-clang profile. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\kv\service_kvdb_time.c` owns three functions:

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default initializer | `[0x585618,0x58562C)` | 20 | checksum the factory record |
| `_kvdbUpdataTime` | `[0x58562C,0x585758)` | 300 | diagnose/migrate stored data |
| `SVC_KvdbWriteTime` | `[0x585758,0x585806)` | 174 | update time fields, checksum, and persist |

The complete interval is `[0x00585618,0x00585840)`, 552 bytes, SHA-256
`ce83c1da7ce27e3198cb0c5119e5b7a9108c4f25a07577da9820f1bb76f9740c`.
The bodies contribute 494 bytes with concatenated SHA-256
`cf04cb41b7fc34e0d6a00c30478062f7a33bb00e7720b87a7124a678e0741c5c`;
the 58-byte tail contains alignment plus record, key, path, function, and
diagnostic literals.

Stored roots at `0x006D1E64` and `0x00746D40` recover the two callbacks missed
by the baseline decompiler. Three direct entry calls and 31 body calls close
all ingress and providers. There are no legitimate strict-interior branches or
pointers. One unaligned byte window at `0x0078F39F` happens to encode
`0x00585700`; it overlaps the packed register-name strings `W1/W1X/W1Y` and is
explicitly pinned as non-pointer data.

## Record and migration

The twelve-byte `kvTime` record resides at `0x2000380C`:

| Offset | Bytes | Meaning |
|---:|---:|---|
| 0 | 1 | schema version |
| 1 | 3 | preserved reserved bytes |
| 4 | 4 | little-endian timestamp |
| 8 | 1 | signed timezone value |
| 9 | 1 | preserved reserved byte |
| 10 | 2 | little-endian CRC-16 |

The authenticated factory image is `010000002b2d376820000000`. Default
initialization writes CRC `0x18F0` over the first ten bytes without changing
version 1. The writer accepts timestamp and timezone as separate arguments,
updates only those fields, forces version 3, recomputes the CRC, and persists
the complete record. Rewriting the factory values therefore produces CRC
`0xC67A` while preserving bytes 1–3 and 9.

Migration never imports its stack temporary. Missing data rewrites the current
timestamp/timezone. A successful read rewrites only when the stored CRC differs
from current and stored version is less than 3. A version-3 CRC mismatch is
deliberately ignored.

## Reconstruction boundary

`components/apollo_main/core_overlay/kvdb_time.c` is an independently authored
three-entry candidate (3,329 bytes, SHA-256
`1643ea64328e021ae2176b55513df76d79ab7c6e0f7eabaecf982b42a211d13c`).
Host tests pin the initialized and upgraded checksums, field-specific writer,
reserved-byte preservation, and every migration branch. Freestanding
compilation exposes exactly three global Thumb text symbols. The analyzer and
manifests pin every body, literal, retained string, ingress edge, initialized
byte, and the one qualified accidental byte window.

The exact historical source revision is unresolved, and diagnostics remain
abstract. The candidate is absent from `overlay.json`; provider binding,
placement, redirects, and package verification remain pending, so it claims
zero package ownership bytes.

## Production routing

The candidate is now routed into the Apollo main overlay byte-identically
(3,329 bytes, SHA-256 `1643ea64328e021ae2176b55513df76d79ab7c6e0f7eabaecf982b42a211d13c`)
under the reviewed apple-clang profile. Provider binding uses the retained
CRC-16/CCITT provider at `0x0049ACD4` (null seed selects `0xFFFF`) and the
database-zero KVDB blob read/write adapters at `0x004D956C` and `0x004D957E`,
matching the recovered call ABI exactly. Placement appends three relocated
leaves to the overlay: the 28-byte default initializer, the 54-byte
timestamp/timezone writer carrying a 7-byte `kvTime` key-string read-only
closure, and the 100-byte migration callback carrying the same key-string
closure with the writer body inlined by the reviewed toolchain. Three `B.W`
entry redirects with NOP fill replace the 494 stock body bytes across
`[0x00585618,0x00585806)`; the 58-byte literal tail stays retained stock
data, and the two stored roots at `0x006D1E64`/`0x00746D40` plus all three
direct entry calls reach the source leaves through the redirects. The fixed
SRAM record at `0x2000380C` is untouched.

Apple Clang 21 overlay/component/package sizes are `145443/3668839/4447333`
with SHA-256 `9e790387bac8377eff483564ef771c6ee48607f372f335bc5aa8766843bb5cb7`,
`ecfbc642e29bc7a43dc317850470b8c5bef9cf51ef65742a5ff16cebc65d7248`, and
`e0f3dc6bd40c9d8744ed2592ae4e4403e80aa36016ee5f746c4e67a566f33964`. The
leaves and redirects are gated `apple-clang`; the linux-clang profile keeps
its recorded pins, and linux-clang leaf pins await Linux toolchain
regeneration. Ownership is 494 replaced stock body bytes. The component
build, source package, `open_cfw verify`, and the fail-closed analyzer and
manifest census all pass.

## Analyzer production flip (2026-08-19)

Post-routing follow-up: the fail-closed analyzer
`tools/analyze_g2_kvdb_time.py` now validates the production routing
recorded above instead of reporting the object as not routed. It re-reads
`overlay.json` on every run and fails closed unless the expected patch
sites (addresses, sizes, stock SHA-256 digests, `b_w` branches, apple-clang
gating) and the relocated leaves (source SHA-256, apple-clang profiles) match
exactly; the report now states `production_routed: true` with 494
ownership bytes and 58 retained stock tail bytes, matching the ownership
accounting in this document. The analyzer's census, closure, and factory
record pins are unchanged.
