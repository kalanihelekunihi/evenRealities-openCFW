# G2 NVDB advertising-magic recovery

Status: complete binary census, host/Thumb-qualified clean-room candidate,
and production routing into the Apollo main overlay. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The compact first-party NVDB object immediately before
`service_nvdb_mac.c` owns three functions and a ten-byte alignment/literal
tail. The complete physical object is `[0x005D9ED0,0x005D9F48)`, 120 bytes,
SHA-256
`624d7bfd338051fe5493107be887f052c41475e1b32f8aeac148889f046ad4f7`.
Its bodies contribute 110 bytes with concatenated SHA-256
`54c2a7586a070563f062b418177500ac9af47f88e334029e28ef0ac262f57ba7`.

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default CRC initializer | `[0x5D9ED0,0x5D9EE4)` | 20 | checksum the boot/default record |
| loader/migrator | `[0x5D9EE4,0x5D9F1C)` | 56 | read and conditionally rewrite the record |
| persistent updater | `[0x5D9F1C,0x5D9F3E)` | 34 | update magic, checksum, and persist |

Stored Thumb pointers at `0x006D1E7C` and `0x0078F514` root the first two
bodies; two internal calls root the updater. Six direct calls leave or remain
within the TU, and no stored or directly branched strict-interior target
survives the whole-image scan. The tail contains two alignment bytes followed
by the SRAM-record and key pointers.

## Record and migration policy

The four-byte `nvAdvMagic` record at SRAM `0x200038D4` contains version at
offset 0, magic byte at offset 1, and little-endian CCITT-FALSE at offset 2.
Authenticated boot bytes are `01200000`: version 1, default magic `0x20`, and
an initially zero checksum. Initialization checksums the first two bytes and
stores `0x0A5C`.

The loader reads four bytes from key `nvAdvMagic`. A missing record rewrites
the current default. On success, it compares only the stored CRC field with
the current SRAM record's CRC; a mismatch is rewritten only for version zero.
It neither validates the read payload against its own CRC nor imports it.
The updater stores the requested magic, forces version 1, recomputes the CRC,
and writes all four bytes.

## Evidence boundary

Unlike the adjacent MAC and buzzer objects, this object retains no source path
or function-name string. Its attribution is therefore intentionally limited to
the exact `nvAdvMagic` key, SRAM record, initialization-table roots, source-
ordered adjacency, and behavior. No exact original filename or symbol name is
claimed.

`components/apollo_main/core_overlay/nvdb_adv_magic.c` is an independently
authored three-entry behavioral candidate. Host tests cover initialization,
update/write, missing-record recovery, v0 migration, equal-CRC behavior, and
the v1 mismatch no-op; freestanding Thumb compilation exposes exactly three
global text symbols.

Production routing remains deferred until initialization ownership, fixed
record/key/provider seams, placement, guarded redirects, and package validation
are closed. This increment claims zero package ownership bytes and performs no
hardware operation.

## Production routing

The candidate is now routed into the Apollo main overlay byte-identically
(3,211 bytes, SHA-256
`6385cb384472a5789331ed22cc0068f20272c0c689ab241b90d589c13a692c21`) under the
reviewed apple-clang profile. Provider binding uses the retained CRC-16
provider at `0x0049ACD4` and the retained NVDB blob read/write adapters at
`0x005105F0`/`0x00510602`. Placement appends three relocated leaves to the
overlay: the 28-byte default-record CRC initializer, the 50-byte persistent
updater, and the 62-byte migration callback, with a single two-byte
alignment pad before the migration callback. Three `B.W` entry redirects
with NOP fill replace the 110 stock body bytes across
`[0x005D9ED0,0x005D9F3E)`; the ten-byte alignment and literal tail
`[0x005D9F3E,0x005D9F48)` stays retained stock data, and the two stored
entry roots at `0x006D1E7C`/`0x0078F514` reach the source leaves through
the redirects. The fixed four-byte SRAM record at `0x200038D4`, the
`nvAdvMagic` key, and the boot defaults are untouched.

Apple Clang 21 overlay/component/package sizes are `151286/3674682/4453176`
with SHA-256 `d30879825d2c513dcef88a951a0aac9a9c3ff476da56720c2138d22f5ba9c9f5`,
`8aac36ba8830d740aa08e461e43c711af9e04bf59a529eb5b5671be84774be9f`, and
`5fd04249a65b195c17a971d1ba105972d062976267451967fd4c0f840da4145d`. The
leaves and redirects are gated `apple-clang`; the linux-clang profile keeps
its recorded pins, and linux-clang leaf pins await Linux toolchain
regeneration. Ownership is 110 replaced stock body bytes. The component
build, source package, `open_cfw verify`, and the fail-closed analyzer and
manifest census all pass. No package was signed or flashed and no hardware
was accessed.
