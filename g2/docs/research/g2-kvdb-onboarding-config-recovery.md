# G2 onboarding-config KVDB recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
not production-routed. Run addresses use
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
