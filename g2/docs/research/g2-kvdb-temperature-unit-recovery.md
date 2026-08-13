# G2 KVDB temperature-unit recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\kv\service_kvdb_temperature_unit.c` owns three
functions in one physical object:

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default initializer | `[0x49B014,0x49B028)` | 20 | checksum the factory record |
| `_kvdbUpdataTemperatureUnit` | `[0x49B028,0x49B0F8)` | 208 | diagnose/migrate stored data |
| `SVC_KvdbWriteTemperatureUnit` | `[0x49B0F8,0x49B166)` | 110 | replace, checksum, and persist |

The complete interval is `[0x0049B014,0x0049B198)`, 388 bytes, SHA-256
`c03f4581a435c010b7315a9f949a08103d8dcea72869f5f8cba44a57e0fd55d8`.
The three bodies contribute 338 bytes with concatenated SHA-256
`4d9a4d88a10e5938b06f23c46e152295575d41dbe6ce7179bdf4864d26be4500`;
the 50-byte tail contains the record, key, path, function, and diagnostic
literals.

The default and migration callbacks were missed as standalone functions by
the baseline decompiler, but their prologue-to-return Thumb bodies and stored
roots at `0x006D1E54` and `0x00746D38` are exact. Three direct entry calls and
21 complete body calls close all ingress and providers. No raw word, direct
branch, or stored pointer targets a strict body interior.

## Record and behavior

The twelve-byte `kvTemperatureUnit` record resides at `0x200037FC`. Its first
byte is schema version 1, bytes zero through seven are covered by
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
left alone. This is the same unusual non-importing migration family observed
in adjacent first-party NVDB/KVDB helpers.

## Reconstruction boundary

`components/apollo_main/core_overlay/kvdb_temperature_unit.c` is an
independently authored three-entry behavioral candidate (4,260 bytes,
SHA-256 `288f83e95b9526816845f197d0ca7c355a259a03348c0e2140346cb30a01e808`).
Host tests cover initialization, full-record replacement, and every migration
branch. Freestanding target compilation exposes exactly three global Thumb
text symbols. The analyzer and manifests pin all bodies, literals, retained
strings, ingress, and initialized record bytes.

The exact historical source revision remains unresolved. Retained diagnostic
formatting is abstracted behind a hook. The candidate is absent from
`overlay.json`; placement, provider/logger binding, redirects, and package
validation remain pending, so it claims zero package ownership bytes.
