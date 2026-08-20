# G2 NVDB system-data recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
production-routed into the Apollo main overlay. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\NV\service_nvdb_sys_dt.c` owns thirteen functions,
a 172-byte persistent record, a 40-entry legacy-product table, and the PSN OTP
journal logic. The complete physical object is
`[0x004AEE28,0x004B03E0)`, 5,560 bytes, SHA-256
`b26a244bac13d02e90a91a82a4f4332b7c7331258f1b1c3a5d6cb7f856ffbc67`.
Its bodies contribute 5,084 bytes with concatenated SHA-256
`5ab990b798f06a9bbe3e56b66c86f5b1ddd33bb0dc7f29dfad1ad91b4c31f1a1`;
seven split alignment/literal regions contribute the remaining 476 bytes.

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default initializer | `[0x4AEE28,0x4AEE3E)` | 22 | checksum the factory record |
| `_nvdbUpdataSysDt` | `[0x4AEE3E,0x4AF11C)` | 734 | audit/migrate stored data and PSN sources |
| `SVC_NvdbWriteSysData` | `[0x4AF11C,0x4AF73A)` | 1,566 | indexed update and whole-record persistence |
| system-data getter | `[0x4AF73A,0x4AF7B8)` | 126 | return exact field pointers |
| `SVC_NvdbReadSysData` | `[0x4AF7B8,0x4AF87E)` | 198 | direct import followed by PSN override |
| `SVC_NvdbparsePsn` | `[0x4AF8D0,0x4AFBB6)` | 742 | decode the fourteen-character PSN |
| manufacturer helper | `[0x4AFBBC,0x4AFBCE)` | 18 | map manufacturer code |
| year helper | `[0x4AFBCE,0x4AFBE4)` | 22 | map A-Z to 2024-2049 |
| month helper | `[0x4AFBE4,0x4AFC0C)` | 40 | format A-Z as decimal 1-26 |
| aging reset | `[0x4AFC10,0x4AFC64)` | 84 | clear three time payloads and statuses |
| legacy-PSN scan | `[0x4AFC68,0x4AFCA2)` | 58 | set the legacy-device flag |
| `SVC_ReadPSNFromOTP` | `[0x4AFCDC,0x4AFF54)` | 632 | find the newest valid OTP PSN |
| `SVC_WritePSNToOTP` | `[0x4AFFC0,0x4B030A)` | 842 | validate, deduplicate, and append a PSN |

The default and migration roots are stored at `0x006D1EAC` and `0x0078F52C`.
Thirty-seven direct entry calls and 299 complete body calls close the remaining
ingress/provider topology. No legitimate direct branch or stored pointer
targets a strict body interior. Forty-eight raw four-byte windows happen to
decode as interior values; eight are aligned instruction/table coincidences.
The sole BL-like interior target at `0x004AB932 -> 0x004AF9EC` starts on the
second halfword of a real 32-bit `mul` and is rejected explicitly.

## Persistent record

The `nvSysDt` record resides at `0x20003994`:

| Offset | Size | Recovered role |
|---:|---:|---|
| `0x00` | 1 | schema version, current value 2 |
| `0x01` | 15 | product serial, fourteen characters plus NUL |
| `0x10` | 22 | board serial |
| `0x26` | 2 | CRC-16/CCITT-FALSE over `[0x00,0x26)` |
| `0x28` | 4 | lux base |
| `0x2C` | 1 | canvas X |
| `0x2D` | 1 | canvas Y |
| `0x2E` | 1 | panel current |
| `0x2F` | 1 | reserved/alignment byte |
| `0x30` | 40 | aging start time payload |
| `0x58` | 40 | aging end time payload |
| `0x80` | 40 | aging SOC-to-10 time payload |
| `0xA8` | 1 | wrong-touch status |
| `0xA9` | 1 | begin-charge SOC |
| `0xAA` | 1 | total-times counter |
| `0xAB` | 1 | aging-finish flag |

The authenticated IAR initialized-SRAM stream yields the exact 172-byte
factory image, SHA-256
`f2b3d283ef574404c0d9c402a52a43cba58c0d415f23d7d6d8f38005aca7f05d`.
It contains product serial `S200LDBE210001`, board serial
`S200EVBTLN25063011111`, lux base 78,953, canvas 12×10, and panel current 15.
The loader CRC bytes start zero; the default initializer writes `0x1DC7`.

Update indices zero through twelve address the individual fields in record
order; index thirteen replaces all 172 bytes. Every valid update then forces
version 2, recomputes the first-38-byte CRC, and writes the entire record.
Invalid indices and null values do nothing. The getter returns field pointers
for zero through twelve and the record base for every other index, including
thirteen.

## Migration and PSN behavior

The migration callback is deliberately non-importing. It clears the live PSN
terminator, parses the current PSN, reads FlashDB into a stack temporary, runs
the legacy-PSN scan, and lets the latest valid OTP PSN replace the live PSN.
It rewrites the current record only when the key is missing or when the stored
CRC field differs from the current CRC and the stored version is below 2. It
does **not** import the temporary record and does **not** reset aging state.

The ordinary read API differs: it imports all 172 bytes directly into live
SRAM, runs the same legacy scan and OTP override, then returns the requested
field pointer.

The exact 40-pointer legacy table is at `0x006D3358`, 160 bytes, SHA-256
`ced8332c75782b5c1b3d18e99500f923aad63ad01807e8c2f31bc357eda9a0e1`.
The analyzer authenticates every pointed-to fourteen-character serial.

The OTP journal begins at offset `0x340` and contains eight 16-byte slots.
Each slot stores a fourteen-character PSN and two zero pad bytes. A valid PSN
starts `S2` and has decimal digits in positions 8 through 13. Reading scans
all slots and returns the last valid entry, but a failed word read ends the
scan; cleanup occurs on every path. Writing validates and deduplicates first,
then appends through four word writes and rejects a full journal.

## Reconstruction boundary

`components/apollo_main/core_overlay/nvdb_sys_dt.c` is an independently
authored thirteen-entry behavioral candidate (22,347 bytes, SHA-256
`a18152b8a7e769142bb21795cb724ef29df2c8ea18176050d12d8606189516c7`).
Host tests cover factory initialization, all indexed fields, migration/read
differences, PSN parsing and legacy classification, aging reset, OTP scanning,
deduplication, capacity, and failure cleanup. Freestanding target compilation
requires exactly thirteen global Thumb text symbols.

The analyzer and three manifests pin every body, split pool, retained string,
call root, factory byte, legacy serial, and interior-ingress classification.
The exact historical source revision remains unresolved. Diagnostic formatting
and hardware-specific OTP gate/provider calls are abstracted behind hooks.

## Production routing

The candidate is now routed into the Apollo main overlay under the reviewed
apple-clang profile. The routing adds one seam to the candidate: the legacy
scan reads its table through `OPEN_CFW_NVDB_SYS_DT_LEGACY_PSNS`, which the
host build defaults to the candidate's own 40-entry copy and the production
leaves bind to the retained stock table at `0x006D3358` — the overlay closure
extractor rejects the pointer-relocated read-only data a built-in copy would
require, and the stock body read the same retained table. Provider binding is
exact: the retained CRC-16 provider at `0x0049ACD4`, the retained NVDB blob
read/write adapters at `0x005105F0`/`0x00510602`, the source-owned
peripheral-power enable/disable entries at `0x0047F5B8`/`0x0047F7AE` and the
source-owned CMSIS delay at `0x00449376` (through the pinned
`-DOPEN_CFW_NVDB_SYS_DT_OTP_BEGIN`/`_END` leaf flags, which reproduce the
stock enable-0x1D/enable-0x17/delay and disable-0x17/disable-0x1D gate
sequences), and the retained OTP INFOC word accessors at
`0x0051381A`/`0x00513850`. The fourteen-field parse diagnostic sink is
compiled out by the pinned `-DOPEN_CFW_NVDB_SYS_DT_PARSED` no-op binding, the
same deliberate no-op policy the other NVDB closures use for retained
diagnostics. Placement appends thirteen relocated leaves to the overlay:
4,338 text bytes plus the two 23-byte read-only string closures carried by
the manufacturer and month helpers and twelve alignment pad bytes. Thirteen
`B.W` entry redirects with NOP fill replace the 5,084 stock body bytes across
`[0x004AEE28,0x004B03E0)`; the seven split alignment/literal islands (476
bytes) stay retained stock data, and the two stored entry roots at
`0x006D1EAC`/`0x0078F52C` plus the 37 direct entry calls reach the source
leaves through the redirects. The 172-byte SRAM record at `0x20003994`, the
`nvSysDt` key, the legacy table, and the factory defaults are untouched.

Apple Clang 21 overlay/component/package sizes are `155682/3679078/4457572`
with SHA-256 `3bb04fb7f66d8a3d5e53ec1028bb73b5f832bb8e1e39827baf8a6c014d3c5d39`,
`5160689a88da1ba7a0163c7f05739d3fcc3caa0f9863e6d7ac2e5fa8d54e8dea`, and
`f66065fe5ea21f701985897f3f2629ff84a0fb050a563d300ebefa9ec55d7c4b`. The
leaves and redirects are gated `apple-clang`; the linux-clang profile keeps
its recorded pins, and linux-clang leaf pins await Linux toolchain
regeneration. Ownership is 5,084 replaced stock body bytes. The component
build, source package, `open_cfw verify`, and the fail-closed analyzer and
manifest census all pass. No package was signed or flashed and no hardware
was accessed.
