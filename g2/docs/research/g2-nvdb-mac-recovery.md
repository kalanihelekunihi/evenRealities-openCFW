# G2 NVDB MAC recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\NV\service_nvdb_mac.c` owns three functions in
source order and a 32-byte literal tail. The complete physical object is
`[0x005D9F48,0x005DA080)`, 312 bytes, SHA-256
`731244e0484db0daef87d3a5224d07640f46631a999ec6fab405b79518de599f`.
The bodies contribute 280 bytes with concatenated SHA-256
`0b74f6f5656bfe25a9412b1dff7171be025a791ad0addbdef48c472f4e0986d1`.

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default initializer | `[0x5D9F48,0x5D9FC2)` | 122 | derive a stable static-random address from the Apollo510 chip IDs |
| `_nvdbUpdataMac` | `[0x5D9FC2,0x5DA034)` | 114 | read and migrate the persistent record |
| persistent updater | `[0x5DA034,0x5DA060)` | 44 | copy an address, checksum, and write the record |

The first two bodies are rooted by stored Thumb pointers at `0x006D1E8C`
and `0x0078F51C`. Two internal calls root the updater. Eighteen direct calls
leave or remain within the TU. A whole-image scan finds no stored or directly
branched strict-interior target.

## Record and address derivation

The ten-byte record at SRAM `0x200038E4` is:

| Offset | Type | Meaning |
|---:|---|---|
| 0 | `uint8_t` | schema version, current value 1 |
| 1 | 6 bytes | derived BLE static-random device address |
| 7 | `uint8_t` | reserved byte retained in the checksum |
| 8 | `uint16_t` | little-endian CRC-16/CCITT-FALSE |

The authenticated boot bytes are `01000000000000000000`. The default
initializer asks the already source-owned Apollo510 information provider for
the 64-byte device record, then constructs an eight-byte serial input as
`CHIPID1` followed by `CHIPID0`, both in native little-endian order. It derives
the six address bytes as follows:

1. canonical reflected CRC-32 of the eight serial bytes, copied little-endian
   into address bytes 0--3;
2. CRC-16/CCITT-FALSE of the same bytes, with its high then low byte copied
   into address bytes 4--5;
3. final address byte transformed as `(byte & 0xFC) | 0xC0`.

It then computes CCITT-FALSE across record bytes `[0,8)` and stores the result
at offset 8. The initialized address and record checksum are device-specific;
they are not fixed image data. For the host qualification vector
`CHIPID0=0x01234567`, `CHIPID1=0x89ABCDEF`, the complete initialized record is
`0147e23b4411c800ef1d`.

## Persistence policy

`_nvdbUpdataMac` reads key `nvMAC` into a temporary ten-byte record. If the
read fails, it writes the current derived address. If the read succeeds, it
compares only the temporary CRC field with the current SRAM record's CRC. A
mismatch is rewritten only when the temporary version is zero. It neither
validates the temporary payload against its own CRC nor imports that payload
into the current record. The updater copies six requested address bytes,
forces version 1, recomputes the checksum over the first eight bytes, and
writes all ten bytes.

This is the same non-obvious migration family seen in the adjacent buzzer and
product-mode helpers, and the clean-room candidate intentionally preserves it.

## Evidence and reconstruction boundary

The object retains category `nv.mac`, key `nvMAC`, exact misspelled symbol
`_nvdbUpdataMac`, and the original absolute path. The exact product source and
historical generating commit have not been recovered, so no whole-source
identity or redistributability claim is made.

`components/apollo_main/core_overlay/nvdb_mac.c` is an independently authored
three-entry behavioral candidate. Its host fixture tests chip-ID ordering,
CRC-derived address construction, static-random masking, update/write, missing
record recovery, v0 migration, and the v1 mismatch no-op. The source also
compiles for `thumbv7em-none-eabi` with exactly three global text symbols.
The analyzer and manifests pin stock bytes, literals, strings, calls, stored
roots, and record ABI.

Production routing remains deferred until fixed SRAM/key/provider seams,
retained diagnostics, placement, guarded redirects, and complete package
validation are closed. This increment claims zero package ownership bytes and
does not access or modify hardware.
