# G2 bootloader atomic and wrapper source closure

Three authenticated low-level runtime bodies at
`[0x00422AAC,0x00422AD2)` now compile from maintained MIT C at
their exact stock addresses. The 28-byte snapshot helper has SHA-256
`7d5250344a7e889515915c327cf7a10ce0a248a7be5b86784de3f5f3633542cd`;
it saves `PRIMASK`, disables interrupts, samples one volatile word three times,
restores `PRIMASK`, and publishes the three samples to the caller buffer. The
two-byte no-op has SHA-256
`c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8`.
The eight-byte query wrapper has installed SHA-256
`71476a7b2f4e36a5351aca1a4b62c5cbe7f99c4d657bdb42e8932fd47d0041ad`
and unrelocated SHA-256
`c27d4a49b161be022ccdfdf92c47a4912090c2316b87ed52a61f20660f5f4dc3`;
one strict call binds retained provider `0x0041CDB8`.

`runtime_atomic_wrappers_422aac.c` is 1,606 bytes with SHA-256
`fc4ba09be768eb231e1281b4acb95efd9400c7666327b4068b691495d380e9e0`.
Three focused tests pin bodies, caller, provider and successor alignment;
exercise snapshot, no-op and retained-query behavior; and compile both reviewed
Cortex-M55 profiles.

Canonical accounting becomes 20,865 source-owned, 16,528 generated patch, 16
alignment, and 126,431 retained official bytes, including 362 cave bytes and
5,278 exact in-place bytes across 259 source-owned functions and 201 patch
sites. Provider and unsigned-package hashes remain unchanged. The
4,617,928-byte flash plan has SHA-256
`d45be493c3f226ec9b567c576d08194a47f48b67c74b6d0845439f82a7b9965a`
with 6,635 placed, two unresolved, five container-only and six protected
regions.

No hardware operation occurred. Interrupt masking, volatile sampling and the
retained query require authorized Apollo510 evidence, unavailable because no
authorized responsive right temple exists and the left temple must remain
stock. Firmware-wide functional completeness is not claimed; after a retained
two-byte alignment, the next executable body begins at `0x00422AD4`.
