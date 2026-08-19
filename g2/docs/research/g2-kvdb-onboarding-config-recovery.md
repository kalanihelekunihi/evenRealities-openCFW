# G2 onboarding-config KVDB recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
production-routed under the reviewed apple-clang profile. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\kv\service_kvdb_onboarding_config.c` owns six
functions:

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| `SVC_SetKvdbOnboardingConfig` | `[0x4A777C,0x4A77D2)` | 86 | update the indexed live byte |
| `SVC_KvdbBlobWriteOnboardingConfig` | `[0x4A77D2,0x4A7820)` | 78 | persist the live byte |
| update-and-persist wrapper | `[0x4A7820,0x4A7832)` | 18 | compose setter and writer |
| scalar getter | `[0x4A7832,0x4A7838)` | 6 | return the live byte |
| pointer getter | `[0x4A7838,0x4A7846)` | 14 | return the live address |
| `SVC_KvdbReadOnboardingConfig` | `[0x4A7846,0x4A789A)` | 84 | load and return the live address |

The complete interval is `[0x004A777C,0x004A78D0)`, 340 bytes, SHA-256
`5e36bd2e41d5291d353576207da6c5584405af347f3af9a32503c3f40fdd9362`.
The bodies contribute 286 bytes with concatenated SHA-256
`16069fe85f9c1bc5e5bd94870e699c63f560ac3a8b9bf8047b821c4cf406e986`.
The 54-byte owned tail contains two alignment bytes plus the record, key,
path, function, and diagnostic literals.

Eighteen direct `BL` sites root every entry, including the three internal
composition calls. The bodies contain 20 direct calls in total. An exhaustive
image scan finds no stored entry pointer, no `B.W` entry, no direct branch to
a strict interior, and no raw aligned or unaligned interior-pointer window.

## Record and behavior

`kvOnboardingConfig` is a single byte at `0x20000040`; the authenticated
initialized value is `00`. It has no schema version, checksum, reserved byte,
or migration temporary. This is structurally different from the adjacent
versioned KVDB records.

Only data index zero is writable. A nonzero index emits the retained
`Unknown kv dataIdx` diagnostic and returns minus one. Index zero with a null
value deliberately returns success without changing the byte. The
update-and-persist wrapper skips persistence after an invalid index, otherwise
propagating the database writer's result.

The pointer getter returns `0x20000040` for every index; both branch arms load
the same literal. The read function always reads one byte directly into the
live record, diagnoses exactly a zero backend result, and then returns that
same pointer. Unlike the neighboring migration objects, a read therefore
imports the stored byte immediately.

## Reconstruction boundary

`components/apollo_main/core_overlay/kvdb_onboarding_config.c` is an
independently authored six-entry candidate (3,130 bytes, SHA-256
`f8c3154fe326878b2f89908555238ddc190a6cecc6c874aeed342624b24d561e`).
Host tests cover valid, null, and invalid indexed updates; write-result
propagation; write suppression; both getters; and zero/nonzero read results.
Freestanding compilation exposes exactly six global Thumb text symbols. The
analyzer and manifests pin every body, literal, retained string, ingress edge,
and the initialized byte.

The exact historical source revision is unresolved, and diagnostic formatting
remains abstract. The candidate is absent from `overlay.json`; provider
binding, placement, redirects, and package verification remain pending, so it
claims zero package ownership bytes.

## Production routing

The candidate is now routed into the Apollo main overlay byte-identically
(3,130 bytes, SHA-256
`f8c3154fe326878b2f89908555238ddc190a6cecc6c874aeed342624b24d561e`) under the
reviewed apple-clang profile. Provider binding uses the retained database-zero
KVDB blob read/write adapters at `0x004D956C` and `0x004D957E`, matching the
recovered call ABI exactly. Placement appends six relocated leaves to the
overlay: the 32-byte indexed live-byte setter, the 22-byte live-byte writer
carrying a 19-byte `kvOnboardingConfig` key-string read-only closure, the
42-byte update-and-persist wrapper carrying the same key-string closure with
the setter and writer bodies inlined by the reviewed toolchain, the 10-byte
scalar getter, the 8-byte pointer getter, and the 30-byte live-record loader
carrying the key-string closure with the pointer getter inlined. Six `B.W`
entry redirects with NOP fill replace the 286 stock body bytes across
`[0x004A777C,0x004A789A)`; the 54-byte literal tail stays retained stock
data, and all eighteen direct entry calls reach the source leaves through the
redirects. The fixed SRAM record at `0x20000040` is untouched.

Apple Clang 21 overlay/component/package sizes are `146645/3670041/4448535`
with SHA-256 `4df8082fef07195e41a826ae997059f0e0ce16f38576a07e7a5a7c21f32f080c`,
`f464eb05a4b207f3e24958bf2687fa9a217b5601d9ebfa5fefeae2ff753bb94b`, and
`4689b4809ae8521a0a5d5d8e13f54bc216f3991f6395e39a059f6da03be37173`. The
leaves and redirects are gated `apple-clang`; the linux-clang profile keeps
its recorded pins, and linux-clang leaf pins await Linux toolchain
regeneration. Ownership is 286 replaced stock body bytes. The component
build, source package, `open_cfw verify`, and the fail-closed analyzer and
manifest census all pass.
