# G2 KVDB time-format recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
not production-routed. Run addresses use
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
