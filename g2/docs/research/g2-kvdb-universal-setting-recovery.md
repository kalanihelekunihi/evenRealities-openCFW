# G2 KVDB universal-setting recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
production-routed under the reviewed apple-clang profile. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\kv\service_kvdb_universal_setting.c` owns three
functions:

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default initializer | `[0x49AD0C,0x49AD20)` | 20 | checksum the factory record |
| `_kvdbUpdataUniversalSetting` | `[0x49AD20,0x49ADF0)` | 208 | diagnose/migrate stored data |
| `SVC_KvdbWriteUniversalSetting` | `[0x49ADF0,0x49AE60)` | 112 | replace, checksum, and persist |

The complete interval is `[0x0049AD0C,0x0049AE90)`, 388 bytes, SHA-256
`a8c3b7fe6bb4fa598fc9b206a8b4aea9f92a46c5684a2f906f2e81ed3f06be96`.
The bodies contribute 340 bytes with concatenated SHA-256
`0c7b17a6828276160a44ec967144a55e1acf465153aded28414832c7df06eea6`;
the 48-byte tail contains the record, key, path, function, and diagnostic
literals.

Stored roots at `0x006D1E74` and `0x00746D48` recover the two callbacks that
the baseline decompiler missed. Three direct entry calls and 22 body calls
close all ingress and providers. No raw word, direct branch, or stored pointer
targets a strict body interior.

## Record and behavior

The twenty-byte `kvUniversalSetting` record resides at `0x20003824`. Byte zero
is schema version 3, bytes zero through seventeen are covered by
CRC-16/CCITT-FALSE, and the CRC occupies bytes eighteen and nineteen. Payload
field names remain opaque rather than inferred from values alone.

The authenticated initialized record is
`030000000100000000000000ffffffffffff0000`. Its boot CRC field is zero; the
default initializer computes `0xA967`.

The writer copies all twenty caller bytes, forces version 3, recomputes the
first-eighteen-byte CRC, persists the whole record, and returns zero even when
the provider reports failure. Migration reads a stack temporary but never
imports it. Missing data rewrites current SRAM defaults. A successful read
rewrites current data only when the stored CRC differs and stored version is
less than 3; a version-3 mismatch is left unchanged.

## Reconstruction boundary

`components/apollo_main/core_overlay/kvdb_universal_setting.c` is an
independently authored three-entry candidate (4,291 bytes, SHA-256
`1399f2936a27bb0a3643c139b62b8fb77a4aca70d0d6802a7988e14b87a0f1a0`).
Host tests cover initialization, replacement, missing data, pre-v3 migration,
and the current-version mismatch case. Freestanding compilation exposes
exactly three global Thumb text symbols. The analyzer and manifests pin the
bodies, literals, retained strings, ingress, and initialized record.

The exact historical source revision is unresolved, and diagnostics remain
abstracted behind a hook. The candidate is absent from `overlay.json`, so
placement, provider/logger binding, redirects, and package validation remain
pending and package ownership remains zero.

## Production routing

The candidate is now routed into the Apollo main overlay byte-identically
(4,291 bytes, SHA-256 `1399f2936a27bb0a3643c139b62b8fb77a4aca70d0d6802a7988e14b87a0f1a0`)
under the reviewed apple-clang profile. Provider binding uses the retained
CRC-16/CCITT provider at `0x0049ACD4` (null seed selects `0xFFFF`) and the
database-zero KVDB blob read/write adapters at `0x004D956C` and `0x004D957E`,
matching the recovered call ABI exactly. Placement appends three relocated
leaves to the overlay: the 28-byte default initializer, the 128-byte
whole-record writer carrying a 19-byte `kvUniversalSetting` key-string
read-only closure, and the 92-byte migration callback carrying the same
key-string closure with the writer body inlined by the reviewed toolchain.
Three `B.W` entry redirects with NOP fill replace the 340 stock body bytes
across `[0x0049AD0C,0x0049AE60)`; the 48-byte literal tail stays retained
stock data, and the two stored roots at `0x006D1E74`/`0x00746D48` plus all
three direct entry calls reach the source leaves through the redirects. The
fixed SRAM record at `0x20003824` is untouched.

Apple Clang 21 overlay/component/package sizes are `146227/3669623/4448117`
with SHA-256 `1701d7ebe15fe0c0fc48c623132bb3779e04f96e1595bc11b69de771a4f3ff0c`,
`2042c3ea001e95ba59a264fed06042b505c2f67627bfe19751e94fc1ffd2267b`, and
`a65f379437f03a2719103623fc3c46abb69a5f01c5e074ff92609d7d11297fb4`. The
leaves and redirects are gated `apple-clang`; the linux-clang profile keeps
its recorded pins, and linux-clang leaf pins await Linux toolchain
regeneration. Ownership is 340 replaced stock body bytes. The component
build, source package, `open_cfw verify`, and the fail-closed analyzer and
manifest census all pass.
