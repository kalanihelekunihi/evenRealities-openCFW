# G2 KVDB time-format recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
production-routed under the reviewed apple-clang profile. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\kv\service_kvdb_time_format.c` owns three
functions in one physical object:

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default initializer | `[0x49AE90,0x49AEA4)` | 20 | checksum the factory record |
| `_kvdbUpdataTimeFormat` | `[0x49AEA4,0x49AF74)` | 208 | diagnose/migrate stored data |
| `SVC_KvdbWriteTimeFormat` | `[0x49AF74,0x49AFE2)` | 110 | replace, checksum, and persist |

The complete interval is `[0x0049AE90,0x0049B014)`, 388 bytes, SHA-256
`e75b4c89bfb846c04e656ec8def696f8565097e80319cfb4d9921e23282c32bd`.
The three bodies contribute 338 bytes with concatenated SHA-256
`b08b331f35aab05b6b15d5ec7b56b44b0c0db4e82d3e47889df6473ad650a7ea`;
the 50-byte tail contains the record, key, path, function, and diagnostic
literals.

The default and migration callbacks were missed as standalone functions by
the baseline decompiler, but their prologue-to-return Thumb bodies and stored
roots at `0x006D1E6C` and `0x00746D44` are exact. Three direct entry calls and
21 complete body calls close all ingress and providers. No raw word, direct
branch, or stored pointer targets a strict body interior.

## Record and behavior

The twelve-byte `kvTimeFormat` record resides at `0x20003818`. Its first byte
is schema version 1, bytes zero through seven are covered by
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
left alone. This exactly matches the adjacent temperature-unit migration
family while retaining separate keys, records, functions, and evidence.

## Reconstruction boundary

`components/apollo_main/core_overlay/kvdb_time_format.c` is an independently
authored three-entry behavioral candidate (4,014 bytes, SHA-256
`97c415e62c39745311e2110d38aeb7dab854f78f8dd12d5fdc391de8d37327c1`).
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
(4,014 bytes, SHA-256 `97c415e62c39745311e2110d38aeb7dab854f78f8dd12d5fdc391de8d37327c1`)
under the reviewed apple-clang profile. Provider binding uses the retained
CRC-16/CCITT provider at `0x0049ACD4` (null seed selects `0xFFFF`) and the
database-zero KVDB blob read/write adapters at `0x004D956C` and `0x004D957E`,
matching the recovered call ABI exactly. Placement appends three relocated
leaves to the overlay: the 28-byte default initializer, the 96-byte
whole-record writer carrying a 13-byte `kvTimeFormat` key-string read-only
closure, and the 90-byte migration callback carrying the same key-string
closure with the writer body inlined by the reviewed toolchain. Three `B.W`
entry redirects with NOP fill replace the 338 stock body bytes across
`[0x0049AE90,0x0049AFE2)`; the 50-byte literal tail stays retained stock
data, and the two stored roots at `0x006D1E6C`/`0x00746D44` plus all three
direct entry calls reach the source leaves through the redirects. The fixed
SRAM record at `0x20003818` is untouched.

Apple Clang 21 overlay/component/package sizes are `145687/3669083/4447577`
with SHA-256 `332daed353fcaed5d24e7d456bf3ace85f04a1814a0968ffc92f1028473e7ed0`,
`f345bff784b400d51d05d10a4f1417fa1195953f0630f98a68b12ecfb6845b6c`, and
`432e69e1414b73c25355b4f36d0ebd017782671d72bc4444ea83e056a5738547`. The
leaves and redirects are gated `apple-clang`; the linux-clang profile keeps
its recorded pins, and linux-clang leaf pins await Linux toolchain
regeneration. Ownership is 338 replaced stock body bytes. The component
build, source package, `open_cfw verify`, and the fail-closed analyzer and
manifest census all pass.
