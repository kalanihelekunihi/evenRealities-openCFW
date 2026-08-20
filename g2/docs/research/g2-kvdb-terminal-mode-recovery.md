# G2 terminal-mode KVDB recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
production-routed under the reviewed apple-clang profile. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\kv\service_kvdb_terminal_mode.c` owns three
functions:

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default initializer | `[0x4B03E0,0x4B03F4)` | 20 | checksum the factory record |
| `_kvdbUpdataTerminalMode` | `[0x4B03F4,0x4B04C4)` | 208 | diagnose/migrate stored data |
| `SVC_KvdbWriteTerminalMode` | `[0x4B04C4,0x4B052E)` | 106 | replace, checksum, and persist |

The complete interval is `[0x004B03E0,0x004B0560)`, 384 bytes, SHA-256
`65d3de37ac6d66eeb7bba08453e6fd602d49e0f3331cc5cdc1c53906124b6461`.
The bodies contribute 334 bytes with concatenated SHA-256
`72b928ec066496784ff1b8ffa5c9bf14b44a32ca4972f351c7fe3338d866feba`;
the 50-byte tail contains alignment plus record, key, path, function, and
diagnostic literals.

Stored roots at `0x006D1E5C` and `0x00746D3C` recover the two callbacks missed
by the baseline decompiler. Three direct entry calls and 21 body calls close
all ingress and providers. No raw word, direct branch, or stored pointer
targets a strict body interior.

## Record and migration

The four-byte `kvTerminalMode` record resides at `0x20003808`. Byte zero is
the schema version, byte one is the terminal mode, and the little-endian CRC
occupies bytes two and three. The external setter at `0x0046C63C` writes its
argument to byte one and passes the record to `SVC_KvdbWriteTerminalMode`,
independently establishing the payload field.

The authenticated factory image is `01000000`: version 1, mode zero, and a
zero boot CRC field. Default initialization writes CRC `0x2E3E` over the first
two bytes.

The writer copies all four input bytes, forces version 1, recomputes the CRC
over version and mode, persists the record, and returns zero irrespective of
persistence status. Migration never imports its stack temporary. Missing data
rewrites the current record; a successful read rewrites only when the stored
CRC differs from current and stored version is zero. A version-1 CRC mismatch
is deliberately ignored.

## Reconstruction boundary

`components/apollo_main/core_overlay/kvdb_terminal_mode.c` is an independently
authored three-entry candidate (3,705 bytes, SHA-256
`33caff3263530ce7e7db7c59caa9b470f019fdccd1fdd720e2b495f2a1e97bfb`).
Host tests pin the factory checksum, mode writer, version forcing, and every
migration branch. Freestanding compilation exposes exactly three global Thumb
text symbols. The analyzer and manifests pin every body, literal, retained
string, ingress edge, and initialized byte.

The exact historical source revision is unresolved, and diagnostics remain
abstract. The candidate is absent from `overlay.json`; provider binding,
placement, redirects, and package verification remain pending, so it claims
zero package ownership bytes.

## Production routing

The candidate is now routed into the Apollo main overlay byte-identically
(3,705 bytes, SHA-256 `33caff3263530ce7e7db7c59caa9b470f019fdccd1fdd720e2b495f2a1e97bfb`)
under the reviewed apple-clang profile. Provider binding uses the retained
CRC-16/CCITT provider at `0x0049ACD4` (null seed selects `0xFFFF`) and the
database-zero KVDB blob read/write adapters at `0x004D956C` and `0x004D957E`,
matching the recovered call ABI exactly. Placement appends three relocated
leaves to the overlay: the 28-byte default initializer, the 52-byte
whole-record writer carrying a 15-byte `kvTerminalMode` key-string read-only
closure, and the 94-byte migration callback carrying the same key-string
closure with the writer body inlined by the reviewed toolchain. Three `B.W`
entry redirects with NOP fill replace the 334 stock body bytes across
`[0x004B03E0,0x004B052E)`; the 50-byte literal tail stays retained stock
data, and the two stored roots at `0x006D1E5C`/`0x00746D3C` plus all three
direct entry calls reach the source leaves through the redirects. The fixed
SRAM record at `0x20003808` is untouched.

Apple Clang 21 overlay/component/package sizes are `146433/3669829/4448323`
with SHA-256 `bb69a3a64a302eda921189f8375bef6cbaf0be171ea4a3ecd32b9ba4a81df203`,
`ab37d9c813e2ac79e2c1cd3a714708eaf8eef6b500a88c9a568d8391b9dcdb45`, and
`6f226b2652ef85768f9f12607a3beab99f9381b6e611b1ea3d71965e60dec85a`. The
leaves and redirects are gated `apple-clang`; the linux-clang profile keeps
its recorded pins, and linux-clang leaf pins await Linux toolchain
regeneration. Ownership is 334 replaced stock body bytes. The component
build, source package, `open_cfw verify`, and the fail-closed analyzer and
manifest census all pass.

## Analyzer production flip (2026-08-19)

Post-routing follow-up: the fail-closed analyzer
`tools/analyze_g2_kvdb_terminal_mode.py` now validates the production routing
recorded above instead of reporting the object as not routed. It re-reads
`overlay.json` on every run and fails closed unless the expected patch
sites (addresses, sizes, stock SHA-256 digests, `b_w` branches, apple-clang
gating) and the relocated leaves (source SHA-256, apple-clang profiles) match
exactly; the report now states `production_routed: true` with 334
ownership bytes and 50 retained stock tail bytes, matching the ownership
accounting in this document. The analyzer's census, closure, and factory
record pins are unchanged.
