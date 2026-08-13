# G2 terminal-mode KVDB recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
not production-routed. Run addresses use
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
