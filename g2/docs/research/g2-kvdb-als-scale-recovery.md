# G2 ALS-scale KVDB recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\kv\service_kvdb_als_scale.c` owns three functions:

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default initializer | `[0x4AECA4,0x4AECB8)` | 20 | checksum the factory record |
| `_kvdbUpdataAlsScale` | `[0x4AECB8,0x4AED88)` | 208 | diagnose/migrate stored data |
| `SVC_KvdbWriteAlsScale` | `[0x4AED88,0x4AEDF6)` | 110 | replace, checksum, and persist |

The complete interval is `[0x004AECA4,0x004AEE28)`, 388 bytes, SHA-256
`441f205adb26893cd98b4edcc5802512ee42f427740f113bd037c07068a98800`.
The bodies contribute 338 bytes with concatenated SHA-256
`a215781fb9f1596bd1bd35cf3602e02575418a1d62fd62649ccbfaee6dc806f7`;
the 50-byte tail contains alignment plus record, key, path, function, and
diagnostic literals.

Stored roots at `0x006D1E3C` and `0x00746D20` recover the two callbacks missed
by the baseline decompiler. Three direct entry calls and 21 body calls close
all ingress and providers. No raw word, direct branch, or stored pointer
targets a strict body interior.

## Record and migration

The twelve-byte `kvAlsScale` record resides at `0x200037BC`. Bytes zero through
seven are CRC-covered, the CRC occupies bytes eight and nine, and bytes ten
and eleven remain trailing record data. Payload field names are deliberately
not inferred from the initialized values.

The authenticated factory image is `010000000004000000000000`: its embedded
schema version is 1 and its boot CRC field is zero. Default initialization
writes CRC `0xAA2D` without changing the version.

The writer copies all twelve bytes, forces version 1, computes CRC over the
first eight bytes, persists the record, and returns zero irrespective of
persistence status. The two trailing bytes are copied but excluded from the
CRC.

Migration never imports its stack temporary. Missing data rewrites the current
record. A successful read rewrites only when the stored CRC differs from
current and stored version is zero. A version-1 CRC mismatch is deliberately
ignored.

## Reconstruction boundary

`components/apollo_main/core_overlay/kvdb_als_scale.c` is an independently
authored three-entry candidate (3,508 bytes, SHA-256
`626119a5b2298aa233d22294cfd6121b6c5dad45a2bacacb84cb0124899649d4`).
Host tests pin the factory checksum, whole-record writer, version forcing, and
all migration branches. Freestanding compilation exposes exactly three global
Thumb text symbols. The analyzer and manifests pin every body, literal,
retained string, ingress edge, and initialized byte.

The exact historical source revision is unresolved, and payload field names
and diagnostics remain abstract. The candidate is absent from `overlay.json`;
provider binding, placement, redirects, and package verification remain
pending, so it claims zero package ownership bytes.
