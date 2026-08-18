# G2 ALS-scale KVDB recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
production-routed under the reviewed apple-clang profile. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\kv\service_kvdb_als_scale.c` owns three functions:

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| default initializer | `[0x4AECA4,0x4AECB8)` | 20 | checksum the factory record |
| `_kvdbUpdataAlsScale` | `[0x4AECB8,0x4AED88)` | 208 | diagnose/migrate stored data |
| `SVC_KvdbWriteAlsScale` | `[0x4AED88,0x4AEDF6)` | 110 | replace, checksum, and persist |

The complete interval is `[0x004AECA4,0x004AEE28)`, 388 bytes, SHA-256
`441f205adb26893cd98b4edcc5802512ee42f427740f113bd037c07068a98800`.
The bodies contribute 338 bytes with concatenated SHA-256
`a215781fb9f1596bd1bd35cf3602e02575418a1d62fd62649ccbfaee6dc806f7`;
the 50-byte tail contains alignment plus record, key, path, function, and
diagnostic literals.

Stored roots at `0x006D1E3C` and `0x00746D20` recover the two callbacks missed
by the baseline decompiler. Three direct entry calls and 21 body calls close
all ingress and providers. No raw word, direct branch, or stored pointer
targets a strict body interior.

## Record and migration

The twelve-byte `kvAlsScale` record resides at `0x200037BC`. Bytes zero through
seven are CRC-covered, the CRC occupies bytes eight and nine, and bytes ten
and eleven remain trailing record data. Payload field names are deliberately
not inferred from the initialized values.

The authenticated factory image is `010000000004000000000000`: its embedded
schema version is 1 and its boot CRC field is zero. Default initialization
writes CRC `0xAA2D` without changing the version.

The writer copies all twelve bytes, forces version 1, computes CRC over the
first eight bytes, persists the record, and returns zero irrespective of
persistence status. The two trailing bytes are copied but excluded from the
CRC.

Migration never imports its stack temporary. Missing data rewrites the current
record. A successful read rewrites only when the stored CRC differs from
current and stored version is zero. A version-1 CRC mismatch is deliberately
ignored.

## Reconstruction boundary

`components/apollo_main/core_overlay/kvdb_als_scale.c` is an independently
authored three-entry candidate (3,508 bytes, SHA-256
`626119a5b2298aa233d22294cfd6121b6c5dad45a2bacacb84cb0124899649d4`).
Host tests pin the factory checksum, whole-record writer, version forcing, and
all migration branches. Freestanding compilation exposes exactly three global
Thumb text symbols. The analyzer and manifests pin every body, literal,
retained string, ingress edge, and initialized byte.

The exact historical source revision is unresolved, and payload field names
and diagnostics remain abstract. The candidate is absent from `overlay.json`;
provider binding, placement, redirects, and package verification remain
pending, so it claims zero package ownership bytes.

## Production routing

The candidate is now routed into the Apollo main overlay byte-identically
(3,508 bytes, SHA-256 `626119a5b2298aa233d22294cfd6121b6c5dad45a2bacacb84cb0124899649d4`)
under the reviewed apple-clang profile. Provider binding uses the retained
CRC-16/CCITT provider at `0x0049ACD4` (null seed selects `0xFFFF`) and the
database-zero blob read/write adapters at `0x004D956C` and `0x004D957E`,
matching the recovered call ABI exactly. Placement appends three relocated
leaves to the overlay: the 28-byte default initializer, the 90-byte migration
callback, and the 96-byte whole-record writer, the latter two each carrying an
11-byte `kvAlsScale` key-string read-only closure. Three `B.W` entry redirects
with NOP fill replace the 338 stock body bytes `[0x004AECA4,0x004AEDF6)`;
the 50-byte literal tail stays retained stock data, and the two stored roots
at `0x006D1E3C`/`0x00746D20` plus all three direct entry calls reach the
source leaves through the redirects. The fixed SRAM record at `0x200037BC`
is untouched.

Apple Clang 21 overlay/component/package sizes are `143227/3666623/4445117`
with SHA-256 `200b0b3385c26dbe93cfab37503d21f45d3a6a32ee2dd32451c1ce8c63308b10`,
`ad895f785a66f249a9c4d45ea353b559acebf57ad8f82fedf43af2361e79e83b`, and
`62569df0c68123922de03f482f0affae3975114186581dd30adce650d45f28f6`. The
leaves and redirects are gated `apple-clang`; the linux-clang profile keeps
its recorded pins, and linux-clang leaf pins await Linux toolchain
regeneration. Ownership is 338 replaced stock body bytes. The component
build, source package, `open_cfw verify`, and the fail-closed analyzer and
manifest census all pass.
