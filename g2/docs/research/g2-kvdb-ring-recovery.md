# G2 ring KVDB recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\kv\service_kvdb_ring.c` owns three functions:

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default initializer | `[0x5D9B6C,0x5D9B82)` | 22 | checksum the factory record |
| `_kvdbUpdataRing` | `[0x5D9B82,0x5D9D40)` | 446 | diagnose/migrate stored data |
| `SVC_KvdbWriteRing` | `[0x5D9D40,0x5D9E88)` | 328 | update, checksum, and persist |

The complete interval is `[0x005D9B6C,0x005D9ED0)`, 868 bytes, SHA-256
`2b319f20a4542cc7e036eb7cb6264af5c571139de15657518826b13275f2c489`.
The bodies contribute 796 bytes with concatenated SHA-256
`890a82e4756f95ebeb75bd253b5c2914b58fc7f30b125ea0589a1832153bb5ad`;
the 72-byte tail contains record, field, key, path, function, and diagnostic
literals.

Stored roots at `0x006D1E44` and `0x00746D30` recover the initializer and
migration body missed by the baseline decompiler. Two internal calls root the
writer, and 45 direct body calls close all providers. No raw word, `BL`,
`B.W`, or stored pointer targets a strict body interior.

## Record and migration

The 24-byte `kvRing` record at `0x200037C8` is:

| Offset | Bytes | Meaning |
|---:|---:|---|
| 0 | 1 | schema version |
| 1 | 6 | MAC address |
| 7 | 14 | ring name buffer |
| 21 | 1 | preserved reserved byte |
| 22 | 2 | little-endian CRC-16 |

The authenticated factory bytes are
`01ffffffffffff4556454e2052315f464646464646000000`: version 1, broadcast
MAC, name `EVEN R1_FFFFFF`, reserved zero, and zero boot CRC. Default
initialization writes checksum `0x06D4` over the first 22 bytes.

The writer copies six MAC bytes or fills them with `0xFF` for a null pointer.
A non-null name has `strncpy(..., 14)` semantics and then unconditionally
forces name byte 13 (record offset 20) to NUL. A null name instead fills all
fourteen name bytes with `0xFF`; it does not apply the forced NUL. The writer
preserves byte 21, forces version 1, recomputes the first-22-byte CRC, and
persists all 24 bytes.

Migration reads a stack temporary but never imports it. Missing data rewrites
the current MAC/name. A successful read rewrites only when the stored CRC
differs from the live CRC and stored version is zero; a version-1 mismatch is
ignored. Rewriting the initialized factory record through its non-null live
name truncates the final `F` at offset 20 and produces CRC `0xA1BE`.

## Reconstruction boundary

`components/apollo_main/core_overlay/kvdb_ring.c` is an independently authored
three-entry candidate (4,391 bytes, SHA-256
`a18825d4061845a39b2cb5926a3b8100f9aba9aaf927e74f0c4d08a7db288a13`).
Host tests pin the initialized CRC, non-null and null update rules, reserved
byte preservation, missing-data rewrite, every version/CRC branch, and
non-importing migration. Freestanding compilation exposes exactly three
global Thumb text symbols. The analyzer and manifests pin every body, literal,
retained string, ingress edge, and initialized byte.

The exact historical source revision is unresolved, and diagnostic formatting
remains abstract. The candidate is absent from `overlay.json`; provider
binding, placement, redirects, and package verification remain pending, so it
claims zero package ownership bytes.
