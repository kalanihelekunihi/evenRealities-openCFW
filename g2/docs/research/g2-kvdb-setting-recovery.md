# G2 primary KVDB setting recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
production-routed under the reviewed apple-clang profile. Run addresses use
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

## Production routing

The candidate is now routed into the Apollo main overlay byte-identically
(3,628 bytes, SHA-256 `8205380cddd721ee7e74e08c1ea50618f07cd56158c34b3727bfe4364d240e58`)
under the reviewed apple-clang profile. Provider binding uses the retained
CRC-16/CCITT provider at `0x0049ACD4` (null seed selects `0xFFFF`) and the
database-zero KVDB blob read/write adapters at `0x004D956C` and `0x004D957E`,
matching the recovered call ABI exactly. Placement appends three relocated
leaves to the overlay: the 28-byte default initializer, the 160-byte
whole-record writer carrying a 10-byte `kvSetting` key-string read-only
closure, and the 64-byte migration callback carrying the same key-string
closure and calling the source-owned writer leaf. Three `B.W` entry redirects
with NOP fill replace the 340 stock body bytes across
`[0x004AEB20,0x004AEC74)`; the 48-byte literal tail stays retained stock
data, and the two stored roots at `0x006D1E4C`/`0x00746D34` plus all three
direct entry calls reach the source leaves through the redirects. The fixed
SRAM record at `0x200037E0` is untouched.

Apple Clang 21 overlay/component/package sizes are `145242/3668638/4447132`
with SHA-256 `8f891d528010c954f330e3cf1a05cf50af559147f502690e0854d15167cb838a`,
`15ce61e3713f3f9ac0cd7a83e80001641ea57317e8e4d0b49c248cd9733aa48e`, and
`203ecd4c6bfbf9458d94d80676bfb2edbc91b8bad783e7b42d1baa084befbcf8`. The
leaves and redirects are gated `apple-clang`; the linux-clang profile keeps
its recorded pins, and linux-clang leaf pins await Linux toolchain
regeneration. Ownership is 340 replaced stock body bytes. The component
build, source package, `open_cfw verify`, and the fail-closed analyzer and
manifest census all pass.
