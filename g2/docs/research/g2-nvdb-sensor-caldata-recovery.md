# G2 NVDB sensor-calibration recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\NV\service_nvdb_sensor_caldata.c` owns eight
functions and two calibration records. The complete physical object is
`[0x00509764,0x00509B48)`, 996 bytes, SHA-256
`aea081d2dc99d08bbdc14fdb96a4e6b9e55825f41335e1dbf36dce6e4c60ae3b`.
Its bodies contribute 900 bytes with concatenated SHA-256
`4baf671c1b1f3e1c18a80ecd6bb5e614aa0ceae3cdbc82949cac0d411475ff6a`.

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| primary default initializer | `[0x509764,0x50977C)` | 24 | checksum the factory `nvSCald` record |
| `_nvdbUpdataSensorCaldata` | `[0x50977C,0x50990C)` | 400 | read/diagnose/migrate the primary record |
| primary updater | `[0x50990C,0x509984)` | 120 | replace all primary payloads and persist |
| AG default initializer | `[0x509984,0x50999A)` | 22 | checksum the factory `nvSCaldAG` record |
| AG migration callback | `[0x50999A,0x50999E)` | 4 | return zero without reading or writing |
| AG updater | `[0x50999E,0x5099F8)` | 90 | selectively replace AG payloads and persist |
| AG reader | `[0x5099F8,0x509A3E)` | 70 | import AG data, validate, and copy it out |
| `_nvdbCheckSensorCaldata` | `[0x509A40,0x509AEA)` | 170 | replace one suspicious matrix pattern |

Stored Thumb roots at `0x006D1E9C`, `0x006D1EA4`, `0x0078F524`, and
`0x0078F528` identify both default/migration pairs. Ten direct entry calls and
50 complete body calls account for all other ingress and providers. No direct
branch or aligned stored pointer targets a strict body interior. Two unaligned
four-byte windows happen to equal interior addresses; both begin at odd image
addresses and are pinned as byte coincidences, not pointers.

## Persistent records

The primary `nvSCald` record resides at `0x200038F4`:

| Offset | Size | Recovered role |
|---:|---:|---|
| `0x00` | 1 | schema version, current value 1 |
| `0x01` | 3 | alignment/reserved |
| `0x04` | 12 | three-float payload A |
| `0x10` | 12 | three-float payload B |
| `0x1C` | 16 | four-float payload C |
| `0x2C` | 16 | four-word fixed payload |
| `0x3C` | 4 | float scale |
| `0x40` | 24 | opaque calibration payload |
| `0x58` | 2 | CRC-16/CCITT-FALSE over `[0x00,0x58)` |
| `0x5A` | 2 | trailing alignment/reserved |

The authenticated 92-byte boot image has `1.25f` defaults in both 3-vectors,
all four payload-C lanes, and the scale; fixed words
`{-1234567,1234567,1234567,-1234567}`; and 24 `0xFF` opaque bytes. Its CRC
field starts zero in the loader image and the default initializer writes
`0xD886`.

The AG record `nvSCaldAG` resides at `0x20003950`:

| Offset | Size | Recovered role |
|---:|---:|---|
| `0x00` | 1 | schema version, current value 1 |
| `0x01` | 3 | alignment/reserved |
| `0x04` | 12 | three-float payload A |
| `0x10` | 12 | three-float payload B |
| `0x1C` | 36 | row-major 3×3 float matrix |
| `0x40` | 2 | CRC-16/CCITT-FALSE over `[0x00,0x40)` |
| `0x42` | 2 | trailing alignment/reserved |

Its vectors boot as zero. The 36 matrix bytes exactly equal the compiled
fallback at `0x00759C60` (SHA-256
`07beb66d765a155d2367c308a22d9b7f039818d27bf8bdd8f8adab756001bfea`).
Initialization writes CRC `0x82FC`.

## Persistence and fallback behavior

The primary migration callback reads 92 bytes into a stack temporary. A
missing key rewrites the current SRAM defaults. For a successful read, it
compares only the temporary CRC field with the current SRAM CRC, and rewrites
only when those differ and the temporary version is zero. It never imports
the temporary payload or validates it against its own CRC. This deliberately
matches the unusual migration family used by the adjacent MAC and buzzer
helpers.

The primary updater always replaces every payload, sets version 1, computes
the checksum over the first 88 bytes, and writes all 92 bytes. The AG updater
sets version 1 but treats each of its three pointers independently: null leaves
that block unchanged. It then checksums and writes all 68 bytes.

The AG reader is intentionally different from the primary migration path: it
reads directly into the live SRAM record, calls the checker regardless of the
read result, copies both vectors and matrix to the caller, and returns the raw
read result. The checker first requires the external product predicate to
return exactly 1. It replaces the matrix only when:

- `matrix[0]` is at least `0.6000000834` and below `0.8500000238`; and
- `matrix[5]` is at least `-0.9499999285` and below `-0.6999999881`.

On that narrow pattern it emits the retained abnormal-calibration diagnostic,
copies the compiled default matrix, and returns 1. Every other path returns 0.
The checker does not recompute or persist the AG CRC after the replacement.

## Reconstruction boundary

The stock image retains category `nv.s.cald`, both keys, exact misspelled
symbol `_nvdbUpdataSensorCaldata`, exact `_nvdbCheckSensorCaldata`, and the
absolute product path. Exact original source and historical generating commit
remain unresolved; payload names beyond sizes and observed use are therefore
kept conservative.

`components/apollo_main/core_overlay/nvdb_sensor_caldata.c` is an independently
authored eight-entry behavioral candidate. Host tests cover both default CRCs,
primary layout/update/migration, partial AG updates, direct AG import, predicate
gating, and the suspicious-pattern replacement. Freestanding target
compilation requires exactly eight global Thumb text symbols. The analyzer and
manifests pin every body, literal, retained string, call root, record byte, and
matrix byte.

Production routing remains deferred until fixed SRAM/key/provider seams,
diagnostics, placement, guarded redirects, and package validation close. This
increment claims zero package ownership bytes and does not access hardware.
