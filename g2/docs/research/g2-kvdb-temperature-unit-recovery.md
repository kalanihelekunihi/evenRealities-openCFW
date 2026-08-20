# G2 KVDB temperature-unit recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
production-routed under the reviewed apple-clang profile. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\kv\service_kvdb_temperature_unit.c` owns three
functions in one physical object:

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default initializer | `[0x49B014,0x49B028)` | 20 | checksum the factory record |
| `_kvdbUpdataTemperatureUnit` | `[0x49B028,0x49B0F8)` | 208 | diagnose/migrate stored data |
| `SVC_KvdbWriteTemperatureUnit` | `[0x49B0F8,0x49B166)` | 110 | replace, checksum, and persist |

The complete interval is `[0x0049B014,0x0049B198)`, 388 bytes, SHA-256
`c03f4581a435c010b7315a9f949a08103d8dcea72869f5f8cba44a57e0fd55d8`.
The three bodies contribute 338 bytes with concatenated SHA-256
`4d9a4d88a10e5938b06f23c46e152295575d41dbe6ce7179bdf4864d26be4500`;
the 50-byte tail contains the record, key, path, function, and diagnostic
literals.

The default and migration callbacks were missed as standalone functions by
the baseline decompiler, but their prologue-to-return Thumb bodies and stored
roots at `0x006D1E54` and `0x00746D38` are exact. Three direct entry calls and
21 complete body calls close all ingress and providers. No raw word, direct
branch, or stored pointer targets a strict body interior.

## Record and behavior

The twelve-byte `kvTemperatureUnit` record resides at `0x200037FC`. Its first
byte is schema version 1, bytes zero through seven are covered by
CRC-16/CCITT-FALSE, the CRC occupies bytes eight and nine, and bytes ten and
eleven are trailing record data/reserved bytes. Field names inside the opaque
seven-byte payload are deliberately not guessed.

The authenticated IAR initialized-SRAM image is
`010000000000000000000000`. Its CRC bytes start zero; the default initializer
writes `0x76ED`.

The writer copies all twelve caller bytes, forces version 1, recomputes the
first-eight-byte CRC, writes the full record, and returns zero even if the
persistence provider reports failure. The migration callback reads into a
stack temporary but never imports it. A missing key rewrites the current SRAM
record. A successful read rewrites only when the stored CRC field differs
from the current CRC and the stored version is zero; a version-1 mismatch is
left alone. This is the same unusual non-importing migration family observed
in adjacent first-party NVDB/KVDB helpers.

## Reconstruction boundary

`components/apollo_main/core_overlay/kvdb_temperature_unit.c` is an
independently authored three-entry behavioral candidate (4,260 bytes,
SHA-256 `288f83e95b9526816845f197d0ca7c355a259a03348c0e2140346cb30a01e808`).
Host tests cover initialization, full-record replacement, and every migration
branch. Freestanding target compilation exposes exactly three global Thumb
text symbols. The analyzer and manifests pin all bodies, literals, retained
strings, ingress, and initialized record bytes.

The exact historical source revision remains unresolved. Retained diagnostic
formatting is abstracted behind a hook. The candidate is absent from
`overlay.json`; placement, provider/logger binding, redirects, and package
validation remain pending, so it claims zero package ownership bytes.

## Production routing

The candidate is now routed into the Apollo main overlay byte-identically
(4,260 bytes, SHA-256 `288f83e95b9526816845f197d0ca7c355a259a03348c0e2140346cb30a01e808`)
under the reviewed apple-clang profile. Provider binding uses the retained
CRC-16/CCITT provider at `0x0049ACD4` (null seed selects `0xFFFF`) and the
database-zero KVDB blob read/write adapters at `0x004D956C` and `0x004D957E`,
matching the recovered call ABI exactly. Placement appends three relocated
leaves to the overlay: the 28-byte default initializer, the 96-byte
whole-record writer carrying an 18-byte `kvTemperatureUnit` key-string
read-only closure, and the 90-byte migration callback carrying the same
key-string closure with the writer body inlined by the reviewed toolchain.
Three `B.W` entry redirects with NOP fill replace the 338 stock body bytes
across `[0x0049B014,0x0049B166)`; the 50-byte literal tail stays retained
stock data, and the two stored roots at `0x006D1E54`/`0x00746D38` plus all
three direct entry calls reach the source leaves through the redirects. The
fixed SRAM record at `0x200037FC` is untouched.

Apple Clang 21 overlay/component/package sizes are `145940/3669336/4447830`
with SHA-256 `50e4865c2e6932f09e2aff2c039fe113d9121ef91cba6566f1008dc8a1794303`,
`72f6225bfb3da8aecb5a1994186b39a60a4dc6f0cd56f30cd307c60c9dbdbdcc`, and
`7b3301d8d934584d40a9bcb5a994fb2dc36f1ceae3bf15bae74d2378da0863be`. The
leaves and redirects are gated `apple-clang`; the linux-clang profile keeps
its recorded pins, and linux-clang leaf pins await Linux toolchain
regeneration. Ownership is 338 replaced stock body bytes. The component
build, source package, `open_cfw verify`, and the fail-closed analyzer and
manifest census all pass.

## Analyzer production flip (2026-08-19)

Post-routing follow-up: the fail-closed analyzer
`tools/analyze_g2_kvdb_temperature_unit.py` now validates the production routing
recorded above instead of reporting the object as not routed. It re-reads
`overlay.json` on every run and fails closed unless the expected patch
sites (addresses, sizes, stock SHA-256 digests, `b_w` branches, apple-clang
gating) and the relocated leaves (source SHA-256, apple-clang profiles) match
exactly; the report now states `production_routed: true` with 338
ownership bytes and 50 retained stock tail bytes, matching the ownership
accounting in this document. The analyzer's census, closure, and factory
record pins are unchanged.
