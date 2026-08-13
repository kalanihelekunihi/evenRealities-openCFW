# G2 primary KVDB setting recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\kv\service_kvdb_setting.c` owns three functions:

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default initializer | `[0x4AEB20,0x4AEB34)` | 20 | checksum the factory record |
| `_kvdbUpdataSetting` | `[0x4AEB34,0x4AEC04)` | 208 | diagnose/migrate stored data |
| `SVC_KvdbWriteSetting` | `[0x4AEC04,0x4AEC74)` | 112 | replace, checksum, and persist |

The complete interval is `[0x004AEB20,0x004AECA4)`, 388 bytes, SHA-256
`30946d06c30667b33120a1ae4f2d5d0b3a671e9723f4372b9f0a7e342bd9e6c4`.
The bodies contribute 340 bytes with concatenated SHA-256
`e8b2fc69b27a134b51d4bd037f80ec0977f9f49729a16332c0bbc5d350b992ef`;
the 48-byte tail contains record, key, path, function, and diagnostic literals.

Stored roots at `0x006D1E4C` and `0x00746D34` recover the two callbacks missed
by the baseline decompiler. Three direct entry calls and 22 body calls close
all ingress and providers. No raw word, direct branch, or stored pointer
targets a strict body interior.

## Record and migration

The 28-byte `kvSetting` record resides at `0x200037E0`. Bytes zero through 23
are CRC-covered, the CRC occupies bytes 24 and 25, and bytes 26 and 27 remain
trailing record data. Payload field names are deliberately not inferred from
the initialized values.

The authenticated factory image is
`0164010000000000060101001e000000000000000000000000000000`: its embedded
schema version is 1 and its boot CRC field is zero. Default initialization
writes CRC `0xA288` without changing the version.

The writer copies all 28 bytes, forces version 4, computes CRC over the first
24 bytes, persists the record, and returns zero irrespective of persistence
status. Rewriting the factory record therefore upgrades byte zero to 4 and
changes its CRC to `0x4987` while preserving the two trailing bytes.

Migration never imports its stack temporary. Missing data rewrites and
upgrades the current record. A successful read rewrites only when the stored
CRC differs from current and stored version is less than 4. A version-4 CRC
mismatch is deliberately ignored.

## Reconstruction boundary

`components/apollo_main/core_overlay/kvdb_setting.c` is an independently
authored three-entry candidate (3,628 bytes, SHA-256
`8205380cddd721ee7e74e08c1ea50618f07cd56158c34b3727bfe4364d240e58`).
Host tests pin the factory checksum, version upgrade, whole-record writer, and
all migration branches. Freestanding compilation exposes exactly three global
Thumb text symbols. The analyzer and manifests pin every body, literal,
retained string, ingress edge, and initialized byte.

The exact historical source revision is unresolved, and payload field names
and diagnostics remain abstract. The candidate is absent from `overlay.json`;
provider binding, placement, redirects, and package verification remain
pending, so it claims zero package ownership bytes.
