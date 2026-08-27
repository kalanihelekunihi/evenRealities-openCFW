# G2 bootloader address-identified validated runtime-call wrapper source closure

Status: software implemented and production-routed; physical validation blocked.

The complete 50-byte entry `[0x004161CE,0x00416200)` has SHA-256
`e57752e75553f8e047c24eefdd649e5d9f1b2941234488ec1868197557986a55`
and authenticated direct callers at `0x0042E28C` and `0x0042E29C`. It returns
`-6` when the source-owned critical-context predicate is true, returns `-4`
when argument zero is null or argument one is outside the inclusive range
`[1,56]`, and otherwise forwards both exact 32-bit arguments to retained
address `0x0041806E` before returning zero. The address-derived name avoids
assigning unsupported platform meaning to that retained call.

`runtime_call_4161ce.c` is a 1,042-byte GPL-3.0-or-later clean-room
implementation with SHA-256
`4299722e909a534791cca21918dae909fe2ff2918e2f8406e63c91585505f298`.
Apple clang emits a 44-byte leaf at overlay offset 3,310/runtime
`0x00435166`. Its unrelocated SHA-256 is
`8acd2052030d8f7fcb37730da9066f02279202b0aafe79e5d3cec03f0374ff7c`
and its relocated SHA-256 is
`06639fc553e7a802f9bbd7189c2120bb875c9f4574e2e9c6413972a279743d49`.
Strict `R_ARM_THM_CALL` relocations at offsets six and 36 bind the existing
source-owned critical-context leaf and retained address `0x0041806E`. The
stock entry is replaced by `1ef0cabf` plus 23 Thumb NOPs. Homebrew clang
22.1.8 emits the same unrelocated leaf at profile offset 3,300/runtime
`0x0043515C`; its relocated SHA-256 is
`404ea58cf5a930b50f81f9f0f05e7595f134d51fd5fca93b8d75bdc95997c237`.

Host tests pin critical-context precedence, all invalid boundary classes,
valid selectors one and 56, exact full-width argument forwarding, retained
call suppression, and exactly-once retained calls. Both reviewed toolchains
also compile and relocate under fail-closed source, ABI, symbol-type, and
artifact pins.

This extends the runtime tranche to 21 entries at
`[0x00415844,0x00416200)`: 2,456 exact stock bytes, 118 authenticated caller
edges, 2,242 canonical compiled Thumb bytes, and 37 strict relocations. The
canonical overlay is 3,354 bytes with SHA-256
`90a30940c0a370ba1deb8adf5509059eea5c4f2cc5b64378ef27e263013c1d11`.
The 151,954-byte provider hashes to
`7e1ff337739ca6a03055b8603bf905ce1287c843c5defbc5b36496c7781699ca`,
has CRC-32C/MSB `0x08F8673E`, and accounts for 3,347 source, 3,908 patch,
eight alignment, and 144,691 retained authenticated bytes. It ends at
`0x00435192`, leaving 11,886 bytes before Apollo main. The Linux overlay is
3,344 bytes with SHA-256
`9a5db6c89f574d2eba1a4b9a94fa2f446e12418d858646b2b0e3f88e7de34af7`;
its 151,944-byte provider hashes to
`122ff96d81e3d8299688e212235bcd77bb80d72cfecccad21f5e2ed60201907e`.

The canonical unsigned package is 4,733,532 bytes with SHA-256
`8af5d254af31f39141101cd01727f29762664ea236055d27c17d2da2ae1b90f2`.
Its 4,346,204-byte flash plan hashes to
`14c7101201ded90871e47996bb6f834abc77429087dbf7b6dd25dc67d01868d7`
and records 6,260 placed, two unresolved, five container-only, and six
protected regions. The independent Linux package is 4,509,532 bytes with
SHA-256
`9a7252e77517f2417704851f4d8030e51cbb13205ca9f127e424cdddeff880ca`;
its 2,313,376-byte plan hashes to
`7bad01ac648542d0d98e5d58839a4bad0ed4beceeb217d6c34bc4fb2c1008fac`
and records 3,326 placed regions plus the same two unresolved boundaries.

This checkpoint is superseded by
`g2-bootloader-runtime-action-416200-source-closure.md`, which closes the next
complete callable body. No image was signed, installed, flashed, reset, or booted.
Authorized physical validation is blocked because the right temple is
nonresponsive, the left must remain stock, and no responsive authorized unit
or equivalent trace is available. Consequently this closure makes no live
retained-call, caller-path, or concurrency claim and does not declare
bootloader or firmware-wide functional completeness.
