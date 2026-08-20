# G2 NVDB buzzer recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
production-routed under the reviewed apple-clang profile. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\NV\service_nvdb_buzzer.c` owns five functions in
source order and a 28-byte literal tail. The complete physical object is
`[0x0058F9D4,0x0058FAAC)`, 216 bytes, SHA-256
`d6b02b1bed7012f6c8288b83f106454d7a992acba1f92fa10e390f82fe0b0e8b`.
The five bodies contribute 188 bytes with concatenated SHA-256
`70118688652fb4a53ee42a522f5df58b6defcba717b99cd8bd420b305bcb95e3`.

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default CRC initializer | `[0x58F9D4,0x58F9E8)` | 20 | checksum the boot/default record |
| `_nvdbUpdataBuzzer` | `[0x58F9E8,0x58FA60)` | 120 | read and migrate the persistent record |
| frequency getter | `[0x58FA60,0x58FA66)` | 6 | return frequency at record offset 4 |
| duty getter | `[0x58FA66,0x58FA6C)` | 6 | return duty at offset 8 |
| persistent updater | `[0x58FA6C,0x58FA90)` | 36 | update, checksum, and write the record |

The first two bodies are rooted by stored Thumb pointers at `0x006D1E84`
and `0x0078F518`. Five direct calls root the other three bodies. Eleven direct
calls leave or remain within the TU. A whole-image scan finds no stored or
directly branched strict-interior target.

## Record ABI and policy

The twelve-byte record at SRAM `0x200038D8` is:

| Offset | Type | Meaning |
|---:|---|---|
| 0 | `uint8_t` | schema version, current value 2 |
| 1 | 3 bytes | retained reserved bytes |
| 4 | `uint32_t` | frequency in Hz |
| 8 | `uint8_t` | duty percentage |
| 9 | 1 byte | retained reserved byte |
| 10 | `uint16_t` | little-endian CRC-16/CCITT-FALSE |

The authenticated boot bytes are `02000000a00f00001e000000`: version 2,
4,000 Hz, 30%, and an initially zero checksum. The initializer runs the
already source-owned stock provider at `0x0049ACD4` over bytes `[0,10)` with
a null seed, producing `0x9B1E`, then stores it at offset 10.

`_nvdbUpdataBuzzer` reads key `nvBuzzer` into a temporary twelve-byte record.
If the read fails, it writes the current defaults. If the read succeeds, it
compares only the temporary CRC field with the current record's CRC. A mismatch
is rewritten only when the temporary version is below 2. It does not validate
the temporary payload against its own CRC and does not copy that payload into
the current SRAM record. The clean-room candidate intentionally preserves this
non-obvious stock behavior.

The updater stores the requested frequency and duty, forces version 2,
recomputes the checksum over the first ten bytes, and writes all twelve bytes
to `nvBuzzer` through the existing NVDB wrapper.

## Evidence and reconstruction boundary

The object retains category `nv.buzzer`, key `nvBuzzer`, exact misspelled
symbol `_nvdbUpdataBuzzer`, and the original absolute path. The exact product
source and historical generating commit have not been recovered, so no
whole-source identity or redistributability claim is made.

`components/apollo_main/core_overlay/nvdb_buzzer.c` is an independently
authored five-entry behavioral candidate. Its host fixture tests initialization,
accessors, update/write, missing-record recovery, pre-v2 migration, equal-CRC
handling, and the current-v2 mismatch no-op. The same source compiles for
`thumbv7em-none-eabi` with exactly five global text symbols. The analyzer and
manifests pin the stock bytes, literals, strings, call topology, and record ABI.

Production routing remains deferred until the fixed record/key/provider seams,
retained diagnostic binding, placement, guarded redirects, and complete package
validation are closed. This increment claims zero package ownership bytes and
does not access or modify hardware.

## Production routing

The candidate is now routed into the Apollo main overlay byte-identically
(4,043 bytes, SHA-256
`c4ed1b989c5e7ab019bd00fa9e57ee6ed166afe24caef7f1d37700efefe9656b`) under the
reviewed apple-clang profile. Provider binding uses the retained CRC-16
provider at `0x0049ACD4` and the retained NVDB blob read/write adapters at
`0x005105F0`/`0x00510602`, matching the recovered call ABI exactly; the
retained diagnostic hook stays the candidate's deliberate no-op. Placement
appends five relocated leaves to the overlay: the 28-byte default-record CRC
initializer, the 52-byte persistent updater, the 64-byte `_nvdbUpdataBuzzer`
migration callback, the 12-byte frequency getter, and the 12-byte duty
getter, preceded once by a two-byte alignment pad. Five `B.W` entry
redirects with NOP fill replace the 188 stock body bytes across
`[0x0058F9D4,0x0058FA90)`; the 28-byte literal tail
`[0x0058FA90,0x0058FAAC)` stays retained stock data, and the two stored
entry roots at `0x006D1E84`/`0x0078F518` plus the five direct entry calls
reach the source leaves through the redirects. The fixed twelve-byte SRAM
record at `0x200038D8`, the `nvBuzzer` key, and the boot defaults are
untouched.

Apple Clang 21 overlay/component/package sizes are `150692/3674088/4452582`
with SHA-256 `58920545ebe56b89e488bc916aec218f47bef3271d3558c4e8c63d5f646ff7d0`,
`0b88c15009a58a851c3d3408084cf8c685782029cea1c64107315f4f5177d9bc`, and
`5d1efae37054e4a8bc33dd95cf5511ce321e1f4d0c9cb127d8bf0e2b7eb893f1`. The
leaves and redirects are gated `apple-clang`; the linux-clang profile keeps
its recorded pins, and linux-clang leaf pins await Linux toolchain
regeneration. Ownership is 188 replaced stock body bytes. The component
build, source package, `open_cfw verify`, and the fail-closed analyzer and
manifest census all pass. No package was signed or flashed and no hardware
was accessed.
