# G2 KVDB universal-setting recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
not production-routed. Run addresses use
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
