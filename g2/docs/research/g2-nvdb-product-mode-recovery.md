# G2 NVDB product-mode recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
not production-routed.

The retained first-party `service_nvdb_product_mode.c` object is exactly
`[0x004ABD90,0x004ABEC8)`, 312 bytes, SHA-256
`ff1ab9f69ab28b170f754280b7afa0073010217748706b238c21b3cc717addb4`.
Six linked bodies contribute 270 bytes; their concatenated SHA-256 is
`1bfe7d97d0352877f2563deaee8402758c6d79f816a9de19916bad5c46918584`.
The remaining 42 bytes are alignment and owned literals. Two stored Thumb
pointers root the default and migration entries, 54 direct calls root the
remaining API surface, and 18 calls leave or remain within the object. No
stored or branched strict-interior ingress survives.

The four-byte record at `0x200038F0` is `{version, mode, crc16}`. Boot bytes
are `01000000`; initializing CRC-16/CCITT-FALSE over the first two bytes stores
`0x2E3E`. `_nvdbUpdataProdMd` reads `nvProdMode` into a temporary record and
rewrites current defaults after a missing read or mismatched CRC only when the
stored version is zero. A version-1 mismatch is intentionally left alone.
`set_product_mode` changes SRAM only; the updater forces version 1, recomputes
CRC, and writes four bytes. The separate read API imports all four persistent
bytes into SRAM without validating them and returns the imported mode.

`components/apollo_main/core_overlay/nvdb_product_mode.c` independently
recreates all six entries. Host tests cover the CRC, RAM-only set/get,
persistence, read import, and every migration branch; freestanding Thumb
compilation exposes exactly six global text symbols. The exact product source
and historical commit remain unresolved. Production routing, placement,
diagnostics, redirects, and package validation remain deferred, so this work
adds zero ownership bytes and performs no hardware access.

## Production routing

The candidate is now routed into the Apollo main overlay byte-identically
(3,013 bytes, SHA-256
`443764591c25b14678180a5dfb6777c627f3ae4a805ef4adcf5e86347812c91d`) under the
reviewed apple-clang profile. Provider binding uses the retained CRC-16
provider at `0x0049ACD4` and the retained NVDB blob read/write adapters at
`0x005105F0`/`0x00510602`, matching the recovered call ABI exactly; the
retained diagnostic hook stays the candidate's deliberate no-op. Placement
appends six relocated leaves to the overlay: the 28-byte default-record CRC
initializer, the 12-byte `set_product_mode` RAM-only setter, the 12-byte
`productModeGet` getter, the 52-byte persistent updater, the 62-byte
`_nvdbUpdataProdMd` migration callback, and the 30-byte `productModeRead`
persistent reader, with a single two-byte alignment pad before the reader.
Six `B.W` entry redirects with NOP fill replace the 270 stock body bytes
across `[0x004ABD90,0x004ABE9E)`; the 42-byte alignment and literal island
`[0x004ABE9E,0x004ABEC8)` stays retained stock data, and the two stored
entry roots at `0x006D1E94`/`0x0078F520` plus the 54 direct entry calls
reach the source leaves through the redirects. The fixed four-byte SRAM
record at `0x200038F0`, the `nvProdMode` key, and the boot defaults are
untouched.

Apple Clang 21 overlay/component/package sizes are `150890/3674286/4452780`
with SHA-256 `21b94e548366f0c7a6b2165220a807536dc17269a670e310bb96129bb766e29b`,
`2ad978b4702752c89c1e2cb9d553652b23a22bd3f77da787b547ccf9445114a2`, and
`4106477807c01bde3ad09631e10e58b843a11b1060ba1aeb24022d1c0dc054e7`. The
leaves and redirects are gated `apple-clang`; the linux-clang profile keeps
its recorded pins, and linux-clang leaf pins await Linux toolchain
regeneration. Ownership is 270 replaced stock body bytes. The component
build, source package, `open_cfw verify`, and the fail-closed analyzer and
manifest census all pass. No package was signed or flashed and no hardware
was accessed.
